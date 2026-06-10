"""Run release smoke checks against a built and installed wheel."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PACKAGE_CONTENT_PARTS = (
    "/plugins/aisee-plugin/",
    "/skills/",
    "/references/",
    "/team-knowledge/",
    "/plugin-metadata/",
    "schema-pack/",
)


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode != 0:
        print_output(result)
        raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)
    return result


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_aisee(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "aisee.exe"
    return venv_dir / "bin" / "aisee"


def pipx_aisee(bin_dir: Path) -> Path:
    if os.name == "nt":
        return bin_dir / "aisee.exe"
    return bin_dir / "aisee"


def latest_wheel(dist_dir: Path) -> Path:
    wheels = sorted(dist_dir.glob("aisee_plugin-*.whl"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not wheels:
        raise RuntimeError("dist/ 中没有 aisee_plugin wheel，请确认 python -m build 成功。")
    return wheels[0]


def latest_sdist(dist_dir: Path) -> Path:
    sdists = sorted(dist_dir.glob("aisee_plugin-*.tar.gz"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not sdists:
        raise RuntimeError("dist/ 中没有 aisee_plugin sdist，请确认 python -m build 成功。")
    return sdists[0]


def assert_cli_only_archive_contents(wheel: Path, sdist: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        assert_no_forbidden_package_content(wheel, archive.namelist())
    with tarfile.open(sdist, "r:gz") as archive:
        assert_no_forbidden_package_content(sdist, archive.getnames())


def assert_no_forbidden_package_content(archive_path: Path, names: list[str]) -> None:
    blocked = [
        name
        for name in names
        if any(part in f"/{name}" for part in FORBIDDEN_PACKAGE_CONTENT_PARTS)
    ]
    if blocked:
        sample = "\n".join(blocked[:20])
        raise RuntimeError(f"{archive_path.name} contains plugin content that must not ship in the PyPI package:\n{sample}")


def assert_json_command(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> dict[str, object]:
    result = run(command, cwd=cwd, env=env)
    print_output(result)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"命令没有输出合法 JSON: {' '.join(command)}") from exc


def assert_invalid_choice(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode != 2 or "invalid choice" not in result.stderr:
        print_output(result)
        raise RuntimeError(f"命令应返回 argparse invalid choice: {' '.join(command)}")
    print_output(result)
    return result


def run_venv_smoke(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="aisee-release-smoke-") as temp:
        temp_dir = Path(temp)
        venv_dir = temp_dir / "venv"
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        venv.EnvBuilder(with_pip=True).create(venv_dir)
        py = venv_python(venv_dir)
        aisee = venv_aisee(venv_dir)

        print_output(run([str(py), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)]))
        run_cli_smoke(aisee, project_dir)


def run_pipx_smoke(wheel: Path) -> int:
    pipx = shutil.which("pipx")
    if not pipx:
        print("Missing command: pipx", file=sys.stderr)
        print("Install pipx before running the pipx release smoke check.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="aisee-pipx-smoke-") as temp:
        temp_dir = Path(temp)
        home_dir = temp_dir / "pipx-home"
        bin_dir = temp_dir / "pipx-bin"
        man_dir = temp_dir / "pipx-man"
        project_dir = temp_dir / "project"
        project_dir.mkdir()
        bin_dir.mkdir()
        man_dir.mkdir()

        env = os.environ.copy()
        env.update(
            {
                "PIPX_HOME": str(home_dir),
                "PIPX_BIN_DIR": str(bin_dir),
                "PIPX_MAN_DIR": str(man_dir),
                "PIPX_DEFAULT_PYTHON": sys.executable,
            }
        )

        print_output(run([pipx, "install", "--python", sys.executable, str(wheel)], env=env))
        run_cli_smoke(pipx_aisee(bin_dir), project_dir)
    return 0


def run_cli_smoke(aisee: Path, project_dir: Path) -> None:
    agent_home = project_dir.parent / "agent-home"
    codex_home = agent_home / ".codex"
    codex_home.mkdir(parents=True)
    env = os.environ.copy()
    env.update({
        "HOME": str(agent_home),
        "CODEX_HOME": str(codex_home),
        "AISEE_AGENT_RUNTIME": "codex",
    })

    print_output(run([str(aisee), "--version"], env=env))
    doctor = assert_json_command([str(aisee), "doctor", "--json"], cwd=project_dir, env=env)
    inspect = assert_json_command([str(aisee), "plugin", "inspect", "--json"], cwd=project_dir, env=env)
    export_dest = project_dir / "plugin-bundle"
    export = assert_invalid_choice(
        [str(aisee), "plugin", "export", "--target", "codex", "--dest", str(export_dest), "--json"],
        cwd=project_dir,
        env=env,
    )
    schemas = assert_json_command([str(aisee), "schemas", "list", "--json"], cwd=project_dir, env=env)
    assert_json_command([str(aisee), "schemas", "check", "--json"], cwd=project_dir, env=env)
    assert_json_command([str(aisee), "schemas", "format", "--check", "--json"], cwd=project_dir, env=env)
    if "codex_marketplace" not in doctor:
        raise RuntimeError("doctor output did not include codex_marketplace")
    if inspect.get("mode") != "cli-only":
        raise RuntimeError("plugin inspect should report CLI-only mode in installed wheel")
    if "export" not in export.stderr:
        raise RuntimeError("plugin export invalid choice output should mention the removed subcommand")
    if export_dest.exists():
        raise RuntimeError("plugin export invalid choice should not create the destination directory")
    if schemas.get("source") is not None:
        raise RuntimeError("schema list should not report packaged schema source in installed wheel")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run release smoke checks against a built and installed wheel.")
    parser.add_argument("--with-pipx", action="store_true", help="also install the built wheel through pipx in an isolated temp home")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print_output(run([sys.executable, "scripts/check_versions.py"]))

    if find_spec("build") is None:
        print("Missing Python module: build", file=sys.stderr)
        print("Install it before release smoke checks:", file=sys.stderr)
        print("  python -m pip install build", file=sys.stderr)
        return 2

    dist_dir = ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    print_output(run([sys.executable, "-m", "build"]))
    wheel = latest_wheel(dist_dir)
    sdist = latest_sdist(dist_dir)
    assert_cli_only_archive_contents(wheel, sdist)
    print(f"Built wheel: {wheel.name}")

    run_venv_smoke(wheel)
    if args.with_pipx:
        pipx_status = run_pipx_smoke(wheel)
        if pipx_status != 0:
            return pipx_status

    print("Release smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
