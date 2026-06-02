"""Bootstrap planning for Aisee projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.doctor import build_doctor
from aisee_cli.paths import id_registry_path, inspect_layout, sources_path
from aisee_cli.project import rel


def build_bootstrap_plan(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    doctor = build_doctor(root)
    actions = []
    if not (root / "AGENTS.md").exists():
        actions.append(action("create", "AGENTS.md", "Run aisee:init to create the project AI-agent rules entrypoint."))
    openspec_initialized = (root / "openspec" / "config.yaml").exists() and (root / "openspec" / "changes").exists()
    if not openspec_initialized:
        actions.append(action("run", "openspec init", "Run OpenSpec CLI initialization; do not create OpenSpec internals by hand."))
    layout = inspect_layout(root)
    for item in layout["legacy_only"]:
        actions.append(action(
            "migrate",
            f"{item['legacy']} -> {item['canonical']}",
            "Prompt the user first. If the user explicitly asks to migrate, move this legacy Aisee artifact into the canonical aisee/ layout after confirming it is current; bootstrap does not move files automatically.",
        ))
    for item in layout["dual"]:
        actions.append(action(
            "review",
            item["legacy"],
            f"Prompt the user first. {item['canonical']} is authoritative; compare before changing, and only remove or archive this legacy path after the user confirms it is stale.",
        ))
    sources = sources_path(root)
    if not sources.exists():
        actions.append(action("create", rel(root, sources), "Create empty sources registry."))
    registry = id_registry_path(root)
    if not registry.exists():
        actions.append(action("create", rel(root, registry), "Create empty ID lifecycle registry."))
    if not (root / "openspec" / "schemas").exists():
        actions.append(action("install", "openspec/schemas", "Install selected schema pack with aisee schemas install."))

    return {
        "status": "ready" if actions else "noop",
        "writes": False,
        "doctor_status": doctor["status"],
        "actions": actions,
        "layout": layout,
        "meta": {
            "command": "aisee bootstrap --plan --json",
            "apply_supported": False,
        },
    }


def build_bootstrap_apply_response() -> dict[str, Any]:
    return {
        "status": "blocked",
        "writes": False,
        "issues": [
            {
                "code": "BOOTSTRAP_APPLY_NOT_IMPLEMENTED",
                "severity": "blocker",
                "message": "bootstrap --apply is intentionally not implemented yet; use --plan and explicit setup commands",
            }
        ],
        "summary": {"blocker": 1, "risk": 0, "info": 0, "total": 1},
    }


def action(kind: str, path: str, reason: str) -> dict[str, str]:
    return {
        "kind": kind,
        "path": path,
        "reason": reason,
    }
