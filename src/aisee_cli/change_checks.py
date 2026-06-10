"""Change gate checks for verify and archive stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.context_pack import build_context_pack, schema_has_capability
from aisee_cli.output import issue, summarize_issues


SCHEMA_EVIDENCE_REQUIREMENTS = {
    "docsite_evidence": ("docsite", ("build", "links", "preview", "manual")),
    "infra_evidence": ("infra", ("rollback", "post_change")),
    "security_evidence": ("security", ("reviews", "sast", "dependency_scan", "penetration_test", "tests")),
    "quick_fix_evidence": ("quick_fix", ("tests", "manual_verification", "monitoring", "rollback")),
}


def build_verify_check(project_root: Path, change: str) -> dict[str, Any]:
    pack = build_context_pack(project_root, change, "aisee-verify")
    task_state = pack["facts"]["derived"]["task_state"]
    tasks_required = schema_requires_tasks(pack)
    verification_required = schema_requires_verification_evidence(pack)
    checks = pack["facts"]["derived"].get("checks", {})
    evidence = pack["evidence"]
    blockers = [normalize_gap(gap) for gap in pack["gaps"] if gap.get("severity") == "blocker"]
    warnings = [normalize_gap(gap) for gap in pack["gaps"] if gap.get("severity") == "risk"]

    if tasks_required and task_state["total"] == 0:
        blockers.append(issue("TASKS_MISSING", "blocker", "tasks.md has no checkbox tasks", "tasks.md"))
    if tasks_required and task_state["blocked"]:
        blockers.append(issue("TASKS_BLOCKED", "blocker", "tasks.md has blocked tasks", "tasks.md"))
    if verification_required and not evidence_has_verification(evidence):
        warnings.append(issue("TEST_EVIDENCE_MISSING", "risk", "no test or verification evidence was found", "tasks.md"))
    append_evidence_issues(evidence, blockers, warnings, archive_mode=False)
    append_schema_evidence_issues(pack, blockers, warnings, archive_mode=False)
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
    tasks_required = schema_requires_tasks(pack)
    blockers = list(verify["blockers"])
    warnings = [
        warning
        for warning in verify["warnings"]
        if warning.get("code") != "SCHEMA_EVIDENCE_MISSING"
    ]

    if tasks_required and task_state["open"]:
        blockers.append(issue("TASKS_OPEN", "blocker", "tasks.md still has open tasks", "tasks.md"))
    if pack["evidence"].get("openspec_validate") is None:
        blockers.append(issue("VALIDATE_EVIDENCE_MISSING", "blocker", "openspec validate evidence was not found", "openspec"))
    append_archive_review_blockers(pack["evidence"], blockers)
    append_accepted_risk_issues(pack["evidence"], blockers)
    append_schema_evidence_issues(pack, blockers, warnings, archive_mode=True)

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


def schema_requires_tasks(pack: dict[str, Any]) -> bool:
    schema = pack["facts"]["parsed"].get("schema", {})
    return bool(schema.get("tasks_required"))


def schema_requires_verification_evidence(pack: dict[str, Any]) -> bool:
    schema = pack["facts"]["parsed"].get("schema", {})
    if not schema.get("tasks_required"):
        return False
    if any(schema_has_capability(schema, capability) for capability in SCHEMA_EVIDENCE_REQUIREMENTS):
        return False
    return not schema_has_capability(schema, "research_only")


def append_schema_evidence_issues(
    pack: dict[str, Any],
    blockers: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    *,
    archive_mode: bool,
) -> None:
    schema = pack["facts"]["parsed"].get("schema", {})
    schema_name = str(schema.get("name") or "")
    evidence = pack["evidence"]
    for capability, requirement in SCHEMA_EVIDENCE_REQUIREMENTS.items():
        if not schema_has_capability(schema, capability):
            continue
        domain, categories = requirement
        evidence_paths = [
            path
            for category in categories
            for path in evidence.get(domain, {}).get(category, [])
        ]
        if not evidence_paths:
            target = blockers if archive_mode else warnings
            severity = "blocker" if archive_mode else "risk"
            target.append(
                issue(
                    "SCHEMA_EVIDENCE_MISSING",
                    severity,
                    f"{schema_name} requires evidence for {domain}: {', '.join(categories)}",
                    "docs/verification",
                )
            )
            continue

        for item in parsed_domain_evidence(evidence, domain, categories):
            status = item.get("status")
            path = str(item.get("path") or "docs/verification")
            if status == "failed":
                blockers.append(issue("SCHEMA_EVIDENCE_FAILED", "blocker", f"{schema_name} evidence reports failure", path))
            elif status == "unknown":
                warnings.append(issue("SCHEMA_EVIDENCE_UNKNOWN", "risk", f"{schema_name} evidence has unknown status", path))


def parsed_domain_evidence(evidence: dict[str, Any], domain: str, categories: tuple[str, ...]) -> list[dict[str, Any]]:
    details = evidence.get("details") if isinstance(evidence.get("details"), dict) else {}
    domain_details = details.get("domain") if isinstance(details.get("domain"), dict) else {}
    category_details = domain_details.get(domain) if isinstance(domain_details.get(domain), dict) else {}
    items: list[dict[str, Any]] = []
    for category in categories:
        for item in category_details.get(category, []):
            if isinstance(item, dict):
                items.append(item)
    return items


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
    ) or any(evidence.get("quick_fix", {}).get(key) for key in ("monitoring", "rollback"))


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


def append_accepted_risk_issues(evidence: dict[str, Any], blockers: list[dict[str, Any]]) -> None:
    details = evidence.get("details") if isinstance(evidence.get("details"), dict) else {}
    for risk in details.get("accepted_risks", []):
        if not isinstance(risk, dict):
            continue
        text = str(risk.get("text") or "")
        missing = missing_accepted_risk_fields(text)
        if missing:
            blockers.append(
                issue(
                    "ACCEPTED_RISK_INCOMPLETE",
                    "blocker",
                    f"accepted risk is missing required fields: {', '.join(missing)}",
                    str(risk.get("path") or "docs/reviews"),
                )
            )


def missing_accepted_risk_fields(text: str) -> list[str]:
    lowered = text.lower()
    fields = {
        "owner": ("owner:", "负责人", "责任人"),
        "reason": ("reason:", "理由", "原因"),
        "impact": ("impact:", "影响"),
        "follow-up": ("follow-up:", "followup:", "后续", "处理方式"),
    }
    return [
        name
        for name, markers in fields.items()
        if not any(marker in lowered or marker in text for marker in markers)
    ]


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
