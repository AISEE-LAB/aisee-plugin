"""Schema pack inspection and installation helpers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from aisee_cli.assets import resolve_schema_pack_dir
from aisee_cli.context_pack import parse_schema
from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.project import rel


def schema_pack_dir(root: Path) -> Path:
    return resolve_schema_pack_dir(root)


def list_available_schemas(root: Path) -> list[str]:
    base = schema_pack_dir(root)
    if not base.exists():
        return []
    return sorted(path.name for path in base.iterdir() if (path / "schema.yaml").exists())


def list_schema_packs(root: Path) -> dict[str, Any]:
    available = list_available_schemas(root)
    installed_base = root / "openspec" / "schemas"
    schemas = []
    for name in available:
        installed_path = installed_base / name
        schemas.append({
            "name": name,
            "source": rel(root, schema_pack_dir(root) / name),
            "installed": installed_path.exists(),
            "installed_path": rel(root, installed_path),
        })
    issues = [] if available else [issue("SCHEMA_PACK_MISSING", "risk", "schema pack source was not found", rel(root, schema_pack_dir(root)))]
    return {
        "status": status_from_issues(issues),
        "source": rel(root, schema_pack_dir(root)),
        "target": rel(root, installed_base),
        "schemas": schemas,
        "issues": issues,
        "summary": summarize_issues(issues),
    }


def check_schema_packs(root: Path) -> dict[str, Any]:
    listed = list_schema_packs(root)
    issues = list(listed["issues"])
    for item in listed["schemas"]:
        schema_file = schema_pack_dir(root) / item["name"] / "schema.yaml"
        try:
            schema_info = parse_schema(schema_file)
        except Exception as error:
            issues.append(issue("SCHEMA_PARSE_FAILED", "blocker", f"{item['name']} schema failed to parse: {error}", item["source"]))
            continue
        for artifact in schema_info["artifacts"]:
            template = artifact.template
            if template and not (schema_file.parent / "templates" / template).exists():
                issues.append(
                    issue(
                        "SCHEMA_TEMPLATE_MISSING",
                        "blocker",
                        f"{item['name']} artifact {artifact.artifact_id} template is missing: {template}",
                        f"{item['source']}/templates/{template}",
                    )
                )
    return {
        **listed,
        "status": status_from_issues(issues),
        "issues": issues,
        "summary": summarize_issues(issues),
    }


def install_schema_packs(root: Path, selected: list[str], *, force: bool = False) -> dict[str, Any]:
    available = set(list_available_schemas(root))
    names = sorted(available if selected == ["*"] else selected)
    if not names:
        raise ValueError("no schema selected")
    unknown = [name for name in names if name not in available]
    if unknown:
        raise ValueError(f"unknown schema: {', '.join(unknown)}")

    results = []
    for name in names:
        source = schema_pack_dir(root) / name
        target = root / "openspec" / "schemas" / name
        if target.exists() and not force:
            state = "skipped"
        else:
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
            state = "installed"
        results.append({
            "schema": name,
            "state": state,
            "source": rel(root, source),
            "target": rel(root, target),
        })
    return {
        "status": "ok",
        "installed": results,
        "meta": {
            "command": "aisee schemas install --json",
        },
    }
