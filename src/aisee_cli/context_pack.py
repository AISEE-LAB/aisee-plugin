"""Minimal context pack builder for Aisee changes.

This module intentionally uses conservative, template-aware heuristics. It
discovers files and trace hints; it does not try to understand arbitrary
Markdown as a second source of truth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from aisee_cli.anchor_refs import extract_anchor_refs, extract_local_ids, parse_anchor_ref
from aisee_cli.assets import resolve_source_asset_root
from aisee_cli.index import build_index
from aisee_cli.project import inspect_project_rules, rel
from aisee_cli.source_map import parse_source_map
from aisee_cli.tool_checks import check_compound_plugin


SUPPORTED_TARGETS = {"ce-work", "aisee-verify", "ce-doc-review", "ce-code-review"}
CONTEXT_SCHEMA_VERSION = "1.0"

PATH_PATTERN = re.compile(
    r"(?<![\w./-])"
    r"((?:src|app|apps|lib|libs|packages|tests|test|aisee/docs|docs|openspec|assets|config|contracts)"
    r"/[A-Za-z0-9_./@:+-]+)"
)
CHECKBOX_PATTERN = re.compile(r"^\s*-\s+\[(?P<mark>[ xX~-])\]\s*(?P<title>.*)$")
PRODUCED_LOCAL_ID_PREFIXES = ("SPEC-", "API-", "DATA-", "TASK-", "TEST-", "HW-", "FW-", "RT-", "VER-")
REQUIREDNESS_VALUES = {"always", "conditional", "never"}


@dataclass(frozen=True)
class ArtifactSpec:
    artifact_id: str
    generates: str | None = None
    template: str | None = None
    requires: tuple[str, ...] = ()
    requiredness: str = "always"
    na_requires_reason: bool = False
    capabilities: tuple[str, ...] = ()
    role: str | None = None


@dataclass(frozen=True)
class SchemaPaths:
    installed_path: Path | None
    source_path: Path | None

    @property
    def effective_path(self) -> Path | None:
        return self.installed_path or self.source_path


def build_context_pack(project_root: Path, change: str, target: str) -> dict[str, Any]:
    """Build a conservative context pack for a single OpenSpec change."""

    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"unsupported context target: {target}")

    root = project_root.resolve()
    change_path = root / "openspec" / "changes" / change
    schema_resolution = resolve_change_schema(root, change_path)
    schema_name = schema_resolution["effective_schema"]
    schema_paths = find_schema_paths(root, schema_name)
    schema_path = schema_paths.effective_path
    schema_info = parse_schema(schema_path) if schema_path else default_schema_info(schema_name)
    artifact_specs = schema_info["artifacts"]
    source_map_required = schema_generates_source_map(schema_info)
    tasks_required = schema_requires_tasks(schema_info)
    source_map = parse_source_map(change_path) if source_map_required else not_applicable_source_map()

    artifact_entries = order_artifact_entries_for_authoring(build_artifact_entries(change_path, artifact_specs))
    full_parsed_artifacts = parse_artifacts(change_path, artifact_entries)
    source_map_text = read_text(change_path / "source-map.md") if source_map_required else ""
    tasks_text = read_text(change_path / "tasks.md") if tasks_required else ""
    combined_text = collect_artifact_text(full_parsed_artifacts)

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

    sources = inspect_sources(source_map_text)
    task_state = parse_task_state(tasks_text)
    upstream_refs = sorted(extract_anchor_refs(source_map_text))
    produced_local_ids = sorted(extract_produced_local_ids(tasks_text) | extract_produced_local_ids(combined_text))
    all_change_local_ids = sorted(extract_ids(combined_text))
    source_reference_index = inspect_source_reference_index(root, upstream_refs, all_change_local_ids)
    traceability_mode = derive_traceability_mode(upstream_refs, produced_local_ids)
    parsed_artifacts = slim_artifacts(full_parsed_artifacts) if target == "ce-work" else full_parsed_artifacts

    evidence = build_evidence(root, change)

    gaps = build_gaps(
        change_path=change_path,
        artifact_entries=artifact_entries,
        task_state=task_state,
        code_paths=code_paths,
        test_paths=test_paths,
        target=target,
        source_reference_index=source_reference_index,
        source_map=source_map,
        source_map_required=source_map_required,
        unmapped_reference_paths=unmapped_reference_paths,
        tasks_text=tasks_text,
        schema_info=schema_info,
        schema_resolution=schema_resolution,
        schema_paths=schema_paths,
        produced_local_ids=produced_local_ids,
        evidence=evidence,
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
                    "installed": schema_paths.installed_path is not None,
                    "installed_path": rel(root, schema_paths.installed_path) if schema_paths.installed_path else None,
                    "source_path": rel(root, schema_paths.source_path) if schema_paths.source_path else None,
                    "metadata_present": schema_resolution["metadata_present"],
                    "metadata_path": schema_resolution["metadata_path"],
                    "metadata_schema": schema_resolution["metadata_schema"],
                    "config_schema": schema_resolution["config_schema"],
                    "resolved_from": schema_resolution["resolved_from"],
                    "hint_mismatches": schema_resolution["hint_mismatches"],
                    "artifacts": artifact_entries,
                    "capabilities": schema_info.get("capabilities", []),
                    "apply_requires": schema_info.get("apply_requires", []),
                    "apply_tracks": schema_info.get("apply_tracks"),
                    "archive_tracks": derive_archive_tracks(schema_info),
                    "source_map_required": source_map_required,
                    "tasks_required": tasks_required,
                    "issues": schema_info.get("issues", []),
                },
                "artifacts": parsed_artifacts,
                "source_map": source_map,
                "sources": sources,
                "source_reference_index": source_reference_index,
            },
            "derived": {
                "read_order": read_order,
                "scope": derive_scope(read_text(change_path / "proposal.md"), source_map_text),
                "traceability": {
                    "upstream_refs": upstream_refs,
                    "mode": traceability_mode,
                    "produced_local_ids": produced_local_ids,
                    "resolved_source_refs": source_reference_index["resolved"],
                    "unresolved_source_refs": source_reference_index["missing_references"],
                    "numbering_links": derive_id_links(source_map_text, tasks_text),
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
                "artifact_order": [entry["id"] for entry in artifact_entries],
                "task_state": task_state,
                "verification_requirements": derive_verification_requirements(tasks_text),
                "open_questions": extract_tagged_lines(combined_text, ("[ASSUMPTION]", "[SPEC-GAP]", "[SOURCE-MAP-GAP]")),
            },
        },
        "generated": None,
        "gaps": gaps,
        "guardrails": build_guardrails(target, source_map_required, tasks_required),
        "evidence": evidence,
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
            "completion_gate": build_completion_gate(
                apply_tracks=pack["facts"]["parsed"]["schema"]["apply_tracks"],
                task_state=task_state,
                evidence=evidence,
            ),
        }
        pack["facts"]["derived"]["execution"]["brief"] = build_execution_brief(
            root=root,
            change_path=change_path,
            read_order=read_order,
            scope=pack["facts"]["derived"]["scope"],
            traceability=pack["facts"]["derived"]["traceability"],
            allowed_paths=pack["facts"]["derived"]["execution"]["allowed_paths"],
            start_from=pack["facts"]["derived"]["execution"]["start_from"],
            verification_requirements=pack["facts"]["derived"]["verification_requirements"],
            gaps=gaps,
            task_state=task_state,
            evidence=evidence,
            apply_tracks=pack["facts"]["parsed"]["schema"]["apply_tracks"],
        )
    elif target == "aisee-verify":
        pack["facts"]["derived"]["checks"] = {
            "schema_artifacts": summarize_artifact_checks(artifact_entries),
            "traceability": summarize_trace_checks(
                upstream_refs,
                produced_local_ids,
                mode=traceability_mode,
            ),
            "tasks": summarize_task_checks(task_state),
            "contracts": summarize_contract_checks(artifact_entries, source_map, source_map.get("contract_sync")),
            "implementation": summarize_implementation_checks(code_paths, test_paths, source_map_required),
            "review_and_tests": summarize_review_and_test_checks(
                evidence=evidence,
                task_state=task_state,
                apply_tracks=pack["facts"]["parsed"]["schema"]["apply_tracks"],
            ),
        }
        pack["facts"]["derived"]["drift_candidates"] = []
    elif target == "ce-doc-review":
        pack["facts"]["derived"]["review"] = {
            "focus": ["schema_artifacts", "traceability", "tasks", "contracts", "open_questions"],
            "schema_artifacts": summarize_artifact_checks(artifact_entries),
            "traceability": summarize_trace_checks(
                upstream_refs,
                produced_local_ids,
                mode=traceability_mode,
            ),
            "tasks": summarize_task_checks(task_state),
            "contracts": summarize_contract_checks(artifact_entries, source_map, source_map.get("contract_sync")),
        }
    elif target == "ce-code-review":
        pack["facts"]["derived"]["review"] = {
            "focus": ["implementation", "tests", "source-map" if source_map_required else "schema-artifacts", "task_state"],
            "implementation": summarize_implementation_checks(code_paths, test_paths, source_map_required),
            "tasks": summarize_task_checks(task_state),
            "evidence": pack["evidence"],
        }

    return pack


def resolve_change_schema(root: Path, change_path: Path) -> dict[str, Any]:
    metadata = read_text(change_path / ".openspec.yaml")
    metadata_schema = read_yaml_scalar(metadata, "schema")
    config = read_text(root / "openspec" / "config.yaml")
    config_schema = read_yaml_scalar(config, "schema")
    schema_hints = read_schema_hints(change_path)
    effective_schema = metadata_schema or config_schema or "spec-driven"
    hint_mismatches = []
    for hint in schema_hints:
        if metadata_schema and hint["schema"] != metadata_schema:
            hint_mismatches.append({
                "path": hint["path"],
                "declared_schema": hint["schema"],
                "metadata_schema": metadata_schema,
            })
    return {
        "effective_schema": effective_schema,
        "metadata_present": bool(metadata_schema),
        "metadata_path": rel(root, change_path / ".openspec.yaml") if (change_path / ".openspec.yaml").exists() else None,
        "metadata_schema": metadata_schema,
        "config_schema": config_schema,
        "resolved_from": "change-metadata" if metadata_schema else ("project-config" if config_schema else "default"),
        "hint_mismatches": hint_mismatches,
    }


def find_schema_paths(root: Path, schema_name: str) -> SchemaPaths:
    asset_root = resolve_source_asset_root(root)
    installed_path = root / "openspec" / "schemas" / schema_name / "schema.yaml"
    source_path = None
    if asset_root is not None:
        candidate = asset_root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / schema_name / "schema.yaml"
        if candidate.exists():
            source_path = candidate
    return SchemaPaths(
        installed_path=installed_path if installed_path.exists() else None,
        source_path=source_path,
    )


def read_schema_hints(change_path: Path) -> list[dict[str, str]]:
    hints: list[dict[str, str]] = []
    for relative_path in ("proposal.md", "source-map.md"):
        text = read_text(change_path / relative_path)
        for line in text.splitlines():
            match = re.match(r"^\s*schema\s*:\s*([A-Za-z0-9_.-]+)\s*$", line, flags=re.IGNORECASE)
            if match:
                hints.append({"path": relative_path, "schema": match.group(1)})
    return hints


def parse_schema(schema_path: Path) -> dict[str, Any]:
    text = read_text(schema_path)
    data = yaml.safe_load(text) if text else {}
    if not isinstance(data, dict):
        raise ValueError("schema.yaml must be a YAML mapping")

    issues: list[dict[str, str]] = []
    raw_capabilities = data.get("capabilities")
    capabilities = parse_capabilities(raw_capabilities)
    if raw_capabilities is None:
        issues.append(schema_issue("SCHEMA_CAPABILITIES_MISSING", "blocker", "schema.yaml must define top-level capabilities"))
    elif not isinstance(raw_capabilities, list) or any(not isinstance(item, str) or not item.strip() for item in raw_capabilities):
        issues.append(schema_issue("SCHEMA_CAPABILITIES_INVALID", "blocker", "schema capabilities must be a non-empty string list"))

    artifacts: list[ArtifactSpec] = []
    raw_artifacts = data.get("artifacts")
    if not isinstance(raw_artifacts, list):
        raise ValueError("schema.yaml must define artifacts")
    for item in raw_artifacts:
        if not isinstance(item, dict):
            raise ValueError("schema artifact entries must be mappings")
        artifact_issues = validate_artifact_schema(item)
        issues.extend(artifact_issues)
        artifacts.append(to_artifact_spec(item))

    apply = data.get("apply") if isinstance(data.get("apply"), dict) else {}
    archive = data.get("archive") if isinstance(data.get("archive"), dict) else {}
    apply_requires = parse_string_list(apply.get("requires"))
    apply_tracks = normalize_track_value(apply.get("tracks"))
    archive_tracks = parse_tracks(archive.get("tracks"))
    if apply_tracks is None and "apply_execution" in capabilities:
        issues.append(schema_issue("SCHEMA_APPLY_TRACKS_MISSING", "blocker", "schema capability apply_execution requires apply.tracks"))
    if "archive_authority" in capabilities and not archive_tracks:
        issues.append(schema_issue("SCHEMA_ARCHIVE_TRACKS_MISSING", "risk", "schema capability archive_authority should declare archive.tracks"))

    return {
        "name": str(data.get("name") or schema_path.parent.name),
        "version": parse_int(None if data.get("version") is None else str(data.get("version"))),
        "artifacts": artifacts,
        "capabilities": capabilities,
        "apply_requires": apply_requires,
        "apply_tracks": apply_tracks,
        "archive_tracks": archive_tracks,
        "issues": issues,
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
        "capabilities": [],
        "apply_requires": ["tasks"],
        "apply_tracks": "tasks.md",
        "archive_tracks": ["tasks.md"],
        "issues": [schema_issue("SCHEMA_CONTRACT_UNAVAILABLE", "blocker", "schema.yaml is unavailable, so capability parsing cannot proceed")],
    }


def parse_capabilities(value: Any) -> list[str]:
    return dedupe(parse_string_list(value))


def parse_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return parse_inline_list(value)
    return []


def parse_tracks(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    normalized = normalize_track_value(value)
    return [normalized] if normalized else []


def normalize_track_value(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def validate_artifact_schema(data: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    artifact_id = str(data.get("id") or "")
    requiredness = str(data.get("requiredness") or "")
    capabilities = data.get("capabilities")
    if not artifact_id:
        issues.append(schema_issue("SCHEMA_ARTIFACT_ID_MISSING", "blocker", "schema artifact is missing id"))
    if requiredness not in REQUIREDNESS_VALUES:
        issues.append(
            schema_issue(
                "SCHEMA_ARTIFACT_REQUIREDNESS_INVALID",
                "blocker",
                f"artifact {artifact_id or '<unknown>'} must declare requiredness as one of: always, conditional, never",
            )
        )
    if capabilities is None:
        issues.append(
            schema_issue(
                "SCHEMA_ARTIFACT_CAPABILITIES_MISSING",
                "blocker",
                f"artifact {artifact_id or '<unknown>'} must declare capabilities",
            )
        )
    elif not isinstance(capabilities, list) or any(not isinstance(item, str) or not item.strip() for item in capabilities):
        issues.append(
            schema_issue(
                "SCHEMA_ARTIFACT_CAPABILITIES_INVALID",
                "blocker",
                f"artifact {artifact_id or '<unknown>'} capabilities must be a string list",
            )
        )
    na_requires_reason = data.get("na_requires_reason")
    if requiredness == "conditional" and not isinstance(na_requires_reason, bool):
        issues.append(
            schema_issue(
                "SCHEMA_ARTIFACT_NA_POLICY_MISSING",
                "blocker",
                f"artifact {artifact_id or '<unknown>'} must declare na_requires_reason for conditional requiredness",
            )
        )
    return issues


def schema_issue(code: str, severity: str, message: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
    }


def schema_has_capability(schema_info: dict[str, Any], capability: str) -> bool:
    capabilities = schema_info.get("capabilities", [])
    return capability in capabilities if isinstance(capabilities, list) else False


def artifact_has_capability(artifact: ArtifactSpec | dict[str, Any], capability: str) -> bool:
    if isinstance(artifact, ArtifactSpec):
        capabilities = artifact.capabilities
    else:
        capabilities = artifact.get("capabilities", [])
    return capability in capabilities if isinstance(capabilities, (list, tuple)) else False


def schema_generates_source_map(schema_info: dict[str, Any]) -> bool:
    return schema_has_capability(schema_info, "source_map_routing")


def schema_requires_tasks(schema_info: dict[str, Any]) -> bool:
    apply_tracks = schema_info.get("apply_tracks")
    if apply_tracks == "tasks.md":
        return True
    return any(
        spec.artifact_id == "tasks" or spec.generates == "tasks.md"
        for spec in schema_info.get("artifacts", [])
        if isinstance(spec, ArtifactSpec)
    )


def not_applicable_source_map() -> dict[str, Any]:
    return {
        "path": None,
        "status": "not_applicable",
        "parse_level": "not_applicable",
        "upstream_sources": [],
        "source_context": [],
        "artifact_applicability": [],
        "contract_sync": {"available": False, "values": {}, "machine_readable_contracts": []},
        "implementation_paths": [],
        "verification_evidence": [],
        "out_of_scope": [],
        "anchor_refs": [],
        "local_ids": [],
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
                "requiredness": spec.requiredness,
                "na_requires_reason": spec.na_requires_reason,
                "capabilities": list(spec.capabilities),
                "role": spec.role,
                "path": ", ".join(paths) if len(paths) > 1 else (paths[0] if paths else None),
                "required": spec.requiredness == "always",
                "status": "present" if paths else "missing",
            }
        )
    return entries


def order_artifact_entries_for_authoring(artifact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not artifact_entries:
        return []

    original_index = {entry["id"]: index for index, entry in enumerate(artifact_entries)}
    entries_by_id = {entry["id"]: entry for entry in artifact_entries}
    indegree = {entry["id"]: 0 for entry in artifact_entries}
    dependents: dict[str, list[str]] = {entry["id"]: [] for entry in artifact_entries}

    for entry in artifact_entries:
        for required_id in entry.get("requires", []):
            if required_id not in entries_by_id:
                continue
            indegree[entry["id"]] += 1
            dependents[required_id].append(entry["id"])

    def sort_key(artifact_id: str) -> tuple[int, int]:
        entry = entries_by_id[artifact_id]
        capabilities = entry.get("capabilities", [])
        is_apply_track = 1 if "apply_track" in capabilities else 0
        return (is_apply_track, original_index[artifact_id])

    ready = sorted((artifact_id for artifact_id, count in indegree.items() if count == 0), key=sort_key)
    ordered_ids: list[str] = []

    while ready:
        artifact_id = ready.pop(0)
        ordered_ids.append(artifact_id)
        for dependent_id in dependents[artifact_id]:
            indegree[dependent_id] -= 1
            if indegree[dependent_id] == 0:
                ready.append(dependent_id)
                ready.sort(key=sort_key)

    if len(ordered_ids) != len(artifact_entries):
        return artifact_entries
    return [entries_by_id[artifact_id] for artifact_id in ordered_ids]


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


def extract_produced_local_ids(text: str) -> set[str]:
    return {item for item in extract_ids(text) if item.startswith(PRODUCED_LOCAL_ID_PREFIXES)}


def slim_artifacts(parsed_artifacts: dict[str, Any]) -> dict[str, Any]:
    slimmed: dict[str, Any] = {}
    for key, value in parsed_artifacts.items():
        if isinstance(value, dict):
            slimmed[key] = {field: field_value for field, field_value in value.items() if field != "text"}
        elif isinstance(value, list):
            slimmed[key] = [{field: field_value for field, field_value in item.items() if field != "text"} for item in value]
        else:
            slimmed[key] = value
    return slimmed


def derive_traceability_mode(upstream_refs: list[str], produced_local_ids: list[str]) -> str:
    if upstream_refs:
        return "source-ref"
    if produced_local_ids:
        return "numbered"
    return "empty"


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


def inspect_source_reference_index(root: Path, references: list[str], local_ids: list[str]) -> dict[str, Any]:
    index = build_index(root, write_cache=False)
    documents = {item.get("path"): item for item in index.get("documents", []) if isinstance(item, dict)}
    reference_index = index.get("references", {})
    resolved: list[dict[str, Any]] = []
    missing_references: list[str] = []
    errors: list[str] = []
    for reference in references:
        try:
            parsed = parse_anchor_ref(reference)
        except ValueError as error:
            errors.append(str(error))
            missing_references.append(reference)
            continue
        document = parsed["document"]
        canonical_ref = f"{document}#{parsed['local_id']}" if document else None
        occurrences = reference_index.get(canonical_ref, []) if canonical_ref else []
        if document and any(item.get("document") == document for item in occurrences):
            resolved.append({
                "reference": reference,
                "canonical_reference": canonical_ref,
                "document": document,
                "local_id": parsed["local_id"],
                "reference_type": parsed["reference_type"],
            })
        else:
            missing_references.append(reference)
    return {
        "available": True,
        "checked": True,
        "scan_source": "internal",
        "queried_references": sorted(references),
        "queried_local_ids": sorted(local_ids),
        "resolved": sorted(resolved, key=lambda item: item["reference"]),
        "missing_references": sorted(set(missing_references)),
        "temporary_local_ids": sorted([item for item in local_ids if "-NEW-" in item]),
        "documents": sorted(path for path in documents if isinstance(path, str)),
        "errors": errors,
    }


def inspect_sources(source_map_text: str) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for path in sorted(extract_paths(source_map_text)):
        if path.startswith(("aisee/docs/", "docs/")):
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
    source_reference_index: dict[str, Any],
    source_map: dict[str, Any],
    source_map_required: bool,
    unmapped_reference_paths: list[str],
    tasks_text: str,
    schema_info: dict[str, Any],
    schema_resolution: dict[str, Any],
    schema_paths: SchemaPaths,
    produced_local_ids: list[str],
    evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not change_path.exists():
        gaps.append(gap("MISSING_CHANGE", "blocker", "Change directory does not exist", "openspec/changes"))
        return gaps

    if not schema_resolution.get("metadata_present"):
        gaps.append(
            gap(
                "SCHEMA_METADATA_MISSING",
                "blocker",
                "Change metadata does not declare a schema; author and execution stages must stop until .openspec.yaml is fixed",
                ".openspec.yaml",
            )
        )

    hint_mismatches = schema_resolution.get("hint_mismatches", [])
    if hint_mismatches:
        details = ", ".join(
            f"{item['path']} declares {item['declared_schema']}" for item in hint_mismatches if item.get("path")
        )
        gaps.append(
            gap(
                "SCHEMA_MISMATCH",
                "blocker",
                f"Change schema metadata conflicts with schema hints in current artifacts: {details}",
                ".openspec.yaml",
            )
        )

    if schema_paths.installed_path is None:
        schema_name = schema_resolution["effective_schema"]
        owner_artifact = f"openspec/schemas/{schema_name}/schema.yaml"
        if schema_paths.source_path is not None:
            gaps.append(
                gap(
                    "SCHEMA_NOT_INSTALLED",
                    "blocker",
                    "Selected schema is available from marketplace plugin assets but not installed into the current project",
                    owner_artifact,
                    suggested_fix={
                        "skill": "aisee-schema-pack",
                        "command": f"node <skill-dir>/scripts/setup-schemas.js --schema {schema_name}",
                        "writes": True,
                    },
                )
            )
        else:
            gaps.append(
                gap(
                    "SCHEMA_NOT_FOUND",
                    "blocker",
                    "Selected schema is not available in the current project or marketplace plugin assets",
                    owner_artifact,
                )
            )

    if source_map_required:
        gaps.extend(source_map.get("issues", []))
    for schema_issue_item in schema_info.get("issues", []):
        gaps.append(
            gap(
                str(schema_issue_item.get("code") or "SCHEMA_ISSUE"),
                str(schema_issue_item.get("severity") or "risk"),
                str(schema_issue_item.get("message") or "schema issue"),
                f"openspec/schemas/{schema_resolution['effective_schema']}/schema.yaml",
            )
        )

    for entry in artifact_entries:
        if entry["status"] == "missing":
            if artifact_not_required(entry, source_map):
                continue
            severity = "blocker" if entry.get("requiredness") == "always" else "risk"
            gaps.append(
                gap(
                    "MISSING_ARTIFACT",
                    severity,
                    f"Schema artifact is missing: {entry['id']}",
                    entry.get("generates") or entry["id"],
                )
            )

    reference_owner_artifact = "source-map.md" if source_map_required else "schema artifacts"
    temporary_ids = source_reference_index.get("temporary_local_ids", [])
    if temporary_ids:
        gaps.append(
            gap(
                "NUMBERING_FINALIZATION_REQUIRED",
                "risk",
                "Change contains temporary numbers that must be finalized before authoring completes",
                reference_owner_artifact,
                temporary_ids,
            )
        )
    missing_references = source_reference_index.get("missing_references", [])
    if missing_references:
        gaps.append(
            gap(
                "SOURCE_REF_RESOLUTION_MISSING",
                "risk",
                "Change references source refs that could not be resolved",
                reference_owner_artifact,
                missing_references,
            )
        )
    if source_map_required and not missing_references and not source_reference_index.get("resolved") and not produced_local_ids:
        gaps.append(
            gap(
                "SOURCE_CONTEXT_MISSING",
                "risk",
                "source-map.md has no source refs and no produced numbers",
                "source-map.md",
            )
        )
    if target == "ce-work":
        if schema_requires_tasks(schema_info) and task_state["total"] == 0:
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
    apply_track_stale_gap = build_apply_track_writeback_gap(
        schema_info=schema_info,
        task_state=task_state,
        evidence=evidence,
    )
    if apply_track_stale_gap is not None:
        gaps.append(apply_track_stale_gap)
    gaps.extend(contract_sync_gaps(schema_info, artifact_entries, source_map, tasks_text))
    return gaps


def gap(
    code: str,
    severity: str,
    message: str,
    owner_artifact: str,
    related_refs: list[str] | None = None,
    suggested_fix: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "owner_artifact": owner_artifact,
        "related_refs": related_refs or [],
        "suggested_fix": suggested_fix,
    }


def artifact_not_required(entry: dict[str, Any], source_map: dict[str, Any]) -> bool:
    requiredness = str(entry.get("requiredness") or "always")
    if requiredness == "never":
        return True
    if requiredness != "conditional":
        return False
    for row in source_map.get("artifact_applicability", []):
        if not isinstance(row, dict):
            continue
        artifact_id = str(entry.get("id") or "")
        generates = str(entry.get("generates") or "")
        artifact = str(row.get("artifact") or "")
        if artifact not in {artifact_id, generates}:
            continue
        required = str(row.get("required") or "").strip().lower()
        if required == "no" and str(row.get("reason") or "").strip():
            return True
    return False


def contract_sync_gaps(
    schema_info: dict[str, Any],
    artifact_entries: list[dict[str, Any]],
    source_map: dict[str, Any],
    tasks_text: str,
) -> list[dict[str, Any]]:
    if not schema_has_capability(schema_info, "contract_sync"):
        return []
    service_contract = next((entry for entry in artifact_entries if artifact_has_capability(entry, "contract_sync")), None)
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
    tracks = schema_info.get("archive_tracks")
    if isinstance(tracks, list) and tracks:
        return [str(item) for item in tracks if str(item).strip()]
    apply_tracks = schema_info.get("apply_tracks")
    if isinstance(apply_tracks, str) and apply_tracks:
        return [apply_tracks]
    return []


def derive_scope(proposal_text: str, source_map_text: str) -> dict[str, list[str]]:
    return {
        "in": extract_section_lines(proposal_text + "\n" + source_map_text, ("## 变更范围", "## Change Scope", "## In Scope")),
        "out": extract_section_lines(proposal_text + "\n" + source_map_text, ("## 不在范围", "## Out of Scope", "## 不在本 Change 范围")),
        "follow_up_candidates": extract_tagged_lines(proposal_text + "\n" + source_map_text, ("[FOLLOW-UP]", "[SOURCE-MAP-GAP]")),
    }


def derive_id_links(source_map_text: str, tasks_text: str) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    for line in (source_map_text + "\n" + tasks_text).splitlines():
        refs = sorted(extract_anchor_refs(line))
        local_ids = sorted(extract_ids(line))
        if len(refs) + len(local_ids) >= 2:
            links.append({"refs": refs, "local_ids": local_ids, "source": line.strip()})
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


def build_execution_brief(
    *,
    root: Path,
    change_path: Path,
    read_order: list[str],
    scope: dict[str, Any],
    traceability: dict[str, Any],
    allowed_paths: list[str],
    start_from: list[str],
    verification_requirements: list[str],
    gaps: list[dict[str, Any]],
    task_state: dict[str, Any],
    evidence: dict[str, Any],
    apply_tracks: str | None,
) -> dict[str, Any]:
    authoritative_sources = [
        rel(root, change_path / relative_path)
        for relative_path in ("proposal.md", "source-map.md", "tasks.md")
        if (change_path / relative_path).exists()
    ]
    risk_items = [
        {"code": item["code"], "severity": item["severity"], "message": item["message"]}
        for item in gaps
        if item.get("severity") in {"blocker", "risk"}
    ]
    return {
        "authoritative_sources": authoritative_sources,
        "scope": {
            "in": scope.get("in", []),
            "out": scope.get("out", []),
        },
        "read_first": read_order[:8],
        "source_refs": {
            "upstream_refs": traceability.get("upstream_refs", []),
            "mode": traceability.get("mode"),
        },
        "produced_local_ids": traceability.get("produced_local_ids", []),
        "allowed_paths": allowed_paths,
        "task_start": start_from,
        "verification": verification_requirements,
        "completion_gate": build_completion_gate(
            apply_tracks=apply_tracks,
            task_state=task_state,
            evidence=evidence,
        ),
        "risks": risk_items,
    }


def build_guardrails(target: str, source_map_required: bool, tasks_required: bool) -> list[str]:
    common = [
        "Use the current change as the only scope entry.",
        "Do not treat generated summaries as authoritative.",
        "Write durable conclusions back to OpenSpec artifacts.",
    ]
    if target == "ce-work":
        common.append(
            "Follow tasks.md; do not create a parallel durable plan."
            if tasks_required
            else "Follow the current schema apply tracks; do not create a parallel durable plan."
        )
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


def build_completion_gate(
    *,
    apply_tracks: str | None,
    task_state: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    completion_evidence = collect_completion_evidence_paths(evidence)
    return {
        "apply_tracks": apply_tracks,
        "must_write_back_before_complete": bool(apply_tracks),
        "task_state": {
            "total": task_state["total"],
            "done": task_state["done"],
            "open": task_state["open"],
            "blocked": task_state["blocked"],
        },
        "completion_evidence_paths": completion_evidence,
        "status": (
            "writeback-required"
            if apply_tracks and completion_evidence and task_state["done"] == 0 and task_state["total"] > 0
            else "ready"
        ),
    }


def build_evidence(root: Path, change: str) -> dict[str, Any]:
    review_dir = root / "docs" / "reviews"
    review_files: list[str] = []
    if review_dir.exists():
        review_files = [rel(root, path) for path in sorted(review_dir.glob(f"*{change}*")) if path.is_file()]
    aisee_review_lens = [path for path in review_files if is_aisee_reviewer_path(path)]
    ce_review_files = [path for path in review_files if path not in aisee_review_lens]
    verification_dir = root / "docs" / "verification"
    verification_files = []
    if verification_dir.exists():
        verification_files = [rel(root, path) for path in sorted(verification_dir.glob(f"*{change}*")) if path.is_file()]
    classified = classify_evidence(ce_review_files, verification_files)
    return {
        "openspec_validate": first_matching(verification_files, ("validate", "openspec")),
        "ce_doc_review": [path for path in ce_review_files if "doc" in path],
        "ce_code_review": [path for path in ce_review_files if "code" in path],
        "aisee_review_lens": aisee_review_lens,
        "tests": [path for path in verification_files if "test" in path],
        "manual_verification": [path for path in verification_files if "manual" in path or "verify" in path],
        "docsite": classified["docsite"],
        "infra": classified["infra"],
        "security": classified["security"],
        "quick_fix": classified["quick_fix"],
        "details": build_evidence_details(root, ce_review_files, aisee_review_lens, verification_files, classified),
    }


def collect_completion_evidence_paths(evidence: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("ce_doc_review", "ce_code_review", "aisee_review_lens", "tests", "manual_verification"):
        value = evidence.get(key)
        if isinstance(value, list):
            paths.extend(path for path in value if isinstance(path, str))
    domain = evidence.get("details", {}).get("domain", {})
    if isinstance(domain, dict):
        for categories in domain.values():
            if not isinstance(categories, dict):
                continue
            for entries in categories.values():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if isinstance(entry, dict):
                        path = entry.get("path")
                        if isinstance(path, str) and path:
                            paths.append(path)
    return dedupe(paths)


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
    ce_review_files: list[str],
    aisee_review_lens: list[str],
    verification_files: list[str],
    classified: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    validate_path = first_matching(verification_files, ("validate", "openspec"))
    return {
        "openspec_validate": parse_status_file(root, validate_path) if validate_path else None,
        "reviews": [parse_review_file(root, path) for path in ce_review_files],
        "aisee_review_lens": [parse_review_file(root, path) for path in aisee_review_lens],
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
        "accepted_risks": collect_accepted_risks(root, ce_review_files + aisee_review_lens + verification_files),
    }


def is_aisee_reviewer_path(path: str) -> bool:
    lowered = path.lower()
    return any(
        marker in lowered
        for marker in (
            "aisee-change-architect",
            "aisee-spec-reviewer",
            "aisee-implementation-reviewer",
        )
    )


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
    if any(item["code"] in {"SOURCE_MAP_UNSTRUCTURED", "SOURCE_MAP_GAP", "SOURCE_MAP_UNMAPPED_PATH"} for item in gaps):
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
                "reason": "review context pack gaps, scope guardrails, and review recommendation before CE execution",
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


def summarize_trace_checks(
    upstream_refs: list[str],
    produced_local_ids: list[str],
    mode: str | None = None,
) -> list[dict[str, Any]]:
    return [{
        "mode": mode,
        "upstream_ref_count": len(upstream_refs),
        "produced_local_id_count": len(produced_local_ids),
    }]


def summarize_task_checks(task_state: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"total": task_state["total"], "done": task_state["done"], "open": task_state["open"], "blocked": task_state["blocked"]}]


def summarize_contract_checks(
    artifact_entries: list[dict[str, Any]],
    source_map: dict[str, Any],
    contract_sync: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    checks = [
        {"artifact": entry["id"], "status": "not_required" if artifact_not_required(entry, source_map) else entry["status"]}
        for entry in artifact_entries
        if artifact_has_capability(entry, "contract_surface")
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


def summarize_review_and_test_checks(
    *,
    evidence: dict[str, Any],
    task_state: dict[str, Any],
    apply_tracks: str | None,
) -> list[dict[str, Any]]:
    completion_evidence = collect_completion_evidence_paths(evidence)
    return [{
        "apply_tracks": apply_tracks,
        "completion_evidence_count": len(completion_evidence),
        "completion_evidence_paths": completion_evidence,
        "task_done_count": task_state["done"],
        "writeback_consistent": not (apply_tracks and completion_evidence and task_state["done"] == 0 and task_state["total"] > 0),
    }]


def build_apply_track_writeback_gap(
    *,
    schema_info: dict[str, Any],
    task_state: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any] | None:
    apply_tracks = schema_info.get("apply_tracks")
    if not isinstance(apply_tracks, str) or not apply_tracks.strip():
        return None
    completion_evidence = collect_completion_evidence_paths(evidence)
    if not completion_evidence or task_state["total"] == 0 or task_state["done"] > 0:
        return None
    return gap(
        "APPLY_TRACKS_WRITEBACK_REQUIRED",
        "blocker",
        "implementation or verification evidence exists, but apply tracks still show no completed tasks; update apply tracks before reporting work complete",
        apply_tracks,
        completion_evidence,
    )


def extract_paths(text: str) -> set[str]:
    paths = {match.group(1).rstrip(".,;:)]}") for match in PATH_PATTERN.finditer(text)}
    return {path for path in paths if not path.endswith("/")}


def extract_ids(text: str) -> set[str]:
    return extract_local_ids(text)


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
        requiredness=str(data.get("requiredness") or "always"),
        na_requires_reason=bool(data.get("na_requires_reason", False)),
        capabilities=tuple(parse_capabilities(data.get("capabilities"))),
        role=clean_value(str(data.get("role") or "")) or None,
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
