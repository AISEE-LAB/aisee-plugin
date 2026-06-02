"""ID lookup and trace helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.id_registry import load_registry, lookup_entry, parse_id, registry_path
from aisee_cli.index import build_index
from aisee_cli.output import issue
from aisee_cli.project import rel


def get_id(project_root: Path, full_id: str) -> dict[str, Any]:
    parsed = parse_id(full_id)
    root = project_root.resolve()
    registry_file = registry_path(root)
    registry_available = registry_file.exists()
    registry = load_registry(root) if registry_available else {"version": 1, "scopes": {}}
    entry = lookup_entry(registry, full_id)
    index = build_index(root, write_cache=False)
    references = index["ids"].get(full_id, [])
    primary = choose_primary_source(entry, references)
    registry_label = rel(root, registry_file)
    issues = build_lookup_issues(full_id, entry, references, registry_available, registry_label)
    relations = build_relations(references)

    return {
        "status": lookup_status(entry, references),
        "id": full_id,
        "scope": parsed["scope"],
        "type": parsed["type"],
        "number": parsed["number"],
        "registry": {
            "available": registry_available,
            "path": registry_label,
            "entry": entry,
        },
        "source": primary,
        "references": references,
        "relations": relations,
        "issues": issues,
        "summary": {
            "reference_count": len(references),
            "change_count": len(relations["changes"]),
            "related_id_count": len(relations["ids"]),
            "code_path_count": len(relations["code_paths"]),
            "test_path_count": len(relations["test_paths"]),
            "issue_count": len(issues),
        },
        "meta": {
            "command": f"aisee get {full_id} --json",
            "source_index_written": False,
        },
    }


def trace_id(project_root: Path, full_id: str) -> dict[str, Any]:
    result = get_id(project_root, full_id)
    result["meta"]["command"] = f"aisee trace {full_id} --json"
    return result


def choose_primary_source(entry: dict[str, Any] | None, references: list[dict[str, Any]]) -> dict[str, Any] | None:
    owner = str(entry.get("owner") or "") if isinstance(entry, dict) else ""
    if owner:
        for reference in references:
            if reference.get("path") == owner:
                return {
                    "path": reference.get("path"),
                    "line": reference.get("line"),
                    "heading": reference.get("heading"),
                    "text": reference.get("text"),
                }
        return {
            "path": owner,
            "line": None,
            "heading": None,
            "text": None,
        }
    if references:
        reference = references[0]
        return {
            "path": reference.get("path"),
            "line": reference.get("line"),
            "heading": reference.get("heading"),
            "text": reference.get("text"),
        }
    return None


def build_relations(references: list[dict[str, Any]]) -> dict[str, Any]:
    changes: set[str] = set()
    related_ids: set[str] = set()
    code_paths: set[str] = set()
    test_paths: set[str] = set()
    for reference in references:
        path = str(reference.get("path") or "")
        parts = path.split("/")
        if parts[:2] == ["openspec", "changes"] and len(parts) >= 3:
            changes.add(parts[2])
        for related_id in reference.get("related_ids", []):
            if isinstance(related_id, str):
                related_ids.add(related_id)
        for related_path in reference.get("paths", []):
            if not isinstance(related_path, str):
                continue
            if is_test_path(related_path):
                test_paths.add(related_path)
            elif is_code_path(related_path):
                code_paths.add(related_path)
    return {
        "changes": sorted(changes),
        "ids": sorted(related_ids),
        "code_paths": sorted(code_paths),
        "test_paths": sorted(test_paths),
    }


def build_lookup_issues(
    full_id: str,
    entry: dict[str, Any] | None,
    references: list[dict[str, Any]],
    registry_available: bool,
    registry_label: str,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not registry_available:
        issues.append(issue("ID_REGISTRY_MISSING", "risk", f"{registry_label} is missing", registry_label))
    if entry is None:
        severity = "risk" if references else "info"
        issues.append(issue("ID_NOT_REGISTERED", severity, f"{full_id} is not registered", registry_label))
    elif entry.get("status") != "active":
        issues.append(issue("ID_NOT_ACTIVE", "info", f"{full_id} status is {entry.get('status')}", registry_label))
    if entry is not None and entry.get("status") == "active" and not references:
        issues.append(issue("ID_NO_REFERENCES", "risk", f"{full_id} is active but has no scanned references", str(entry.get("owner") or "")))
    return issues


def lookup_status(entry: dict[str, Any] | None, references: list[dict[str, Any]]) -> str:
    if entry is None:
        return "unregistered" if references else "missing"
    if entry.get("status") == "active" and references:
        return "linked"
    return str(entry.get("status") or "registered")


def is_test_path(path: str) -> bool:
    parts = path.split("/")
    return any(part in {"test", "tests", "__tests__"} for part in parts) or path.endswith(("_test.py", ".test.ts", ".spec.ts"))


def is_code_path(path: str) -> bool:
    return path.split("/", 1)[0] in {"src", "app", "apps", "lib", "libs", "packages"}
