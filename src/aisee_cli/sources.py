"""Aisee sources registry helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.paths import sources_path
from aisee_cli.project import rel


REGISTRY_VERSION = 1
VALID_TYPES = {
    "srs",
    "ui-content",
    "architecture",
    "design-assets",
    "svg-assets",
    "device-context",
    "service-context",
    "data-context",
    "verification",
}


def list_sources(root: Path) -> dict[str, Any]:
    path = sources_path(root)
    data, issues = load_sources(root)
    sources = data.get("sources", []) if isinstance(data, dict) else []
    result_issues = issues + validate_sources(root, sources)
    return {
        "status": "missing" if not path.exists() else status_from_issues(result_issues),
        "path": rel(root, path),
        "version": data.get("version") if isinstance(data, dict) else None,
        "sources": sources,
        "issues": result_issues,
        "summary": summarize_issues(result_issues),
    }


def check_sources(root: Path) -> dict[str, Any]:
    result = list_sources(root)
    if result["status"] == "missing":
        path_label = result["path"]
        result["issues"] = [
            issue("SOURCES_MISSING", "risk", f"{path_label} is missing", path_label),
        ]
        result["summary"] = summarize_issues(result["issues"])
        result["status"] = status_from_issues(result["issues"])
    return result


def add_source(root: Path, scope: str, source_type: str, path: str, template: str | None, parser: str | None) -> dict[str, Any]:
    if not scope:
        raise ValueError("--scope is required")
    if source_type not in VALID_TYPES:
        raise ValueError(f"unsupported source type: {source_type}")
    if not path:
        raise ValueError("--path is required")

    data, issues = load_sources(root)
    if issues and any(item.get("severity") == "blocker" for item in issues):
        raise ValueError(issues[0]["message"])

    sources = data.setdefault("sources", [])
    if not isinstance(sources, list):
        raise ValueError("sources must be a list")

    entry = {
        "scope": scope,
        "type": source_type,
        "path": path,
        "template": template or source_type,
        "parser": parser or source_type,
    }
    for current in sources:
        if not isinstance(current, dict):
            continue
        if current.get("scope") == scope and current.get("type") == source_type and current.get("path") == path:
            return {
                "status": "ok",
                "path": rel(root, sources_path(root)),
                "source": current,
                "changed": False,
                "issues": validate_sources(root, sources),
            }

    sources.append(entry)
    save_sources(root, data)
    issues = validate_sources(root, sources)
    return {
        "status": status_from_issues(issues),
        "path": rel(root, sources_path(root)),
        "source": entry,
        "changed": True,
        "issues": issues,
        "summary": summarize_issues(issues),
    }


def remove_source(root: Path, scope: str, source_type: str, path: str) -> dict[str, Any]:
    data, issues = load_sources(root)
    if issues and any(item.get("severity") == "blocker" for item in issues):
        raise ValueError(issues[0]["message"])
    sources = data.setdefault("sources", [])
    if not isinstance(sources, list):
        raise ValueError("sources must be a list")

    kept = [
        item for item in sources
        if not (
            isinstance(item, dict)
            and item.get("scope") == scope
            and item.get("type") == source_type
            and item.get("path") == path
        )
    ]
    changed = len(kept) != len(sources)
    data["sources"] = kept
    if changed:
        save_sources(root, data)
    result_issues = validate_sources(root, kept)
    return {
        "status": status_from_issues(result_issues),
        "path": rel(root, sources_path(root)),
        "changed": changed,
        "sources": kept,
        "issues": result_issues,
        "summary": summarize_issues(result_issues),
    }


def load_sources(root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    path = sources_path(root)
    if not path.exists():
        return {"version": REGISTRY_VERSION, "sources": []}, []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        path_label = rel(root, path)
        return {"version": REGISTRY_VERSION, "sources": []}, [
            issue("SOURCES_INVALID_JSON", "blocker", f"invalid JSON in {path_label}: {error}", path_label)
        ]
    if not isinstance(raw, dict):
        path_label = rel(root, path)
        return {"version": REGISTRY_VERSION, "sources": []}, [
            issue("SOURCES_SCHEMA_INVALID", "blocker", f"{path_label} must be a JSON object", path_label)
        ]
    return normalize_sources(raw), []


def normalize_sources(data: dict[str, Any]) -> dict[str, Any]:
    data.setdefault("version", REGISTRY_VERSION)
    sources = data.get("sources")
    if isinstance(sources, list):
        return data
    normalized: list[dict[str, Any]] = []
    for category, value in data.items():
        if category in {"version", "sources"}:
            continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    normalized.append({"category": category, **item})
    data["sources"] = normalized
    return data


def validate_sources(root: Path, sources: Any) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    sources_label = rel(root, sources_path(root))
    if not isinstance(sources, list):
        return [issue("SOURCES_SCHEMA_INVALID", "blocker", "sources must be a list", sources_label)]

    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(sources):
        owner = f"{sources_label}#{index}"
        if not isinstance(item, dict):
            issues.append(issue("SOURCE_ENTRY_INVALID", "blocker", "source entry must be an object", owner))
            continue
        scope = str(item.get("scope") or "")
        source_type = str(item.get("type") or "")
        path = str(item.get("path") or "")
        if not scope:
            issues.append(issue("SOURCE_SCOPE_MISSING", "blocker", "source scope is missing", owner))
        if not source_type:
            issues.append(issue("SOURCE_TYPE_MISSING", "blocker", "source type is missing", owner))
        elif source_type not in VALID_TYPES:
            issues.append(issue("SOURCE_TYPE_UNSUPPORTED", "risk", f"unsupported source type: {source_type}", owner))
        if not path:
            issues.append(issue("SOURCE_PATH_MISSING", "blocker", "source path is missing", owner))
        elif not (root / path).exists():
            issues.append(issue("SOURCE_PATH_NOT_FOUND", "risk", f"source path does not exist: {path}", path))
        key = (scope, source_type, path)
        if key in seen:
            issues.append(issue("SOURCE_DUPLICATE", "risk", f"duplicate source: {scope}/{source_type}/{path}", owner))
        seen.add(key)
    return issues


def save_sources(root: Path, data: dict[str, Any]) -> None:
    path = sources_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalize_sources(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
