"""Canonical and legacy Aisee project paths."""

from __future__ import annotations

from pathlib import Path
from typing import Any


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


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


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


def inspect_layout(root: Path) -> dict[str, Any]:
    """Inspect canonical Aisee layout and legacy fallback paths without writing."""

    checks = [
        layout_check(root, "sources", registry_dir(root) / "sources.json", legacy_aisee_root(root) / "sources.json"),
        layout_check(root, "id_registry", registry_dir(root) / "id-registry.json", legacy_aisee_root(root) / "id-registry.json"),
        layout_check(root, "context_index", cache_dir(root) / "context-index.json", legacy_aisee_root(root) / "cache" / "context-index.json"),
        layout_check(root, "memory_rules", memory_dir(root) / "rules.md", legacy_memory_dir(root) / "rules.md"),
        layout_check(root, "memory_index", memory_dir(root) / "index.md", legacy_memory_dir(root) / "index.md"),
        layout_check(root, "hooks", hooks_dir(root), legacy_aisee_root(root) / "hooks"),
        layout_check(root, "requirements_docs", docs_dir(root) / "requirements", root / "docs" / "requirements"),
        layout_check(root, "ui_content_docs", docs_dir(root) / "ui-content", root / "docs" / "ui-content"),
        layout_check(root, "architecture_docs", docs_dir(root) / "architecture", root / "docs" / "architecture"),
        layout_check(root, "change_plan_docs", docs_dir(root) / "change-plan", root / "docs" / "change-plan"),
        layout_check(root, "reflect_docs", docs_dir(root) / "reflect", root / "docs" / "reflect"),
    ]
    return {
        "canonical_root": rel(root, aisee_root(root)),
        "legacy_root": rel(root, legacy_aisee_root(root)),
        "checks": checks,
        "legacy_only": [item for item in checks if item["state"] == "legacy-only"],
        "dual": [item for item in checks if item["state"] == "dual"],
        "policy": {
            "new_projects": "write canonical aisee/ layout only",
            "legacy_projects": "read legacy paths as fallback only",
            "dual_paths": "prefer canonical aisee/ paths and treat legacy paths as potentially stale",
            "migration": "doctor/bootstrap only report migration hints; no automatic file move",
        },
    }


def layout_check(root: Path, name: str, canonical: Path, legacy: Path) -> dict[str, Any]:
    canonical_exists = canonical.exists()
    legacy_exists = legacy.exists()
    if canonical_exists and legacy_exists:
        state = "dual"
        active = canonical
    elif canonical_exists:
        state = "canonical"
        active = canonical
    elif legacy_exists:
        state = "legacy-only"
        active = legacy
    else:
        state = "missing"
        active = canonical
    return {
        "name": name,
        "state": state,
        "active": rel(root, active),
        "canonical": rel(root, canonical),
        "legacy": rel(root, legacy),
    }
