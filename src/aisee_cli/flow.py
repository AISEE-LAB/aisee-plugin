"""Workflow state inspection for Aisee projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.change_checks import build_archive_check, build_verify_check
from aisee_cli.context_pack import build_context_pack
from aisee_cli.doctor import build_doctor


def build_flow(project_root: Path, *, change: str | None = None) -> dict[str, Any]:
    root = project_root.resolve()
    doctor = build_doctor(root)
    if doctor["status"] == "blocked":
        return flow_result("uninitialized", ["aisee:setup"], ["doctor has blockers"], doctor, change)

    if not change:
        sources = doctor["aisee"]["sources"]
        if sources["sources"]:
            return flow_result("context-ready", ["aisee:change-plan"], [], doctor, change)
        return flow_result("idea", ["aisee:srs"], ["no change selected"], doctor, change)

    change_path = root / "openspec" / "changes" / change
    if not change_path.exists():
        return flow_result("change-planned", ["aisee:change-author"], [f"change is missing: {change}"], doctor, change)

    pack = build_context_pack(root, change, "ce-work")
    verify = build_verify_check(root, change)
    archive = build_archive_check(root, change)
    if archive["status"] == "archive-ready":
        stage = "archive-ready"
        recommended = ["openspec archive"]
    elif verify["status"] in {"ready", "risk"} and pack["facts"]["derived"]["task_state"]["done"]:
        stage = "verified" if verify["status"] == "ready" else "implemented"
        recommended = ["aisee:archive-guard"]
    elif pack["facts"]["derived"].get("execution", {}).get("requires_ce_plan"):
        stage = "change-authored"
        recommended = ["aisee:implementation-bridge", "ce-plan"]
    else:
        stage = "implementation-ready"
        recommended = ["aisee:implementation-bridge", "ce-work"]

    blocking = [item["message"] for item in archive["blockers"]]
    return {
        "status": "ok",
        "stage": stage,
        "change": change,
        "recommended_path": recommended,
        "blocking": blocking,
        "doctor": {"status": doctor["status"], "summary": doctor["summary"]},
        "checks": {
            "verify": {"status": verify["status"], "summary": verify["summary"]},
            "archive": {"status": archive["status"], "summary": archive["summary"]},
        },
        "guardrails": [
            "do not create a parallel source of truth",
            "do not enter ce-work without a single explicit change",
            "write durable conclusions back to OpenSpec artifacts",
        ],
        "meta": {
            "command": f"aisee flow inspect --change {change} --json",
        },
    }


def flow_result(stage: str, recommended: list[str], blocking: list[str], doctor: dict[str, Any], change: str | None) -> dict[str, Any]:
    return {
        "status": "ok" if not blocking else "blocked",
        "stage": stage,
        "change": change,
        "recommended_path": recommended,
        "blocking": blocking,
        "doctor": {"status": doctor["status"], "summary": doctor["summary"]},
        "guardrails": [
            "do not create a parallel source of truth",
            "schema is decided by aisee:change-plan per change",
        ],
        "meta": {
            "command": "aisee flow inspect --json",
        },
    }
