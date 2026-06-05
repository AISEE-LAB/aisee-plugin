"""Team knowledge guardrail retrieval for Aisee CLI."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # PyYAML is optional; tests run with it, installed packages may not.
    import yaml  # type: ignore
except Exception:  # pragma: no cover - exercised only without PyYAML.
    yaml = None

from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.paths import knowledge_config_path, knowledge_index_path
from aisee_cli.project import rel


KNOWLEDGE_SCHEMA_VERSION = "1.0"
DEFAULT_MAX_CARDS = 3
CARD_REQUIRED_FIELDS = ("id", "title", "status", "applies_to", "trigger", "recommended_action", "boundaries")
TEXT_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_:+.-]+|[\u4e00-\u9fff]+")


def build_knowledge_inspect(root: Path) -> dict[str, Any]:
    config, config_issues = load_knowledge_config(root)
    team_root = resolve_team_root(root, config)
    pack_results, card_results, load_issues = load_configured_knowledge(root, config, team_root)
    issues = config_issues + load_issues
    status = "missing" if not config.get("available") else status_from_issues(issues)
    return {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": status,
        "config": config_public(root, config, team_root),
        "packs": pack_results,
        "cards": summarize_cards(card_results),
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "aisee knowledge inspect --json",
            "reads": ["aisee/knowledge.yaml", "knowledge/packs/*.yaml", "knowledge/cards frontmatter"],
            "cache_is_fact_source": False,
        },
    }


def build_knowledge_query(
    root: Path,
    *,
    phase: str | None = None,
    surfaces: list[str] | None = None,
    schema: str | None = None,
    stack: str | None = None,
    query: str | None = None,
    from_change: str | None = None,
    target: str | None = None,
    max_cards: int | None = None,
    debug: bool = False,
) -> dict[str, Any]:
    config, config_issues = load_knowledge_config(root)
    team_root = resolve_team_root(root, config)
    pack_results, team_cards, load_issues = load_configured_knowledge(root, config, team_root)
    feature_data = extract_query_features(
        root,
        phase=phase,
        surfaces=surfaces or [],
        schema=schema,
        stack=stack,
        query=query,
        from_change=from_change,
        target=target,
    )
    project_candidates = load_project_candidates(root) if retrieval_config(config).get("include_project_candidates", True) else []
    limit = normalize_max_cards(max_cards or retrieval_config(config).get("max_cards") or DEFAULT_MAX_CARDS)
    matches, explanations = match_cards(
        team_cards,
        project_candidates,
        feature_data,
        max_cards=limit,
        debug=debug,
    )
    issues = config_issues + load_issues
    if not config.get("available"):
        issues.append(issue("KNOWLEDGE_CONFIG_MISSING", "info", "aisee/knowledge.yaml was not found", rel(root, knowledge_config_path(root))))
    result_status = "ok" if not any(item.get("severity") == "blocker" for item in issues) else "blocked"
    return {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": result_status,
        "feature_source": "from-change" if from_change else "direct",
        "features": feature_data,
        "knowledge": {
            "enabled": bool(config.get("available")),
            "source": knowledge_source(config),
            "matches": matches,
            "explain": explanations,
        },
        "config": config_public(root, config, team_root),
        "packs": pack_results,
        "project_candidates": {
            "count": len(project_candidates),
            "paths": [item["path"] for item in project_candidates],
        },
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": build_query_command(from_change, target, phase, surfaces or [], schema, stack),
            "cache_is_fact_source": False,
            "full_card_body_read": bool(debug),
        },
    }


def build_knowledge_index(root: Path, *, write_cache: bool = True) -> dict[str, Any]:
    config, config_issues = load_knowledge_config(root)
    team_root = resolve_team_root(root, config)
    pack_results, cards, load_issues = load_configured_knowledge(root, config, team_root)
    issues = config_issues + load_issues
    documents = []
    for card in cards:
        metadata = card.get("metadata", {})
        tokens = sorted(tokens_for_card(metadata))
        source_path = card.get("path")
        text = read_text((team_root / source_path) if source_path and team_root else Path(""))
        documents.append({
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "status": metadata.get("status"),
            "path": source_path,
            "pack": card.get("pack"),
            "tokens": tokens,
            "hash": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None,
        })
    result = {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "index": {
            "path": rel(root, knowledge_index_path(root)),
            "writes": write_cache,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "config": config_public(root, config, team_root),
        "packs": pack_results,
        "cards": documents,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "aisee knowledge index --json",
            "cache_is_fact_source": False,
        },
    }
    if write_cache:
        path = knowledge_index_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def load_knowledge_config(root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    path = knowledge_config_path(root)
    if not path.exists():
        return {
            "available": False,
            "path": rel(root, path),
            "repo": None,
            "ref": None,
            "local_path": None,
            "packs": [],
            "retrieval": {"max_cards": DEFAULT_MAX_CARDS, "include_project_candidates": True},
        }, []
    data, parse_error = load_yaml_file(path)
    issues: list[dict[str, str]] = []
    if parse_error:
        issues.append(issue("KNOWLEDGE_CONFIG_INVALID", "blocker", parse_error, rel(root, path)))
        data = {}
    packs = normalize_string_list(data.get("packs"))
    retrieval = data.get("retrieval") if isinstance(data.get("retrieval"), dict) else {}
    max_cards = normalize_max_cards(retrieval.get("max_cards") if isinstance(retrieval, dict) else None)
    return {
        "available": True,
        "path": rel(root, path),
        "repo": data.get("repo") if isinstance(data, dict) else None,
        "ref": data.get("ref") if isinstance(data, dict) else None,
        "local_path": data.get("path") if isinstance(data, dict) else None,
        "packs": packs,
        "retrieval": {
            "max_cards": max_cards,
            "include_project_candidates": bool(retrieval.get("include_project_candidates", True)) if isinstance(retrieval, dict) else True,
            "vector": retrieval.get("vector") if isinstance(retrieval, dict) else None,
        },
    }, issues


def resolve_team_root(root: Path, config: dict[str, Any]) -> Path | None:
    local_path = config.get("local_path")
    if not local_path:
        return None
    candidate = Path(str(local_path))
    return candidate if candidate.is_absolute() else root / candidate


def load_configured_knowledge(
    root: Path,
    config: dict[str, Any],
    team_root: Path | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    if not config.get("available"):
        return [], [], issues
    if team_root is None:
        issues.append(issue("KNOWLEDGE_PATH_MISSING", "risk", "aisee/knowledge.yaml does not declare a local path", config.get("path")))
        return [], [], issues
    if not team_root.exists():
        issues.append(issue("KNOWLEDGE_REPO_MISSING", "risk", f"configured team knowledge path does not exist: {team_root}", rel(root, team_root)))
        return [], [], issues

    pack_results: list[dict[str, Any]] = []
    cards: list[dict[str, Any]] = []
    for pack_id in config.get("packs", []):
        pack_path = team_root / "knowledge" / "packs" / f"{pack_id}.yaml"
        if not pack_path.exists():
            pack_results.append({"id": pack_id, "status": "missing", "path": rel(root, pack_path), "cards": []})
            issues.append(issue("KNOWLEDGE_PACK_MISSING", "risk", f"knowledge pack was not found: {pack_id}", rel(root, pack_path)))
            continue
        pack_data, parse_error = load_yaml_file(pack_path)
        if parse_error:
            pack_results.append({"id": pack_id, "status": "invalid", "path": rel(root, pack_path), "cards": []})
            issues.append(issue("KNOWLEDGE_PACK_INVALID", "blocker", parse_error, rel(root, pack_path)))
            continue
        pack_cards, card_issues = load_pack_cards(root, team_root, pack_id, pack_data)
        cards.extend(pack_cards)
        issues.extend(card_issues)
        pack_results.append({
            "id": pack_id,
            "status": str(pack_data.get("status") or "active"),
            "path": rel(root, pack_path),
            "cards": [card["metadata"].get("id") for card in pack_cards],
            "card_count": len(pack_cards),
        })
    return pack_results, cards, issues


def load_pack_cards(root: Path, team_root: Path, pack_id: str, pack_data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    disabled = set(normalize_string_list(pack_data.get("disabled_cards")))
    declared_paths: set[Path] = set()
    cards_by_id = {item for item in normalize_string_list(pack_data.get("cards"))}
    for card_id in cards_by_id:
        if card_id in disabled:
            continue
        found = find_card_by_id(team_root, card_id)
        if found is None:
            issues.append(issue("KNOWLEDGE_CARD_MISSING", "risk", f"pack references missing card: {card_id}", pack_id))
            continue
        declared_paths.add(found)
    for pattern in normalize_string_list(pack_data.get("card_globs")):
        for path in sorted((team_root).glob(pattern)):
            if path.is_file() and is_under(path, team_root):
                declared_paths.add(path)

    cards: list[dict[str, Any]] = []
    for path in sorted(declared_paths):
        metadata, body, parse_error = load_card(path)
        if parse_error:
            issues.append(issue("KNOWLEDGE_CARD_INVALID", "risk", parse_error, rel(root, path)))
            continue
        card_id = str(metadata.get("id") or "")
        if not card_id or card_id in disabled:
            continue
        missing = [field for field in CARD_REQUIRED_FIELDS if not metadata.get(field)]
        if missing:
            issues.append(issue("KNOWLEDGE_CARD_FIELDS_MISSING", "risk", f"card missing required fields: {', '.join(missing)}", rel(root, path)))
        cards.append({
            "pack": pack_id,
            "path": rel(team_root, path),
            "metadata": metadata,
            "body": body,
        })
    return cards, issues


def find_card_by_id(team_root: Path, card_id: str) -> Path | None:
    for suffix in (".md", ".yaml", ".yml"):
        for path in sorted((team_root / "knowledge" / "cards").rglob(f"*{suffix}")):
            metadata, _body, _error = load_card(path)
            if str(metadata.get("id") or "") == card_id:
                return path
    return None


def load_card(path: Path) -> tuple[dict[str, Any], str, str | None]:
    text = read_text(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        data, error = load_yaml_text(text, str(path))
        return (data if isinstance(data, dict) else {}), "", error
    frontmatter, body = split_frontmatter(text)
    if not frontmatter:
        return {}, body, f"card has no YAML frontmatter: {path}"
    data, error = load_yaml_text(frontmatter, str(path))
    return (data if isinstance(data, dict) else {}), body, error


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1].strip(), parts[2].lstrip()


def load_project_candidates(root: Path) -> list[dict[str, Any]]:
    base = root / "aisee" / "docs" / "reflect" / "knowledge-candidates"
    if not base.exists():
        return []
    candidates = []
    for path in sorted(base.rglob("*.md")):
        metadata, body = parse_project_candidate(path)
        if metadata:
            candidates.append({
                "pack": "project-local",
                "path": rel(root, path),
                "metadata": metadata,
                "body": body,
            })
    return candidates


def parse_project_candidate(path: Path) -> tuple[dict[str, Any], str]:
    text = read_text(path)
    card_block = extract_fenced_yaml_after_heading(text, "Card Draft")
    if card_block:
        data, _error = load_yaml_text(card_block, str(path))
        return data if isinstance(data, dict) else {}, text
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return {"id": path.stem, "title": title or path.stem, "status": "candidate"}, text


def extract_fenced_yaml_after_heading(text: str, heading: str) -> str:
    lines = text.splitlines()
    in_section = False
    in_fence = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == f"## {heading}":
            in_section = True
            continue
        if not in_section:
            continue
        if line.startswith("## ") and not in_fence:
            break
        if line.strip() in {"```yaml", "```yml"}:
            in_fence = True
            continue
        if line.strip() == "```" and in_fence:
            break
        if in_fence:
            collected.append(line)
    return "\n".join(collected).strip()


def extract_query_features(
    root: Path,
    *,
    phase: str | None,
    surfaces: list[str],
    schema: str | None,
    stack: str | None,
    query: str | None,
    from_change: str | None,
    target: str | None,
) -> dict[str, Any]:
    features = {
        "phase": phase,
        "phases": [phase] if phase else [],
        "surfaces": normalize_string_list(surfaces),
        "schema": schema,
        "schemas": [schema] if schema else [],
        "stack": stack,
        "stacks": [stack] if stack else [],
        "query": query or "",
        "risk_signals": [],
        "paths": [],
        "change": from_change,
        "target": target,
    }
    if not from_change:
        return features

    from aisee_cli.context_pack import build_context_pack

    pack = build_context_pack(root, from_change, target or "ce-work")
    derived = pack["facts"]["derived"]
    parsed = pack["facts"]["parsed"]
    paths = sorted(set(derived.get("code_paths", []) + derived.get("test_paths", [])))
    surfaces_from_paths = derive_surfaces(paths, parsed.get("artifacts", {}), target)
    schema_name = pack["change"].get("schema")
    phase_name = phase_for_target(target or "ce-work")
    features.update({
        "phase": phase or phase_name,
        "phases": sorted(set([*(features["phases"] or []), phase_name])),
        "schema": schema or schema_name,
        "schemas": sorted(set([item for item in [schema, schema_name] if item])),
        "surfaces": sorted(set(features["surfaces"] + surfaces_from_paths)),
        "paths": paths,
        "query": query or " ".join([
            pack["change"].get("id", ""),
            " ".join(paths),
            " ".join(surfaces_from_paths),
        ]),
        "risk_signals": derive_risk_signals(paths, parsed.get("artifacts", {})),
    })
    return features


def match_cards(
    team_cards: list[dict[str, Any]],
    project_candidates: list[dict[str, Any]],
    features: dict[str, Any],
    *,
    max_cards: int,
    debug: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    project_by_similarity = build_project_similarity(project_candidates)
    candidates: list[tuple[int, dict[str, Any], str]] = []
    explanations: list[dict[str, Any]] = []
    for card in team_cards:
        metadata = card.get("metadata", {})
        include, reason = passes_hard_filters(metadata, features)
        if not include:
            explanations.append({"id": metadata.get("id"), "status": "filtered", "reason": reason})
            continue
        score = score_card(metadata, features)
        if score <= 0 and features.get("query"):
            explanations.append({"id": metadata.get("id"), "status": "filtered", "reason": "lexical score is zero"})
            continue
        candidates.append((score, card, reason))

    candidates.sort(key=lambda item: (-item[0], str(item[1].get("metadata", {}).get("id") or "")))
    matches: list[dict[str, Any]] = []
    for score, card, filter_reason in candidates[:max_cards]:
        metadata = card.get("metadata", {})
        card_id = str(metadata.get("id") or "")
        project_match = project_by_similarity.get(card_id) or project_by_similarity.get(normalize_key(str(metadata.get("title") or "")))
        dedupe = {"status": "unique"}
        if project_match:
            dedupe = {
                "status": "deduped_project_candidate",
                "project_candidate": project_match.get("path"),
                "notes": "team active card covers a project-local candidate",
            }
        match = {
            "id": card_id,
            "title": metadata.get("title"),
            "score": score,
            "match_reason": build_match_reason(metadata, features, filter_reason),
            "recommended_action": normalize_string_list(metadata.get("recommended_action")),
            "boundaries": normalize_string_list(metadata.get("boundaries")),
            "source": {
                "pack": card.get("pack"),
                "path": card.get("path"),
            },
            "dedupe": dedupe,
        }
        if debug:
            match["debug"] = {"body_excerpt": str(card.get("body") or "")[:800]}
        matches.append(match)
    return matches, explanations[:20]


def passes_hard_filters(metadata: dict[str, Any], features: dict[str, Any]) -> tuple[bool, str]:
    if metadata.get("status") != "active":
        return False, f"status is {metadata.get('status') or 'missing'}"
    applies = metadata.get("applies_to") if isinstance(metadata.get("applies_to"), dict) else {}
    checks = (
        ("phases", features.get("phases", [])),
        ("surfaces", features.get("surfaces", [])),
        ("schemas", features.get("schemas", [])),
        ("stacks", features.get("stacks", [])),
    )
    for key, requested in checks:
        declared = normalize_string_list(applies.get(key))
        requested_values = normalize_string_list(requested)
        if declared and requested_values and not intersects(declared, requested_values):
            return False, f"{key} do not match"
    return True, "hard filters matched"


def score_card(metadata: dict[str, Any], features: dict[str, Any]) -> int:
    query_tokens = set(tokenize(" ".join([
        str(features.get("query") or ""),
        " ".join(features.get("surfaces", [])),
        " ".join(features.get("schemas", [])),
        " ".join(features.get("phases", [])),
        " ".join(features.get("stacks", [])),
    ])))
    card_tokens = tokens_for_card(metadata)
    overlap = len(query_tokens & card_tokens)
    applies = metadata.get("applies_to") if isinstance(metadata.get("applies_to"), dict) else {}
    exact = 0
    for key in ("phases", "surfaces", "schemas", "stacks"):
        if intersects(normalize_string_list(applies.get(key)), normalize_string_list(features.get(key, []))):
            exact += 3
    return overlap + exact


def tokens_for_card(metadata: dict[str, Any]) -> set[str]:
    parts = [
        metadata.get("id"),
        metadata.get("title"),
        " ".join(normalize_string_list(metadata.get("trigger"))),
        " ".join(normalize_string_list(metadata.get("recommended_action"))),
        " ".join(normalize_string_list(metadata.get("tags"))),
    ]
    applies = metadata.get("applies_to") if isinstance(metadata.get("applies_to"), dict) else {}
    for key in ("phases", "surfaces", "schemas", "stacks", "frameworks"):
        parts.append(" ".join(normalize_string_list(applies.get(key))))
    return set(tokenize(" ".join(str(item or "") for item in parts)))


def build_project_similarity(project_candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for candidate in project_candidates:
        metadata = candidate.get("metadata", {})
        if metadata.get("id"):
            result[str(metadata["id"])] = candidate
        if metadata.get("title"):
            result[normalize_key(str(metadata["title"]))] = candidate
    return result


def build_match_reason(metadata: dict[str, Any], features: dict[str, Any], filter_reason: str) -> str:
    surfaces = ", ".join(features.get("surfaces", [])[:4])
    schema = features.get("schema")
    parts = [filter_reason]
    if surfaces:
        parts.append(f"surfaces: {surfaces}")
    if schema:
        parts.append(f"schema: {schema}")
    return "; ".join(parts)


def derive_surfaces(paths: list[str], artifacts: dict[str, Any], target: str | None) -> list[str]:
    surfaces: set[str] = set()
    for path in paths:
        lower = path.lower()
        if "cli" in lower or "__main__.py" in lower:
            surfaces.add("cli")
        if "contract" in lower or "openapi" in lower or "api" in lower:
            surfaces.add("contract")
        if "test" in lower or "spec" in lower:
            surfaces.add("testing")
        if "context_pack" in lower or "context-pack" in lower:
            surfaces.add("context-pack")
        if "schema" in lower:
            surfaces.add("schema")
        if "server" in lower or "http" in lower:
            surfaces.add("http-service")
    artifact_text = json.dumps(artifacts, ensure_ascii=False).lower()
    if "service_contract" in artifact_text or "service-contract" in artifact_text:
        surfaces.add("contract")
    if target:
        surfaces.add(target)
    return sorted(surfaces)


def derive_risk_signals(paths: list[str], artifacts: dict[str, Any]) -> list[str]:
    text = " ".join(paths).lower() + " " + json.dumps(artifacts, ensure_ascii=False).lower()
    signals = []
    if any(term in text for term in ("cli", "__main__", "json")):
        signals.append("public-contract")
    if any(term in text for term in ("contract", "openapi", "api")):
        signals.append("contract")
    if any(term in text for term in ("security", "auth", "token", "secret")):
        signals.append("security")
    return sorted(set(signals))


def phase_for_target(target: str) -> str:
    return {
        "ce-work": "implementation",
        "aisee-verify": "verify",
        "ce-code-review": "review",
        "ce-doc-review": "review",
    }.get(target, target)


def load_yaml_file(path: Path) -> tuple[dict[str, Any], str | None]:
    return load_yaml_text(read_text(path), str(path))


def load_yaml_text(text: str, label: str) -> tuple[dict[str, Any], str | None]:
    if not text.strip():
        return {}, None
    if yaml is not None:
        try:
            data = yaml.safe_load(text) or {}
            if not isinstance(data, dict):
                return {}, f"YAML root must be a mapping: {label}"
            return data, None
        except Exception as error:
            return {}, f"invalid YAML in {label}: {error}"
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}, None
    except json.JSONDecodeError as error:
        return {}, f"YAML parser unavailable and JSON parse failed in {label}: {error}"


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def normalize_max_cards(value: Any) -> int:
    try:
        number = int(value)
    except Exception:
        number = DEFAULT_MAX_CARDS
    return max(1, min(number, 10))


def retrieval_config(config: dict[str, Any]) -> dict[str, Any]:
    retrieval = config.get("retrieval")
    return retrieval if isinstance(retrieval, dict) else {}


def config_public(root: Path, config: dict[str, Any], team_root: Path | None) -> dict[str, Any]:
    return {
        "available": bool(config.get("available")),
        "path": config.get("path"),
        "repo": config.get("repo"),
        "ref": config.get("ref"),
        "local_path": rel(root, team_root) if team_root else config.get("local_path"),
        "local_path_exists": bool(team_root and team_root.exists()),
        "packs": config.get("packs", []),
        "retrieval": config.get("retrieval", {}),
    }


def summarize_cards(cards: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(cards),
        "active": sum(1 for card in cards if card.get("metadata", {}).get("status") == "active"),
        "candidate": sum(1 for card in cards if card.get("metadata", {}).get("status") == "candidate"),
        "items": [
            {
                "id": card.get("metadata", {}).get("id"),
                "title": card.get("metadata", {}).get("title"),
                "status": card.get("metadata", {}).get("status"),
                "pack": card.get("pack"),
                "path": card.get("path"),
            }
            for card in cards
        ],
    }


def knowledge_source(config: dict[str, Any]) -> str | None:
    if not config.get("available"):
        return None
    repo = config.get("repo") or config.get("local_path") or "local"
    ref = config.get("ref")
    return f"{repo}@{ref}" if ref else str(repo)


def build_query_command(
    from_change: str | None,
    target: str | None,
    phase: str | None,
    surfaces: list[str],
    schema: str | None,
    stack: str | None,
) -> str:
    if from_change:
        return f"aisee knowledge query --from-change {from_change} --for {target or 'ce-work'} --json"
    parts = ["aisee knowledge query"]
    if phase:
        parts.extend(["--phase", phase])
    for surface in surfaces:
        parts.extend(["--surface", surface])
    if schema:
        parts.extend(["--schema", schema])
    if stack:
        parts.extend(["--stack", stack])
    parts.append("--json")
    return " ".join(parts)


def tokenize(text: str) -> list[str]:
    return [item.lower() for item in TEXT_TOKEN_PATTERN.findall(text)]


def normalize_key(text: str) -> str:
    return "-".join(tokenize(text))


def intersects(left: list[str], right: list[str]) -> bool:
    left_norm = {item.lower() for item in left}
    right_norm = {item.lower() for item in right}
    return bool(left_norm & right_norm)


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")
