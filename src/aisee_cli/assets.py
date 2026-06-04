"""Locate Aisee plugin assets in source checkouts and installed packages."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable

ASSET_PACKAGE = "aisee_plugin_assets"


def repo_asset_root(project_root: Path) -> Path:
    return project_root


def packaged_asset_root() -> Path:
    root = resources.files(ASSET_PACKAGE)
    return Path(str(root))


def first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def resolve_asset_root(project_root: Path) -> Path:
    """Return source checkout assets when present, otherwise installed package assets."""

    source_root = repo_asset_root(project_root)
    if (
        (source_root / "skills" / "aisee-srs" / "SKILL.md").exists()
        and (source_root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack").exists()
    ):
        return source_root
    return packaged_asset_root()


def resolve_schema_pack_dir(project_root: Path) -> Path:
    source_schema_pack = project_root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack"
    if source_schema_pack.exists():
        return source_schema_pack
    return packaged_asset_root() / "skills" / "aisee-schema-pack" / "assets" / "schema-pack"


def resolve_plugin_metadata(target: str, project_root: Path | None = None) -> Path:
    roots = []
    if project_root is not None:
        roots.append(repo_asset_root(project_root))
    roots.append(packaged_asset_root())

    candidates: list[Path] = []
    for root in roots:
        if target == "codex":
            candidates.append(root / ".codex-plugin" / "plugin.json")
            candidates.append(root / "plugin-metadata" / "codex" / "plugin.json")
        elif target == "claude":
            candidates.append(root / ".claude-plugin" / "plugin.json")
            candidates.append(root / "plugin-metadata" / "claude" / "plugin.json")
        elif target == "cursor":
            candidates.append(root / ".cursor-plugin" / "plugin.json")
            candidates.append(root / "plugin-metadata" / "cursor" / "plugin.json")
        else:
            raise ValueError(f"unsupported plugin target: {target}")

    found = first_existing(candidates)
    if found is None:
        raise ValueError(f"plugin metadata not found for target: {target}")
    return found
