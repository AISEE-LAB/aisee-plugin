"""Workflow state inspection for Aisee projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.author_check import build_author_check
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
    author = build_author_check(root, change)
    verify = build_verify_check(root, change)
    archive = build_archive_check(root, change)
    schema = pack["facts"]["parsed"]["schema"]
    task_state = pack["facts"]["derived"]["task_state"]
    execution = pack["facts"]["derived"].get("execution", {})
    pack_gap_summary = summarize_pack_gaps(pack["gaps"])
    implementation_gap_summary = summarize_pack_gaps(relevant_implementation_gaps(pack["gaps"], schema))
    if author["status"] == "blocked":
        stage = "change-authored"
        recommended = ["aisee:change-author"]
    elif archive["status"] == "archive-ready":
        stage = "archive-ready"
        recommended = ["openspec archive"]
    elif implementation_gap_summary["blocker"]:
        stage = "change-authored"
        recommended = ["aisee:change-author"]
    elif verify["status"] in {"ready", "risk"} and (task_state["done"] or not schema.get("tasks_required")):
        stage = "verified" if verify["status"] == "ready" else "implemented"
        recommended = ["aisee:archive-guard"]
    elif execution.get("requires_ce_plan"):
        stage = "change-authored"
        recommended = ["aisee:implementation-bridge", "ce-plan"]
    else:
        stage = "implementation-ready"
        recommended = ["aisee:implementation-bridge", "ce-work"]

    blocking_sources = author["blockers"] + relevant_implementation_gaps(pack["gaps"], schema)
    if stage in {"implemented", "verified", "archive-ready"}:
        blocking_sources += archive["blockers"]
    blocking = [item["message"] for item in blocking_sources if item.get("severity") == "blocker"]
    source_map = pack["facts"]["parsed"]["source_map"]
    return {
        "status": flow_status(
            stage,
            blocking,
            author=author,
            verify=verify,
            archive=archive,
            gap_summary=implementation_gap_summary,
        ),
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
            "source_map": source_map["status"],
            "source_map_parse_level": source_map.get("parse_level"),
            "source_map_issue_codes": issue_codes(source_map.get("issues", [])),
            "task_state": task_state,
            "implementation_references": pack["facts"]["derived"]["implementation_references"],
            "execution": execution,
            "evidence": summarize_evidence(pack["evidence"]),
        },
        "checks": {
            "author": {
                "status": author["status"],
                "schema_valid": author["schema"]["valid"],
                "blocker_codes": issue_codes(author["blockers"]),
                "warning_codes": issue_codes(author["warnings"]),
            },
            "gaps": pack_gap_summary,
            "implementation_gaps": implementation_gap_summary,
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


def summarize_pack_gaps(gaps: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "blocked"
        if any(item.get("severity") == "blocker" for item in gaps)
        else ("risk" if any(item.get("severity") == "risk" for item in gaps) else "clear"),
        "blocker": sum(1 for item in gaps if item.get("severity") == "blocker"),
        "risk": sum(1 for item in gaps if item.get("severity") == "risk"),
        "info": sum(1 for item in gaps if item.get("severity") == "info"),
        "codes": issue_codes(gaps),
    }


def relevant_implementation_gaps(gaps: list[dict[str, Any]], schema: dict[str, Any]) -> list[dict[str, Any]]:
    ignored_codes: set[str] = set()
    if not schema.get("tasks_required"):
        ignored_codes.add("TASK_GAP")
    if not schema.get("source_map_required") and not schema.get("tasks_required"):
        ignored_codes.add("IMPLEMENTATION_PATHS_GAP")
    return [item for item in gaps if item.get("code") not in ignored_codes]


def flow_status(
    stage: str,
    blocking: list[str],
    *,
    author: dict[str, Any],
    verify: dict[str, Any],
    archive: dict[str, Any],
    gap_summary: dict[str, Any],
) -> str:
    if blocking or author.get("status") == "blocked" or gap_summary.get("blocker"):
        return "blocked"
    if stage in {"implemented", "verified", "archive-ready"} and archive.get("status") == "blocked":
        return "blocked"
    if author.get("status") in {"needs-work", "risk"} or gap_summary.get("risk"):
        return "risk"
    if verify.get("status") == "risk" or archive.get("status") == "risk":
        return "risk"
    return "ok"


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
    if stage in {"implementation-ready", "change-authored"}:
        commands.append(f"aisee context pack --change {change} --for ce-work --json")
    elif stage in {"implemented", "verified", "archive-ready"}:
        commands.append(f"aisee context pack --change {change} --for aisee-verify --json")
    return commands
