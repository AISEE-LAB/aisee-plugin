"""Read-only project health checks for Aisee CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.id_registry import check_registry
from aisee_cli.index import index_path
from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.paths import inspect_layout
from aisee_cli.project import inspect_project_rules, rel
from aisee_cli.schema_pack import list_schema_packs
from aisee_cli.sources import check_sources


def build_doctor(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    issues: list[dict[str, Any]] = []
    rules = inspect_project_rules(root)
    if not rules["primary"]:
        issues.append(issue("AGENTS_MISSING", "risk", "AGENTS.md is missing", "AGENTS.md"))

    openspec_config = root / "openspec" / "config.yaml"
    openspec_changes = root / "openspec" / "changes"
    if not openspec_config.exists():
        issues.append(issue("OPENSPEC_CONFIG_MISSING", "blocker", "openspec/config.yaml is missing", "openspec/config.yaml"))
    if not openspec_changes.exists():
        issues.append(issue("OPENSPEC_CHANGES_MISSING", "blocker", "openspec/changes is missing", "openspec/changes"))

    layout = inspect_layout(root)
    for item in layout["legacy_only"]:
        issues.append(issue(
            "AISEE_LEGACY_PATH",
            "risk",
            f"{item['legacy']} is used as a legacy fallback; migrate it to {item['canonical']}",
            item["legacy"],
        ))
    for item in layout["dual"]:
        issues.append(issue(
            "AISEE_DUAL_PATH",
            "risk",
            f"both {item['canonical']} and legacy {item['legacy']} exist; {item['canonical']} is authoritative and legacy may be stale",
            item["legacy"],
        ))

    sources = check_sources(root)
    registry = check_registry(root)
    schemas = list_schema_packs(root)
    issues.extend(item for item in sources["issues"] if item.get("severity") == "blocker")
    issues.extend(item for item in registry["issues"] if item.get("severity") == "blocker")
    issues.extend(item for item in schemas["issues"] if item.get("severity") == "blocker")

    return {
        "status": status_from_issues(issues),
        "project_rules": rules,
        "openspec": {
            "config": rel(root, openspec_config) if openspec_config.exists() else None,
            "changes": rel(root, openspec_changes) if openspec_changes.exists() else None,
            "initialized": openspec_config.exists() and openspec_changes.exists(),
        },
        "aisee": {
            "layout": layout,
            "sources": sources,
            "id_registry": registry,
            "schemas": schemas,
            "context_index": {
                "path": rel(root, index_path(root)),
                "exists": index_path(root).exists(),
                "fact_source": False,
            },
        },
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "aisee doctor --json",
            "writes": False,
        },
    }
