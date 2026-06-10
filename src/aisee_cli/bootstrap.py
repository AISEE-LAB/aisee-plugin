"""Bootstrap planning for Aisee projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.doctor import build_doctor
from aisee_cli.marketplace import MARKETPLACE_ADD_COMMAND, PLUGIN_ADD_COMMAND
from aisee_cli.paths import inspect_layout, sources_path
from aisee_cli.project import rel


def build_bootstrap_plan(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    doctor = build_doctor(root)
    actions = []
    if not doctor["openspec"]["cli"]["available"]:
        actions.append(action("install", "openspec-cli", "Install or expose the OpenSpec CLI before running OpenSpec commands."))
    if doctor["compound"]["status"] != "ok":
        actions.append(action("install", "compound-engineering-plugin", "Install or enable Compound Engineering when CE review/work skills are part of the workflow."))
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
    if doctor["codex_marketplace"]["status"] != "ok":
        actions.append(action(
            "install",
            "aisee-plugin marketplace",
            f"Install Aisee plugin content with `{MARKETPLACE_ADD_COMMAND}` and `{PLUGIN_ADD_COMMAND}`.",
        ))
    if not (root / "openspec" / "schemas").exists():
        actions.append(action(
            "create",
            "openspec/schemas",
            "Use the marketplace-installed `aisee:schema-pack` skill to initialize project schema packs; bootstrap only reports the missing project directory.",
        ))

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


def action(kind: str, path: str, reason: str) -> dict[str, str]:
    return {
        "kind": kind,
        "path": path,
        "reason": reason,
    }
