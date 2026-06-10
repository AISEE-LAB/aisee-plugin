"""Build a rebuildable context index for Aisee projects."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aisee_cli.anchor_refs import extract_anchor_refs, extract_local_ids, parse_anchor_ref
from aisee_cli.output import status_from_issues, summarize_issues
from aisee_cli.planning_docs import inspect_planning_docs
from aisee_cli.project import inspect_project_rules, rel


INDEX_SCHEMA_VERSION = "1.0"
PATH_PATTERN = re.compile(
    r"(?<![\w./-])"
    r"((?:src|app|apps|lib|libs|packages|tests|test|aisee/docs|docs|openspec|assets|config)"
    r"/[A-Za-z0-9_./@:+-]+)"
)
HEADING_PATTERN = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+)$")
SCAN_DIRS = ("aisee/docs", "docs", "openspec", "skills", "references")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}


def build_index(root: Path, *, write_cache: bool) -> dict[str, Any]:
    documents = scan_documents(root)
    planning_docs = inspect_planning_docs(root)
    references = collect_reference_occurrences(documents)
    issues = planning_docs["issues"]

    result = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "index": {
            "writes": write_cache,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "project_rules": inspect_project_rules(root),
        "documents": documents,
        "planning_docs": planning_docs,
        "references": references,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "internal context index",
            "cache_is_fact_source": False,
        },
    }
    if write_cache:
        raise ValueError("context index cache writes are not supported")
    return result


def scan_documents(root: Path) -> list[dict[str, Any]]:
    paths: set[str] = set()
    for dirname in SCAN_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                paths.add(rel(root, path))

    documents: list[dict[str, Any]] = []
    for rel_path in sorted(paths):
        path = root / rel_path
        if not path.exists() or not path.is_file():
            documents.append({
                "path": rel_path,
                "status": "missing",
                "local_ids": [],
                "anchor_refs": [],
                "paths": [],
                "headings": [],
                "hash": None,
            })
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        documents.append(parse_document(rel_path, text))
    return documents


def parse_document(path: str, text: str) -> dict[str, Any]:
    local_ids = sorted(extract_local_ids(text))
    anchor_refs = sorted(extract_anchor_refs(text))
    paths = sorted(set(PATH_PATTERN.findall(text)))
    headings: list[dict[str, Any]] = []
    current_heading: dict[str, Any] | None = None
    occurrences: list[dict[str, Any]] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            current_heading = {
                "level": len(heading_match.group("level")),
                "title": heading_match.group("title").strip(),
                "line": line_number,
            }
            headings.append(current_heading)

        line_local_ids = sorted(extract_local_ids(line))
        line_anchor_refs = sorted(extract_anchor_refs(line))
        if not line_local_ids and not line_anchor_refs:
            continue
        line_paths = sorted(set(PATH_PATTERN.findall(line)))
        occurrences.append({
            "line": line_number,
            "heading": current_heading,
            "local_ids": line_local_ids,
            "anchor_refs": line_anchor_refs,
            "paths": line_paths,
            "text": line.strip(),
        })

    return {
        "path": path,
        "status": "present",
        "hash": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "local_ids": local_ids,
        "anchor_refs": anchor_refs,
        "paths": paths,
        "headings": headings,
        "occurrences": occurrences,
    }


def collect_reference_occurrences(documents: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    references: dict[str, list[dict[str, Any]]] = {}
    for document in documents:
        if document.get("status") != "present":
            continue
        for occurrence in document.get("occurrences", []):
            if not isinstance(occurrence, dict):
                continue
            line_local_ids = [item for item in occurrence.get("local_ids", []) if isinstance(item, str)]
            document_local_ids = [item for item in document.get("local_ids", []) if isinstance(item, str)]
            for local_id in line_local_ids:
                append_anchor_occurrence(
                    references,
                    canonical_ref=f"{document['path']}#{local_id}",
                    document=document,
                    occurrence=occurrence,
                    related_local_ids=sorted({item for item in [*line_local_ids, *document_local_ids] if item != local_id}),
                )
            for anchor_ref in occurrence.get("anchor_refs", []):
                if not isinstance(anchor_ref, str):
                    continue
                try:
                    parsed = parse_anchor_ref(anchor_ref)
                except ValueError:
                    continue
                append_anchor_occurrence(
                    references,
                    canonical_ref=str(parsed["canonical_reference"] or anchor_ref),
                    document=document,
                    occurrence=occurrence,
                    related_local_ids=[],
                )
    return {key: value for key, value in sorted(references.items())}


def append_anchor_occurrence(
    references: dict[str, list[dict[str, Any]]],
    *,
    canonical_ref: str,
    document: dict[str, Any],
    occurrence: dict[str, Any],
    related_local_ids: list[str],
) -> None:
    local_id = canonical_ref.rsplit("#", 1)[-1]
    references.setdefault(canonical_ref, []).append({
        "reference": canonical_ref,
        "path": document["path"],
        "document": document["path"],
        "local_id": local_id,
        "line": occurrence["line"],
        "heading": occurrence.get("heading"),
        "text": occurrence.get("text", ""),
        "related_local_ids": related_local_ids,
        "anchor_refs": occurrence.get("anchor_refs", []),
        "paths": occurrence.get("paths", []),
    })
