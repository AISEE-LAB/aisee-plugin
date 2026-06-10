"""Project-local memory retrieval and writes for Aisee CLI."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.paths import cache_dir, legacy_memory_dir, memory_dir, memory_index_path, memory_rules_path
from aisee_cli.project import rel


MEMORY_SCHEMA_VERSION = "1.0"
MEMORY_TYPES = ("arch", "pref", "ctx", "stack")
MEMORY_STATUSES = ("active", "stale", "deprecated")
MEMORY_PRIORITIES = ("high", "normal", "low")
DEFAULT_LIMIT = 5
MAX_LIMIT = 20
SUMMARY_CHARS = 300
BODY_EXCERPT_CHARS = 800
TEXT_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_:+.-]+|[\u4e00-\u9fff]+")
SAFE_SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


def build_memory_inspect(root: Path) -> dict[str, Any]:
    entries, issues = load_memory_entries(root)
    layout = memory_layout(root)
    status = "missing" if not layout["available"] else status_from_issues(issues)
    return {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "status": status,
        "memory": {
            **layout,
            "types": list(MEMORY_TYPES),
            "statuses": list(MEMORY_STATUSES),
            "priorities": list(MEMORY_PRIORITIES),
            "summary": summarize_entries(entries),
            "limits": {
                "default_search_limit": DEFAULT_LIMIT,
                "max_search_limit": MAX_LIMIT,
                "summary_chars": SUMMARY_CHARS,
                "body_excerpt_chars": BODY_EXCERPT_CHARS,
            },
            "policy": memory_policy(),
            "next_commands": [
                "aisee memory list --json",
                'aisee memory search --query "<task>" --json',
                'aisee memory add --type pref --title "<title>" --summary "<summary>" --body "<body>" --json',
            ],
        },
        "entries": summarize_memory_entries(entries, include_body=False),
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "aisee memory inspect --json",
            "writes": False,
            "cache_is_fact_source": False,
        },
    }


def build_memory_list(
    root: Path,
    *,
    types: list[str] | None = None,
    status: str | None = None,
    priority: str | None = None,
    include_body: bool = False,
) -> dict[str, Any]:
    entries, issues = load_memory_entries(root)
    filter_issues = validate_filters(types or [], status, priority)
    filtered = filter_entries(entries, types=types or [], status=status or "active", priority=priority)
    command = build_list_command(types or [], status, priority, include_body)
    return {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "status": status_from_issues(issues + filter_issues),
        "memory": memory_layout(root),
        "entries": summarize_memory_entries(filtered, include_body=include_body),
        "issues": issues + filter_issues,
        "summary": summarize_issues(issues + filter_issues),
        "meta": {
            "command": command,
            "writes": False,
            "cache_is_fact_source": False,
            "full_body_read": include_body,
        },
    }


def build_memory_search(
    root: Path,
    *,
    query: str,
    types: list[str] | None = None,
    limit: int | None = None,
    include_body: bool = False,
    include_stale: bool = False,
    include_deprecated: bool = False,
) -> dict[str, Any]:
    entries, issues = load_memory_entries(root, include_body=include_body)
    filter_issues = validate_filters(types or [], None, None)
    capped_limit = normalize_limit(limit)
    matches, explain = match_entries(
        entries,
        query=query,
        types=types or [],
        limit=capped_limit,
        include_stale=include_stale,
        include_deprecated=include_deprecated,
        include_body=include_body,
    )
    conflicts = detect_conflicts(entries)
    command = build_search_command(query, types or [], capped_limit, include_body, include_stale, include_deprecated)
    return {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "status": status_from_issues(issues + filter_issues),
        "feature_source": "direct",
        "query": query,
        "memory": {
            "available": memory_layout(root)["available"],
            "matches": matches,
            "explain": explain,
            "conflicts": conflicts,
        },
        "issues": issues + filter_issues,
        "summary": summarize_issues(issues + filter_issues),
        "meta": {
            "command": command,
            "writes": False,
            "cache_is_fact_source": False,
            "full_body_read": include_body,
        },
    }


def build_memory_add(
    root: Path,
    *,
    memory_type: str,
    title: str,
    summary: str,
    body: str,
    priority: str = "normal",
    source_refs: list[str] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if memory_type not in MEMORY_TYPES:
        issues.append(issue("MEMORY_TYPE_INVALID", "blocker", f"unsupported memory type: {memory_type}"))
    if priority not in MEMORY_PRIORITIES:
        issues.append(issue("MEMORY_PRIORITY_INVALID", "blocker", f"unsupported memory priority: {priority}"))
    if not title.strip():
        issues.append(issue("MEMORY_TITLE_MISSING", "blocker", "memory title is required"))
    if not summary.strip():
        issues.append(issue("MEMORY_SUMMARY_MISSING", "blocker", "memory summary is required"))
    if not body.strip():
        issues.append(issue("MEMORY_BODY_MISSING", "blocker", "memory body is required"))

    slug = slugify(title)
    if not slug:
        issues.append(issue("MEMORY_SLUG_INVALID", "blocker", f"could not derive a safe slug from title: {title}"))
    if issues:
        return memory_write_result(root, [], False, issues, "aisee memory add --json")

    target_dir = memory_dir(root) / memory_type
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename_for_type(memory_type, slug)
    if target.exists():
        target = unique_path(target_dir, target.stem, target.suffix)

    metadata = {
        "id": slug,
        "title": title.strip(),
        "type": memory_type,
        "status": "active",
        "priority": priority,
        "summary": truncate(summary.strip(), SUMMARY_CHARS),
        "source_refs": source_refs or [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    target.write_text(render_memory_markdown(metadata, body), encoding="utf-8")
    entries, parse_issues = load_memory_entries(root)
    index_path = write_memory_index(root, entries)
    cache_path = write_memory_cache(root, entries, parse_issues)
    written = [rel(root, target), rel(root, index_path), rel(root, cache_path)]
    return memory_write_result(root, written, True, parse_issues, "aisee memory add --json")


def build_memory_update_index(root: Path) -> dict[str, Any]:
    entries, issues = load_memory_entries(root)
    if any(item.get("severity") == "blocker" for item in issues):
        return memory_write_result(root, [], False, issues, "aisee memory update-index --json")
    index_path = write_memory_index(root, entries)
    cache_path = write_memory_cache(root, entries, issues)
    return memory_write_result(
        root,
        [rel(root, index_path), rel(root, cache_path)],
        True,
        issues,
        "aisee memory update-index --json",
    )


def build_memory_query_for_context_pack(root: Path, *, change: str, target: str, query: str | None = None) -> dict[str, Any]:
    search = build_memory_search(
        root,
        query=query or f"{change} {target}",
        limit=DEFAULT_LIMIT,
        include_body=False,
    )
    payload = search.get("memory", {})
    return {
        "status": search.get("status"),
        "matches": payload.get("matches", []),
        "conflicts": payload.get("conflicts", []),
        "summary": search.get("summary", {}),
        "issues": search.get("issues", []),
        "meta": {
            "cache_is_fact_source": search.get("meta", {}).get("cache_is_fact_source", False),
            "full_body_read": search.get("meta", {}).get("full_body_read", False),
        },
    }


def load_memory_entries(root: Path, *, include_body: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    base = active_memory_dir(root)
    if base is None:
        return [], []
    entries: list[dict[str, Any]] = []
    for memory_type in MEMORY_TYPES:
        type_dir = base / memory_type
        if not type_dir.exists():
            continue
        for path in sorted(type_dir.glob("*.md")):
            entry, entry_issues = parse_memory_file(root, path, memory_type, include_body=include_body)
            issues.extend(entry_issues)
            if entry:
                entries.append(entry)
    return sorted(entries, key=lambda item: (item["type"], item["path"])), issues


def parse_memory_file(root: Path, path: Path, default_type: str, *, include_body: bool) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    metadata, body = split_frontmatter(text)
    legacy = False
    if not metadata:
        metadata, body = parse_legacy_memory(text, default_type, path)
        legacy = True
    memory_type = normalize_string(metadata.get("type") or default_type)
    entry_id = normalize_string(metadata.get("id") or path.stem)
    title = normalize_string(metadata.get("title") or first_heading(text) or path.stem)
    status = normalize_string(metadata.get("status") or "active")
    priority = normalize_string(metadata.get("priority") or "normal")
    summary = normalize_string(metadata.get("summary") or extract_summary(text))
    source_refs = normalize_string_list(metadata.get("source_refs") or metadata.get("source_refs[]") or metadata.get("source_ref"))
    updated_at = normalize_string(metadata.get("updated_at") or metadata.get("date") or metadata.get("日期"))
    tags = normalize_string_list(metadata.get("tags"))
    issues: list[dict[str, str]] = []
    rel_path = rel(root, path)
    if memory_type not in MEMORY_TYPES:
        issues.append(issue("MEMORY_TYPE_INVALID", "risk", f"unsupported memory type: {memory_type}", rel_path))
    if status not in MEMORY_STATUSES:
        issues.append(issue("MEMORY_STATUS_INVALID", "risk", f"unsupported memory status: {status}", rel_path))
    if priority not in MEMORY_PRIORITIES:
        issues.append(issue("MEMORY_PRIORITY_INVALID", "risk", f"unsupported memory priority: {priority}", rel_path))
    if not summary:
        issues.append(issue("MEMORY_SUMMARY_MISSING", "risk", "memory summary is missing", rel_path))
    entry = {
        "id": entry_id,
        "type": memory_type if memory_type in MEMORY_TYPES else default_type,
        "title": title,
        "status": status if status in MEMORY_STATUSES else "active",
        "priority": priority if priority in MEMORY_PRIORITIES else "normal",
        "summary": truncate(summary, SUMMARY_CHARS),
        "source_refs": source_refs,
        "updated_at": updated_at or None,
        "tags": tags,
        "path": rel_path,
        "legacy_format": legacy,
        "hash": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "_body": body,
    }
    if include_body:
        entry["body_excerpt"] = truncate(body.strip(), BODY_EXCERPT_CHARS)
    return entry, issues


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    collected: list[str] = []
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            data = yaml.safe_load("\n".join(collected).strip()) or {}
            return data if isinstance(data, dict) else {}, "\n".join(lines[index + 1 :]).lstrip()
        collected.append(line)
    return {}, text


def parse_legacy_memory(text: str, default_type: str, path: Path) -> tuple[dict[str, Any], str]:
    metadata: dict[str, Any] = {"type": default_type, "id": path.stem, "status": "active", "priority": "normal"}
    heading = first_heading(text)
    if heading:
        metadata["title"] = heading
    date_match = re.search(r"\*\*(?:日期|Date)：?\*\*\s*([^\n]+)", text)
    type_match = re.search(r"\*\*(?:类型|Type)：?\*\*\s*([A-Za-z0-9_-]+)", text)
    if date_match:
        metadata["updated_at"] = date_match.group(1).strip()
    if type_match:
        metadata["type"] = type_match.group(1).strip()
    summary = section_text(text, "摘要") or section_text(text, "Summary")
    if summary:
        metadata["summary"] = summary
    return metadata, text


def memory_layout(root: Path) -> dict[str, Any]:
    canonical = memory_dir(root)
    legacy = legacy_memory_dir(root)
    canonical_exists = canonical.exists()
    legacy_exists = legacy.exists()
    active = active_memory_dir(root) or canonical
    state = "missing"
    if canonical_exists and legacy_exists:
        state = "dual"
    elif canonical_exists:
        state = "canonical"
    elif legacy_exists:
        state = "legacy-only"
    return {
        "available": canonical_exists or legacy_exists,
        "state": state,
        "root": rel(root, active),
        "canonical_root": rel(root, canonical),
        "legacy_root": rel(root, legacy),
        "rules": rel(root, memory_rules_path(root)) if memory_rules_path(root).exists() else None,
        "index": rel(root, memory_index_path(root)) if memory_index_path(root).exists() else None,
    }


def active_memory_dir(root: Path) -> Path | None:
    canonical = memory_dir(root)
    legacy = legacy_memory_dir(root)
    if canonical.exists():
        return canonical
    if legacy.exists():
        return legacy
    return None


def memory_policy() -> dict[str, Any]:
    return {
        "auto_read": True,
        "auto_write": False,
        "write_requires_user_confirmation": True,
        "hooks_can_read": True,
        "hooks_can_write": False,
        "fact_source": False,
        "overridden_by": ["openspec", "source-map.md", "tasks.md"],
    }


def summarize_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_type = {memory_type: 0 for memory_type in MEMORY_TYPES}
    by_status = {status: 0 for status in MEMORY_STATUSES}
    for entry in entries:
        by_type[entry["type"]] = by_type.get(entry["type"], 0) + 1
        by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
    return {
        "entries": len(entries),
        "by_type": by_type,
        "by_status": by_status,
    }


def summarize_memory_entries(entries: list[dict[str, Any]], *, include_body: bool) -> list[dict[str, Any]]:
    result = []
    for entry in entries:
        item = {key: entry.get(key) for key in ("id", "type", "title", "status", "priority", "summary", "path", "source_refs", "updated_at", "tags")}
        item["legacy_format"] = bool(entry.get("legacy_format"))
        if include_body:
            item["body_excerpt"] = truncate(str(entry.get("body_excerpt") or entry.get("_body") or ""), BODY_EXCERPT_CHARS)
        result.append(item)
    return result


def filter_entries(entries: list[dict[str, Any]], *, types: list[str], status: str, priority: str | None) -> list[dict[str, Any]]:
    result = []
    for entry in entries:
        if types and entry["type"] not in types:
            continue
        if status and entry["status"] != status:
            continue
        if priority and entry["priority"] != priority:
            continue
        result.append(entry)
    return result


def match_entries(
    entries: list[dict[str, Any]],
    *,
    query: str,
    types: list[str],
    limit: int,
    include_stale: bool,
    include_deprecated: bool,
    include_body: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    query_tokens = set(tokenize(query))
    candidates: list[tuple[int, dict[str, Any]]] = []
    explain: list[dict[str, Any]] = []
    for entry in entries:
        if types and entry["type"] not in types:
            explain.append({"id": entry["id"], "status": "filtered", "reason": "type does not match"})
            continue
        if entry["status"] == "stale" and not include_stale:
            explain.append({"id": entry["id"], "status": "filtered", "reason": "status is stale"})
            continue
        if entry["status"] == "deprecated" and not include_deprecated:
            explain.append({"id": entry["id"], "status": "filtered", "reason": "status is deprecated"})
            continue
        if entry["status"] not in {"active", "stale", "deprecated"}:
            continue
        score = score_entry(entry, query_tokens)
        if score <= 0 and query_tokens:
            explain.append({"id": entry["id"], "status": "filtered", "reason": "lexical score is zero"})
            continue
        candidates.append((score, entry))
    candidates.sort(key=lambda item: (-item[0], priority_rank(item[1]["priority"]), item[1]["id"]))
    matches = []
    for score, entry in candidates[:limit]:
        item = summarize_memory_entries([entry], include_body=include_body)[0]
        item["score"] = score
        item["match_reason"] = "lexical match; project memory is guidance, not OpenSpec truth"
        matches.append(item)
    return matches, explain[:20]


def score_entry(entry: dict[str, Any], query_tokens: set[str]) -> int:
    tokens = tokens_for_entry(entry)
    overlap = len(query_tokens & tokens)
    type_bonus = 0
    if entry["type"] == "pref" and {"style", "format", "commit", "偏好", "风格"} & query_tokens:
        type_bonus += 2
    if entry["type"] == "stack" and {"test", "build", "version", "dependency", "env", "测试", "构建"} & query_tokens:
        type_bonus += 2
    if entry["priority"] == "high":
        type_bonus += 1
    return overlap + type_bonus


def tokens_for_entry(entry: dict[str, Any]) -> set[str]:
    parts = [
        entry.get("id"),
        entry.get("type"),
        entry.get("title"),
        entry.get("summary"),
        " ".join(entry.get("source_refs") or []),
        " ".join(entry.get("tags") or []),
    ]
    return set(tokenize(" ".join(str(item or "") for item in parts)))


def detect_conflicts(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for entry in entries:
        if entry.get("status") != "active":
            continue
        key = (entry.get("type", ""), normalize_key(str(entry.get("title") or "")))
        seen.setdefault(key, []).append(entry)
    conflicts = []
    for (memory_type, title_key), grouped in seen.items():
        if title_key and len(grouped) > 1:
            conflicts.append({
                "type": memory_type,
                "title_key": title_key,
                "entries": [item["path"] for item in grouped],
            })
    return conflicts


def validate_filters(types: list[str], status: str | None, priority: str | None) -> list[dict[str, str]]:
    issues = []
    for memory_type in types:
        if memory_type not in MEMORY_TYPES:
            issues.append(issue("MEMORY_TYPE_INVALID", "blocker", f"unsupported memory type: {memory_type}"))
    if status and status not in MEMORY_STATUSES:
        issues.append(issue("MEMORY_STATUS_INVALID", "blocker", f"unsupported memory status: {status}"))
    if priority and priority not in MEMORY_PRIORITIES:
        issues.append(issue("MEMORY_PRIORITY_INVALID", "blocker", f"unsupported memory priority: {priority}"))
    return issues


def normalize_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    return max(1, min(int(limit), MAX_LIMIT))


def normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def tokenize(text: str) -> list[str]:
    return [item.lower() for item in TEXT_TOKEN_PATTERN.findall(text)]


def normalize_key(text: str) -> str:
    return "-".join(tokenize(text))


def slugify(title: str) -> str:
    tokens = tokenize(title)
    slug = "-".join(token for token in tokens if re.fullmatch(r"[a-z0-9_.:+-]+", token))[:80].strip("-._:+")
    if not slug:
        digest = hashlib.sha1(title.strip().encode("utf-8")).hexdigest()[:12]
        slug = f"memory-{digest}"
    slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    return slug if SAFE_SLUG_PATTERN.fullmatch(slug) else ""


def filename_for_type(memory_type: str, slug: str) -> str:
    if memory_type in {"arch", "ctx"}:
        return f"{date.today().isoformat()}-{slug}.md"
    return f"{slug}.md"


def unique_path(directory: Path, stem: str, suffix: str) -> Path:
    for index in range(2, 100):
        candidate = directory / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise ValueError(f"could not allocate unique memory path for {stem}{suffix}")


def render_memory_markdown(metadata: dict[str, Any], body: str) -> str:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n\n# {metadata['title']}\n\n{body.strip()}\n"


def write_memory_index(root: Path, entries: list[dict[str, Any]]) -> Path:
    path = memory_dir(root) / "index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    grouped = {memory_type: [] for memory_type in MEMORY_TYPES}
    for entry in entries:
        grouped.setdefault(entry["type"], []).append(entry)
    lines = [
        "# Memory Index",
        "",
        "> 项目记忆入口。Project memory 是项目本地指导信息，不是事实源，不替代 OpenSpec、source-map 或 tasks。",
        "> 使用 `aisee memory inspect --json` 发现命令，使用 `aisee memory search --query \"<task>\" --json` 按需检索。",
        "",
    ]
    headings = {
        "arch": "## 架构决策（arch/）",
        "pref": "## 用户偏好（pref/）",
        "ctx": "## 上下文快照（ctx/）",
        "stack": "## 技术栈笔记（stack/）",
    }
    for memory_type in MEMORY_TYPES:
        lines.extend([headings[memory_type], ""])
        for entry in sorted(grouped.get(memory_type, []), key=lambda item: item["path"]):
            if entry["status"] == "deprecated":
                continue
            prefix = f"[{entry['updated_at']}]" if entry.get("updated_at") else f"[{entry['priority']}]"
            lines.append(f"- {prefix} {entry['summary']} -> {entry['path']}")
        if not grouped.get(memory_type):
            lines.append(f"<!-- 暂无 {memory_type} 记忆 -->")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_memory_cache(root: Path, entries: list[dict[str, Any]], issues: list[dict[str, str]]) -> Path:
    path = cache_dir(root) / "memory-index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cache_is_fact_source": False,
        "entries": summarize_memory_entries(entries, include_body=False),
        "issues": issues,
        "summary": summarize_issues(issues),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def memory_write_result(root: Path, written: list[str], changed: bool, issues: list[dict[str, str]], command: str) -> dict[str, Any]:
    return {
        "schema_version": MEMORY_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "memory": memory_layout(root),
        "written": written,
        "changed": changed,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": command,
            "writes": changed,
            "cache_is_fact_source": False,
        },
    }


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def section_text(text: str, heading: str) -> str:
    lines = text.splitlines()
    collected: list[str] = []
    in_section = False
    for line in lines:
        if re.match(rf"^#+\s+{re.escape(heading)}\s*$", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and line.startswith("#"):
            break
        if in_section and line.strip():
            collected.append(line.strip())
    return " ".join(collected).strip()


def extract_summary(text: str) -> str:
    return section_text(text, "摘要") or section_text(text, "Summary")


def truncate(text: str, limit: int) -> str:
    value = text.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def priority_rank(priority: str) -> int:
    return {"high": 0, "normal": 1, "low": 2}.get(priority, 3)


def build_list_command(types: list[str], status: str | None, priority: str | None, include_body: bool) -> str:
    parts = ["aisee memory list"]
    for memory_type in types:
        parts.extend(["--type", memory_type])
    if status:
        parts.extend(["--status", status])
    if priority:
        parts.extend(["--priority", priority])
    if include_body:
        parts.append("--include-body")
    parts.append("--json")
    return " ".join(parts)


def build_search_command(query: str, types: list[str], limit: int, include_body: bool, include_stale: bool, include_deprecated: bool) -> str:
    parts = ["aisee memory search", "--query", query, "--limit", str(limit)]
    for memory_type in types:
        parts.extend(["--type", memory_type])
    if include_body:
        parts.append("--include-body")
    if include_stale:
        parts.append("--include-stale")
    if include_deprecated:
        parts.append("--include-deprecated")
    parts.append("--json")
    return " ".join(parts)
