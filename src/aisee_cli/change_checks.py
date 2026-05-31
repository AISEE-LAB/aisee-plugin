"""Change gate checks for verify and archive stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.context_pack import build_context_pack
from aisee_cli.output import issue, summarize_issues


def build_verify_check(project_root: Path, change: str) -> dict[str, Any]:
    pack = build_context_pack(project_root, change, "aisee-verify")
    task_state = pack["facts"]["derived"]["task_state"]
    checks = pack["facts"]["derived"].get("checks", {})
    evidence = pack["evidence"]
    blockers = [normalize_gap(gap) for gap in pack["gaps"] if gap.get("severity") == "blocker"]
    warnings = [normalize_gap(gap) for gap in pack["gaps"] if gap.get("severity") == "risk"]

    if task_state["total"] == 0:
        blockers.append(issue("TASKS_MISSING", "blocker", "tasks.md has no checkbox tasks", "tasks.md"))
    if task_state["blocked"]:
        blockers.append(issue("TASKS_BLOCKED", "blocker", "tasks.md has blocked tasks", "tasks.md"))
    if not evidence_has_verification(evidence):
        warnings.append(issue("TEST_EVIDENCE_MISSING", "risk", "no test or verification evidence was found", "tasks.md"))

    issues = blockers + warnings
    return {
        "schema_version": "1.0",
        "change": pack["change"],
        "status": status_from_blockers(blockers, warnings, ready_status="ready"),
        "checks": checks,
        "evidence": evidence,
        "blockers": blockers,
        "warnings": warnings,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": f"aisee change verify-check {change} --json",
            "source_context_target": "aisee-verify",
        },
    }


def build_archive_check(project_root: Path, change: str) -> dict[str, Any]:
    verify = build_verify_check(project_root, change)
    pack = build_context_pack(project_root, change, "aisee-verify")
    task_state = pack["facts"]["derived"]["task_state"]
    blockers = list(verify["blockers"])
    warnings = list(verify["warnings"])

    if task_state["open"]:
        blockers.append(issue("TASKS_OPEN", "blocker", "tasks.md still has open tasks", "tasks.md"))
    if pack["evidence"].get("openspec_validate") is None:
        warnings.append(issue("VALIDATE_EVIDENCE_MISSING", "risk", "openspec validate evidence was not found", "openspec"))

    issues = blockers + warnings
    return {
        "schema_version": "1.0",
        "change": pack["change"],
        "status": status_from_blockers(blockers, warnings, ready_status="archive-ready"),
        "evidence": pack["evidence"],
        "task_state": task_state,
        "blockers": blockers,
        "warnings": warnings,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": f"aisee change archive-check {change} --json",
            "source_context_target": "aisee-verify",
        },
    }


def normalize_gap(gap: dict[str, Any]) -> dict[str, str]:
    return {
        "code": str(gap.get("code") or "GAP"),
        "severity": str(gap.get("severity") or "risk"),
        "message": str(gap.get("message") or ""),
        "path": str(gap.get("owner_artifact") or ""),
    }


def evidence_has_verification(evidence: dict[str, Any]) -> bool:
    return any(
        evidence.get(key)
        for key in ("ce_code_review", "tests", "manual_verification")
    )


def status_from_blockers(blockers: list[dict[str, Any]], warnings: list[dict[str, Any]], *, ready_status: str) -> str:
    if blockers:
        return "blocked"
    if warnings:
        return "risk"
    return ready_status
