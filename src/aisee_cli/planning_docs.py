"""Planning document discovery and read-only diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from aisee_cli.output import issue, summarize_issues
from aisee_cli.project import rel


VALID_DOC_TYPES = {
    "srs",
    "ui-content",
    "architecture",
    "design-spec",
    "design-assets",
    "implementation-brief",
    "reflect",
}
VALID_STATUSES = {"draft", "active", "superseded", "archived"}
PLANNING_DOC_PREFIXES = {
    "aisee/docs/requirements/": "srs",
    "docs/requirements/": "srs",
    "aisee/docs/ui-content/": "ui-content",
    "docs/ui-content/": "ui-content",
    "aisee/docs/architecture/": "architecture",
    "docs/architecture/": "architecture",
    "aisee/docs/design-spec/": "design-spec",
    "docs/design-spec/": "design-spec",
    "aisee/docs/design-assets/": "design-assets",
    "docs/design-assets/": "design-assets",
    "aisee/docs/reflect/": "reflect",
    "docs/reflect/": "reflect",
    "aisee/cache/implementation-bridge/": "implementation-brief",
}
REQUIRED_FIELDS = {"title", "doc_type", "status", "date", "scope", "owner", "source_refs", "change_refs"}


def inspect_planning_docs(root: Path) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    for prefix, path_hint in PLANNING_DOC_PREFIXES.items():
        base = root / prefix
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            rel_path = rel(root, path)
            seen_paths.add(rel_path)
            item, item_issues = inspect_planning_doc_path(root, path, rel_path=rel_path, path_hint=path_hint)
            items.append(item)
            issues.extend(item_issues)

    issues.extend(find_active_scope_conflicts(items))
    return {
        "count": len(items),
        "items": items,
        "summary": summarize_issues(issues),
        "issues": issues,
    }


def inspect_planning_doc_path(root: Path, path: Path, *, rel_path: str, path_hint: str | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    frontmatter_text, _body = split_frontmatter(text)
    issues: list[dict[str, Any]] = []
    data: dict[str, Any] = {}

    if frontmatter_text:
        try:
            loaded = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError as exc:
            issues.append(issue("PLANNING_DOC_FRONTMATTER_INVALID", "risk", f"invalid planning doc frontmatter: {exc}", rel_path))
            loaded = {}
        if isinstance(loaded, dict):
            data = loaded
        else:
            issues.append(issue("PLANNING_DOC_FRONTMATTER_INVALID", "risk", "planning doc frontmatter must be a YAML mapping", rel_path))

    item = {
        "path": rel_path,
        "path_hint": path_hint,
        "frontmatter_present": bool(frontmatter_text),
        "title": _string(data.get("title")),
        "doc_type": _string(data.get("doc_type")) or path_hint,
        "status": _string(data.get("status")),
        "date": _string(data.get("date")),
        "scope": _string(data.get("scope")),
        "owner": _string(data.get("owner")),
        "source_refs": _string_list(data.get("source_refs")),
        "change_refs": _string_list(data.get("change_refs")),
        "anchors": _string_list(data.get("anchors")),
        "linked_change_paths": [],
        "issue_codes": [],
    }

    if not frontmatter_text:
        if path_hint is not None:
            issues.append(issue("PLANNING_DOC_FRONTMATTER_MISSING", "risk", "planning doc is missing YAML frontmatter", rel_path))
        item["issue_codes"] = [entry["code"] for entry in issues]
        return item, issues

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in data)
    if missing_fields:
        issues.append(issue(
            "PLANNING_DOC_FIELD_MISSING",
            "risk",
            f"planning doc frontmatter is missing required fields: {', '.join(missing_fields)}",
            rel_path,
        ))

    doc_type = _string(data.get("doc_type"))
    if doc_type and doc_type not in VALID_DOC_TYPES:
        issues.append(issue("PLANNING_DOC_TYPE_INVALID", "risk", f"invalid planning doc doc_type: {doc_type}", rel_path))
    status = _string(data.get("status"))
    if status and status not in VALID_STATUSES:
        issues.append(issue("PLANNING_DOC_STATUS_INVALID", "risk", f"invalid planning doc status: {status}", rel_path))

    source_refs = _string_list(data.get("source_refs"))
    if not source_refs:
        issues.append(issue("PLANNING_DOC_SOURCE_REFS_MISSING", "risk", "planning doc is missing source_refs", rel_path))

    change_refs = _string_list(data.get("change_refs"))
    if not change_refs:
        issues.append(issue("PLANNING_DOC_CHANGE_REFS_MISSING", "risk", "planning doc is missing change_refs", rel_path))

    linked_change_paths: list[str] = []
    invalid_change_refs: list[str] = []
    for candidate in change_refs:
        resolved = resolve_change_ref(root, candidate)
        if resolved is None:
            invalid_change_refs.append(candidate)
            continue
        linked_change_paths.append(resolved)
    item["linked_change_paths"] = linked_change_paths
    if invalid_change_refs:
        issues.append(issue(
            "PLANNING_DOC_CHANGE_REF_INVALID",
            "risk",
            f"planning doc has invalid change_refs: {', '.join(invalid_change_refs)}",
            rel_path,
        ))
    if status == "active" and not linked_change_paths:
        issues.append(issue(
            "PLANNING_DOC_STALE_ACTIVE",
            "risk",
            "active planning doc is not linked to any existing active or archived OpenSpec change",
            rel_path,
        ))

    item["issue_codes"] = [entry["code"] for entry in issues]
    return item, issues


def split_frontmatter(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "".join(lines[1:index]).strip(), "".join(lines[index + 1 :]).lstrip()
    return "", text


def find_active_scope_conflicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_groups: dict[tuple[str, str], list[str]] = {}
    for item in items:
        doc_type = _string(item.get("doc_type"))
        scope = _string(item.get("scope"))
        status = _string(item.get("status"))
        if doc_type not in VALID_DOC_TYPES or not scope or status != "active":
            continue
        active_groups.setdefault((doc_type, scope), []).append(str(item["path"]))

    issues: list[dict[str, Any]] = []
    for (doc_type, scope), paths in sorted(active_groups.items()):
        if len(paths) < 2:
            continue
        message = f"multiple active planning docs share scope '{scope}' for doc_type '{doc_type}'"
        for path in paths:
            issues.append(issue("PLANNING_DOC_ACTIVE_SCOPE_CONFLICT", "risk", message, path))
    return issues


def resolve_change_ref(root: Path, change_ref: str) -> str | None:
    path_text = change_ref.split("#", 1)[0].strip()
    if not path_text:
        return None

    path = Path(path_text)
    parts = path.parts
    if len(parts) < 3 or parts[0] != "openspec" or parts[1] != "changes":
        return None

    direct = root / path
    if parts[2] == "archive":
        if len(parts) < 4 or not direct.is_dir():
            return None
        return path.as_posix()

    if direct.is_dir():
        return path.as_posix()

    name = path.name
    archive_root = root / "openspec" / "changes" / "archive"
    if not archive_root.exists():
        return None

    for candidate in sorted(archive_root.rglob("*")):
        if candidate.is_dir() and candidate.name == name:
            return rel(root, candidate)
    return None


def _string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]
