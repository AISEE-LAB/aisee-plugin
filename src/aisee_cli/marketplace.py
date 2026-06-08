"""Codex marketplace setup hints for Aisee CLI."""

from __future__ import annotations

from typing import Any

from aisee_cli.output import issue


MARKETPLACE_SOURCE = "AISEE-LAB/aisee-plugin"
MARKETPLACE_ADD_COMMAND = f"codex plugin marketplace add {MARKETPLACE_SOURCE} --ref main"
PLUGIN_ADD_COMMAND = "codex plugin add aisee-plugin@aisee-plugin"


def marketplace_setup_hint() -> dict[str, Any]:
    return {
        "runtime": "codex",
        "marketplace_source": MARKETPLACE_SOURCE,
        "commands": [
            MARKETPLACE_ADD_COMMAND,
            PLUGIN_ADD_COMMAND,
        ],
        "writes_codex_state": False,
        "note": "Run these commands yourself to let Codex install the Aisee plugin content from GitHub.",
    }


def marketplace_issue(code: str, severity: str, message: str, path: str | None = None) -> dict[str, Any]:
    result = issue(code, severity, message, path)
    result["setup_hint"] = marketplace_setup_hint()
    return result


def marketplace_summary() -> str:
    return f"Add the Aisee Codex marketplace with `{MARKETPLACE_ADD_COMMAND}`, then run `{PLUGIN_ADD_COMMAND}`."
