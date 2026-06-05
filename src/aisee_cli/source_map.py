"""Source-map parser for Aisee companion routing data."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-(?:NEW-)?\d+\b")
PATH_PATTERN = re.compile(
    r"(?<![\w./-])"
    r"((?:src|app|apps|lib|libs|packages|tests|test|docs|openspec|assets|config|contracts)"
    r"/[A-Za-z0-9_./@:+-]+)"
)
IMPLEMENTATION_PATH_SECTION_TOKENS = (
    "Affected Paths Index",
    "影响路径索引",
    "候选影响路径",
    "Implementation Paths",
    "实现路径",
    "代码路径",
)
EVIDENCE_SECTION_TOKENS = (
    "Expected Evidence Index",
    "预期证据索引",
    "Verification Evidence",
    "验证证据",
)


def parse_source_map(change_path: Path) -> dict[str, Any]:
    path = change_path / "source-map.md"
    text = read_text(path)
    sections = parse_sections(text)
    tables = parse_tables(sections)
    implementation_paths = extract_implementation_paths(tables, text)
    evidence = extract_evidence(tables)
    artifact_applicability = extract_artifact_applicability(tables)
    contract_sync = extract_contract_sync(tables)
    id_trace = extract_id_trace(tables)
    upstream_sources = extract_upstream_sources(tables)
    out_of_scope = extract_bullets(sections, {"不在本 Change 范围", "不在范围", "Out of Scope", "Follow-up", "后续处理"})
    issues = build_issues(path.exists(), tables, implementation_paths, artifact_applicability)
    return {
        "path": "source-map.md",
        "status": "present" if path.exists() else "missing",
        "parse_level": "structured" if tables else ("metadata" if text else "missing"),
        "upstream_sources": upstream_sources,
        "id_trace": id_trace,
        "artifact_applicability": artifact_applicability,
        "contract_sync": contract_sync,
        "implementation_paths": implementation_paths,
        "verification_evidence": evidence,
        "out_of_scope": out_of_scope,
        "ids": sorted(set(ID_PATTERN.findall(text))),
        "paths": sorted(set(PATH_PATTERN.findall(text))),
        "issues": issues,
    }


def parse_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"": []}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def parse_tables(sections: dict[str, list[str]]) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    for title, lines in sections.items():
        rows = table_rows(lines)
        if rows:
            tables[title] = rows
    return tables


def table_rows(lines: list[str]) -> list[dict[str, str]]:
    table_lines = [line.strip() for line in lines if line.strip().startswith("|") and line.strip().endswith("|")]
    if len(table_lines) < 2:
        return []
    header = split_table_line(table_lines[0])
    separator = split_table_line(table_lines[1])
    if not header or not all(set(cell) <= {"-", ":"} for cell in separator if cell):
        return []
    rows = []
    for line in table_lines[2:]:
        cells = split_table_line(line)
        if not cells:
            continue
        row = {normalize_key(header[index]): cells[index].strip() if index < len(cells) else "" for index in range(len(header))}
        rows.append(row)
    return rows


def split_table_line(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_key(key: str) -> str:
    lowered = key.strip().lower()
    mapping = {
        "来源": "source",
        "source": "source",
        "路径 / 描述": "path",
        "path / description": "path",
        "path / command": "path",
        "sources.json id": "source_id",
        "source id": "source_id",
        "状态": "status",
        "status": "status",
        "备注": "notes",
        "notes": "notes",
        "类型": "type",
        "type": "type",
        "完整 id": "id",
        "id": "id",
        "标题 / 名称": "title",
        "title": "title",
        "本 change 处理方式": "handling",
        "handling": "handling",
        "后续 artifact": "artifact",
        "产生 artifact": "artifact",
        "artifact": "artifact",
        "required": "required",
        "依据上游 id": "ids",
        "ids": "ids",
        "原因 / n/a 说明": "reason",
        "原因": "reason",
        "reason": "reason",
        "相关约束转交": "handoff",
        "handoff": "handoff",
        "kind": "kind",
        "path": "path",
        "mode": "mode",
        "key": "key",
        "value": "value",
        "值": "value",
        "项目": "key",
    }
    return mapping.get(lowered, lowered.replace(" ", "_"))


def extract_upstream_sources(tables: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    rows = []
    for title, table in tables.items():
        if any(token in title for token in ("上游来源", "上游规划来源", "上游事实来源", "Upstream Sources")):
            for row in table:
                rows.append({
                    "source": row.get("source") or row.get("来源") or "",
                    "path": row.get("path") or "",
                    "source_id": row.get("source_id") or "",
                    "status": normalize_status(row.get("status") or ""),
                    "notes": row.get("notes") or "",
                })
    return rows


def extract_id_trace(tables: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    rows = []
    for title, table in tables.items():
        if any(token in title for token in ("上游输入 ID", "本 Change 覆盖", "本 Change 产出 ID", "ID Trace")):
            for row in table:
                text = " ".join(row.values())
                rows.append({
                    "type": row.get("type") or "",
                    "ids": sorted(set(ID_PATTERN.findall(text))),
                    "title": row.get("title") or "",
                    "source": row.get("source") or "",
                    "handling": row.get("handling") or "",
                    "artifact": row.get("artifact") or "",
                })
    return rows


def extract_artifact_applicability(tables: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows = []
    for title, table in tables.items():
        if "Artifact 适用性" in title or "Artifact Applicability" in title:
            for row in table:
                artifact = row.get("artifact") or row.get("source") or ""
                if not artifact:
                    continue
                rows.append({
                    "artifact": artifact,
                    "required": normalize_required(row.get("required") or ""),
                    "ids": row.get("ids") or "",
                    "reason": row.get("reason") or "",
                    "handoff": row.get("handoff") or "",
                })
    return rows


def extract_contract_sync(tables: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    values: dict[str, dict[str, str]] = {}
    for title, table in tables.items():
        if not any(token in title for token in ("Contract Ownership", "契约归属", "契约同步", "Contract Sync")):
            continue
        for row in table:
            key = normalize_contract_key(row.get("key") or row.get("source") or "")
            if not key:
                continue
            values[key] = {
                "value": row.get("value") or row.get("path") or "",
                "status": normalize_status(row.get("status") or ""),
                "notes": row.get("notes") or row.get("reason") or "",
            }
    return {
        "available": bool(values),
        "values": values,
        "machine_readable_contracts": split_contract_paths(values.get("machine_readable_contract", {}).get("value", "")),
    }


def normalize_contract_key(value: str) -> str:
    lowered = value.strip().lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "contract_source": "canonical_source",
        "canonical_contract": "canonical_source",
        "frontend_consumer": "consumer_repo",
        "backend_provider": "provider_repo",
        "external_repo/package/artifact_path": "machine_readable_contract",
        "external_repo_/_package_/_artifact_path": "machine_readable_contract",
        "version/commit/tag": "version_ref",
        "version_/_commit_/_tag": "version_ref",
    }
    return mapping.get(lowered, lowered)


def split_contract_paths(value: str) -> list[str]:
    if not value or value.strip().lower() in {"n/a", "na", "none", "无"}:
        return []
    parts = re.split(r"[,，\n]| / |；|;", value)
    return [part.strip() for part in parts if part.strip() and part.strip().lower() not in {"n/a", "na"}]


def extract_implementation_paths(tables: dict[str, list[dict[str, str]]], text: str) -> list[dict[str, Any]]:
    rows = []
    for title, table in tables.items():
        if any(token in title for token in IMPLEMENTATION_PATH_SECTION_TOKENS):
            for row in table:
                path = row.get("path") or ""
                if not path:
                    continue
                rows.append({
                    "kind": normalize_kind(row.get("kind") or path),
                    "path": path,
                    "ids": sorted(set(ID_PATTERN.findall(" ".join(row.values())))),
                    "mode": row.get("mode") or "",
                    "notes": row.get("notes") or "",
                })
    if rows:
        return rows
    return [
        {
            "kind": normalize_kind(path),
            "path": path,
            "ids": [],
            "mode": "",
            "notes": "fallback path scan",
        }
        for path in sorted(set(PATH_PATTERN.findall(text)))
        if is_implementation_path(path)
    ]


def extract_evidence(tables: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    rows = []
    for title, table in tables.items():
        if any(token in title for token in EVIDENCE_SECTION_TOKENS):
            for row in table:
                text = " ".join(row.values())
                rows.append({
                    "type": row.get("type") or "",
                    "path": row.get("path") or "",
                    "status": normalize_status(row.get("status") or ""),
                    "ids": sorted(set(ID_PATTERN.findall(text))),
                    "notes": row.get("notes") or "",
                })
    return rows


def extract_bullets(sections: dict[str, list[str]], titles: set[str]) -> list[str]:
    bullets = []
    for title, lines in sections.items():
        if title not in titles:
            continue
        bullets.extend(line.strip()[2:].strip() for line in lines if line.strip().startswith("- "))
    return [item for item in bullets if item]


def build_issues(
    exists: bool,
    tables: dict[str, list[dict[str, str]]],
    implementation_paths: list[dict[str, Any]],
    applicability: list[dict[str, str]],
) -> list[dict[str, str]]:
    issues = []
    if not exists:
        return [source_map_issue("SOURCE_MAP_MISSING", "blocker", "source-map.md is missing")]
    if not tables:
        issues.append(source_map_issue("SOURCE_MAP_UNSTRUCTURED", "risk", "source-map.md has no parseable tables; falling back to metadata scan"))
    if not implementation_paths:
        issues.append(source_map_issue("SOURCE_MAP_PATHS_MISSING", "risk", "source-map.md has no affected paths index"))
    for row in applicability:
        if row["required"] == "no" and not row["reason"]:
            issues.append(source_map_issue("SOURCE_MAP_NA_REASON_MISSING", "risk", f"{row['artifact']} is not required without reason"))
    return issues


def normalize_status(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"已确认", "confirmed", "pass", "passed", "ok", "done"}:
        return "confirmed" if lowered == "已确认" else lowered
    if lowered in {"缺失", "missing"}:
        return "missing"
    if lowered in {"风险", "risk"}:
        return "risk"
    if lowered in {"失败", "failed"}:
        return "failed"
    if lowered in {"n/a", "na"}:
        return "N/A"
    return value.strip()


def normalize_required(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"yes", "true", "是", "required"}:
        return "yes"
    if lowered in {"no", "false", "否", "n/a", "na"}:
        return "no"
    return value.strip()


def normalize_kind(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith(("tests/", "test/")) or "/tests/" in lowered or lowered.endswith((".test.ts", ".spec.ts", "_test.py")):
        return "test"
    if lowered.startswith(("src/", "app/", "apps/", "lib/", "libs/", "packages/")):
        return "code"
    if lowered.startswith(("docs/", "openspec/")):
        return "docs"
    return value.strip() or "reference"


def is_implementation_path(path: str) -> bool:
    return normalize_kind(path) in {"code", "test", "docs"}


def source_map_issue(code: str, severity: str, message: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "owner_artifact": "source-map.md",
    }


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
