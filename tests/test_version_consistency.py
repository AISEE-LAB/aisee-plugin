from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


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


def test_marketplace_and_plugin_metadata_use_package_version() -> None:
    expected = read_pyproject_version()
    for path in (
        ".agents/plugins/marketplace.json",
        "plugins/aisee-plugin/.codex-plugin/plugin.json",
        "plugins/aisee-plugin/.claude-plugin/plugin.json",
        "plugins/aisee-plugin/.cursor-plugin/plugin.json",
    ):
        metadata = json.loads((ROOT / path).read_text(encoding="utf-8"))
        assert metadata["version"] == expected
