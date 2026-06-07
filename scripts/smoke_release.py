"""Run release smoke checks against a built and installed wheel."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}")
    return subprocess.run(command, cwd=cwd, env=env, text=True, check=True, capture_output=True)


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


def main() -> int:
    print_output(run([sys.executable, "scripts/check_versions.py"]))

    dist_dir = ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    print_output(run([sys.executable, "-m", "build"]))
    wheel = latest_wheel(dist_dir)
    print(f"Built wheel: {wheel.name}")

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
        print_output(run([str(aisee), "--version"]))
        assert_json_command([str(aisee), "doctor", "--json"], cwd=project_dir)
        assert_json_command([str(aisee), "plugin", "inspect", "--json"], cwd=project_dir)
        assert_json_command([str(aisee), "plugin", "export", "--target", "codex", "--dest", str(export_dir), "--json"], cwd=project_dir)
        assert_json_command([str(aisee), "schemas", "list", "--json"], cwd=project_dir)
        assert_json_command([str(aisee), "schemas", "check", "--json"], cwd=project_dir)

    print("Release smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
