"""Locate Aisee plugin assets for source-checkout development only."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from aisee_cli.marketplace import marketplace_summary

DEV_ASSET_ENV = "AISEE_PLUGIN_ASSET_ROOT"


def repo_asset_root(project_root: Path) -> Path | None:
    root = project_root.resolve()
    return root if is_aisee_source_checkout(root) else None


def first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def explicit_dev_asset_root() -> Path | None:
    value = os.environ.get(DEV_ASSET_ENV)
    if not value:
        return None
    root = Path(value).expanduser().resolve()
    return root if is_aisee_asset_root(root) else None


def is_aisee_source_checkout(root: Path) -> bool:
    manifest = root / ".codex-plugin" / "plugin.json"
    if not manifest.exists() or not (root / "src" / "aisee_cli").is_dir():
        return False
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        return False
    return data.get("name") == "aisee-plugin" and is_aisee_asset_root(root)


def is_aisee_asset_root(root: Path) -> bool:
    return (
        (root / "skills" / "aisee-srs" / "SKILL.md").exists()
        and (root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack").exists()
        and (root / "references").is_dir()
    )


def resolve_source_asset_root(project_root: Path) -> Path | None:
    return explicit_dev_asset_root() or repo_asset_root(project_root)


def missing_asset_error() -> FileNotFoundError:
    return FileNotFoundError(f"Aisee plugin content is not available to the CLI. {marketplace_summary()}")


def resolve_asset_root(project_root: Path) -> Path:
    """Return source checkout assets for development, otherwise fail with a setup hint."""

    source_root = resolve_source_asset_root(project_root)
    if source_root is not None:
        return source_root
    raise missing_asset_error()


def resolve_schema_pack_dir(project_root: Path) -> Path:
    source_root = resolve_source_asset_root(project_root)
    if source_root is not None:
        source_schema_pack = source_root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack"
        return source_schema_pack
    raise missing_asset_error()


def resolve_plugin_metadata(target: str, project_root: Path | None = None) -> Path:
    roots = []
    if project_root is not None:
        source_root = resolve_source_asset_root(project_root)
        if source_root is not None:
            roots.append(source_root)
    if not roots:
        raise missing_asset_error()

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
