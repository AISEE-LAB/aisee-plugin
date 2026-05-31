"""Build a rebuildable context index for Aisee projects."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.project import inspect_project_rules, rel
from aisee_cli.sources import load_sources, sources_path, validate_sources


INDEX_SCHEMA_VERSION = "1.0"
ID_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-(?:NEW-)?\d+\b")
PATH_PATTERN = re.compile(
    r"(?<![\w./-])"
    r"((?:src|app|apps|lib|libs|packages|tests|test|docs|openspec|assets|config)"
    r"/[A-Za-z0-9_./@:+-]+)"
)
HEADING_PATTERN = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+)$")
SCAN_DIRS = ("docs", "openspec", "skills", "references")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt"}


def index_path(root: Path) -> Path:
    return root / ".aisee" / "cache" / "context-index.json"


def build_index(root: Path, *, write_cache: bool) -> dict[str, Any]:
    sources_data, source_load_issues = load_sources(root)
    source_entries = sources_data.get("sources", []) if isinstance(sources_data, dict) else []
    source_issues = source_load_issues + validate_sources(root, source_entries)
    documents = scan_documents(root, source_entries)
    id_occurrences = collect_id_occurrences(documents)
    duplicate_sources = find_duplicate_sources(source_entries)
    issues = source_issues + duplicate_sources

    result = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "index": {
            "path": rel(root, index_path(root)),
            "writes": write_cache,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "project_rules": inspect_project_rules(root),
        "sources": {
            "path": rel(root, sources_path(root)),
            "count": len(source_entries) if isinstance(source_entries, list) else 0,
            "items": source_entries if isinstance(source_entries, list) else [],
        },
        "documents": documents,
        "ids": id_occurrences,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "aisee index --json",
            "cache_is_fact_source": False,
        },
    }
    if write_cache:
        path = index_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def scan_documents(root: Path, source_entries: Any) -> list[dict[str, Any]]:
    paths: set[str] = set()
    for dirname in SCAN_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                paths.add(rel(root, path))

    if isinstance(source_entries, list):
        for item in source_entries:
            if isinstance(item, dict) and item.get("path"):
                paths.add(str(item["path"]))

    documents: list[dict[str, Any]] = []
    for rel_path in sorted(paths):
        path = root / rel_path
        if not path.exists() or not path.is_file():
            documents.append({
                "path": rel_path,
                "status": "missing",
                "ids": [],
                "paths": [],
                "headings": [],
                "hash": None,
            })
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        documents.append(parse_document(rel_path, text))
    return documents


def parse_document(path: str, text: str) -> dict[str, Any]:
    ids = sorted(set(ID_PATTERN.findall(text)))
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

        line_ids = sorted(set(ID_PATTERN.findall(line)))
        if not line_ids:
            continue
        line_paths = sorted(set(PATH_PATTERN.findall(line)))
        occurrences.append({
            "line": line_number,
            "heading": current_heading,
            "ids": line_ids,
            "paths": line_paths,
            "text": line.strip(),
        })

    return {
        "path": path,
        "status": "present",
        "hash": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "ids": ids,
        "paths": paths,
        "headings": headings,
        "occurrences": occurrences,
    }


def collect_id_occurrences(documents: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    ids: dict[str, list[dict[str, Any]]] = {}
    for document in documents:
        if document.get("status") != "present":
            continue
        for occurrence in document.get("occurrences", []):
            if not isinstance(occurrence, dict):
                continue
            line_ids = [item for item in occurrence.get("ids", []) if isinstance(item, str)]
            document_ids = [item for item in document.get("ids", []) if isinstance(item, str)]
            for full_id in line_ids:
                ids.setdefault(full_id, []).append({
                    "path": document["path"],
                    "line": occurrence["line"],
                    "heading": occurrence.get("heading"),
                    "text": occurrence.get("text", ""),
                    "related_ids": sorted({item for item in [*line_ids, *document_ids] if item != full_id}),
                    "paths": occurrence.get("paths", []),
                })
    return {key: value for key, value in sorted(ids.items())}


def find_duplicate_sources(source_entries: Any) -> list[dict[str, str]]:
    if not isinstance(source_entries, list):
        return []
    seen: set[tuple[str, str, str]] = set()
    issues: list[dict[str, str]] = []
    for item in source_entries:
        if not isinstance(item, dict):
            continue
        key = (
            str(item.get("scope") or ""),
            str(item.get("type") or ""),
            str(item.get("path") or ""),
        )
        if key in seen:
            issues.append(issue("SOURCE_DUPLICATE", "risk", f"duplicate source: {'/'.join(key)}", ".aisee/sources.json"))
        seen.add(key)
    return issues
