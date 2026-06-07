from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_pyproject_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def test_version_check_script_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_versions.py"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert read_pyproject_version() in result.stdout


def test_exported_plugin_metadata_uses_package_version(tmp_path: Path) -> None:
    destination = tmp_path / "bundle"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "plugin",
            "export",
            "--target",
            "codex",
            "--dest",
            str(destination),
            "--json",
        ],
        cwd=ROOT,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    metadata = json.loads((destination / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert metadata["version"] == read_pyproject_version()
