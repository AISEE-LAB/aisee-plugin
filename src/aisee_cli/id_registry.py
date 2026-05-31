"""ID registry helpers for Aisee projects."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


REGISTRY_VERSION = 1
VALID_STATUSES = {"reserved", "active", "deprecated", "merged", "split", "removed"}
ID_PATTERN = re.compile(r"^(?P<scope>[A-Za-z][A-Za-z0-9_-]*):(?P<type>[A-Z]+)-(?P<number>\d+)$")
ID_REFERENCE_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-\d+\b")
SCAN_DIRS = (
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


def check_registry(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    path = registry_path(root)
    if not path.exists():
        return {
            "status": "missing",
            "registry": path.relative_to(root).as_posix(),
            "issues": [
                issue("REGISTRY_MISSING", "blocker", ".aisee/id-registry.json is missing", ".aisee/id-registry.json"),
            ],
            "summary": {"blocker": 1, "risk": 0, "info": 0, "total": 1},
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


def load_registry(project_root: Path) -> dict[str, Any]:
    path = registry_path(project_root)
    if not path.exists():
        return {"version": REGISTRY_VERSION, "scopes": {}}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ValueError(".aisee/id-registry.json must be a JSON object")
    return normalize_registry(raw)


def save_registry(project_root: Path, registry: dict[str, Any]) -> None:
    path = registry_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_registry(registry)
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_registry(root: Path, registry: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    registered_ids: set[str] = set()
    scopes = registry.get("scopes", {})
    if not isinstance(scopes, dict):
        return [issue("REGISTRY_SCHEMA_INVALID", "blocker", "scopes must be an object", ".aisee/id-registry.json")]

    for scope, scope_data in scopes.items():
        if not isinstance(scope_data, dict):
            issues.append(issue("REGISTRY_SCOPE_INVALID", "blocker", f"scope {scope} must be an object", ".aisee/id-registry.json"))
            continue
        counters = scope_data.get("counters", {})
        ids = scope_data.get("ids", {})
        if not isinstance(counters, dict) or not isinstance(ids, dict):
            issues.append(issue("REGISTRY_SCOPE_INVALID", "blocker", f"scope {scope} must contain counters and ids objects", ".aisee/id-registry.json"))
            continue

        max_numbers: dict[str, int] = {}
        for full_id, entry in ids.items():
            registered_ids.add(full_id)
            parsed = try_parse_id(full_id)
            if parsed is None:
                issues.append(issue("ID_FORMAT_INVALID", "blocker", f"invalid ID format: {full_id}", ".aisee/id-registry.json"))
                continue
            if parsed["scope"] != scope:
                issues.append(issue("ID_SCOPE_MISMATCH", "blocker", f"{full_id} is stored under scope {scope}", ".aisee/id-registry.json"))
            if not isinstance(entry, dict):
                issues.append(issue("ID_ENTRY_INVALID", "blocker", f"{full_id} entry must be an object", ".aisee/id-registry.json"))
                continue
            if entry.get("type") != parsed["type"] or entry.get("number") != parsed["number"]:
                issues.append(issue("ID_ENTRY_MISMATCH", "blocker", f"{full_id} entry type or number does not match the ID", ".aisee/id-registry.json"))
            if entry.get("status") not in VALID_STATUSES:
                issues.append(issue("ID_STATUS_INVALID", "blocker", f"{full_id} has invalid status: {entry.get('status')}", ".aisee/id-registry.json"))
            if entry.get("status") == "active":
                owner = str(entry.get("owner") or "")
                if not owner:
                    issues.append(issue("ID_OWNER_MISSING", "risk", f"{full_id} is active without owner", ".aisee/id-registry.json"))
                elif not (root / owner).exists():
                    issues.append(issue("ID_OWNER_NOT_FOUND", "risk", f"{full_id} owner does not exist: {owner}", owner))
            max_numbers[parsed["type"]] = max(max_numbers.get(parsed["type"], 0), parsed["number"])

        for id_type, max_number in max_numbers.items():
            counter = counters.get(id_type)
            if not isinstance(counter, int) or counter < max_number:
                issues.append(issue("ID_COUNTER_BEHIND", "blocker", f"{scope}:{id_type} counter is behind allocated IDs", ".aisee/id-registry.json"))

    for full_id, owner_path in scan_id_references(root):
        if full_id not in registered_ids:
            issues.append(issue("ID_UNREGISTERED_REFERENCE", "risk", f"unregistered ID reference: {full_id}", owner_path))

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
    return project_root / ".aisee" / "id-registry.json"


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
