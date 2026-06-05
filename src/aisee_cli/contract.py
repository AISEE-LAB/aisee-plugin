"""Read-only contract context access for OpenSpec/Aisee changes."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aisee_cli.context_pack import build_context_pack


DEFAULT_MAX_CHARS = 4000
SUMMARY_MAX_CHARS = 800
CONTRACT_ARTIFACT_IDS = {"service-contract", "ui-contract", "data-model", "change-context"}
SECTION_PATTERN = re.compile(r"^(?P<level>#{2,6})\s+(?P<title>.+?)\s*$")
CHANGE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class TextLimit:
    content: str
    truncated: bool
    original_chars: int
    max_chars: int


def build_contract_manifest(project_root: Path, max_chars: int = SUMMARY_MAX_CHARS) -> dict[str, Any]:
    root = project_root.resolve()
    changes = []
    for change_path in discover_changes(root):
        change = change_path.name
        try:
            pack = build_context_pack(root, change, "aisee-verify")
        except ValueError:
            continue
        contracts = contract_entries_from_pack(root, change_path, pack, include_sections=False, max_chars=max_chars)
        if not contracts:
            continue
        changes.append(
            {
                "id": change,
                "path": rel(root, change_path),
                "schema": pack["change"]["schema"],
                "status": pack["change"]["status"],
                "contract_sync": pack["facts"]["parsed"]["source_map"].get("contract_sync", {}),
                "contracts": contracts,
            }
        )
    return {
        "schema_version": "1.0",
        "status": "ok",
        "project": {"path": rel(root, root)},
        "changes": changes,
        "meta": {
            "command": "aisee contract manifest --json",
            "generated_at": now_iso(),
            "mode": "manifest-first",
        },
    }


def build_contract_summary(project_root: Path, change: str, max_chars: int = SUMMARY_MAX_CHARS) -> dict[str, Any]:
    root = project_root.resolve()
    change_path = resolve_change_path(root, change)
    pack = build_context_pack(root, change, "aisee-verify")
    contracts = contract_entries_from_pack(root, change_path, pack, include_sections=True, max_chars=max_chars)
    return {
        "schema_version": "1.0",
        "status": "ok",
        "change": pack["change"],
        "contract_sync": pack["facts"]["parsed"]["source_map"].get("contract_sync", {}),
        "contracts": contracts,
        "meta": {
            "command": f"aisee contract summary --change {change} --json",
            "generated_at": now_iso(),
        },
    }


def build_contract_get(
    project_root: Path,
    change: str,
    artifact: str,
    *,
    section: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    raw: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    change_path = resolve_change_path(root, change)
    pack = build_context_pack(root, change, "aisee-verify")
    artifact_entry = find_contract_artifact(pack, artifact)
    if artifact_entry is None:
        raise ValueError(f"contract artifact not found: {artifact}")
    path_value = str(artifact_entry.get("path") or artifact_entry.get("generates") or "")
    if not path_value or "," in path_value:
        raise ValueError(f"contract artifact has no single readable path: {artifact}")
    path = resolve_contract_artifact_path(change_path, path_value)
    text = read_text(path)
    if text == "":
        raise ValueError(f"contract artifact is empty or missing: {path_value}")

    sections = parse_markdown_sections(text)
    selected_title = None
    content = text
    if section:
        selected = find_section(sections, section)
        if selected is None:
            raise ValueError(f"contract section not found: {section}")
        selected_title = selected["title"]
        content = selected["content"]
    elif not raw:
        limit = limit_text(summarize_text(text), max_chars)
        return {
            "schema_version": "1.0",
            "status": "ok",
            "change": pack["change"],
            "artifact": contract_artifact_identity(root, change_path, artifact_entry),
            "section": None,
            "content": limit.content,
            "truncated": limit.truncated,
            "original_chars": limit.original_chars,
            "max_chars": limit.max_chars,
            "sections": section_index(sections),
            "source_files": [rel(root, path)],
            "etag": etag_for_paths([path]),
            "meta": {
                "command": f"aisee contract get --change {change} --artifact {artifact} --json",
                "generated_at": now_iso(),
                "raw": False,
            },
        }

    limit = limit_text(content, max_chars)
    return {
        "schema_version": "1.0",
        "status": "ok",
        "change": pack["change"],
        "artifact": contract_artifact_identity(root, change_path, artifact_entry),
        "section": {"id": slugify(selected_title or "raw"), "title": selected_title} if section else None,
        "content": limit.content,
        "truncated": limit.truncated,
        "original_chars": limit.original_chars,
        "max_chars": limit.max_chars,
        "sections": section_index(sections),
        "source_files": [rel(root, path)],
        "etag": etag_for_paths([path]),
        "meta": {
            "command": f"aisee contract get --change {change} --artifact {artifact} --json",
            "generated_at": now_iso(),
            "raw": raw,
        },
    }


def discover_changes(root: Path) -> list[Path]:
    changes_dir = root / "openspec" / "changes"
    if not changes_dir.exists():
        return []
    return sorted(path for path in changes_dir.iterdir() if path.is_dir())


def contract_entries_from_pack(
    root: Path,
    change_path: Path,
    pack: dict[str, Any],
    *,
    include_sections: bool,
    max_chars: int,
) -> list[dict[str, Any]]:
    entries = []
    for artifact in pack["facts"]["parsed"]["schema"].get("artifacts", []):
        if not is_contract_artifact(artifact):
            continue
        applicability = artifact_applicability_for(artifact, pack)
        identity = contract_artifact_identity(root, change_path, artifact)
        path_value = str(artifact.get("path") or "")
        path: Path | None = None
        path_error: str | None = None
        if path_value and "," not in path_value:
            try:
                path = resolve_contract_artifact_path(change_path, path_value)
            except ValueError as error:
                path_error = str(error)
        text = read_text(path) if path else ""
        sections = parse_markdown_sections(text)
        summary = limit_text(summarize_text(text), max_chars)
        entry: dict[str, Any] = {
            **identity,
            "status": contract_entry_status(artifact, applicability, path_error),
            "required": applicability["required"],
            "reason": applicability["reason"],
            "summary": summary.content,
            "truncated": summary.truncated,
            "original_chars": summary.original_chars,
            "etag": etag_for_paths([path]) if path else None,
        }
        if path_error:
            entry["issue"] = path_error
        if include_sections:
            entry["sections"] = section_index(sections)
        entries.append(entry)
    return entries


def find_contract_artifact(pack: dict[str, Any], artifact_name: str) -> dict[str, Any] | None:
    normalized = normalize_artifact_name(artifact_name)
    for artifact in pack["facts"]["parsed"]["schema"].get("artifacts", []):
        if not is_contract_artifact(artifact):
            continue
        candidates = {
            normalize_artifact_name(str(artifact.get("id") or "")),
            normalize_artifact_name(str(artifact.get("generates") or "")),
            normalize_artifact_name(str(artifact.get("path") or "")),
        }
        if normalized in candidates:
            return artifact
    return None


def is_contract_artifact(artifact: dict[str, Any]) -> bool:
    artifact_id = str(artifact.get("id") or "")
    generates = str(artifact.get("generates") or "")
    return artifact_id in CONTRACT_ARTIFACT_IDS or "contract" in artifact_id or "contract" in generates


def contract_artifact_identity(root: Path, change_path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    path_value = artifact.get("path")
    path_label = path_value
    if path_value and "," not in str(path_value):
        try:
            path_label = rel(root, resolve_contract_artifact_path(change_path, str(path_value)))
        except ValueError:
            path_label = str(path_value)
    return {
        "id": artifact.get("id"),
        "generates": artifact.get("generates"),
        "path": path_label,
    }


def parse_markdown_sections(text: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = SECTION_PATTERN.match(line)
        if not match:
            continue
        headings.append(
            {
                "line": index,
                "id": slugify(match.group("title").strip()),
                "title": match.group("title").strip(),
                "level": len(match.group("level")),
            }
        )

    sections: list[dict[str, Any]] = []
    for position, heading in enumerate(headings):
        end = len(lines)
        for following in headings[position + 1:]:
            if following["level"] <= heading["level"]:
                end = following["line"]
                break
        content = "\n".join(lines[heading["line"]:end]).strip()
        sections.append({**heading, "content": content})
    return sections


def section_index(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": section["id"],
            "title": section["title"],
            "level": section["level"],
            "chars": len(section["content"]),
        }
        for section in sections
    ]


def find_section(sections: list[dict[str, Any]], section: str) -> dict[str, Any] | None:
    normalized = slugify(section)
    for item in sections:
        if normalized in {item["id"], slugify(item["title"])}:
            return item
    return None


def summarize_text(text: str) -> str:
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped)
        if len("\n".join(headings)) >= SUMMARY_MAX_CHARS:
            break
    return "\n".join(headings)


def limit_text(text: str, max_chars: int) -> TextLimit:
    normalized_max = max(1, max_chars)
    original = len(text)
    if original <= normalized_max:
        return TextLimit(text, False, original, normalized_max)
    return TextLimit(text[:normalized_max], True, original, normalized_max)


def etag_for_paths(paths: list[Path | None]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        if path is None or not path.exists():
            continue
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def normalize_artifact_name(value: str) -> str:
    path = value.strip()
    if path.endswith(".md"):
        path = path[:-3]
    return path.replace("_", "-")


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^\w\u4e00-\u9fff]+", "-", lowered)
    return lowered.strip("-")


def resolve_change_path(root: Path, change: str) -> Path:
    validate_change_name(change)
    change_path = root / "openspec" / "changes" / change
    require_change(change_path, change)
    return change_path


def validate_change_name(change: str) -> None:
    if not CHANGE_NAME_PATTERN.fullmatch(change):
        raise ValueError(f"unsafe change name: {change}")


def require_change(change_path: Path, change: str) -> None:
    if not change_path.exists():
        raise ValueError(f"change not found: {change}")


def resolve_contract_artifact_path(change_path: Path, path_value: str) -> Path:
    relative = Path(path_value)
    if relative.is_absolute():
        raise ValueError(f"contract artifact path must be relative to the change directory: {path_value}")
    resolved_change = change_path.resolve()
    resolved = (change_path / relative).resolve()
    try:
        resolved.relative_to(resolved_change)
    except ValueError as error:
        raise ValueError(f"contract artifact path escapes the change directory: {path_value}") from error
    return resolved


def artifact_applicability_for(artifact: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    artifact_id = str(artifact.get("id") or "")
    generates = str(artifact.get("generates") or "")
    for row in pack["facts"]["parsed"]["source_map"].get("artifact_applicability", []):
        if not isinstance(row, dict):
            continue
        row_artifact = str(row.get("artifact") or "")
        if row_artifact not in {artifact_id, generates}:
            continue
        required = row.get("required") != "no"
        return {
            "required": required,
            "reason": str(row.get("reason") or ""),
        }
    return {"required": True, "reason": ""}


def contract_entry_status(artifact: dict[str, Any], applicability: dict[str, Any], path_error: str | None) -> str:
    if path_error:
        return "invalid_path"
    if not applicability["required"]:
        return "not_required"
    return str(artifact.get("status") or "unknown")


def read_text(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
