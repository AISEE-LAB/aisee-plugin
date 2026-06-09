"""Preflight checks for authoring a single OpenSpec change."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.context_pack import artifact_not_required, build_context_pack


def build_author_check(project_root: Path, change: str) -> dict[str, Any]:
    root = project_root.resolve()
    pack = build_context_pack(root, change, "aisee-verify")
    parsed = pack["facts"]["parsed"]
    derived = pack["facts"]["derived"]
    schema = parsed["schema"]
    artifacts = schema["artifacts"]
    anchor_index = parsed["anchor_index"]

    schema_issues = inspect_schema(schema, artifacts, root)
    artifact_order = build_artifact_order(artifacts)
    source_map = parsed.get("source_map", {})
    missing_artifacts = [
        artifact_summary(item)
        for item in artifacts
        if item.get("status") == "missing" and not artifact_not_required(item, source_map)
    ]
    id_actions = build_id_actions(anchor_index)
    blockers = build_blockers(pack["gaps"], schema_issues)
    warnings = build_warnings(pack["gaps"], schema_issues)
    next_actions = build_next_actions(missing_artifacts, id_actions, blockers)

    return {
        "schema_version": "1.0",
        "change": pack["change"],
        "status": "blocked" if blockers else ("needs-work" if warnings or missing_artifacts else "ready"),
        "schema": {
            "name": schema["name"],
            "version": schema["version"],
            "path": schema["path"],
            "valid": not any(issue["severity"] == "blocker" for issue in schema_issues),
            "issues": schema_issues,
        },
        "artifact_order": artifact_order,
        "missing_artifacts": missing_artifacts,
        "artifact_applicability": derived["artifact_applicability"],
        "anchors": {
            "upstream_refs": derived["traceability"]["upstream_refs"],
            "produced_local_ids": derived["traceability"]["produced_local_ids"],
            "resolution": {
                "available": anchor_index["available"],
                "path": anchor_index["path"],
                "resolved": anchor_index["resolved"],
                "missing_references": anchor_index["missing_references"],
                "temporary_local_ids": anchor_index["temporary_local_ids"],
                "legacy_full_ids": anchor_index["legacy_full_ids"],
            },
            "actions": id_actions,
        },
        "tasks": derived["task_state"],
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": next_actions,
        "meta": {
            "command": f"aisee change author-check {change} --json",
            "source_context_target": "aisee-verify",
        },
    }


def inspect_schema(schema: dict[str, Any], artifacts: list[dict[str, Any]], root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    schema_path = schema.get("path")
    if not schema_path:
        issues.append(issue("SCHEMA_NOT_FOUND", "blocker", "schema.yaml was not found", "openspec/schemas"))
        return issues

    schema_file = root / schema_path
    known_ids = {item["id"] for item in artifacts}
    for item in artifacts:
        for requirement in item.get("requires", []):
            if requirement not in known_ids:
                issues.append(
                    issue(
                        "SCHEMA_REQUIRES_UNKNOWN",
                        "blocker",
                        f"{item['id']} requires unknown artifact {requirement}",
                        schema_path,
                    )
                )
        template = item.get("template")
        if template and not (schema_file.parent / "templates" / template).exists():
            issues.append(
                issue(
                    "SCHEMA_TEMPLATE_MISSING",
                    "blocker",
                    f"{item['id']} template is missing: {template}",
                    f"{schema_file.parent.relative_to(root).as_posix()}/templates/{template}",
                )
            )

    for item in artifacts:
        seen = {prior["id"] for prior in artifacts[:artifacts.index(item)]}
        late_requires = [requirement for requirement in item.get("requires", []) if requirement in known_ids and requirement not in seen]
        if late_requires:
            issues.append(
                issue(
                    "SCHEMA_DAG_ORDER",
                    "risk",
                    f"{item['id']} requires artifacts that appear later or itself: {', '.join(late_requires)}",
                    schema_path,
                )
            )
    return issues


def build_artifact_order(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "generates": item.get("generates"),
            "status": item.get("status"),
            "path": item.get("path"),
            "requires": item.get("requires", []),
        }
        for item in artifacts
    ]


def artifact_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "generates": item.get("generates"),
        "requires": item.get("requires", []),
    }


def build_id_actions(anchor_index: dict[str, Any]) -> dict[str, Any]:
    return {
        "finalize_local_ids": anchor_index.get("temporary_local_ids", []),
        "fix_missing_references": anchor_index.get("missing_references", []),
        "remove_legacy_full_ids": anchor_index.get("legacy_full_ids", []),
    }


def build_blockers(gaps: list[dict[str, Any]], schema_issues: list[dict[str, str]]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    blockers.extend(item for item in gaps if item.get("severity") == "blocker")
    blockers.extend(item for item in schema_issues if item.get("severity") == "blocker")
    return blockers


def build_warnings(gaps: list[dict[str, Any]], schema_issues: list[dict[str, str]]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    warnings.extend(item for item in gaps if item.get("severity") == "risk")
    warnings.extend(item for item in schema_issues if item.get("severity") == "risk")
    return warnings


def build_next_actions(missing_artifacts: list[dict[str, Any]], id_actions: dict[str, Any], blockers: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    if id_actions["finalize_local_ids"]:
        actions.append("replace temporary local IDs with final local IDs in current change artifacts")
    if id_actions["fix_missing_references"]:
        actions.append("fix unresolved anchor refs in source-map.md or referenced planning docs")
    if id_actions["remove_legacy_full_ids"]:
        actions.append("replace legacy full IDs with doc-ref#LOCAL-ID anchor refs")
    for item in missing_artifacts:
        actions.append(f"create {item['generates']}")
    if blockers:
        actions.append("resolve blockers before authoring remaining artifacts")
    if not actions:
        actions.append("continue authoring or run openspec validate")
    return actions


def issue(code: str, severity: str, message: str, path: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "path": path,
    }
