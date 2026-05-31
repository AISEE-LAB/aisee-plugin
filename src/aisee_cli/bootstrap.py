"""Bootstrap planning for Aisee projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.doctor import build_doctor


def build_bootstrap_plan(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    doctor = build_doctor(root)
    actions = []
    if not (root / "AGENTS.md").exists():
        actions.append(action("create", "AGENTS.md", "Create project AI-agent rules entrypoint."))
    if not (root / "openspec" / "config.yaml").exists():
        actions.append(action("initialize", "openspec/config.yaml", "Run OpenSpec init or create project config."))
    if not (root / "openspec" / "changes").exists():
        actions.append(action("create", "openspec/changes", "Create OpenSpec active changes directory."))
    if not (root / ".aisee" / "sources.json").exists():
        actions.append(action("create", ".aisee/sources.json", "Create empty sources registry."))
    if not (root / ".aisee" / "id-registry.json").exists():
        actions.append(action("create", ".aisee/id-registry.json", "Create empty ID lifecycle registry."))
    if not (root / "openspec" / "schemas").exists():
        actions.append(action("install", "openspec/schemas", "Install selected schema pack with aisee schemas install."))

    return {
        "status": "ready" if actions else "noop",
        "writes": False,
        "doctor_status": doctor["status"],
        "actions": actions,
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
