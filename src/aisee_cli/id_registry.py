"""ID registry helpers for Aisee projects."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from aisee_cli.paths import id_registry_path
from aisee_cli.project import rel


REGISTRY_VERSION = 1
VALID_STATUSES = {"reserved", "active", "deprecated", "merged", "split", "removed"}
ID_PATTERN = re.compile(r"^(?P<scope>[A-Za-z][A-Za-z0-9_-]*):(?P<type>[A-Z]+)-(?P<number>\d+)$")
ID_REFERENCE_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-\d+\b")
SCAN_DIRS = (
    "aisee/docs",
    "docs",
    "openspec",
    "skills",
    "references",
)


def reserve_ids(project_root: Path, scope: str, id_type: str, count: int) -> dict[str, Any]:
    if count < 1:
        raise ValueError("--count must be greater than 0")
    validate_scope(scope)
    validate_type(id_type)

    root = project_root.resolve()
    registry = load_registry(root)
    scope_data = ensure_scope(registry, scope)
    counters = scope_data["counters"]
    ids = scope_data["ids"]
    next_number = int(counters.get(id_type, 0))
    now = timestamp()
    reserved: list[dict[str, Any]] = []

    for _ in range(count):
        next_number += 1
        full_id = format_id(scope, id_type, next_number)
        while full_id in ids:
            next_number += 1
            full_id = format_id(scope, id_type, next_number)
        ids[full_id] = {
            "type": id_type,
            "number": next_number,
            "status": "reserved",
            "title": "",
            "owner": "",
            "created_at": now,
            "updated_at": now,
        }
        reserved.append({
            "id": full_id,
            "short_id": short_id(id_type, next_number),
            "status": "reserved",
        })

    counters[id_type] = next_number
    save_registry(root, registry)
    return {
        "status": "ok",
        "registry": registry_path(root).relative_to(root).as_posix(),
        "reserved": reserved,
    }


def next_id(project_root: Path, scope: str, id_type: str) -> dict[str, Any]:
    validate_scope(scope)
    validate_type(id_type)

    root = project_root.resolve()
    path = registry_path(root)
    registry = load_registry(root)
    scope_data = registry.get("scopes", {}).get(scope, {})
    counters = scope_data.get("counters", {}) if isinstance(scope_data, dict) else {}
    ids = scope_data.get("ids", {}) if isinstance(scope_data, dict) else {}
    counter_value = counters.get(id_type, 0) if isinstance(counters, dict) else 0
    counter = counter_value if isinstance(counter_value, int) else 0
    allocated_numbers = [
        parsed["number"]
        for full_id in ids
        if isinstance(full_id, str)
        if (parsed := try_parse_id(full_id)) is not None and parsed["type"] == id_type
    ] if isinstance(ids, dict) else []
    number = max([counter, *allocated_numbers]) + 1
    full_id = format_id(scope, id_type, number)
    return {
        "status": "ok",
        "registry": {
            "available": path.exists(),
            "path": path.relative_to(root).as_posix(),
        },
        "next": {
            "id": full_id,
            "short_id": short_id(id_type, number),
            "scope": scope,
            "type": id_type,
            "number": number,
        },
        "writes": False,
    }


def activate_id(project_root: Path, full_id: str, owner: str, title: str) -> dict[str, Any]:
    parsed = parse_id(full_id)
    if not owner:
        raise ValueError("--owner is required")
    if not title:
        raise ValueError("--title is required")

    root = project_root.resolve()
    registry = load_registry(root)
    scope_data = ensure_scope(registry, parsed["scope"])
    entry = scope_data["ids"].get(full_id)
    if not isinstance(entry, dict):
        raise ValueError(f"ID is not reserved: {full_id}")
    if entry.get("status") not in {"reserved", "active"}:
        raise ValueError(f"ID cannot be activated from status {entry.get('status')}: {full_id}")

    now = timestamp()
    entry.update({
        "type": parsed["type"],
        "number": parsed["number"],
        "status": "active",
        "title": title,
        "owner": owner,
        "updated_at": now,
    })
    entry.setdefault("created_at", now)
    save_registry(root, registry)
    return {
        "status": "ok",
        "id": full_id,
        "entry": entry,
    }


def deprecate_id(project_root: Path, full_id: str, replaced_by: list[str], reason: str) -> dict[str, Any]:
    parsed = parse_id(full_id)
    if not reason:
        raise ValueError("--reason is required")
    for replacement in replaced_by:
        parse_id(replacement)

    root = project_root.resolve()
    registry = load_registry(root)
    for replacement in replaced_by:
        if lookup_entry(registry, replacement) is None:
            raise ValueError(f"replacement ID is not registered: {replacement}")
    scope_data = ensure_scope(registry, parsed["scope"])
    entry = scope_data["ids"].get(full_id)
    if not isinstance(entry, dict):
        raise ValueError(f"ID is not registered: {full_id}")
    if entry.get("status") in {"merged", "split", "removed"}:
        raise ValueError(f"ID cannot be deprecated from status {entry.get('status')}: {full_id}")

    now = timestamp()
    entry.update({
        "type": parsed["type"],
        "number": parsed["number"],
        "status": "deprecated",
        "reason": reason,
        "replaced_by": replaced_by,
        "updated_at": now,
    })
    entry.setdefault("created_at", now)
    save_registry(root, registry)
    return {
        "status": "ok",
        "id": full_id,
        "entry": entry,
    }


def check_registry(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    path = registry_path(root)
    if not path.exists():
        path_label = rel(root, path)
        return {
            "status": "ok",
            "registry": path_label,
            "available": False,
            "issues": [],
            "summary": {"blocker": 0, "risk": 0, "info": 0, "total": 0},
        }

    registry = load_registry(root)
    issues = validate_registry(root, registry)
    summary = summarize_issues(issues)
    status = "blocked" if summary["blocker"] else ("risk" if summary["risk"] else "ok")
    return {
        "status": status,
        "registry": path.relative_to(root).as_posix(),
        "version": registry.get("version"),
        "scopes": sorted(registry.get("scopes", {}).keys()),
        "issues": issues,
        "summary": summary,
    }


def trace_id(project_root: Path, full_id: str) -> dict[str, Any]:
    parsed = parse_id(full_id)
    root = project_root.resolve()
    path = registry_path(root)
    registry_available = path.exists()
    registry = load_registry(root) if registry_available else {"version": REGISTRY_VERSION, "scopes": {}}
    scope_data = registry.get("scopes", {}).get(parsed["scope"], {})
    ids = scope_data.get("ids", {}) if isinstance(scope_data, dict) else {}
    entry = ids.get(full_id) if isinstance(ids, dict) else None
    references = scan_id_occurrences(root, full_id)
    changes = sorted({
        parts[2]
        for reference in references
        if (parts := reference["path"].split("/"))[:2] == ["openspec", "changes"] and len(parts) >= 3
    })

    issues: list[dict[str, str]] = []
    registry_label = rel(root, path)
    if entry is None:
        severity = "risk" if references else "info"
        issues.append(issue("ID_NOT_REGISTERED", severity, f"{full_id} is not registered", registry_label))
    elif entry.get("status") != "active":
        issues.append(issue("ID_NOT_ACTIVE", "info", f"{full_id} status is {entry.get('status')}", registry_label))
    if entry is not None and entry.get("status") == "active" and not references:
        issues.append(issue("ID_NO_REFERENCES", "risk", f"{full_id} is active but has no scanned references", str(entry.get("owner") or "")))

    return {
        "status": trace_status(entry, references),
        "id": full_id,
        "scope": parsed["scope"],
        "type": parsed["type"],
        "number": parsed["number"],
        "registry": {
            "available": registry_available,
            "path": path.relative_to(root).as_posix(),
            "entry": entry,
        },
        "references": references,
        "relations": {
            "changes": changes,
        },
        "issues": issues,
        "summary": {
            "reference_count": len(references),
            "change_count": len(changes),
            "issue_count": len(issues),
        },
    }


def load_registry(project_root: Path) -> dict[str, Any]:
    path = registry_path(project_root)
    if not path.exists():
        return {"version": REGISTRY_VERSION, "scopes": {}}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ValueError(f"{rel(project_root, path)} must be a JSON object")
    return normalize_registry(raw)


def save_registry(project_root: Path, registry: dict[str, Any]) -> None:
    path = registry_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_registry(registry)
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_registry(root: Path, registry: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    registry_label = rel(root, registry_path(root))
    registered_ids: set[str] = set()
    scopes = registry.get("scopes", {})
    if not isinstance(scopes, dict):
        return [issue("REGISTRY_SCHEMA_INVALID", "blocker", "scopes must be an object", registry_label)]

    for scope, scope_data in scopes.items():
        if not isinstance(scope_data, dict):
            issues.append(issue("REGISTRY_SCOPE_INVALID", "blocker", f"scope {scope} must be an object", registry_label))
            continue
        counters = scope_data.get("counters", {})
        ids = scope_data.get("ids", {})
        if not isinstance(counters, dict) or not isinstance(ids, dict):
            issues.append(issue("REGISTRY_SCOPE_INVALID", "blocker", f"scope {scope} must contain counters and ids objects", registry_label))
            continue

        max_numbers: dict[str, int] = {}
        for full_id, entry in ids.items():
            registered_ids.add(full_id)
            parsed = try_parse_id(full_id)
            if parsed is None:
                issues.append(issue("ID_FORMAT_INVALID", "blocker", f"invalid ID format: {full_id}", registry_label))
                continue
            if parsed["scope"] != scope:
                issues.append(issue("ID_SCOPE_MISMATCH", "blocker", f"{full_id} is stored under scope {scope}", registry_label))
            if not isinstance(entry, dict):
                issues.append(issue("ID_ENTRY_INVALID", "blocker", f"{full_id} entry must be an object", registry_label))
                continue
            if entry.get("type") != parsed["type"] or entry.get("number") != parsed["number"]:
                issues.append(issue("ID_ENTRY_MISMATCH", "blocker", f"{full_id} entry type or number does not match the ID", registry_label))
            if entry.get("status") not in VALID_STATUSES:
                issues.append(issue("ID_STATUS_INVALID", "blocker", f"{full_id} has invalid status: {entry.get('status')}", registry_label))
            if entry.get("status") == "active":
                owner = str(entry.get("owner") or "")
                if not owner:
                    issues.append(issue("ID_OWNER_MISSING", "risk", f"{full_id} is active without owner", registry_label))
                elif not (root / owner).exists():
                    issues.append(issue("ID_OWNER_NOT_FOUND", "risk", f"{full_id} owner does not exist: {owner}", owner))
            if entry.get("status") in {"deprecated", "merged", "split"}:
                for replacement in entry.get("replaced_by", []):
                    if try_parse_id(str(replacement)) is None:
                        issues.append(issue("ID_REPLACEMENT_INVALID", "blocker", f"{full_id} has invalid replacement ID: {replacement}", registry_label))
            max_numbers[parsed["type"]] = max(max_numbers.get(parsed["type"], 0), parsed["number"])

        for id_type, max_number in max_numbers.items():
            counter = counters.get(id_type)
            if not isinstance(counter, int) or counter < max_number:
                issues.append(issue("ID_COUNTER_BEHIND", "blocker", f"{scope}:{id_type} counter is behind allocated IDs", registry_label))

    inactive_statuses = {"deprecated", "merged", "split", "removed"}
    for full_id, owner_path in scan_id_references(root):
        if full_id not in registered_ids:
            issues.append(issue("ID_UNREGISTERED_REFERENCE", "risk", f"unregistered ID reference: {full_id}", owner_path))
            continue
        entry = lookup_entry(registry, full_id)
        status = entry.get("status") if isinstance(entry, dict) else None
        if status in inactive_statuses:
            severity = "blocker" if status == "removed" else "risk"
            issues.append(issue("ID_INACTIVE_REFERENCE", severity, f"{full_id} is {status} but still referenced", owner_path))

    return issues


def scan_id_references(root: Path) -> list[tuple[str, str]]:
    references: list[tuple[str, str]] = []
    for dirname in SCAN_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel_path = path.relative_to(root).as_posix()
            for match in ID_REFERENCE_PATTERN.finditer(text):
                references.append((match.group(0), rel_path))
    return references


def scan_id_occurrences(root: Path, full_id: str) -> list[dict[str, Any]]:
    occurrences: list[dict[str, Any]] = []
    for dirname in SCAN_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if full_id not in text:
                continue
            rel_path = path.relative_to(root).as_posix()
            for line_number, line in enumerate(text.splitlines(), start=1):
                if full_id in line:
                    occurrences.append({
                        "path": rel_path,
                        "line": line_number,
                        "text": line.strip(),
                    })
    return occurrences


def ensure_scope(registry: dict[str, Any], scope: str) -> dict[str, Any]:
    scopes = registry.setdefault("scopes", {})
    scope_data = scopes.setdefault(scope, {"counters": {}, "ids": {}})
    scope_data.setdefault("counters", {})
    scope_data.setdefault("ids", {})
    return scope_data


def normalize_registry(registry: dict[str, Any]) -> dict[str, Any]:
    registry.setdefault("version", REGISTRY_VERSION)
    registry.setdefault("scopes", {})
    return registry


def lookup_entry(registry: dict[str, Any], full_id: str) -> dict[str, Any] | None:
    parsed = try_parse_id(full_id)
    if parsed is None:
        return None
    scope_data = registry.get("scopes", {}).get(parsed["scope"], {})
    ids = scope_data.get("ids", {}) if isinstance(scope_data, dict) else {}
    entry = ids.get(full_id) if isinstance(ids, dict) else None
    return entry if isinstance(entry, dict) else None


def parse_id(full_id: str) -> dict[str, Any]:
    parsed = try_parse_id(full_id)
    if parsed is None:
        raise ValueError(f"invalid ID format: {full_id}")
    return parsed


def try_parse_id(full_id: str) -> dict[str, Any] | None:
    match = ID_PATTERN.match(full_id)
    if not match:
        return None
    return {
        "scope": match.group("scope"),
        "type": match.group("type"),
        "number": int(match.group("number")),
    }


def validate_scope(scope: str) -> None:
    if not re.match(r"^[A-Za-z][A-Za-z0-9_-]*$", scope):
        raise ValueError(f"invalid scope: {scope}")


def validate_type(id_type: str) -> None:
    if not re.match(r"^[A-Z]+$", id_type):
        raise ValueError(f"invalid ID type: {id_type}")


def format_id(scope: str, id_type: str, number: int) -> str:
    return f"{scope}:{short_id(id_type, number)}"


def short_id(id_type: str, number: int) -> str:
    return f"{id_type}-{number:03d}"


def registry_path(project_root: Path) -> Path:
    return id_registry_path(project_root)


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def issue(code: str, severity: str, message: str, path: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "path": path,
    }


def summarize_issues(issues: list[dict[str, Any]]) -> dict[str, int]:
    blocker = sum(1 for item in issues if item.get("severity") == "blocker")
    risk = sum(1 for item in issues if item.get("severity") == "risk")
    info = sum(1 for item in issues if item.get("severity") == "info")
    return {
        "blocker": blocker,
        "risk": risk,
        "info": info,
        "total": len(issues),
    }


def trace_status(entry: Any, references: list[dict[str, Any]]) -> str:
    if entry is None:
        return "unregistered" if references else "missing"
    if entry.get("status") == "active" and references:
        return "linked"
    return str(entry.get("status") or "registered")
