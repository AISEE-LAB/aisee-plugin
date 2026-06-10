"""Plugin asset inspection and export helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.assets import read_asset_version, resolve_asset_root, resolve_plugin_metadata
from aisee_cli.marketplace import marketplace_issue, marketplace_setup_hint
from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.project import rel

TARGETS = ("codex", "claude", "cursor")


def inspect_plugin_assets(root: Path) -> dict[str, Any]:
    try:
        asset_root = resolve_asset_root(root)
    except FileNotFoundError:
        issues = [marketplace_issue(
            "PLUGIN_CONTENT_UNAVAILABLE",
            "info",
            "Aisee plugin content is provided by the GitHub marketplace plugin, not by the PyPI CLI package.",
        )]
        return {
            "status": "ok",
            "mode": "cli-only",
            "asset_root": None,
            "skills_dir": None,
            "skills": [],
            "targets": [],
            "issues": issues,
            "summary": summarize_issues(issues),
            "setup_hint": marketplace_setup_hint(),
            "meta": {
                "command": "aisee plugin inspect --json",
                "writes": False,
            },
        }
    skills_dir = asset_root / "skills"
    asset_version = read_asset_version(asset_root)
    issues = []
    if not skills_dir.exists():
        issues.append(issue("PLUGIN_SKILLS_MISSING", "blocker", "plugin skills directory was not found", rel(root, skills_dir)))

    targets = []
    for target in TARGETS:
        try:
            metadata = resolve_plugin_metadata(target, root)
            metadata_state = "present"
            metadata_path = rel(root, metadata)
        except ValueError:
            metadata_state = "missing"
            metadata_path = ""
            issues.append(issue("PLUGIN_METADATA_MISSING", "risk", f"{target} plugin metadata was not found", target))
        targets.append({
            "target": target,
            "metadata": metadata_state,
            "metadata_path": metadata_path,
        })

    skills = sorted(path.parent.name for path in skills_dir.glob("*/SKILL.md")) if skills_dir.exists() else []
    return {
        "status": status_from_issues(issues),
        "mode": "source-checkout",
        "asset_root": rel(root, asset_root),
        "asset_version": asset_version,
        "skills_dir": rel(root, skills_dir),
        "skills": skills,
        "targets": targets,
        "issues": issues,
        "summary": summarize_issues(issues),
    }


def plugin_path(root: Path, target: str) -> dict[str, Any]:
    if target not in TARGETS:
        raise ValueError(f"unsupported plugin target: {target}")
    try:
        asset_root = resolve_asset_root(root)
        metadata = resolve_plugin_metadata(target, root)
    except FileNotFoundError:
        issues = [marketplace_issue(
            "PLUGIN_PATH_DEPRECATED",
            "blocker",
            "aisee plugin path no longer resolves plugin content from the PyPI package; Codex manages installed plugin paths.",
        )]
        return {
            "status": "blocked",
            "target": target,
            "asset_root": None,
            "metadata": None,
            "skills": None,
            "issues": issues,
            "summary": summarize_issues(issues),
            "setup_hint": marketplace_setup_hint(),
            "meta": {
                "command": f"aisee plugin path --target {target} --json",
                "writes": False,
                "deprecated": True,
            },
        }
    return {
        "status": "ok",
        "mode": "source-checkout",
        "target": target,
        "asset_root": rel(root, asset_root),
        "asset_version": read_asset_version(asset_root),
        "metadata": rel(root, metadata),
        "skills": rel(root, asset_root / "skills"),
    }
