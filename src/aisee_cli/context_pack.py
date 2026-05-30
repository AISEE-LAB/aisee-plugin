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


SUPPORTED_TARGETS = {"ce-work", "aisee-verify", "ce-doc-review", "ce-code-review"}
CONTEXT_SCHEMA_VERSION = "1.0"

ID_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-(?:NEW-)?\d+\b")
PATH_PATTERN = re.compile(
    r"(?<![\w./-])"
    r"((?:src|app|apps|lib|libs|packages|tests|test|docs|openspec|assets|config)"
    r"/[A-Za-z0-9_./@:+-]+)"
)
CHECKBOX_PATTERN = re.compile(r"^\s*-\s+\[(?P<mark>[ xX~-])\]\s*(?P<title>.*)$")


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

    artifact_entries = build_artifact_entries(change_path, artifact_specs)
    parsed_artifacts = parse_artifacts(change_path, artifact_entries)
    source_map_text = read_text(change_path / "source-map.md")
    tasks_text = read_text(change_path / "tasks.md")
    combined_text = collect_artifact_text(parsed_artifacts)

    source_paths = sorted(extract_paths(source_map_text))
    task_paths = sorted(extract_paths(tasks_text))
    artifact_paths = sorted(extract_paths(combined_text))
    all_paths = sorted(set(source_paths + task_paths + artifact_paths))
    code_paths = [p for p in all_paths if not is_test_path(p)]
    test_paths = [p for p in all_paths if is_test_path(p)]

    id_registry = inspect_id_registry(root)
    sources = inspect_sources(root, source_map_text)
    task_state = parse_task_state(tasks_text)
    upstream_ids = sorted(extract_ids(source_map_text))
    produced_ids = sorted(extract_ids(tasks_text) | extract_ids(combined_text))

    gaps = build_gaps(
        change_path=change_path,
        artifact_entries=artifact_entries,
        task_state=task_state,
        code_paths=code_paths,
        test_paths=test_paths,
        target=target,
        id_registry=id_registry,
    )

    read_order = build_read_order(root, change_path, artifact_entries, all_paths)
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
                },
                "artifacts": parsed_artifacts,
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
                "artifact_applicability": derive_artifact_applicability(source_map_text),
                "code_paths": code_paths,
                "test_paths": test_paths,
                "task_state": task_state,
                "verification_requirements": derive_verification_requirements(tasks_text),
                "open_questions": extract_tagged_lines(combined_text, ("[ASSUMPTION]", "[SPEC-GAP]", "[SOURCE-MAP-GAP]")),
            },
        },
        "generated": None,
        "gaps": gaps,
        "guardrails": build_guardrails(target),
        "evidence": build_evidence(root, change),
        "meta": {
            "command": f"aisee context pack --change {change} --for {target} --json",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "aisee",
            "mode": "parsed-and-derived",
        },
    }

    if target == "ce-work":
        pack["facts"]["derived"]["execution"] = {
            "start_from": task_state["open_items"][:1],
            "suggested_order": task_state["open_items"],
            "allowed_paths": sorted(set(code_paths + test_paths)),
            "forbidden_scope": pack["facts"]["derived"]["scope"]["out"],
            "requires_ce_plan": requires_ce_plan,
            "ce_plan_reason": ce_plan_reason(task_state, code_paths, test_paths, gaps) if requires_ce_plan else None,
        }
    elif target == "aisee-verify":
        pack["facts"]["derived"]["checks"] = {
            "schema_artifacts": summarize_artifact_checks(artifact_entries),
            "traceability": summarize_trace_checks(upstream_ids, produced_ids),
            "tasks": summarize_task_checks(task_state),
            "contracts": summarize_contract_checks(artifact_entries),
            "implementation": summarize_implementation_checks(code_paths, test_paths),
            "review_and_tests": [],
        }
        pack["facts"]["derived"]["drift_candidates"] = []

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
    candidates = [
        root / "openspec" / "schemas" / schema_name / "schema.yaml",
        root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / schema_name / "schema.yaml",
    ]
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


def inspect_id_registry(root: Path) -> dict[str, Any]:
    path = root / ".aisee" / "id-registry.json"
    return {
        "available": path.exists(),
        "checked": path.exists(),
        "path": rel(root, path) if path.exists() else None,
    }


def inspect_sources(root: Path, source_map_text: str) -> list[dict[str, Any]]:
    sources_path = root / ".aisee" / "sources.json"
    sources: list[dict[str, Any]] = []
    if sources_path.exists():
        try:
            data = json.loads(read_text(sources_path))
            if isinstance(data, list):
                sources.extend(item for item in data if isinstance(item, dict))
            elif isinstance(data, dict):
                for key, value in data.items():
                    sources.append({"id": key, "value": value})
        except json.JSONDecodeError:
            sources.append({"path": rel(root, sources_path), "status": "invalid-json"})

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
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not change_path.exists():
        gaps.append(gap("MISSING_CHANGE", "blocker", "Change directory does not exist", "openspec/changes"))
        return gaps

    for entry in artifact_entries:
        if entry["status"] == "missing":
            severity = "blocker" if entry["id"] in {"proposal", "source-map", "tasks"} else "risk"
            gaps.append(
                gap(
                    "MISSING_ARTIFACT",
                    severity,
                    f"Schema artifact is missing: {entry['id']}",
                    entry.get("generates") or entry["id"],
                )
            )

    if not id_registry["available"]:
        gaps.append(gap("ID_REGISTRY_GAP", "risk", ".aisee/id-registry.json is missing", ".aisee/id-registry.json"))

    if target == "ce-work":
        if task_state["total"] == 0:
            gaps.append(gap("TASK_GAP", "blocker", "tasks.md has no checkbox tasks", "tasks.md"))
        if not code_paths and not test_paths:
            gaps.append(
                gap(
                    "SOURCE_MAP_GAP",
                    "risk",
                    "No code or test paths were found from source-map, tasks, or contracts",
                    "source-map.md",
                )
            )
    return gaps


def gap(code: str, severity: str, message: str, owner_artifact: str) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "owner_artifact": owner_artifact,
        "related_ids": [],
        "suggested_fix": None,
    }


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
    return ["tasks.md", "source-map.md", "specs/**/*.md"]


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


def build_guardrails(target: str) -> list[str]:
    common = [
        "Use the current change as the only scope entry.",
        "Do not treat generated summaries as authoritative.",
        "Write durable conclusions back to OpenSpec artifacts.",
    ]
    if target == "ce-work":
        common.extend([
            "Follow tasks.md; do not create a parallel durable plan.",
            "Use only source-map/tasks/contracts paths unless reporting follow-up findings.",
        ])
    elif target == "aisee-verify":
        common.append("Diagnose consistency; do not make archive approval decisions.")
    return common


def build_evidence(root: Path, change: str) -> dict[str, Any]:
    review_dir = root / "docs" / "reviews"
    review_files = []
    if review_dir.exists():
        review_files = [rel(root, path) for path in sorted(review_dir.glob(f"*{change}*")) if path.is_file()]
    return {
        "openspec_validate": None,
        "ce_doc_review": [path for path in review_files if "doc" in path],
        "ce_code_review": [path for path in review_files if "code" in path],
        "tests": [],
        "manual_verification": [],
    }


def should_require_ce_plan(task_state: dict[str, Any], code_paths: list[str], test_paths: list[str], gaps: list[dict[str, Any]]) -> bool:
    if any(item["severity"] == "blocker" for item in gaps):
        return True
    if task_state["total"] == 0:
        return True
    return not code_paths and not test_paths


def ce_plan_reason(task_state: dict[str, Any], code_paths: list[str], test_paths: list[str], gaps: list[dict[str, Any]]) -> str:
    blocker_codes = [item["code"] for item in gaps if item["severity"] == "blocker"]
    if blocker_codes:
        return f"blocked by {', '.join(blocker_codes)}"
    if task_state["total"] == 0:
        return "tasks.md has no executable tasks"
    if not code_paths and not test_paths:
        return "source-map/tasks/contracts do not identify code or test paths"
    return "tasks/source-map need implementation refinement"


def summarize_artifact_checks(artifact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"artifact": entry["id"], "status": entry["status"], "path": entry.get("path")} for entry in artifact_entries]


def summarize_trace_checks(upstream_ids: list[str], produced_ids: list[str]) -> list[dict[str, Any]]:
    return [{"upstream_id_count": len(upstream_ids), "produced_id_count": len(produced_ids)}]


def summarize_task_checks(task_state: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"total": task_state["total"], "done": task_state["done"], "open": task_state["open"], "blocked": task_state["blocked"]}]


def summarize_contract_checks(artifact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"artifact": entry["id"], "status": entry["status"]}
        for entry in artifact_entries
        if "contract" in entry["id"] or entry["id"] in {"change-context", "design"}
    ]


def summarize_implementation_checks(code_paths: list[str], test_paths: list[str]) -> list[dict[str, Any]]:
    return [{"code_path_count": len(code_paths), "test_path_count": len(test_paths)}]


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
