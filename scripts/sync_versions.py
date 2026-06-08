"""Sync package, CLI, and plugin metadata versions from pyproject.toml."""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]

VERSION_FILES = [
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "src/aisee_plugin_assets/plugin-metadata/codex/plugin.json",
    "src/aisee_plugin_assets/plugin-metadata/claude/plugin.json",
    "src/aisee_plugin_assets/plugin-metadata/cursor/plugin.json",
]


def pyproject_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def sync_cli_version(version: str) -> None:
    path = ROOT / "src" / "aisee_cli" / "__init__.py"
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(r'__version__ = "[^"]+"', f'__version__ = "{version}"', text)
    if count != 1:
        raise RuntimeError(f"could not update __version__ in {path}")
    path.write_text(updated, encoding="utf-8")


def sync_metadata_version(path: str, version: str) -> None:
    full_path = ROOT / path
    data = json.loads(full_path.read_text(encoding="utf-8"))
    data["version"] = version
    full_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    version = pyproject_version()
    sync_cli_version(version)
    for path in VERSION_FILES:
        sync_metadata_version(path, version)
    print(f"Synced versions to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
