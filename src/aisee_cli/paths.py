"""Canonical and legacy Aisee project paths."""

from __future__ import annotations

from pathlib import Path


def aisee_root(root: Path) -> Path:
    return root / "aisee"


def registry_dir(root: Path) -> Path:
    return aisee_root(root) / "registry"


def cache_dir(root: Path) -> Path:
    return aisee_root(root) / "cache"


def docs_dir(root: Path) -> Path:
    return aisee_root(root) / "docs"


def memory_dir(root: Path) -> Path:
    return aisee_root(root) / "memory"


def hooks_dir(root: Path) -> Path:
    return aisee_root(root) / "hooks"


def legacy_aisee_root(root: Path) -> Path:
    return root / ".aisee"


def legacy_memory_dir(root: Path) -> Path:
    return root / ".memory"


def existing_or_preferred(preferred: Path, legacy: Path) -> Path:
    if preferred.exists() or not legacy.exists():
        return preferred
    return legacy


def sources_path(root: Path) -> Path:
    return existing_or_preferred(registry_dir(root) / "sources.json", legacy_aisee_root(root) / "sources.json")


def id_registry_path(root: Path) -> Path:
    return existing_or_preferred(registry_dir(root) / "id-registry.json", legacy_aisee_root(root) / "id-registry.json")


def context_index_path(root: Path) -> Path:
    return existing_or_preferred(cache_dir(root) / "context-index.json", legacy_aisee_root(root) / "cache" / "context-index.json")


def memory_rules_path(root: Path) -> Path:
    return existing_or_preferred(memory_dir(root) / "rules.md", legacy_memory_dir(root) / "rules.md")


def memory_index_path(root: Path) -> Path:
    return existing_or_preferred(memory_dir(root) / "index.md", legacy_memory_dir(root) / "index.md")

