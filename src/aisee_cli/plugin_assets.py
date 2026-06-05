"""Plugin asset inspection and export helpers."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from aisee_cli.assets import packaged_asset_root, resolve_asset_root, resolve_plugin_metadata
from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.project import rel

TARGETS = ("codex", "claude", "cursor")


def inspect_plugin_assets(root: Path) -> dict[str, Any]:
    asset_root = resolve_asset_root(root)
    packaged_root = packaged_asset_root()
    skills_dir = asset_root / "skills"
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
        "asset_root": rel(root, asset_root),
        "packaged_asset_root": rel(root, packaged_root),
        "skills_dir": rel(root, skills_dir),
        "skills": skills,
        "targets": targets,
        "issues": issues,
        "summary": summarize_issues(issues),
    }


def export_plugin_assets(root: Path, target: str, dest: Path, *, force: bool = False) -> dict[str, Any]:
    if target not in TARGETS:
        raise ValueError(f"unsupported plugin target: {target}")
    asset_root = resolve_asset_root(root)
    skills_dir = asset_root / "skills"
    if not skills_dir.exists():
        raise ValueError("plugin skills directory was not found")
    metadata = resolve_plugin_metadata(target, root)

    if dest.exists():
        if not force:
            raise ValueError(f"destination already exists: {dest}")
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    shutil.copytree(skills_dir, dest / "skills")
    references_dir = asset_root / "references"
    if references_dir.exists():
        shutil.copytree(references_dir, dest / "references")
    plugin_dir_name = {
        "codex": ".codex-plugin",
        "claude": ".claude-plugin",
        "cursor": ".cursor-plugin",
    }[target]
    plugin_dir = dest / plugin_dir_name
    plugin_dir.mkdir(parents=True, exist_ok=True)

    metadata_data = json.loads(metadata.read_text(encoding="utf-8"))
    if target == "codex":
        metadata_data["skills"] = "./skills/"
    (plugin_dir / "plugin.json").write_text(
        json.dumps(metadata_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "status": "ok",
        "target": target,
        "destination": rel(root, dest),
        "metadata": rel(root, plugin_dir / "plugin.json"),
        "skills": rel(root, dest / "skills"),
        "meta": {
            "command": f"aisee plugin export --target {target} --dest {dest} --json",
            "writes": True,
        },
    }


def plugin_path(root: Path, target: str) -> dict[str, Any]:
    if target not in TARGETS:
        raise ValueError(f"unsupported plugin target: {target}")
    asset_root = resolve_asset_root(root)
    metadata = resolve_plugin_metadata(target, root)
    return {
        "status": "ok",
        "target": target,
        "asset_root": rel(root, asset_root),
        "metadata": rel(root, metadata),
        "skills": rel(root, asset_root / "skills"),
    }
