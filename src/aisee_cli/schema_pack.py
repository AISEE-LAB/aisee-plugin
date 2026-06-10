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
        for schema_issue in schema_info.get("issues", []):
            issues.append(
                issue(
                    str(schema_issue.get("code") or "SCHEMA_ISSUE"),
                    str(schema_issue.get("severity") or "risk"),
                    str(schema_issue.get("message") or "schema issue"),
                    f"{schema_dir_label}/schema.yaml",
                )
            )
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
    if "capabilities" not in data:
        raise ValueError("schema.yaml must define capabilities")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("schema.yaml must define artifacts")


def format_schema_packs(root: Path, *, check: bool = False, write: bool = False) -> dict[str, Any]:
    listed = list_schema_packs(root)
    issues = list(listed["issues"])
    drifted: list[dict[str, Any]] = []
    written: list[str] = []
    for item in listed["schemas"]:
        schema_dir_label = item["installed_path"] if item["installed"] else item["source"]
        if schema_dir_label is None:
            continue
        schema_file = root / schema_dir_label / "schema.yaml"
        try:
            original = schema_file.read_text(encoding="utf-8")
            data = yaml.safe_load(original)
            if not isinstance(data, dict):
                raise ValueError("schema.yaml must be a YAML mapping")
            canonical = dump_schema_yaml(canonicalize_schema_yaml(data))
        except Exception as error:
            issues.append(issue("SCHEMA_FORMAT_FAILED", "blocker", f"{item['name']} schema could not be formatted: {error}", f"{schema_dir_label}/schema.yaml"))
            continue
        if original != canonical:
            drifted.append({"name": item["name"], "path": f"{schema_dir_label}/schema.yaml"})
            if write:
                schema_file.write_text(canonical, encoding="utf-8")
                written.append(f"{schema_dir_label}/schema.yaml")
    if check and drifted:
        for item in drifted:
            issues.append(issue("SCHEMA_FORMAT_DRIFT", "risk", f"{item['name']} schema.yaml is not in canonical format", item["path"]))
    return {
        **listed,
        "status": status_from_issues(issues),
        "issues": issues,
        "summary": summarize_issues(issues),
        "drifted": drifted,
        "written": written,
        "meta": {
            "command": "aisee schemas format --json",
            "writes": write,
            "check": check,
        },
    }


def canonicalize_schema_yaml(data: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for key in ("name", "version", "description", "capabilities"):
        if key in data:
            canonical[key] = data[key]
    artifacts = data.get("artifacts")
    if isinstance(artifacts, list):
        canonical["artifacts"] = [canonicalize_artifact_yaml(item) for item in artifacts if isinstance(item, dict)]
    for key in ("apply", "archive"):
        if isinstance(data.get(key), dict):
            canonical[key] = canonicalize_block_yaml(data[key])
    for key, value in data.items():
        if key not in canonical:
            canonical[key] = value
    return canonical


def canonicalize_artifact_yaml(data: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    ordered_keys = (
        "id",
        "generates",
        "description",
        "template",
        "requires",
        "requiredness",
        "na_requires_reason",
        "capabilities",
        "role",
        "instruction",
    )
    for key in ordered_keys:
        if key in data:
            canonical[key] = data[key]
    for key, value in data.items():
        if key not in canonical:
            canonical[key] = value
    return canonical


def canonicalize_block_yaml(data: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for key in ("requires", "tracks", "instruction"):
        if key in data:
            canonical[key] = data[key]
    for key, value in data.items():
        if key not in canonical:
            canonical[key] = value
    return canonical


def dump_schema_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120).rstrip() + "\n"


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
