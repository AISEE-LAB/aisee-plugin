"""Shared JSON output helpers for the Aisee CLI."""

from __future__ import annotations

import json
import sys
from typing import Any


def summarize_issues(issues: list[dict[str, Any]]) -> dict[str, int]:
    blocker = sum(1 for item in issues if item.get("severity") == "blocker")
    risk = sum(1 for item in issues if item.get("severity") == "risk")
    info = sum(1 for item in issues if item.get("severity") == "info")
    return {
        "blocker": blocker,
        "risk": risk,
        "info": info,
        "total": len(issues),
    }


def status_from_issues(issues: list[dict[str, Any]], ok_status: str = "ok") -> str:
    summary = summarize_issues(issues)
    if summary["blocker"]:
        return "blocked"
    if summary["risk"]:
        return "risk"
    return ok_status


def issue(code: str, severity: str, message: str, path: str | None = None) -> dict[str, str]:
    result = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if path:
        result["path"] = path
    return result


def print_json(data: dict[str, Any], *, stderr: bool = False) -> None:
    stream = sys.stderr if stderr else sys.stdout
    print(json.dumps(data, ensure_ascii=False, indent=2), file=stream)


def error_response(message: str, code: str = "CLI_ERROR") -> dict[str, Any]:
    return {
        "status": "error",
        "message": message,
        "issues": [issue(code, "blocker", message)],
    }


def exit_code_for(result: dict[str, Any], *, fail_on_blocker: bool = False) -> int:
    if result.get("status") == "error":
        return 2
    if not fail_on_blocker:
        return 0
    summary = result.get("summary")
    if isinstance(summary, dict) and int(summary.get("blocker", 0) or 0) > 0:
        return 1
    issues = result.get("issues")
    if isinstance(issues, list) and any(item.get("severity") == "blocker" for item in issues if isinstance(item, dict)):
        return 1
    return 0
