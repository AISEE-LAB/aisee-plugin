"""Team knowledge guardrail retrieval for Aisee CLI."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from aisee_cli.assets import packaged_asset_root
from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.paths import knowledge_config_path, knowledge_index_path
from aisee_cli.project import rel


KNOWLEDGE_SCHEMA_VERSION = "1.0"
DEFAULT_MAX_CARDS = 3
CARD_REQUIRED_FIELDS = ("id", "title", "status", "applies_to", "trigger", "recommended_action", "boundaries")
CARD_STATUSES = {"candidate", "active", "deprecated"}
TEXT_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_:+.-]+|[\u4e00-\u9fff]+")
TEAM_KNOWLEDGE_ASSET_DIR = "team-knowledge"
SCAFFOLD_MARKER = ".aisee-team-knowledge"


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
    pack_results, team_cards, load_issues = load_configured_knowledge(root, config, team_root, include_body=debug)
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


def build_knowledge_index(root: Path, *, write_cache: bool = True, team_path: str | None = None) -> dict[str, Any]:
    if team_path:
        return build_team_knowledge_index(root, Path(team_path), write_cache=write_cache)

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


def build_team_knowledge_index(root: Path, team_path: Path, *, write_cache: bool = True) -> dict[str, Any]:
    team_root = resolve_user_path(root, team_path)
    packs, cards, issues = load_team_knowledge_repository(root, team_root, include_body=False)
    documents = card_index_documents(cards, team_root)
    path = team_root / "indexes" / "lexical-index.json"
    result = {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "index": {
            "path": rel(root, path),
            "scope": "team",
            "writes": write_cache,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "team_knowledge": {
            "path": rel(root, team_root),
            "exists": team_root.exists(),
        },
        "packs": packs,
        "cards": documents,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": f"aisee knowledge index --team-path {team_path} --json",
            "cache_is_fact_source": False,
        },
    }
    if write_cache and not any(item.get("severity") == "blocker" for item in issues):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def build_knowledge_check(root: Path, *, team_path: str | None = None) -> dict[str, Any]:
    config, config_issues = load_knowledge_config(root)
    if team_path:
        team_root = resolve_user_path(root, Path(team_path))
        packs, cards, issues = load_team_knowledge_repository(root, team_root)
        config_payload = None
        command = f"aisee knowledge check --team-path {team_path} --json"
    else:
        team_root = resolve_team_root(root, config)
        packs, cards, issues = load_configured_knowledge(root, config, team_root)
        issues = config_issues + issues
        config_payload = config_public(root, config, team_root)
        command = "aisee knowledge check --json"
        if not config.get("available"):
            issues.append(issue("KNOWLEDGE_CONFIG_MISSING", "risk", "aisee/knowledge.yaml was not found", rel(root, knowledge_config_path(root))))
    return {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "config": config_payload,
        "team_knowledge": {
            "path": rel(root, team_root) if team_root else None,
            "exists": bool(team_root and team_root.exists()),
        },
        "packs": packs,
        "cards": summarize_cards(cards),
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": command,
            "cache_is_fact_source": False,
        },
    }


def build_knowledge_scaffold(root: Path, dest: str, *, force: bool = False) -> dict[str, Any]:
    destination = resolve_user_path(root, Path(dest))
    source = packaged_asset_root() / TEAM_KNOWLEDGE_ASSET_DIR
    if not source.exists():
        raise ValueError("packaged team knowledge scaffold was not found")
    if destination.exists():
        if not force:
            raise ValueError(f"destination already exists: {destination}")
        ensure_safe_scaffold_force(root, destination)
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    written = sorted(rel(root, path) for path in destination.rglob("*") if path.is_file())
    check = build_knowledge_check(root, team_path=str(destination))
    return {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": check["status"],
        "destination": rel(root, destination),
        "source": rel(root, source),
        "written": written,
        "issues": check["issues"],
        "summary": check["summary"],
        "meta": {
            "command": f"aisee knowledge scaffold --dest {dest} --json",
            "writes": True,
            "force": force,
        },
    }


def build_knowledge_install(root: Path, *, allow_dirty: bool = False) -> dict[str, Any]:
    config, issues = load_knowledge_config(root)
    team_root = resolve_team_root(root, config)
    if not config.get("available"):
        issues.append(issue("KNOWLEDGE_CONFIG_MISSING", "blocker", "aisee/knowledge.yaml was not found", rel(root, knowledge_config_path(root))))
    if not config.get("repo"):
        issues.append(issue("KNOWLEDGE_REPO_MISSING", "blocker", "aisee/knowledge.yaml does not declare repo", config.get("path") or rel(root, knowledge_config_path(root))))
    if team_root is None:
        issues.append(issue("KNOWLEDGE_PATH_MISSING", "blocker", "aisee/knowledge.yaml does not declare path", config.get("path") or rel(root, knowledge_config_path(root))))
    if issues:
        return knowledge_git_result(root, "install", config, team_root, False, issues, None)
    assert team_root is not None
    if team_root.exists():
        if (team_root / ".git").exists():
            dirty_issue = ensure_clean_git_worktree(root, team_root, allow_dirty)
            if dirty_issue:
                return knowledge_git_result(root, "install", config, team_root, False, [dirty_issue], None)
            return knowledge_git_result(root, "install", config, team_root, False, [], "already-installed")
        return knowledge_git_result(root, "install", config, team_root, False, [
            issue("KNOWLEDGE_PATH_EXISTS", "blocker", f"configured path already exists and is not a Git checkout: {team_root}", rel(root, team_root))
        ], None)
    command = ["git", "clone", str(config["repo"]), str(team_root)]
    result = run_git_command(command, root)
    clone_issues = git_issues(root, result, rel(root, team_root))
    if not clone_issues and config.get("ref"):
        checkout = run_git_command(["git", "checkout", str(config["ref"])], team_root)
        clone_issues.extend(git_issues(root, checkout, rel(root, team_root)))
        if clone_issues and team_root.exists():
            shutil.rmtree(team_root)
    return knowledge_git_result(root, "install", config, team_root, not clone_issues, clone_issues, "cloned" if not clone_issues else None)


def build_knowledge_update(root: Path, *, allow_dirty: bool = False) -> dict[str, Any]:
    config, issues = load_knowledge_config(root)
    team_root = resolve_team_root(root, config)
    if not config.get("available"):
        issues.append(issue("KNOWLEDGE_CONFIG_MISSING", "blocker", "aisee/knowledge.yaml was not found", rel(root, knowledge_config_path(root))))
    if team_root is None:
        issues.append(issue("KNOWLEDGE_PATH_MISSING", "blocker", "aisee/knowledge.yaml does not declare path", config.get("path") or rel(root, knowledge_config_path(root))))
    elif not (team_root / ".git").exists():
        issues.append(issue("KNOWLEDGE_REPO_MISSING", "blocker", f"configured team knowledge path is not a Git checkout: {team_root}", rel(root, team_root)))
    if issues:
        return knowledge_git_result(root, "update", config, team_root, False, issues, None)
    assert team_root is not None
    dirty_issue = ensure_clean_git_worktree(root, team_root, allow_dirty)
    if dirty_issue:
        return knowledge_git_result(root, "update", config, team_root, False, [dirty_issue], None)
    before = git_head(team_root)
    update_issues: list[dict[str, str]] = []
    fetch = run_git_command(["git", "fetch", "origin"], team_root)
    update_issues.extend(git_issues(root, fetch, rel(root, team_root)))
    if not update_issues and config.get("ref"):
        checkout_target = str(config["ref"])
        remote_branch = f"origin/{checkout_target}"
        if git_ref_exists(team_root, remote_branch):
            checkout = run_git_command(["git", "checkout", "-B", checkout_target, remote_branch], team_root)
        else:
            checkout = run_git_command(["git", "checkout", checkout_target], team_root)
        update_issues.extend(git_issues(root, checkout, rel(root, team_root)))
    after = git_head(team_root)
    changed = bool(not update_issues and before and after and before != after)
    return knowledge_git_result(root, "update", config, team_root, changed, update_issues, "updated" if not update_issues else None)


def build_knowledge_promote_batch(
    root: Path,
    *,
    curation: str,
    team_path: str,
    pack_id: str | None = None,
    category: str = "general",
    activate: bool = False,
) -> dict[str, Any]:
    curation_path = resolve_user_path(root, Path(curation))
    team_root = resolve_user_path(root, Path(team_path))
    issues: list[dict[str, str]] = []
    if not curation_path.exists():
        issues.append(issue("KNOWLEDGE_CURATION_MISSING", "blocker", f"curation file does not exist: {curation}", rel(root, curation_path)))
    if not team_root.exists():
        issues.append(issue("KNOWLEDGE_REPO_MISSING", "blocker", f"team knowledge path does not exist: {team_path}", rel(root, team_root)))
    if pack_id:
        try:
            pack_path = pack_path_for_id(team_root, pack_id)
        except ValueError as error:
            issues.append(issue("KNOWLEDGE_PACK_INVALID", "blocker", str(error), rel(root, team_root / "knowledge" / "packs")))
            pack_path = team_root / "knowledge" / "packs" / f"{pack_id}.yaml"
        if not pack_path.exists():
            issues.append(issue("KNOWLEDGE_PACK_MISSING", "blocker", f"knowledge pack was not found: {pack_id}", rel(root, pack_path)))
    if issues:
        return promote_result(root, curation_path, team_root, [], False, issues)
    try:
        category_id = safe_category(category)
    except ValueError as error:
        issues.append(issue("KNOWLEDGE_CATEGORY_INVALID", "blocker", str(error), rel(root, team_root / "knowledge" / "cards")))
        return promote_result(root, curation_path, team_root, [], False, issues)

    drafts = extract_card_drafts(read_text(curation_path))
    if not drafts:
        issues.append(issue("KNOWLEDGE_DRAFTS_MISSING", "blocker", "no card drafts were found in curation file", rel(root, curation_path)))
        return promote_result(root, curation_path, team_root, [], False, issues)

    prepared: list[dict[str, Any]] = []
    seen_draft_ids: set[str] = set()
    for draft in drafts:
        metadata = dict(draft)
        if activate:
            metadata["status"] = "active"
        metadata.setdefault("status", "candidate")
        card_issues = validate_card_metadata(root, metadata, rel(root, curation_path))
        if card_issues:
            issues.extend({**item, "severity": "blocker"} for item in card_issues)
            continue
        card_id = str(metadata["id"])
        if card_id in seen_draft_ids:
            issues.append(issue("KNOWLEDGE_CARD_DUPLICATE", "blocker", f"duplicate draft card id: {card_id}", rel(root, curation_path)))
            continue
        seen_draft_ids.add(card_id)
        prepared.append(metadata)
    if issues:
        return promote_result(root, curation_path, team_root, [], False, issues)

    targets: list[tuple[dict[str, Any], Path, str]] = []
    pack_data: dict[str, Any] | None = None
    pack_path: Path | None = None
    if pack_id:
        pack_path = pack_path_for_id(team_root, pack_id)
        pack_data, pack_error = load_yaml_file(pack_path)
        if pack_error:
            issues.append(issue("KNOWLEDGE_PACK_INVALID", "blocker", pack_error, rel(root, pack_path)))
    registry = build_card_registry(root, team_root)
    for metadata in prepared:
        card_id = str(metadata["id"])
        card_path = team_root / "knowledge" / "cards" / category_id / f"{card_id}.md"
        rendered = render_card_markdown(metadata)
        existing = registry["by_id"].get(card_id)
        existing_path = existing["path_abs"] if existing else None
        if existing_path is not None and existing_path != card_path:
            issues.append(issue("KNOWLEDGE_CARD_DUPLICATE", "blocker", f"card id already exists at another path: {card_id}", rel(root, existing_path)))
            continue
        if card_path.exists() and read_text(card_path) != rendered:
            issues.append(issue("KNOWLEDGE_CARD_EXISTS", "blocker", f"card already exists and would not be overwritten: {card_path}", rel(root, card_path)))
            continue
        targets.append((metadata, card_path, rendered))
    if issues:
        return promote_result(root, curation_path, team_root, [], False, issues)

    written: list[str] = []
    for metadata, card_path, rendered in targets:
        card_id = str(metadata["id"])
        card_path.parent.mkdir(parents=True, exist_ok=True)
        if not card_path.exists():
            card_path.write_text(rendered, encoding="utf-8")
            written.append(rel(root, card_path))
        if pack_id and pack_path is not None and pack_data is not None:
            changed = add_card_to_pack_data(pack_data, card_id)
            if changed:
                written.append(rel(root, pack_path))
    if pack_id and pack_path is not None and pack_data is not None and rel(root, pack_path) in written:
        pack_path.write_text(yaml.safe_dump(pack_data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return promote_result(root, curation_path, team_root, sorted(set(written)), bool(written) and not issues, issues)


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


def resolve_user_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def resolve_team_root(root: Path, config: dict[str, Any]) -> Path | None:
    local_path = config.get("local_path")
    if not local_path:
        return None
    candidate = Path(str(local_path))
    return candidate if candidate.is_absolute() else root / candidate


def load_team_knowledge_repository(
    root: Path,
    team_root: Path,
    *,
    include_body: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    if not team_root.exists():
        return [], [], [issue("KNOWLEDGE_REPO_MISSING", "blocker", f"team knowledge path does not exist: {team_root}", rel(root, team_root))]
    packs_dir = team_root / "knowledge" / "packs"
    if not packs_dir.exists():
        return [], [], [issue("KNOWLEDGE_PACKS_MISSING", "blocker", "knowledge/packs directory was not found", rel(root, packs_dir))]
    pack_ids = sorted(path.stem for path in packs_dir.glob("*.yaml"))
    if not pack_ids:
        issues.append(issue("KNOWLEDGE_PACKS_MISSING", "risk", "no knowledge packs were found", rel(root, packs_dir)))
    config = {
        "available": True,
        "path": None,
        "local_path": str(team_root),
        "packs": pack_ids,
        "retrieval": {"max_cards": DEFAULT_MAX_CARDS, "include_project_candidates": False},
    }
    packs, cards, load_issues = load_configured_knowledge(root, config, team_root, include_body=include_body)
    issues.extend(load_issues)
    return packs, cards, issues


def card_index_documents(cards: list[dict[str, Any]], team_root: Path | None) -> list[dict[str, Any]]:
    documents = []
    for card in cards:
        metadata = card.get("metadata", {})
        source_path = card.get("path")
        text = read_text((team_root / source_path) if source_path and team_root else Path(""))
        documents.append({
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "status": metadata.get("status"),
            "deprecated_by": metadata.get("deprecated_by"),
            "path": source_path,
            "pack": card.get("pack"),
            "tokens": sorted(tokens_for_card(metadata)),
            "hash": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None,
        })
    return documents


def load_configured_knowledge(
    root: Path,
    config: dict[str, Any],
    team_root: Path | None,
    *,
    include_body: bool = False,
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

    registry = build_card_registry(root, team_root, include_body=include_body)
    issues.extend(registry["issues"])
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
        issues.extend(validate_pack_data(pack_id, pack_data, rel(root, pack_path)))
        pack_cards, card_issues = load_pack_cards(root, team_root, pack_id, pack_data, registry=registry)
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


def load_pack_cards(
    root: Path,
    team_root: Path,
    pack_id: str,
    pack_data: dict[str, Any],
    *,
    registry: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    registry = registry or build_card_registry(root, team_root)
    disabled = set(normalize_string_list(pack_data.get("disabled_cards")))
    declared_paths: set[Path] = set()
    cards_by_id = {item for item in normalize_string_list(pack_data.get("cards"))}
    for card_id in cards_by_id:
        if card_id in disabled:
            continue
        found = registry["by_id"].get(card_id)
        if found is None:
            issues.append(issue("KNOWLEDGE_CARD_MISSING", "risk", f"pack references missing card: {card_id}", pack_id))
            continue
        declared_paths.add(found["path_abs"])
    for pattern in normalize_string_list(pack_data.get("card_globs")):
        pattern_path = Path(pattern)
        if pattern_path.is_absolute() or ".." in pattern_path.parts:
            issues.append(issue("KNOWLEDGE_PACK_INVALID", "risk", f"card_globs must be relative and stay under team root: {pattern}", pack_id))
            continue
        try:
            paths = sorted(team_root.glob(pattern))
        except (NotImplementedError, ValueError) as error:
            issues.append(issue("KNOWLEDGE_PACK_INVALID", "risk", f"invalid card_globs pattern {pattern}: {error}", pack_id))
            continue
        for path in paths:
            if path.is_file() and is_under(path, team_root):
                declared_paths.add(path)

    cards: list[dict[str, Any]] = []
    for path in sorted(declared_paths):
        record = registry["by_path"].get(path.resolve())
        if record is None:
            continue
        metadata = record["metadata"]
        card_id = str(metadata.get("id") or "")
        if not card_id or card_id in disabled:
            continue
        cards.append({
            "pack": pack_id,
            "path": rel(team_root, path),
            "metadata": metadata,
            "body": record.get("body", ""),
        })
    return cards, issues


def build_card_registry(root: Path, team_root: Path, *, include_body: bool = False) -> dict[str, Any]:
    cards_dir = team_root / "knowledge" / "cards"
    by_id: dict[str, dict[str, Any]] = {}
    by_path: dict[Path, dict[str, Any]] = {}
    metadata_by_id: dict[str, dict[str, Any]] = {}
    seen: dict[str, str] = {}
    issues: list[dict[str, str]] = []
    if not cards_dir.exists():
        return {
            "by_id": by_id,
            "by_path": by_path,
            "issues": [issue("KNOWLEDGE_CARDS_MISSING", "risk", "knowledge/cards directory was not found", rel(root, cards_dir))],
        }
    for path in sorted(cards_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml"}:
            continue
        metadata, body, parse_error = load_card(path, include_body=include_body)
        path_label = rel(root, path)
        if parse_error:
            issues.append(issue("KNOWLEDGE_CARD_INVALID", "risk", parse_error, path_label))
            continue
        metadata_issues = validate_card_metadata(root, metadata, path_label)
        issues.extend(metadata_issues)
        if metadata_issues:
            continue
        card_id = str(metadata.get("id") or "")
        if not card_id:
            continue
        record = {
            "path_abs": path,
            "path": rel(team_root, path),
            "metadata": metadata,
            "body": body,
        }
        by_path[path.resolve()] = record
        if card_id in seen and seen[card_id] != path_label:
            issues.append(issue("KNOWLEDGE_CARD_DUPLICATE", "blocker", f"duplicate card id: {card_id}", path_label))
            continue
        seen[card_id] = path_label
        by_id[card_id] = record
        metadata_by_id[card_id] = metadata
    for card_id, metadata in metadata_by_id.items():
        for replacement in normalize_string_list(metadata.get("deprecated_by")):
            if replacement not in metadata_by_id:
                issues.append(issue("KNOWLEDGE_CARD_REPLACEMENT_MISSING", "risk", f"{card_id} references missing replacement card: {replacement}", seen.get(card_id, "")))
            elif metadata_by_id[replacement].get("status") == "deprecated":
                issues.append(issue("KNOWLEDGE_CARD_REPLACEMENT_DEPRECATED", "risk", f"{card_id} replacement is also deprecated: {replacement}", seen.get(card_id, "")))
    return {"by_id": by_id, "by_path": by_path, "issues": issues}


def validate_pack_data(pack_id: str, pack_data: dict[str, Any], path_label: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not pack_data.get("version"):
        issues.append(issue("KNOWLEDGE_PACK_VERSION_MISSING", "risk", "pack missing required field: version", path_label))
    if not pack_data.get("status"):
        issues.append(issue("KNOWLEDGE_PACK_STATUS_MISSING", "risk", "pack missing required field: status", path_label))
    if str(pack_data.get("id") or pack_id) != pack_id:
        issues.append(issue("KNOWLEDGE_PACK_ID_MISMATCH", "risk", f"pack id does not match filename: {pack_data.get('id')} != {pack_id}", path_label))
    status = str(pack_data.get("status") or "active")
    if status not in {"active", "deprecated"}:
        issues.append(issue("KNOWLEDGE_PACK_STATUS_INVALID", "risk", f"pack has invalid status: {status}", path_label))
    for field in ("cards", "card_globs", "disabled_cards"):
        value = pack_data.get(field)
        if value is not None and not isinstance(value, list):
            issues.append(issue("KNOWLEDGE_PACK_FIELD_INVALID", "risk", f"{field} must be a list", path_label))
    return issues


def validate_card_metadata(root: Path, metadata: dict[str, Any], path_label: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    missing = [field for field in CARD_REQUIRED_FIELDS if not metadata.get(field)]
    if missing:
        issues.append(issue("KNOWLEDGE_CARD_FIELDS_MISSING", "risk", f"card missing required fields: {', '.join(missing)}", path_label))
        return issues
    card_id = str(metadata.get("id") or "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", card_id):
        issues.append(issue("KNOWLEDGE_CARD_ID_INVALID", "risk", f"card id must be kebab-case: {card_id}", path_label))
    status = str(metadata.get("status") or "")
    if status not in CARD_STATUSES:
        issues.append(issue("KNOWLEDGE_CARD_STATUS_INVALID", "risk", f"card has invalid status: {status}", path_label))
    applies = metadata.get("applies_to")
    if not isinstance(applies, dict):
        issues.append(issue("KNOWLEDGE_CARD_APPLIES_TO_INVALID", "risk", "applies_to must be a mapping", path_label))
    else:
        for field in ("stacks", "frameworks", "phases", "schemas", "surfaces"):
            value = applies.get(field)
            if value is not None and not isinstance(value, list):
                issues.append(issue("KNOWLEDGE_CARD_APPLIES_TO_INVALID", "risk", f"applies_to.{field} must be a list", path_label))
    for field in ("trigger", "recommended_action", "boundaries"):
        value = metadata.get(field)
        if not isinstance(value, list) or not normalize_string_list(value):
            issues.append(issue("KNOWLEDGE_CARD_FIELD_INVALID", "risk", f"{field} must be a non-empty list", path_label))
    if metadata.get("deprecated_by") is not None and not isinstance(metadata.get("deprecated_by"), list):
        issues.append(issue("KNOWLEDGE_CARD_FIELD_INVALID", "risk", "deprecated_by must be a list", path_label))
    if status == "deprecated" and not metadata.get("deprecated_by"):
        issues.append(issue("KNOWLEDGE_CARD_DEPRECATED_BY_MISSING", "risk", "deprecated card should declare deprecated_by", path_label))
    return issues


def validate_card_uniqueness(root: Path, cards: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: dict[str, str] = {}
    issues: list[dict[str, str]] = []
    for card in cards:
        metadata = card.get("metadata", {})
        card_id = str(metadata.get("id") or "")
        if not card_id:
            continue
        card_path = str(card.get("path") or "")
        if card_id in seen and seen[card_id] != card_path:
            issues.append(issue("KNOWLEDGE_CARD_DUPLICATE", "blocker", f"duplicate card id: {card_id}", card_path))
        seen[card_id] = card_path
    return issues


def load_card(path: Path, *, include_body: bool = False) -> tuple[dict[str, Any], str, str | None]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        data, error = load_yaml_text(read_text(path), str(path))
        return (data if isinstance(data, dict) else {}), "", error
    if include_body:
        frontmatter, body = split_frontmatter(read_text(path), include_body=True)
    else:
        frontmatter, body = read_frontmatter(path), ""
    if not frontmatter:
        return {}, body, f"card has no YAML frontmatter: {path}"
    data, error = load_yaml_text(frontmatter, str(path))
    return (data if isinstance(data, dict) else {}), body, error


def read_frontmatter(path: Path) -> str:
    try:
        with path.open(encoding="utf-8", errors="ignore") as file:
            first_line = file.readline()
            if first_line.strip() != "---":
                return ""
            collected: list[str] = []
            for line in file:
                if line.strip() == "---":
                    return "".join(collected).strip()
                collected.append(line)
    except OSError:
        return ""
    return ""


def split_frontmatter(text: str, *, include_body: bool = False) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body = "".join(lines[index + 1 :]).lstrip() if include_body else ""
            return "".join(lines[1:index]).strip(), body
    return "", text


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
    direct_features = {
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
        return direct_features

    features = {
        "phase": None,
        "phases": [],
        "surfaces": [],
        "schema": None,
        "schemas": [],
        "stack": None,
        "stacks": [],
        "query": query or "",
        "risk_signals": [],
        "paths": [],
        "change": from_change,
        "target": target,
        "hints": {
            "phase": phase,
            "surfaces": normalize_string_list(surfaces),
            "schema": schema,
            "stack": stack,
        },
    }

    from aisee_cli.context_pack import build_context_pack

    pack = build_context_pack(root, from_change, target or "ce-work")
    derived = pack["facts"]["derived"]
    parsed = pack["facts"]["parsed"]
    paths = sorted(set(derived.get("code_paths", []) + derived.get("test_paths", [])))
    surfaces_from_paths = derive_surfaces(paths, parsed.get("artifacts", {}), target)
    schema_name = pack["change"].get("schema")
    phase_name = phase_for_target(target or "ce-work")
    features.update({
        "phase": phase_name,
        "phases": [phase_name],
        "schema": schema_name,
        "schemas": [schema_name] if schema_name else [],
        "surfaces": surfaces_from_paths,
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
    try:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            return {}, f"YAML root must be a mapping: {label}"
        return data, None
    except Exception as error:
        return {}, f"invalid YAML in {label}: {error}"


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


def run_git_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError as error:
        return subprocess.CompletedProcess(command, 127, "", str(error))


def git_head(cwd: Path) -> str | None:
    result = run_git_command(["git", "rev-parse", "HEAD"], cwd)
    return result.stdout.strip() if result.returncode == 0 else None


def git_ref_exists(cwd: Path, ref: str) -> bool:
    result = run_git_command(["git", "rev-parse", "--verify", ref], cwd)
    return result.returncode == 0


def git_issues(root: Path, result: subprocess.CompletedProcess[str], path_label: str) -> list[dict[str, str]]:
    if result.returncode == 0:
        return []
    message = (result.stderr or result.stdout or "git command failed").strip()
    return [issue("KNOWLEDGE_GIT_FAILED", "blocker", message, path_label)]


def ensure_clean_git_worktree(root: Path, team_root: Path, allow_dirty: bool) -> dict[str, str] | None:
    if allow_dirty:
        return None
    result = run_git_command(["git", "status", "--porcelain"], team_root)
    git_issue = git_issues(root, result, rel(root, team_root))
    if git_issue:
        return git_issue[0]
    if result.stdout.strip():
        return issue("KNOWLEDGE_REPO_DIRTY", "blocker", "team knowledge checkout has uncommitted changes", rel(root, team_root))
    return None


def ensure_safe_scaffold_force(root: Path, destination: Path) -> None:
    if destination.is_symlink():
        raise ValueError(f"refusing to overwrite symlink path: {destination}")
    resolved = destination.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"refusing to overwrite scaffold outside project root: {destination}") from error
    protected = {
        root.resolve(),
        Path.home().resolve(),
        packaged_asset_root().resolve(),
        (packaged_asset_root() / TEAM_KNOWLEDGE_ASSET_DIR).resolve(),
    }
    if resolved in protected or resolved.parent == resolved:
        raise ValueError(f"refusing to overwrite protected path: {destination}")
    marker = destination / SCAFFOLD_MARKER
    if not marker.exists():
        raise ValueError(f"refusing to overwrite non-scaffold directory: {destination}")


def knowledge_git_result(
    root: Path,
    action: str,
    config: dict[str, Any],
    team_root: Path | None,
    changed: bool,
    issues: list[dict[str, str]],
    result: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "action": action,
        "result": result,
        "changed": changed,
        "config": config_public(root, config, team_root),
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": f"aisee knowledge {action} --json",
            "writes": changed,
        },
    }


def extract_card_drafts(text: str) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []
    for block in extract_all_fenced_yaml(text):
        data, _error = load_yaml_text(block, "curation draft")
        if not isinstance(data, dict):
            continue
        if data.get("id") and any(field in data for field in CARD_REQUIRED_FIELDS):
            drafts.append(data)
    return drafts


def extract_all_fenced_yaml(text: str) -> list[str]:
    blocks: list[str] = []
    in_fence = False
    collected: list[str] = []
    for line in text.splitlines():
        if line.strip() in {"```yaml", "```yml"}:
            in_fence = True
            collected = []
            continue
        if line.strip() == "```" and in_fence:
            blocks.append("\n".join(collected).strip())
            in_fence = False
            collected = []
            continue
        if in_fence:
            collected.append(line)
    return [block for block in blocks if block]


def safe_category(category: str) -> str:
    value = category.strip().lower().replace("_", "-")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
        raise ValueError(f"invalid category: {category}")
    return value


def safe_pack_id(pack_id: str) -> str:
    value = pack_id.strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
        raise ValueError(f"invalid pack id: {pack_id}")
    return value


def pack_path_for_id(team_root: Path, pack_id: str) -> Path:
    safe_id = safe_pack_id(pack_id)
    packs_dir = team_root / "knowledge" / "packs"
    path = packs_dir / f"{safe_id}.yaml"
    try:
        path.resolve().relative_to(packs_dir.resolve())
    except ValueError as error:
        raise ValueError(f"pack path escapes knowledge/packs: {pack_id}") from error
    return path


def render_card_markdown(metadata: dict[str, Any]) -> str:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n\n## Guardrail\n\n待团队 review 后补充说明。\n"


def add_card_to_pack_data(data: dict[str, Any], card_id: str) -> bool:
    cards = normalize_string_list(data.get("cards"))
    if card_id in cards:
        return False
    cards.append(card_id)
    data["cards"] = cards
    return True


def promote_result(
    root: Path,
    curation_path: Path,
    team_root: Path,
    written: list[str],
    changed: bool,
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": KNOWLEDGE_SCHEMA_VERSION,
        "status": status_from_issues(issues),
        "curation": rel(root, curation_path),
        "team_knowledge": rel(root, team_root),
        "written": written,
        "changed": changed,
        "git_actions": False,
        "issues": issues,
        "summary": summarize_issues(issues),
        "meta": {
            "command": "aisee knowledge promote-batch --json",
            "writes": changed,
            "git_actions": False,
        },
    }


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")
