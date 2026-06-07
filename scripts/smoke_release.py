"""Run release smoke checks against a built and installed wheel."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def assert_json_command(command: list[str], *, cwd: Path = ROOT) -> dict[str, object]:
    result = run(command, cwd=cwd)
    print_output(result)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"命令没有输出合法 JSON: {' '.join(command)}") from exc


def run_venv_smoke(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="aisee-release-smoke-") as temp:
        temp_dir = Path(temp)
        venv_dir = temp_dir / "venv"
        export_dir = temp_dir / "plugin-bundle"
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        venv.EnvBuilder(with_pip=True).create(venv_dir)
        py = venv_python(venv_dir)
        aisee = venv_aisee(venv_dir)

        print_output(run([str(py), "-m", "pip", "install", "--disable-pip-version-check", str(wheel)]))
        run_cli_smoke(aisee, project_dir, export_dir)


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
        export_dir = temp_dir / "plugin-bundle"
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
        run_cli_smoke(pipx_aisee(bin_dir), project_dir, export_dir)
    return 0


def run_cli_smoke(aisee: Path, project_dir: Path, export_dir: Path) -> None:
    print_output(run([str(aisee), "--version"]))
    assert_json_command([str(aisee), "doctor", "--json"], cwd=project_dir)
    assert_json_command([str(aisee), "plugin", "inspect", "--json"], cwd=project_dir)
    assert_json_command([str(aisee), "plugin", "export", "--target", "codex", "--dest", str(export_dir), "--json"], cwd=project_dir)
    assert_json_command([str(aisee), "schemas", "list", "--json"], cwd=project_dir)
    assert_json_command([str(aisee), "schemas", "check", "--json"], cwd=project_dir)


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
