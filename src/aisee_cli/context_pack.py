"""Minimal context pack builder for Aisee changes.

This module intentionally uses conservative, template-aware heuristics. It
discovers files and trace hints; it does not try to understand arbitrary
Markdown as a second source of truth.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aisee_cli.assets import repo_asset_root
from aisee_cli.paths import id_registry_path, sources_path as aisee_sources_path
from aisee_cli.source_map import parse_source_map
from aisee_cli.tool_checks import check_compound_plugin


SUPPORTED_TARGETS = {"ce-work", "aisee-verify", "ce-doc-review", "ce-code-review"}
CONTEXT_SCHEMA_VERSION = "1.0"

ID_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-(?:NEW-)?\d+\b")
PATH_PATTERN = re.compile(
    r"(?<![\w./-])"
    r"((?:src|app|apps|lib|libs|packages|tests|test|aisee/docs|docs|openspec|assets|config|contracts)"
    r"/[A-Za-z0-9_./@:+-]+)"
)
CHECKBOX_PATTERN = re.compile(r"^\s*-\s+\[(?P<mark>[ xX~-])\]\s*(?P<title>.*)$")
OPTIONAL_APP_ARTIFACTS = {
    "change-context",
    "change-context.md",
    "ui-contract",
    "ui-contract.md",
    "service-contract",
    "service-contract.md",
    "data-model",
    "data-model.md",
}


@dataclass(frozen=True)
class ArtifactSpec:
    artifact_id: str
    generates: str | None = None
    template: str | None = None
    requires: tuple[str, ...] = ()


def build_context_pack(project_root: Path, change: str, target: str) -> dict[str, Any]:
    """Build a conservative context pack for a single OpenSpec change."""

    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"unsupported context target: {target}")

    root = project_root.resolve()
    change_path = root / "openspec" / "changes" / change
    schema_name = resolve_change_schema(root, change_path)
    schema_path = find_schema_path(root, schema_name)
    schema_info = parse_schema(schema_path) if schema_path else default_schema_info(schema_name)
    artifact_specs = schema_info["artifacts"]
    source_map_required = schema_generates_source_map(artifact_specs)
    source_map = parse_source_map(change_path) if source_map_required else not_applicable_source_map()

    artifact_entries = build_artifact_entries(change_path, artifact_specs)
    parsed_artifacts = parse_artifacts(change_path, artifact_entries)
    source_map_text = read_text(change_path / "source-map.md") if source_map_required else ""
    tasks_text = read_text(change_path / "tasks.md")
    combined_text = collect_artifact_text(parsed_artifacts)

    task_paths = sorted(extract_paths(tasks_text))
    artifact_paths = sorted(extract_paths(combined_text))
    referenced_paths = sorted(set(task_paths + artifact_paths) | extract_paths(source_map_text))
    if source_map_required:
        source_paths = sorted({item["path"] for item in source_map["implementation_paths"] if item.get("path")})
    else:
        source_paths = [path for path in referenced_paths if is_execution_path(path)]
    unmapped_reference_paths = [
        path
        for path in referenced_paths
        if source_map_required and is_execution_path(path) and path not in source_paths
    ]
    read_paths = sorted(set(source_paths + referenced_paths))
    code_paths = [p for p in source_paths if not is_test_path(p)]
    test_paths = [p for p in source_paths if is_test_path(p)]

    sources = inspect_sources(root, source_map_text)
    task_state = parse_task_state(tasks_text)
    upstream_ids = sorted(extract_ids(source_map_text))
    produced_ids = sorted(extract_ids(tasks_text) | extract_ids(combined_text))
    all_change_ids = sorted(extract_ids(combined_text))
    id_registry = inspect_id_registry(root, all_change_ids)

    gaps = build_gaps(
        change_path=change_path,
        artifact_entries=artifact_entries,
        task_state=task_state,
        code_paths=code_paths,
        test_paths=test_paths,
        target=target,
        id_registry=id_registry,
        source_map=source_map,
        source_map_required=source_map_required,
        unmapped_reference_paths=unmapped_reference_paths,
        tasks_text=tasks_text,
    )

    read_order = build_read_order(root, change_path, artifact_entries, read_paths)
    status = "missing" if not change_path.exists() else ("authored" if task_state["total"] else "draft")
    requires_ce_plan = target == "ce-work" and should_require_ce_plan(task_state, code_paths, test_paths, gaps)

    pack: dict[str, Any] = {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "target": target,
        "change": {
            "id": change,
            "path": rel(root, change_path),
            "schema": schema_name,
            "status": status,
        },
        "facts": {
            "parsed": {
                "project_rules": inspect_project_rules(root),
                "schema": {
                    "name": schema_name,
                    "version": schema_info.get("version"),
                    "path": rel(root, schema_path) if schema_path else None,
                    "artifacts": artifact_entries,
                    "apply_requires": schema_info.get("apply_requires", []),
                    "archive_tracks": derive_archive_tracks(schema_info),
                    "source_map_required": source_map_required,
                    "tasks_required": schema_requires_tasks(schema_info, artifact_specs),
                },
                "artifacts": parsed_artifacts,
                "source_map": source_map,
                "sources": sources,
                "id_registry": id_registry,
            },
            "derived": {
                "read_order": read_order,
                "scope": derive_scope(read_text(change_path / "proposal.md"), source_map_text),
                "traceability": {
                    "upstream_ids": upstream_ids,
                    "produced_ids": produced_ids,
                    "id_links": derive_id_links(source_map_text, tasks_text),
                },
                "artifact_applicability": source_map["artifact_applicability"] or derive_artifact_applicability(source_map_text),
                "code_paths": code_paths,
                "test_paths": test_paths,
                "implementation_references": {
                    "source": "source-map" if source_map_required else "schema-artifacts",
                    "declared_paths": source_paths,
                    "referenced_paths": referenced_paths,
                    "unmapped_reference_paths": unmapped_reference_paths,
                },
                "task_state": task_state,
                "verification_requirements": derive_verification_requirements(tasks_text),
                "open_questions": extract_tagged_lines(combined_text, ("[ASSUMPTION]", "[SPEC-GAP]", "[SOURCE-MAP-GAP]")),
            },
        },
        "generated": None,
        "gaps": gaps,
        "guardrails": build_guardrails(target, source_map_required),
        "evidence": build_evidence(root, change),
        "meta": {
            "command": f"aisee context pack --change {change} --for {target} --json",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "aisee",
            "mode": "parsed-and-derived",
        },
    }

    if target == "ce-work":
        ce_plan_refinement_reason = ce_plan_reason(task_state, code_paths, test_paths, gaps, source_map_required) if requires_ce_plan else None
        pack["facts"]["derived"]["execution"] = {
            "start_from": task_state["open_items"][:1],
            "suggested_order": task_state["open_items"],
            "allowed_paths": sorted(set(code_paths + test_paths)),
            "unmapped_reference_paths": unmapped_reference_paths,
            "forbidden_scope": pack["facts"]["derived"]["scope"]["out"],
            "requires_ce_plan": requires_ce_plan,
            "ce_plan_reason": ce_plan_refinement_reason,
            "reusable_workflow_candidates": build_reusable_workflow_candidates(
                requires_ce_plan=requires_ce_plan,
                ce_plan_refinement_reason=ce_plan_refinement_reason,
                gaps=gaps,
            ),
        }
    elif target == "aisee-verify":
        pack["facts"]["derived"]["checks"] = {
            "schema_artifacts": summarize_artifact_checks(artifact_entries),
            "traceability": summarize_trace_checks(upstream_ids, produced_ids),
            "tasks": summarize_task_checks(task_state),
            "contracts": summarize_contract_checks(artifact_entries, source_map.get("contract_sync")),
            "implementation": summarize_implementation_checks(code_paths, test_paths, source_map_required),
            "review_and_tests": [],
        }
        pack["facts"]["derived"]["drift_candidates"] = []
    elif target == "ce-doc-review":
        pack["facts"]["derived"]["review"] = {
            "focus": ["schema_artifacts", "traceability", "tasks", "contracts", "open_questions"],
            "schema_artifacts": summarize_artifact_checks(artifact_entries),
            "traceability": summarize_trace_checks(upstream_ids, produced_ids),
            "tasks": summarize_task_checks(task_state),
            "contracts": summarize_contract_checks(artifact_entries, source_map.get("contract_sync")),
        }
    elif target == "ce-code-review":
        pack["facts"]["derived"]["review"] = {
            "focus": ["implementation", "tests", "source-map" if source_map_required else "schema-artifacts", "task_state"],
            "implementation": summarize_implementation_checks(code_paths, test_paths, source_map_required),
            "tasks": summarize_task_checks(task_state),
            "evidence": pack["evidence"],
        }

    return pack


def resolve_project_root(cwd: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return Path(result.stdout.strip())
    except Exception:
        return cwd


def resolve_change_schema(root: Path, change_path: Path) -> str:
    metadata = read_text(change_path / ".openspec.yaml")
    schema = read_yaml_scalar(metadata, "schema")
    if schema:
        return schema

    config = read_text(root / "openspec" / "config.yaml")
    schema = read_yaml_scalar(config, "schema")
    return schema or "spec-driven"


def find_schema_path(root: Path, schema_name: str) -> Path | None:
    asset_root = repo_asset_root(root)
    candidates = [
        root / "openspec" / "schemas" / schema_name / "schema.yaml",
    ]
    if asset_root is not None:
        candidates.append(asset_root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / schema_name / "schema.yaml")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def parse_schema(schema_path: Path) -> dict[str, Any]:
    text = read_text(schema_path)
    artifacts: list[ArtifactSpec] = []
    current: dict[str, Any] | None = None
    apply_requires: list[str] = []
    apply_tracks: str | None = None
    in_apply = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped == "apply:":
            if current:
                artifacts.append(to_artifact_spec(current))
                current = None
            in_apply = True
            continue

        if stripped.startswith("- id:"):
            if current:
                artifacts.append(to_artifact_spec(current))
            current = {"id": clean_value(stripped.split(":", 1)[1])}
            in_apply = False
            continue

        if current is not None:
            if stripped.startswith("generates:"):
                current["generates"] = clean_value(stripped.split(":", 1)[1])
            elif stripped.startswith("template:"):
                current["template"] = clean_value(stripped.split(":", 1)[1])
            elif stripped.startswith("requires:"):
                current["requires"] = parse_inline_list(stripped.split(":", 1)[1])
            continue

        if in_apply:
            if stripped.startswith("requires:"):
                apply_requires = parse_inline_list(stripped.split(":", 1)[1])
            elif stripped.startswith("tracks:"):
                apply_tracks = clean_value(stripped.split(":", 1)[1])

    if current:
        artifacts.append(to_artifact_spec(current))

    return {
        "name": read_yaml_scalar(text, "name") or schema_path.parent.name,
        "version": parse_int(read_yaml_scalar(text, "version")),
        "artifacts": artifacts,
        "apply_requires": apply_requires,
        "apply_tracks": apply_tracks,
    }


def default_schema_info(schema_name: str) -> dict[str, Any]:
    artifacts = [
        ArtifactSpec("proposal", "proposal.md"),
        ArtifactSpec("specs", "specs/**/*.md"),
        ArtifactSpec("tasks", "tasks.md"),
    ]
    return {
        "name": schema_name,
        "version": None,
        "artifacts": artifacts,
        "apply_requires": ["tasks"],
        "apply_tracks": "tasks.md",
    }


def schema_generates_source_map(artifact_specs: list[ArtifactSpec]) -> bool:
    return any(
        spec.artifact_id == "source-map" or spec.generates == "source-map.md"
        for spec in artifact_specs
    )


def schema_requires_tasks(schema_info: dict[str, Any], artifact_specs: list[ArtifactSpec]) -> bool:
    apply_requires = schema_info.get("apply_requires", [])
    apply_tracks = schema_info.get("apply_tracks")
    return any(
        spec.artifact_id == "tasks" or spec.generates == "tasks.md"
        for spec in artifact_specs
    ) or "tasks" in apply_requires or apply_tracks == "tasks.md"


def not_applicable_source_map() -> dict[str, Any]:
    return {
        "path": None,
        "status": "not_applicable",
        "parse_level": "not_applicable",
        "upstream_sources": [],
        "id_trace": [],
        "artifact_applicability": [],
        "contract_sync": {"available": False, "values": {}, "machine_readable_contracts": []},
        "implementation_paths": [],
        "verification_evidence": [],
        "out_of_scope": [],
        "ids": [],
        "paths": [],
        "issues": [],
    }


def build_artifact_entries(change_path: Path, artifact_specs: list[ArtifactSpec]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for spec in artifact_specs:
        paths = resolve_artifact_paths(change_path, spec.generates)
        entries.append(
            {
                "id": spec.artifact_id,
                "generates": spec.generates,
                "template": spec.template,
                "requires": list(spec.requires),
                "path": ", ".join(paths) if len(paths) > 1 else (paths[0] if paths else None),
                "required": True,
                "status": "present" if paths else "missing",
            }
        )
    return entries


def parse_artifacts(change_path: Path, artifact_entries: list[dict[str, Any]]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for entry in artifact_entries:
        artifact_id = entry["id"]
        generates = entry.get("generates")
        paths = resolve_artifact_paths(change_path, generates)
        key = artifact_id.replace("-", "_")
        if artifact_id == "specs":
            specs = []
            for path in paths:
                text = read_text(resolve_change_relative_path(change_path, path))
                specs.append({
                    "path": path,
                    "ids": sorted(extract_ids(text)),
                    "paths": sorted(extract_paths(text)),
                    "text": text,
                })
            parsed[key] = specs
            continue

        if paths:
            text = read_text(resolve_change_relative_path(change_path, paths[0]))
            parsed[key] = {
                "path": paths[0],
                "ids": sorted(extract_ids(text)),
                "paths": sorted(extract_paths(text)),
                "text": text,
            }
        else:
            parsed[key] = {
                "path": generates,
                "ids": [],
                "paths": [],
                "text": "",
            }
    return parsed


def resolve_change_relative_path(change_path: Path, path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else change_path / candidate


def collect_artifact_text(parsed_artifacts: dict[str, Any]) -> str:
    chunks: list[str] = []
    for value in parsed_artifacts.values():
        if isinstance(value, dict):
            chunks.append(value.get("text", ""))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    chunks.append(item.get("text", ""))
    return "\n".join(chunks)


def resolve_artifact_paths(change_path: Path, generates: str | None) -> list[str]:
    if not generates:
        return []
    if "*" in generates:
        paths = sorted(change_path.glob(generates))
        return [rel(change_path, path) for path in paths if path.is_file()]
    path = change_path / generates
    return [generates] if path.exists() else []


def inspect_project_rules(root: Path) -> dict[str, Any]:
    primary = root / "AGENTS.md"
    legacy = root / "CLAUDE.md"
    return {
        "primary": rel(root, primary) if primary.exists() else None,
        "legacy_fallback": rel(root, legacy) if legacy.exists() else None,
    }


def inspect_id_registry(root: Path, ids: list[str]) -> dict[str, Any]:
    path = id_registry_path(root)
    result: dict[str, Any] = {
        "available": path.exists(),
        "checked": path.exists(),
        "path": rel(root, path) if path.exists() else None,
        "queried_ids": sorted(ids),
        "registered_ids": [],
        "missing_ids": [],
        "temporary_ids": sorted([item for item in ids if "-NEW-" in item]),
        "inactive_ids": [],
        "status_counts": {},
    }
    if not path.exists():
        return result

    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as error:
        result["error"] = f"invalid-json: {error}"
        return result

    registry_ids: dict[str, dict[str, Any]] = {}
    scopes = data.get("scopes", {}) if isinstance(data, dict) else {}
    if isinstance(scopes, dict):
        for scope_data in scopes.values():
            if isinstance(scope_data, dict) and isinstance(scope_data.get("ids"), dict):
                for full_id, entry in scope_data["ids"].items():
                    if isinstance(entry, dict):
                        registry_ids[full_id] = entry

    formal_ids = [item for item in ids if "-NEW-" not in item]
    registered: list[str] = []
    missing: list[str] = []
    inactive: list[dict[str, str]] = []
    status_counts: dict[str, int] = {}
    for full_id in formal_ids:
        entry = registry_ids.get(full_id)
        if entry is None:
            missing.append(full_id)
            continue
        registered.append(full_id)
        status = str(entry.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        if status in {"deprecated", "merged", "split", "removed"}:
            inactive.append({"id": full_id, "status": status})

    result.update({
        "registered_ids": sorted(registered),
        "missing_ids": sorted(missing),
        "inactive_ids": sorted(inactive, key=lambda item: item["id"]),
        "status_counts": status_counts,
    })
    return {
        **result,
    }


def inspect_sources(root: Path, source_map_text: str) -> list[dict[str, Any]]:
    registry_path = aisee_sources_path(root)
    sources: list[dict[str, Any]] = []
    if registry_path.exists():
        try:
            data = json.loads(read_text(registry_path))
            if isinstance(data, list):
                sources.extend(item for item in data if isinstance(item, dict))
            elif isinstance(data, dict):
                for key, value in data.items():
                    sources.append({"id": key, "value": value})
        except json.JSONDecodeError:
            sources.append({"path": rel(root, registry_path), "status": "invalid-json"})

    for path in sorted(extract_paths(source_map_text)):
        if path.startswith("docs/"):
            sources.append({"path": path, "status": "referenced"})
    return sources


def parse_task_state(tasks_text: str) -> dict[str, Any]:
    done = 0
    open_count = 0
    blocked = 0
    open_items: list[str] = []
    done_items: list[str] = []
    for line in tasks_text.splitlines():
        match = CHECKBOX_PATTERN.match(line)
        if not match:
            continue
        mark = match.group("mark")
        title = match.group("title").strip()
        if mark in {"x", "X"}:
            done += 1
            done_items.append(title)
        elif mark in {"~", "-"}:
            blocked += 1
            open_items.append(title)
        else:
            open_count += 1
            open_items.append(title)
    total = done + open_count + blocked
    return {
        "total": total,
        "done": done,
        "open": open_count,
        "blocked": blocked,
        "open_items": open_items,
        "done_items": done_items,
    }


def build_gaps(
    *,
    change_path: Path,
    artifact_entries: list[dict[str, Any]],
    task_state: dict[str, Any],
    code_paths: list[str],
    test_paths: list[str],
    target: str,
    id_registry: dict[str, Any],
    source_map: dict[str, Any],
    source_map_required: bool,
    unmapped_reference_paths: list[str],
    tasks_text: str,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not change_path.exists():
        gaps.append(gap("MISSING_CHANGE", "blocker", "Change directory does not exist", "openspec/changes"))
        return gaps

    if source_map_required:
        gaps.extend(source_map.get("issues", []))

    for entry in artifact_entries:
        if entry["status"] == "missing":
            if artifact_not_required(entry, source_map):
                continue
            severity = "blocker" if entry["id"] in {"proposal", "source-map", "tasks"} else "risk"
            gaps.append(
                gap(
                    "MISSING_ARTIFACT",
                    severity,
                    f"Schema artifact is missing: {entry['id']}",
                    entry.get("generates") or entry["id"],
                )
            )

    has_change_ids = bool(id_registry.get("queried_ids"))
    id_owner_artifact = "source-map.md" if source_map_required else "schema artifacts"
    if not id_registry["available"] and (source_map_required or has_change_ids):
        gaps.append(gap("ID_REGISTRY_GAP", "risk", "Aisee ID registry is missing", "aisee/registry/id-registry.json"))
    elif id_registry.get("error"):
        gaps.append(gap("ID_REGISTRY_INVALID", "blocker", str(id_registry["error"]), "aisee/registry/id-registry.json"))
    else:
        temporary_ids = id_registry.get("temporary_ids", [])
        if temporary_ids:
            gaps.append(
                gap(
                    "ID_RESERVATION_REQUIRED",
                    "risk",
                    "Change contains temporary IDs that must be reserved before final authoring",
                    id_owner_artifact,
                    temporary_ids,
                )
            )
        missing_ids = id_registry.get("missing_ids", [])
        if missing_ids:
            gaps.append(
                gap(
                    "ID_UNREGISTERED_REFERENCE",
                    "risk",
                    "Change references IDs that are not registered in the Aisee ID registry",
                    id_owner_artifact,
                    missing_ids,
                )
            )
        inactive_ids = id_registry.get("inactive_ids", [])
        if inactive_ids:
            gaps.append(
                gap(
                    "ID_INACTIVE_REFERENCE",
                    "blocker",
                    "Change references deprecated, merged, split, or removed IDs",
                    id_owner_artifact,
                    [item["id"] for item in inactive_ids],
                )
            )

    if target == "ce-work":
        if task_state["total"] == 0:
            gaps.append(gap("TASK_GAP", "blocker", "tasks.md has no checkbox tasks", "tasks.md"))
        if not code_paths and not test_paths:
            owner_artifact = "source-map.md" if source_map_required else "tasks.md"
            message = (
                "No code or test paths were declared by source-map Affected Paths Index"
                if source_map_required
                else "No code or test paths were referenced by schema artifacts"
            )
            gaps.append(
                gap(
                    "SOURCE_MAP_GAP" if source_map_required else "IMPLEMENTATION_PATHS_GAP",
                    "risk",
                    message,
                    owner_artifact,
                )
            )
        if unmapped_reference_paths:
            gaps.append(
                gap(
                    "SOURCE_MAP_UNMAPPED_PATH",
                    "risk",
                    "artifact text references execution paths not declared in source-map Affected Paths Index",
                    "source-map.md",
                    unmapped_reference_paths,
                )
            )
    gaps.extend(contract_sync_gaps(artifact_entries, source_map, tasks_text))
    return gaps


def gap(code: str, severity: str, message: str, owner_artifact: str, related_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "owner_artifact": owner_artifact,
        "related_ids": related_ids or [],
        "suggested_fix": None,
    }


def artifact_not_required(entry: dict[str, Any], source_map: dict[str, Any]) -> bool:
    artifact_id = str(entry.get("id") or "")
    generates = str(entry.get("generates") or "")
    if artifact_id not in OPTIONAL_APP_ARTIFACTS and generates not in OPTIONAL_APP_ARTIFACTS:
        return False
    for row in source_map.get("artifact_applicability", []):
        if not isinstance(row, dict):
            continue
        artifact = str(row.get("artifact") or "")
        if artifact not in {artifact_id, generates}:
            continue
        if row.get("required") == "no" and str(row.get("reason") or "").strip():
            return True
    return False


def contract_sync_gaps(
    artifact_entries: list[dict[str, Any]],
    source_map: dict[str, Any],
    tasks_text: str,
) -> list[dict[str, Any]]:
    service_contract = next((entry for entry in artifact_entries if entry.get("id") == "service-contract"), None)
    if service_contract is None or artifact_not_required(service_contract, source_map):
        return []
    if service_contract.get("status") == "missing":
        return []

    gaps: list[dict[str, Any]] = []
    contract_sync = source_map.get("contract_sync") if isinstance(source_map, dict) else {}
    values = contract_sync.get("values", {}) if isinstance(contract_sync, dict) else {}
    if not values:
        return [
            gap(
                "CONTRACT_SYNC_METADATA_MISSING",
                "risk",
                "service-contract.md is required but source-map.md has no Contract Ownership / Sync table",
                "source-map.md",
            )
        ]

    required_keys = ("contract_owner", "canonical_source", "provider_repo", "consumer_repo", "sync_mode")
    missing_keys = [key for key in required_keys if contract_value_is_missing(values.get(key))]
    if missing_keys:
        gaps.append(
            gap(
                "CONTRACT_SYNC_FIELDS_MISSING",
                "risk",
                f"service-contract.md is required but contract sync fields are missing: {', '.join(missing_keys)}",
                "source-map.md",
            )
        )

    for key, entry in values.items():
        if not isinstance(entry, dict):
            continue
        if str(entry.get("status") or "").strip().lower() == "pending":
            gaps.append(
                gap(
                    "CONTRACT_SYNC_PENDING",
                    "risk",
                    f"contract sync field is still pending: {key}",
                    "source-map.md",
                )
            )

    machine_paths = contract_sync.get("machine_readable_contracts", []) if isinstance(contract_sync, dict) else []
    for path in machine_paths:
        if isinstance(path, str) and path and path not in source_map.get("paths", []):
            gaps.append(
                gap(
                    "CONTRACT_ARTIFACT_PATH_UNTRACKED",
                    "risk",
                    f"machine-readable contract path is not tracked by source-map path scan: {path}",
                    "source-map.md",
                )
            )

    tasks_lower = tasks_text.lower()
    provider = value_from_contract_sync(values, "provider_repo")
    consumer = value_from_contract_sync(values, "consumer_repo")
    if provider and provider.lower() not in {"n/a", "na", "none"} and not has_any_term(
        tasks_text,
        ("provider", "提供方", "服务提供", "后端实现", "后端能力"),
    ):
        gaps.append(
            gap(
                "CONTRACT_PROVIDER_TASK_MISSING",
                "risk",
                "provider repo is declared but tasks.md has no provider implementation task",
                "tasks.md",
            )
        )
    if consumer and consumer.lower() not in {"n/a", "na", "none"} and not has_any_term(
        tasks_text,
        ("consumer", "消费方", "服务消费", "前端接入", "前端调用"),
    ):
        gaps.append(
            gap(
                "CONTRACT_CONSUMER_TASK_MISSING",
                "risk",
                "consumer repo is declared but tasks.md has no consumer integration task",
                "tasks.md",
            )
        )
    if machine_paths and not any(term in tasks_lower for term in ("contract test", "契约测试", "backward compatibility", "兼容")):
        gaps.append(
            gap(
                "CONTRACT_TEST_TASK_MISSING",
                "risk",
                "machine-readable contracts are declared but tasks.md has no contract test or compatibility check",
                "tasks.md",
            )
        )
    return gaps


def contract_value_is_missing(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return True
    value = str(entry.get("value") or "").strip().lower()
    return value in {"", "n/a", "na", "none", "待确认"}


def has_any_term(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered or term in text for term in terms)


def build_read_order(root: Path, change_path: Path, artifact_entries: list[dict[str, Any]], paths: list[str]) -> list[str]:
    read_order: list[str] = []
    agents = root / "AGENTS.md"
    if agents.exists():
        read_order.append(rel(root, agents))
    for entry in artifact_entries:
        path = entry.get("path")
        if path and "," not in path:
            read_order.append(rel(root, change_path / path))
    read_order.extend(paths)
    return dedupe(read_order)


def derive_archive_tracks(schema_info: dict[str, Any]) -> list[str]:
    tracks = schema_info.get("apply_tracks")
    if isinstance(tracks, str) and tracks:
        return [tracks]
    artifact_tracks = [
        spec.generates
        for spec in schema_info.get("artifacts", [])
        if isinstance(spec, ArtifactSpec) and spec.generates in {"tasks.md", "source-map.md", "specs/**/*.md"}
    ]
    return artifact_tracks


def derive_scope(proposal_text: str, source_map_text: str) -> dict[str, list[str]]:
    return {
        "in": extract_section_lines(proposal_text + "\n" + source_map_text, ("## 变更范围", "## Change Scope", "## In Scope")),
        "out": extract_section_lines(proposal_text + "\n" + source_map_text, ("## 不在范围", "## Out of Scope", "## 不在本 Change 范围")),
        "follow_up_candidates": extract_tagged_lines(proposal_text + "\n" + source_map_text, ("[FOLLOW-UP]", "[SOURCE-MAP-GAP]")),
    }


def derive_id_links(source_map_text: str, tasks_text: str) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    for line in (source_map_text + "\n" + tasks_text).splitlines():
        ids = sorted(extract_ids(line))
        if len(ids) >= 2:
            links.append({"ids": ids, "source": line.strip()})
    return links


def derive_artifact_applicability(source_map_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in source_map_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        if ".md" not in line or ("yes" not in line and "no" not in line):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) >= 2:
            rows.append({"artifact": parts[0], "required": parts[1], "source": line.strip()})
    return rows


def derive_verification_requirements(tasks_text: str) -> list[str]:
    return [
        line.strip()
        for line in tasks_text.splitlines()
        if any(term in line.lower() for term in ("test", "verify", "验证", "检查", "evidence"))
    ]


def build_guardrails(target: str, source_map_required: bool) -> list[str]:
    common = [
        "Use the current change as the only scope entry.",
        "Do not treat generated summaries as authoritative.",
        "Write durable conclusions back to OpenSpec artifacts.",
    ]
    if target == "ce-work":
        common.extend([
            "Follow tasks.md; do not create a parallel durable plan.",
        ])
        if source_map_required:
            common.append("Use source-map Affected Paths Index for executable paths; metadata fallback is a risk, and other path references remain gaps or follow-up findings.")
        else:
            common.append("Use executable paths explicitly referenced by current schema artifacts; treat unrelated paths as out of scope.")
    elif target == "aisee-verify":
        common.append("Diagnose consistency; do not make archive approval decisions.")
    elif target == "ce-doc-review":
        common.append("Review OpenSpec artifacts and traceability; do not implement code.")
    elif target == "ce-code-review":
        common.append("Review implementation evidence against the current OpenSpec change.")
    return common


def build_evidence(root: Path, change: str) -> dict[str, Any]:
    review_dir = root / "docs" / "reviews"
    review_files = []
    if review_dir.exists():
        review_files = [rel(root, path) for path in sorted(review_dir.glob(f"*{change}*")) if path.is_file()]
    verification_dir = root / "docs" / "verification"
    verification_files = []
    if verification_dir.exists():
        verification_files = [rel(root, path) for path in sorted(verification_dir.glob(f"*{change}*")) if path.is_file()]
    classified = classify_evidence(review_files, verification_files)
    return {
        "openspec_validate": first_matching(verification_files, ("validate", "openspec")),
        "ce_doc_review": [path for path in review_files if "doc" in path],
        "ce_code_review": [path for path in review_files if "code" in path],
        "tests": [path for path in verification_files if "test" in path],
        "manual_verification": [path for path in verification_files if "manual" in path or "verify" in path],
        "docsite": classified["docsite"],
        "infra": classified["infra"],
        "security": classified["security"],
        "quick_fix": classified["quick_fix"],
        "details": build_evidence_details(root, review_files, verification_files, classified),
    }


def classify_evidence(review_files: list[str], verification_files: list[str]) -> dict[str, dict[str, list[str]]]:
    return {
        "docsite": {
            "build": matching_paths(verification_files, ("build", "site-build")),
            "links": matching_paths(verification_files, ("link", "links")),
            "preview": matching_paths(verification_files, ("preview",)),
            "manual": matching_paths(verification_files, ("manual", "proofread", "review")),
        },
        "infra": {
            "precheck": matching_paths(verification_files, ("precheck", "pre-check", "preflight")),
            "rollback": matching_paths(verification_files, ("rollback",)),
            "post_change": matching_paths(verification_files, ("post-change", "postchange", "post-change-verify", "deployment-verify")),
        },
        "security": {
            "reviews": matching_paths(review_files, ("security", "sec", "audit")),
            "sast": matching_paths(verification_files, ("sast", "static-analysis")),
            "dependency_scan": matching_paths(verification_files, ("dependency", "deps", "cve", "vulnerability", "vuln")),
            "penetration_test": matching_paths(verification_files, ("pentest", "penetration")),
            "tests": matching_paths(verification_files, ("security-test", "security-tests", "auth-test")),
        },
        "quick_fix": {
            "tests": matching_paths(verification_files, ("test",)),
            "manual_verification": matching_paths(verification_files, ("manual", "verify")),
            "monitoring": matching_paths(verification_files, ("monitor", "monitoring", "metrics", "observe")),
            "rollback": matching_paths(verification_files, ("rollback",)),
        },
    }


def matching_paths(paths: list[str], terms: tuple[str, ...]) -> list[str]:
    return [path for path in paths if any(term in path.lower() for term in terms)]


def build_evidence_details(
    root: Path,
    review_files: list[str],
    verification_files: list[str],
    classified: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    validate_path = first_matching(verification_files, ("validate", "openspec"))
    return {
        "openspec_validate": parse_status_file(root, validate_path) if validate_path else None,
        "reviews": [parse_review_file(root, path) for path in review_files],
        "tests": [parse_status_file(root, path) for path in verification_files if "test" in path.lower()],
        "manual_verification": [
            parse_status_file(root, path)
            for path in verification_files
            if "manual" in path.lower() or "verify" in path.lower()
        ],
        "domain": {
            domain: {
                category: [parse_status_file(root, path) for path in paths]
                for category, paths in categories.items()
            }
            for domain, categories in classified.items()
        },
        "accepted_risks": collect_accepted_risks(root, review_files + verification_files),
    }


def parse_review_file(root: Path, path: str) -> dict[str, Any]:
    text = read_text(root / path)
    findings = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        priority = first_priority(line)
        if not priority:
            continue
        findings.append({
            "path": path,
            "line": line_number,
            "priority": priority,
            "status": evidence_line_status(line),
            "text": line.strip(),
        })
    return {
        "path": path,
        "status": aggregate_finding_status(findings),
        "findings": findings,
    }


def parse_status_file(root: Path, path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    text = read_text(root / path)
    return {
        "path": path,
        "status": status_from_text(text),
        "accepted_risks": accepted_risk_lines(text, path),
    }


def collect_accepted_risks(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    risks = []
    for path in paths:
        risks.extend(accepted_risk_lines(read_text(root / path), path))
    return risks


def accepted_risk_lines(text: str, path: str) -> list[dict[str, Any]]:
    risks = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if "[accepted-risk]" in lowered or "accepted risk" in lowered or "接受风险" in line or "已接受风险" in line:
            risks.append({"path": path, "line": line_number, "text": line.strip()})
    return risks


def first_priority(line: str) -> str | None:
    upper = line.upper()
    for priority in ("P0", "P1", "P2", "P3"):
        if priority in upper:
            return priority
    if "CRITICAL" in upper:
        return "P0"
    if "HIGH" in upper:
        return "P1"
    return None


def evidence_line_status(line: str) -> str:
    lowered = line.lower()
    if any(term in lowered for term in ("resolved", "fixed", "done", "accepted", "accept risk")):
        return "closed"
    if any(term in line for term in ("已处理", "已修复", "已接受", "接受风险")):
        return "closed"
    return "open"


def aggregate_finding_status(findings: list[dict[str, Any]]) -> str:
    if any(item["status"] == "open" and item["priority"] == "P0" for item in findings):
        return "failed"
    if any(item["status"] == "open" and item["priority"] == "P1" for item in findings):
        return "risk"
    return "passed"


def status_from_text(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("failed", "failure", "error", "blocked")) or any(term in text for term in ("失败", "未通过", "阻断")):
        return "failed"
    if any(term in lowered for term in ("passed", "success", "succeeded", "ok")) or any(term in text for term in ("通过", "成功")):
        return "passed"
    return "unknown"


def first_matching(paths: list[str], terms: tuple[str, ...]) -> str | None:
    for path in paths:
        lowered = path.lower()
        if all(term in lowered for term in terms):
            return path
    return None


def should_require_ce_plan(task_state: dict[str, Any], code_paths: list[str], test_paths: list[str], gaps: list[dict[str, Any]]) -> bool:
    if any(item["severity"] == "blocker" for item in gaps):
        return True
    if task_state["total"] == 0:
        return True
    return not code_paths and not test_paths


def ce_plan_reason(
    task_state: dict[str, Any],
    code_paths: list[str],
    test_paths: list[str],
    gaps: list[dict[str, Any]],
    source_map_required: bool,
) -> str:
    blocker_codes = [item["code"] for item in gaps if item["severity"] == "blocker"]
    if blocker_codes:
        return f"blocked by {', '.join(blocker_codes)}"
    if task_state["total"] == 0:
        return "tasks.md has no executable tasks"
    if not code_paths and not test_paths:
        if source_map_required:
            return "source-map Affected Paths Index does not identify code or test paths"
        return "schema artifacts do not identify code or test paths"
    return "tasks/source-map need implementation refinement" if source_map_required else "tasks/artifacts need implementation refinement"


def build_reusable_workflow_candidates(
    *,
    requires_ce_plan: bool,
    ce_plan_refinement_reason: str | None,
    gaps: list[dict[str, Any]],
) -> list[dict[str, str]]:
    compound = check_compound_plugin()
    compound_skills = compound.get("skills", {})
    blocker_codes = [str(item.get("code") or "UNKNOWN") for item in gaps if item.get("severity") == "blocker"]
    if blocker_codes:
        return [
            {
                "name": "aisee:change-author",
                "kind": "aisee-skill",
                "status": "required",
                "reason": f"fix blocking artifact or traceability gaps before execution: {', '.join(blocker_codes)}",
            }
        ]

    candidates = [
        {
            "name": "aisee:implementation-bridge",
            "kind": "aisee-skill",
            "status": "recommended",
            "reason": "preflight author-check, gaps, context pack, scope guardrails, and review recommendation before CE execution",
        }
    ]

    if requires_ce_plan:
        candidates.append({
            "name": "ce-plan",
            "kind": "compound-skill",
            "status": "available" if compound_skills.get("ce-plan") else "missing",
            "reason": ce_plan_refinement_reason or "tasks or implementation references need refinement before ce-work",
        })
    else:
        candidates.append({
            "name": "ce-work",
            "kind": "compound-skill",
            "status": "available" if compound_skills.get("ce-work") else "missing",
            "reason": "current change has executable tasks and accepted implementation path references",
        })
    return candidates


def summarize_artifact_checks(artifact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"artifact": entry["id"], "status": entry["status"], "path": entry.get("path")} for entry in artifact_entries]


def summarize_trace_checks(upstream_ids: list[str], produced_ids: list[str]) -> list[dict[str, Any]]:
    return [{"upstream_id_count": len(upstream_ids), "produced_id_count": len(produced_ids)}]


def summarize_task_checks(task_state: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"total": task_state["total"], "done": task_state["done"], "open": task_state["open"], "blocked": task_state["blocked"]}]


def summarize_contract_checks(
    artifact_entries: list[dict[str, Any]],
    contract_sync: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    checks = [
        {"artifact": entry["id"], "status": entry["status"]}
        for entry in artifact_entries
        if "contract" in entry["id"] or entry["id"] in {"change-context", "design"}
    ]
    if contract_sync:
        values = contract_sync.get("values", {}) if isinstance(contract_sync, dict) else {}
        checks.append(
            {
                "artifact": "contract-sync",
                "status": "present" if values else "missing",
                "owner": value_from_contract_sync(values, "contract_owner"),
                "canonical_source": value_from_contract_sync(values, "canonical_source"),
                "provider_repo": value_from_contract_sync(values, "provider_repo"),
                "consumer_repo": value_from_contract_sync(values, "consumer_repo"),
                "sync_mode": value_from_contract_sync(values, "sync_mode"),
                "machine_readable_contracts": contract_sync.get("machine_readable_contracts", []),
            }
        )
    return checks


def value_from_contract_sync(values: Any, key: str) -> str:
    if not isinstance(values, dict):
        return ""
    entry = values.get(key)
    if not isinstance(entry, dict):
        return ""
    return str(entry.get("value") or "")


def summarize_implementation_checks(code_paths: list[str], test_paths: list[str], source_map_required: bool) -> list[dict[str, Any]]:
    return [{
        "source": "source-map" if source_map_required else "schema-artifacts",
        "code_path_count": len(code_paths),
        "test_path_count": len(test_paths),
    }]


def extract_paths(text: str) -> set[str]:
    paths = {match.group(1).rstrip(".,;:)]}") for match in PATH_PATTERN.finditer(text)}
    return {path for path in paths if not path.endswith("/")}


def extract_ids(text: str) -> set[str]:
    return set(ID_PATTERN.findall(text))


def extract_tagged_lines(text: str, tags: tuple[str, ...]) -> list[str]:
    return [line.strip() for line in text.splitlines() if any(tag in line for tag in tags)]


def extract_section_lines(text: str, headings: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    captured: list[str] = []
    active = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            active = any(stripped.startswith(heading) for heading in headings)
            continue
        if active:
            if stripped.startswith("#"):
                break
            if stripped.startswith("- ") or stripped.startswith("|"):
                captured.append(stripped)
    return captured


def is_test_path(path: str) -> bool:
    lowered = path.lower()
    return lowered.startswith(("tests/", "test/")) or "/tests/" in lowered or lowered.endswith((".test.ts", ".test.js", ".spec.ts", ".spec.js", "_test.py"))


def is_execution_path(path: str) -> bool:
    lowered = path.lower()
    return lowered.startswith(("src/", "app/", "apps/", "lib/", "libs/", "packages/", "tests/", "test/"))


def read_yaml_scalar(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    return clean_value(match.group(1))


def parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [clean_value(part) for part in body.split(",")]
    return [clean_value(value)] if value else []


def clean_value(value: str) -> str:
    return value.strip().strip('"').strip("'")


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def to_artifact_spec(data: dict[str, Any]) -> ArtifactSpec:
    return ArtifactSpec(
        artifact_id=data["id"],
        generates=data.get("generates"),
        template=data.get("template"),
        requires=tuple(data.get("requires", [])),
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result
