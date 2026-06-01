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
    schema = pack["facts"]["parsed"]["schema"]
    task_state = pack["facts"]["derived"]["task_state"]
    if archive["status"] == "archive-ready":
        stage = "archive-ready"
        recommended = ["openspec archive"]
    elif verify["status"] in {"ready", "risk"} and (task_state["done"] or not schema.get("tasks_required")):
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
        "schema": {
            "name": schema.get("name"),
            "source_map_required": schema.get("source_map_required"),
            "tasks_required": schema.get("tasks_required"),
            "archive_tracks": schema.get("archive_tracks"),
        },
        "inputs": {
            "source_map": pack["facts"]["parsed"]["source_map"]["status"],
            "task_state": task_state,
            "implementation_references": pack["facts"]["derived"]["implementation_references"],
            "evidence": summarize_evidence(pack["evidence"]),
        },
        "checks": {
            "verify": {
                "status": verify["status"],
                "summary": verify["summary"],
                "blocker_codes": issue_codes(verify["blockers"]),
                "warning_codes": issue_codes(verify["warnings"]),
            },
            "archive": {
                "status": archive["status"],
                "summary": archive["summary"],
                "blocker_codes": issue_codes(archive["blockers"]),
                "warning_codes": issue_codes(archive["warnings"]),
            },
        },
        "required_commands": required_commands(change, stage),
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
        "schema": None,
        "inputs": {},
        "checks": {},
        "required_commands": required_commands(change, stage),
        "guardrails": [
            "do not create a parallel source of truth",
            "schema is decided by aisee:change-plan per change",
        ],
        "meta": {
            "command": "aisee flow inspect --json",
        },
    }


def issue_codes(items: list[dict[str, Any]]) -> list[str]:
    return [str(item.get("code") or "UNKNOWN") for item in items]


def summarize_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "openspec_validate": evidence.get("openspec_validate"),
        "ce_doc_review_count": len(evidence.get("ce_doc_review", [])),
        "ce_code_review_count": len(evidence.get("ce_code_review", [])),
        "test_count": len(evidence.get("tests", [])),
        "manual_verification_count": len(evidence.get("manual_verification", [])),
        "docsite": summarize_domain_evidence(evidence.get("docsite", {})),
        "infra": summarize_domain_evidence(evidence.get("infra", {})),
        "security": summarize_domain_evidence(evidence.get("security", {})),
        "quick_fix": summarize_domain_evidence(evidence.get("quick_fix", {})),
    }


def summarize_domain_evidence(domain: dict[str, Any]) -> dict[str, int]:
    return {
        str(category): len(paths)
        for category, paths in domain.items()
        if isinstance(paths, list) and paths
    }


def required_commands(change: str | None, stage: str) -> list[str]:
    if not change:
        return ["aisee doctor --json", "aisee flow inspect --json"]
    commands = [
        f"aisee change inspect {change} --json",
        f"aisee change author-check {change} --json",
        f"aisee gaps --change {change} --json",
        f"aisee change verify-check {change} --json",
        f"aisee change archive-check {change} --json",
    ]
    if stage == "implementation-ready":
        commands.append(f"aisee context pack --change {change} --for ce-work --json")
    elif stage in {"implemented", "verified", "archive-ready"}:
        commands.append(f"aisee context pack --change {change} --for aisee-verify --json")
    return commands
