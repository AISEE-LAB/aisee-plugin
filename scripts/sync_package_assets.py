"""Mirror plugin resources into the Python package asset directory."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "src" / "aisee_plugin_assets"

RESOURCE_DIRS = {
    "skills": ASSET_ROOT / "skills",
    "references": ASSET_ROOT / "references",
    "docs/architecture": ASSET_ROOT / "docs" / "architecture",
}

PLUGIN_METADATA = {
    ".codex-plugin/plugin.json": ASSET_ROOT / "plugin-metadata" / "codex" / "plugin.json",
    ".claude-plugin/plugin.json": ASSET_ROOT / "plugin-metadata" / "claude" / "plugin.json",
    ".cursor-plugin/plugin.json": ASSET_ROOT / "plugin-metadata" / "cursor" / "plugin.json",
}


def ignore(_: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".DS_Store"}
    ignored.update(name for name in names if name.endswith(".pyc"))
    ignored.update(name for name in names if name == "tests")
    return ignored


def sync_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=ignore)


def sync_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> int:
    for source, target in RESOURCE_DIRS.items():
        sync_tree(ROOT / source, target)
    for source, target in PLUGIN_METADATA.items():
        sync_file(ROOT / source, target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
