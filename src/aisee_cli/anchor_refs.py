"""Anchor reference parsing helpers."""

from __future__ import annotations

import re
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

