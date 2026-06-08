"""Schema pack inspection and installation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from aisee_cli.assets import resolve_schema_pack_dir
from aisee_cli.context_pack import parse_schema
from aisee_cli.marketplace import marketplace_issue, marketplace_setup_hint
from aisee_cli.output import issue, status_from_issues, summarize_issues
from aisee_cli.project import rel


def schema_pack_dir(root: Path) -> Path:
    return resolve_schema_pack_dir(root)


def maybe_schema_pack_dir(root: Path) -> Path | None:
    try:
        return schema_pack_dir(root)
    except FileNotFoundError:
        return None


def list_available_schemas(root: Path) -> list[str]:
    base = maybe_schema_pack_dir(root)
    if base is None or not base.exists():
        return []
    return sorted(path.name for path in base.iterdir() if (path / "schema.yaml").exists())


def list_schema_packs(root: Path) -> dict[str, Any]:
    source_base = maybe_schema_pack_dir(root)
    available = list_available_schemas(root) if source_base is not None else []
    installed_base = root / "openspec" / "schemas"
    installed = sorted(path.name for path in installed_base.iterdir() if (path / "schema.yaml").exists()) if installed_base.exists() else []
    schemas = []
    for name in sorted(set(available) | set(installed)):
        installed_path = installed_base / name
        schemas.append({
            "name": name,
            "source": rel(root, source_base / name) if source_base is not None and name in available else None,
            "installed": installed_path.exists(),
            "installed_path": rel(root, installed_path),
        })
    issues = []
    if source_base is None:
        issues.append(marketplace_issue(
            "SCHEMA_PACK_SOURCE_UNAVAILABLE",
            "info",
            "Aisee schema packs are provided by the GitHub marketplace plugin, not by the PyPI CLI package.",
        ))
    return {
        "status": status_from_issues(issues),
        "source": rel(root, source_base) if source_base is not None else None,
        "target": rel(root, installed_base),
        "schemas": schemas,
        "issues": issues,
        "summary": summarize_issues(issues),
        "setup_hint": marketplace_setup_hint() if source_base is None else None,
    }


def check_schema_packs(root: Path) -> dict[str, Any]:
    listed = list_schema_packs(root)
    issues = list(listed["issues"])
    for item in listed["schemas"]:
        schema_dir_label = item["installed_path"] if item["installed"] else item["source"]
        if schema_dir_label is None:
            continue
        schema_dir = root / schema_dir_label
        schema_file = schema_dir / "schema.yaml"
        try:
            validate_schema_yaml(schema_file)
            schema_info = parse_schema(schema_file)
        except Exception as error:
            issues.append(issue("SCHEMA_PARSE_FAILED", "blocker", f"{item['name']} schema failed to parse: {error}", schema_dir_label))
            continue
        for artifact in schema_info["artifacts"]:
            template = artifact.template
            if template and not (schema_file.parent / "templates" / template).exists():
                issues.append(
                    issue(
                        "SCHEMA_TEMPLATE_MISSING",
                        "blocker",
                        f"{item['name']} artifact {artifact.artifact_id} template is missing: {template}",
                        f"{schema_dir_label}/templates/{template}",
                    )
                )
    return {
        **listed,
        "status": status_from_issues(issues),
        "issues": issues,
        "summary": summarize_issues(issues),
    }


def validate_schema_yaml(schema_file: Path) -> None:
    data = yaml.safe_load(schema_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("schema.yaml must be a YAML mapping")
    if not data.get("name"):
        raise ValueError("schema.yaml is missing name")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("schema.yaml must define artifacts")


def install_schema_packs(root: Path, selected: list[str], *, force: bool = False) -> dict[str, Any]:
    issues = [marketplace_issue(
        "SCHEMA_INSTALL_DEPRECATED",
        "blocker",
        "aisee schemas install no longer installs schema packs from the PyPI package; install the Aisee plugin from the Codex marketplace and use the plugin workflow.",
    )]
    return {
        "status": "blocked",
        "installed": [],
        "selected": selected,
        "target": rel(root, root / "openspec" / "schemas"),
        "issues": issues,
        "summary": summarize_issues(issues),
        "setup_hint": marketplace_setup_hint(),
        "meta": {
            "command": "aisee schemas install --json",
            "writes": False,
            "deprecated": True,
            "force": force,
        },
    }
