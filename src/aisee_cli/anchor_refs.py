"""Anchor reference parsing helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


LOCAL_ID_RE = r"[A-Z]+-(?:NEW-)?\d+"
LOCAL_ID_PATTERN = re.compile(rf"(?<![A-Za-z0-9_:-])(?P<local_id>{LOCAL_ID_RE})\b")
LEGACY_FULL_ID_PATTERN = re.compile(rf"\b[A-Za-z][A-Za-z0-9_-]*:(?P<local_id>{LOCAL_ID_RE})\b")
PATH_ANCHOR_PATTERN = re.compile(
    rf"(?P<document>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+)#(?P<local_id>{LOCAL_ID_RE})"
)
ALIAS_ANCHOR_PATTERN = re.compile(
    rf"(?P<alias>[A-Za-z][A-Za-z0-9_-]*:[A-Za-z0-9][A-Za-z0-9_-]*)#(?P<local_id>{LOCAL_ID_RE})"
)
ANCHOR_REF_PATTERN = re.compile(
    rf"(?P<ref>(?:(?:[A-Za-z][A-Za-z0-9_-]*:[A-Za-z0-9][A-Za-z0-9_-]*)|(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+)#(?:{LOCAL_ID_RE}))"
)


def is_local_id(value: str) -> bool:
    return bool(re.fullmatch(LOCAL_ID_RE, value.strip()))


def extract_local_ids(text: str) -> set[str]:
    return {match.group("local_id") for match in LOCAL_ID_PATTERN.finditer(text)}


def extract_legacy_full_ids(text: str) -> set[str]:
    return {match.group(0) for match in LEGACY_FULL_ID_PATTERN.finditer(text)}


def extract_anchor_refs(text: str) -> set[str]:
    return {match.group("ref") for match in ANCHOR_REF_PATTERN.finditer(text)}


def parse_anchor_ref(reference: str) -> dict[str, Any]:
    value = reference.strip()
    path_match = PATH_ANCHOR_PATTERN.fullmatch(value)
    if path_match:
        document = path_match.group("document")
        local_id = path_match.group("local_id")
        return {
            "reference": value,
            "reference_type": "path-anchor",
            "document": document,
            "alias": None,
            "local_id": local_id,
            "canonical_reference": canonical_anchor(document, local_id),
        }

    alias_match = ALIAS_ANCHOR_PATTERN.fullmatch(value)
    if alias_match:
        alias = alias_match.group("alias")
        local_id = alias_match.group("local_id")
        return {
            "reference": value,
            "reference_type": "alias-anchor",
            "document": None,
            "alias": alias,
            "local_id": local_id,
            "canonical_reference": None,
        }

    raise ValueError(f"invalid anchor ref: {reference}")


def canonical_anchor(document: str, local_id: str) -> str:
    return f"{document}#{local_id}"


def source_aliases(source_entries: Any, path: str) -> list[str]:
    aliases: list[str] = []
    if not isinstance(source_entries, list):
        return aliases
    for entry in source_entries:
        if not isinstance(entry, dict) or str(entry.get("path") or "") != path:
            continue
        alias = str(entry.get("alias") or "").strip()
        source_type = str(entry.get("type") or "").strip()
        if alias:
            aliases.append(alias)
        elif source_type:
            aliases.append(f"{source_type}:{slugify(Path(path).stem)}")
    return sorted(set(aliases))


def resolve_alias_path(source_entries: Any, alias: str) -> str | None:
    if not isinstance(source_entries, list):
        return None
    for entry in source_entries:
        if not isinstance(entry, dict):
            continue
        current_aliases = source_aliases([entry], str(entry.get("path") or ""))
        if alias in current_aliases:
            return str(entry.get("path") or "") or None
    return None


def slugify(value: str) -> str:
    lowered = value.strip().lower().replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]+", "-", lowered).strip("-")
    return slug or "document"
