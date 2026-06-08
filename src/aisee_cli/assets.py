"""Locate Aisee plugin assets without bundling them in the PyPI package."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from aisee_cli.marketplace import marketplace_summary

DEV_ASSET_ENV = "AISEE_PLUGIN_ASSET_ROOT"
RUNTIME_ENV = "AISEE_AGENT_RUNTIME"
DEFAULT_RUNTIME = "codex"
SUPPORTED_RUNTIMES = {"codex", "claude", "cursor", "agents", "none"}


def repo_asset_root(project_root: Path) -> Path | None:
    root = project_root.resolve()
    if not (root / "src" / "aisee_cli").is_dir():
        return None
    plugin_root = root / "plugins" / "aisee-plugin"
    return plugin_root if is_aisee_asset_root(plugin_root) else None


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


def selected_agent_runtime() -> str:
    value = os.environ.get(RUNTIME_ENV, DEFAULT_RUNTIME).strip().lower()
    return value if value in SUPPORTED_RUNTIMES else DEFAULT_RUNTIME


def is_aisee_source_checkout(root: Path) -> bool:
    manifest = root / ".codex-plugin" / "plugin.json"
    if not manifest.exists():
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
    return explicit_dev_asset_root() or repo_asset_root(project_root) or installed_asset_root()


def installed_asset_root() -> Path | None:
    runtime = selected_agent_runtime()
    if runtime == "none":
        return None
    return first_existing(installed_asset_candidates(runtime))


def installed_asset_candidates(runtime: str) -> list[Path]:
    home = Path.home()
    if runtime == "codex":
        codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
        return valid_asset_candidates([
            *codex_marketplace_candidates(codex_home),
            *versioned_plugin_cache_candidates(codex_home / "plugins" / "cache"),
        ])
    if runtime == "claude":
        return valid_asset_candidates(versioned_plugin_cache_candidates(home / ".claude" / "plugins" / "cache"))
    if runtime == "cursor":
        return valid_asset_candidates(versioned_plugin_cache_candidates(home / ".cursor" / "plugins" / "cache"))
    if runtime == "agents":
        return valid_asset_candidates(versioned_plugin_cache_candidates(home / ".agents" / "plugins" / "cache"))
    return []


def valid_asset_candidates(candidates: Iterable[Path]) -> list[Path]:
    return [path for path in candidates if is_aisee_asset_root(path)]


def codex_marketplace_candidates(codex_home: Path) -> list[Path]:
    config = read_toml(codex_home / "config.toml")
    marketplace_names = ["aisee-plugin"]
    marketplaces = config.get("marketplaces") if isinstance(config, dict) else None
    if isinstance(marketplaces, dict):
        for name, item in marketplaces.items():
            if isinstance(name, str) and isinstance(item, dict):
                values = [str(item.get(key) or "") for key in ("source", "repo", "url", "path")]
                if any("AISEE-LAB/aisee-plugin" in value or "aisee-plugin" == value for value in values):
                    marketplace_names.append(name)
    return [
        codex_home / ".tmp" / "marketplaces" / name / "plugins" / "aisee-plugin"
        for name in dict.fromkeys(marketplace_names)
    ]


def versioned_plugin_cache_candidates(cache_root: Path) -> list[Path]:
    candidates = [
        cache_root / "aisee-plugin" / "aisee-plugin",
        cache_root / "AISEE-LAB" / "aisee-plugin",
    ]
    result: list[Path] = []
    for candidate in candidates:
        result.append(candidate)
        if candidate.is_dir():
            result.extend(sorted((item for item in candidate.iterdir() if item.is_dir()), reverse=True))
    return result


def read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
        import tomli as tomllib
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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
