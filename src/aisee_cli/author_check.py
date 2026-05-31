"""Preflight checks for authoring a single OpenSpec change."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aisee_cli.context_pack import build_context_pack
from aisee_cli.id_registry import load_registry, lookup_entry, registry_path


def build_author_check(project_root: Path, change: str) -> dict[str, Any]:
    root = project_root.resolve()
    pack = build_context_pack(root, change, "aisee-verify")
    parsed = pack["facts"]["parsed"]
    derived = pack["facts"]["derived"]
    schema = parsed["schema"]
    artifacts = schema["artifacts"]
    id_registry = parsed["id_registry"]
    all_ids = sorted(set(derived["traceability"]["upstream_ids"]) | set(derived["traceability"]["produced_ids"]))
    registry_entries = inspect_registry_entries(root, all_ids)

    schema_issues = inspect_schema(schema, artifacts, root)
    artifact_order = build_artifact_order(artifacts)
    missing_artifacts = [artifact_summary(item) for item in artifacts if item.get("status") == "missing"]
    id_actions = build_id_actions(id_registry, registry_entries)
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
        "ids": {
            "upstream": derived["traceability"]["upstream_ids"],
            "produced": derived["traceability"]["produced_ids"],
            "registry": {
                "available": id_registry["available"],
                "path": id_registry["path"],
                "missing": id_registry["missing_ids"],
                "temporary": id_registry["temporary_ids"],
                "inactive": id_registry["inactive_ids"],
                "status_counts": id_registry["status_counts"],
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


def inspect_registry_entries(root: Path, ids: list[str]) -> dict[str, dict[str, Any]]:
    path = registry_path(root)
    if not path.exists():
        return {}
    try:
        registry = load_registry(root)
    except ValueError:
        return {}
    entries: dict[str, dict[str, Any]] = {}
    for full_id in ids:
        entry = lookup_entry(registry, full_id)
        if entry is not None:
            entries[full_id] = entry
    return entries


def build_id_actions(id_registry: dict[str, Any], entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    temporary = id_registry.get("temporary_ids", [])
    reserve_counts = Counter()
    for full_id in temporary:
        try:
            reserve_counts[full_id.split(":", 1)[1].split("-", 1)[0]] += 1
        except IndexError:
            reserve_counts["UNKNOWN"] += 1

    activate = [
        {
            "id": full_id,
            "owner": entry.get("owner") or "TODO",
            "title": entry.get("title") or "TODO",
        }
        for full_id, entry in sorted(entries.items())
        if entry.get("status") == "reserved"
    ]

    return {
        "reserve": [{"type": id_type, "count": count} for id_type, count in sorted(reserve_counts.items())],
        "activate": activate,
        "fix_missing": id_registry.get("missing_ids", []),
        "replace_inactive": id_registry.get("inactive_ids", []),
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
    for item in id_actions["reserve"]:
        actions.append(f"aisee id reserve --scope <scope> --type {item['type']} --count {item['count']} --json")
    for item in id_actions["activate"]:
        actions.append(f"aisee id activate {item['id']} --owner <path> --title \"<title>\" --json")
    for item in missing_artifacts:
        actions.append(f"create {item['generates']}")
    if blockers:
        actions.append("resolve blockers before authoring tasks.md")
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
