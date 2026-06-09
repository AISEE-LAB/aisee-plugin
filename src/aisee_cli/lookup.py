"""Anchor lookup and trace helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.anchor_refs import canonical_anchor, parse_anchor_ref, resolve_alias_path
from aisee_cli.index import build_index
from aisee_cli.output import issue


def get_anchor(project_root: Path, reference: str) -> dict[str, Any]:
    root = project_root.resolve()
    parsed = parse_anchor_ref(reference)
    index = build_index(root, write_cache=False)

    document = parsed["document"]
    alias = parsed["alias"]
    if alias:
        document = resolve_alias_path(index["sources"]["items"], alias)

    canonical_reference = canonical_anchor(document, parsed["local_id"]) if document else None
    references = index["anchors"].get(canonical_reference, []) if canonical_reference else []
    primary = choose_primary_source(references, document, parsed["local_id"])
    issues = build_lookup_issues(parsed, document, references, index)
    relations = build_relations(references)

    return {
        "status": lookup_status(document, references),
        "reference_type": parsed["reference_type"],
        "reference": reference,
        "canonical_reference": canonical_reference,
        "document": document,
        "local_id": parsed["local_id"],
        "alias": alias,
        "source": primary,
        "references": references,
        "relations": relations,
        "issues": issues,
        "summary": {
            "reference_count": len(references),
            "change_count": len(relations["changes"]),
            "related_reference_count": len(relations["references"]),
            "code_path_count": len(relations["code_paths"]),
            "test_path_count": len(relations["test_paths"]),
            "issue_count": len(issues),
        },
        "meta": {
            "command": f"aisee get {reference} --json",
            "source_index_written": False,
        },
    }


def trace_anchor(project_root: Path, reference: str) -> dict[str, Any]:
    result = get_anchor(project_root, reference)
    result["meta"]["command"] = f"aisee trace {reference} --json"
    return result


def choose_primary_source(references: list[dict[str, Any]], document: str | None, local_id: str) -> dict[str, Any] | None:
    if references:
        reference = references[0]
        return {
            "path": reference.get("path"),
            "line": reference.get("line"),
            "heading": reference.get("heading"),
            "text": reference.get("text"),
        }
    if document:
        return {
            "path": document,
            "line": None,
            "heading": None,
            "text": f"{document}#{local_id}",
        }
    return None


def build_relations(references: list[dict[str, Any]]) -> dict[str, Any]:
    changes: set[str] = set()
    related_refs: set[str] = set()
    code_paths: set[str] = set()
    test_paths: set[str] = set()
    for reference in references:
        path = str(reference.get("path") or "")
        current_reference = str(reference.get("reference") or "")
        parts = path.split("/")
        if parts[:2] == ["openspec", "changes"] and len(parts) >= 3:
            changes.add(parts[2])
        document = str(reference.get("document") or path)
        for local_id in reference.get("related_local_ids", []):
            if isinstance(local_id, str):
                related_ref = canonical_anchor(document, local_id)
                if related_ref != current_reference:
                    related_refs.add(related_ref)
        for anchor_ref in reference.get("anchor_refs", []):
            if isinstance(anchor_ref, str) and anchor_ref != current_reference:
                related_refs.add(anchor_ref)
        for related_path in reference.get("paths", []):
            if not isinstance(related_path, str):
                continue
            if is_test_path(related_path):
                test_paths.add(related_path)
            elif is_code_path(related_path):
                code_paths.add(related_path)
    return {
        "changes": sorted(changes),
        "references": sorted(related_refs),
        "code_paths": sorted(code_paths),
        "test_paths": sorted(test_paths),
    }


def build_lookup_issues(
    parsed: dict[str, Any],
    document: str | None,
    references: list[dict[str, Any]],
    index: dict[str, Any],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    documents = {item.get("path"): item for item in index.get("documents", []) if isinstance(item, dict)}
    if parsed["reference_type"] == "alias-anchor" and document is None:
        issues.append(issue("ANCHOR_ALIAS_NOT_FOUND", "risk", f"alias is not registered: {parsed['alias']}", "aisee/registry/sources.json"))
    if document and not any(item.get("path") == document for item in index.get("documents", [])):
        issues.append(issue("ANCHOR_DOCUMENT_MISSING", "risk", f"document does not exist: {document}", document))
    if document and not references:
        issues.append(issue("ANCHOR_LOCAL_ID_MISSING", "risk", f"{parsed['local_id']} was not found in {document}", document))
    legacy = set()
    if document and isinstance(documents.get(document), dict):
        legacy.update(item for item in documents[document].get("legacy_full_ids", []) if isinstance(item, str))
    legacy.update(full_id for reference in references for full_id in reference.get("legacy_full_ids", []) if isinstance(full_id, str))
    for full_id in sorted(legacy):
        issues.append(issue("LEGACY_FULL_ID_REFERENCE", "info", f"legacy full ID remains in anchor source context: {full_id}", str(document or "")))
    return issues


def lookup_status(document: str | None, references: list[dict[str, Any]]) -> str:
    if document and references:
        return "linked"
    if document:
        return "missing-local-id"
    return "missing-document"


def is_test_path(path: str) -> bool:
    parts = path.split("/")
    return any(part in {"test", "tests", "__tests__"} for part in parts) or path.endswith(("_test.py", ".test.ts", ".spec.ts"))


def is_code_path(path: str) -> bool:
    return path.split("/", 1)[0] in {"src", "app", "apps", "lib", "libs", "packages"}
