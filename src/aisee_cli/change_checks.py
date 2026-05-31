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
    append_evidence_issues(evidence, blockers, warnings, archive_mode=False)
    warnings.extend(na_artifact_issues(pack))

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
    append_archive_review_blockers(pack["evidence"], blockers)

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


def append_evidence_issues(
    evidence: dict[str, Any],
    blockers: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    *,
    archive_mode: bool,
) -> None:
    details = evidence.get("details") if isinstance(evidence.get("details"), dict) else {}
    validate = details.get("openspec_validate")
    if isinstance(validate, dict):
        if validate.get("status") == "failed":
            blockers.append(issue("VALIDATE_FAILED", "blocker", "openspec validate evidence reports failure", str(validate.get("path") or "openspec")))
        elif validate.get("status") == "unknown":
            warnings.append(issue("VALIDATE_EVIDENCE_UNKNOWN", "risk", "openspec validate evidence has unknown status", str(validate.get("path") or "openspec")))

    for test in details.get("tests", []):
        if not isinstance(test, dict):
            continue
        if test.get("status") == "failed":
            blockers.append(issue("TEST_FAILED", "blocker", "test evidence reports failure", str(test.get("path") or "tests")))
        elif test.get("status") == "unknown":
            warnings.append(issue("TEST_EVIDENCE_UNKNOWN", "risk", "test evidence has unknown status", str(test.get("path") or "tests")))

    for review in details.get("reviews", []):
        if not isinstance(review, dict):
            continue
        for finding in review.get("findings", []):
            if not isinstance(finding, dict) or finding.get("status") != "open":
                continue
            priority = finding.get("priority")
            path = str(finding.get("path") or review.get("path") or "docs/reviews")
            if priority == "P0":
                blockers.append(issue("REVIEW_P0_OPEN", "blocker", "open P0 review finding must be resolved or accepted", path))
            elif priority == "P1":
                target = blockers if archive_mode else warnings
                severity = "blocker" if archive_mode else "risk"
                target.append(issue("REVIEW_P1_OPEN", severity, "open P1 review finding must be resolved or accepted", path))


def append_archive_review_blockers(evidence: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    details = evidence.get("details") if isinstance(evidence.get("details"), dict) else {}
    for review in details.get("reviews", []):
        if not isinstance(review, dict):
            continue
        for finding in review.get("findings", []):
            if not isinstance(finding, dict) or finding.get("status") != "open":
                continue
            if finding.get("priority") == "P1":
                path = str(finding.get("path") or review.get("path") or "docs/reviews")
                blockers.append(issue("REVIEW_P1_OPEN", "blocker", "open P1 review finding must be resolved or accepted", path))


def na_artifact_issues(pack: dict[str, Any]) -> list[dict[str, str]]:
    issues = []
    artifacts = pack["facts"]["parsed"].get("artifacts", {})
    for artifact_id, value in artifacts.items():
        for item in artifact_text_items(artifact_id, value):
            text = item["text"]
            lowered = text.lower()
            if "n/a" in lowered and "原因" not in text and "reason" not in lowered:
                issues.append(
                    issue(
                        "NA_REASON_MISSING",
                        "risk",
                        f"{artifact_id} is marked N/A without an explicit reason",
                        str(item.get("path") or artifact_id),
                    )
                )
    return issues


def artifact_text_items(artifact_id: str, value: Any) -> list[dict[str, str]]:
    if isinstance(value, dict):
        return [{"path": str(value.get("path") or artifact_id), "text": str(value.get("text") or "")}]
    if isinstance(value, list):
        return [
            {"path": str(item.get("path") or artifact_id), "text": str(item.get("text") or "")}
            for item in value
            if isinstance(item, dict)
        ]
    return []


def status_from_blockers(blockers: list[dict[str, Any]], warnings: list[dict[str, Any]], *, ready_status: str) -> str:
    if blockers:
        return "blocked"
    if warnings:
        return "risk"
    return ready_status
