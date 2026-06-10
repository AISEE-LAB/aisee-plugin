"""Schema pack inspection and installation helpers."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from aisee_cli import __version__
from aisee_cli.assets import read_asset_version, resolve_schema_pack_dir, resolve_source_asset_root
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
    source_root = resolve_source_asset_root(root)
    source_base = maybe_schema_pack_dir(root)
    source_version = read_asset_version(source_root)
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
    elif source_version and source_version != __version__:
        issues.append(
            issue(
                "SCHEMA_PACK_VERSION_MISMATCH",
                "risk",
                f"CLI version {__version__} does not match resolved plugin content version {source_version}",
                rel(root, source_root / ".codex-plugin" / "plugin.json") if source_root else None,
            )
        )
    return {
        "status": status_from_issues(issues),
        "source": rel(root, source_base) if source_base is not None else None,
        "source_version": source_version,
        "cli_version": __version__,
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
        issues.extend(inspect_schema_structure(schema_file, schema_dir_label, schema_info))
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


def inspect_schema_structure(schema_file: Path, schema_dir_label: str, schema_info: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    schema_ids = [artifact.artifact_id for artifact in schema_info["artifacts"]]
    duplicate_ids = sorted(artifact_id for artifact_id, count in Counter(schema_ids).items() if count > 1)
    for artifact_id in duplicate_ids:
        issues.append(
            issue(
                "SCHEMA_ARTIFACT_DUPLICATE",
                "blocker",
                f"schema defines duplicate artifact id: {artifact_id}",
                f"{schema_dir_label}/schema.yaml",
            )
        )

    raw_data = yaml.safe_load(schema_file.read_text(encoding="utf-8")) or {}
    if not isinstance(raw_data.get("version"), int):
        issues.append(issue("SCHEMA_VERSION_MISSING", "blocker", "schema.yaml must define integer version", f"{schema_dir_label}/schema.yaml"))
    if not str(raw_data.get("description") or "").strip():
        issues.append(issue("SCHEMA_DESCRIPTION_MISSING", "blocker", "schema.yaml must define description", f"{schema_dir_label}/schema.yaml"))

    known_ids = set(schema_ids)
    ordered_ids: list[str] = []
    for artifact in schema_info["artifacts"]:
        artifact_id = artifact.artifact_id
        if "/" in (artifact.template or "") or "\\" in (artifact.template or ""):
            issues.append(
                issue(
                    "SCHEMA_TEMPLATE_PATH_INVALID",
                    "blocker",
                    f"{artifact_id} template must be a file name under templates/, not a nested path",
                    f"{schema_dir_label}/schema.yaml",
                )
            )
        late_requires = []
        for requirement in artifact.requires:
            if requirement not in known_ids:
                issues.append(
                    issue(
                        "SCHEMA_REQUIRES_UNKNOWN",
                        "blocker",
                        f"{artifact_id} requires unknown artifact {requirement}",
                        f"{schema_dir_label}/schema.yaml",
                    )
                )
            elif requirement not in ordered_ids:
                late_requires.append(requirement)
        if late_requires:
            issues.append(
                issue(
                    "SCHEMA_DAG_ORDER",
                    "risk",
                    f"{artifact_id} requires artifacts that appear later or itself: {', '.join(late_requires)}",
                    f"{schema_dir_label}/schema.yaml",
                )
            )
        ordered_ids.append(artifact_id)

    cycle = first_cycle(schema_info)
    if cycle:
        issues.append(
            issue(
                "SCHEMA_DAG_CYCLE",
                "blocker",
                f"schema artifact dependencies contain a cycle: {' -> '.join(cycle)}",
                f"{schema_dir_label}/schema.yaml",
            )
        )
    return issues


def first_cycle(schema_info: dict[str, Any]) -> list[str]:
    graph = {
        artifact.artifact_id: list(artifact.requires)
        for artifact in schema_info["artifacts"]
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def walk(node: str) -> list[str]:
        if node in visiting:
            index = stack.index(node)
            return [*stack[index:], node]
        if node in visited:
            return []
        visiting.add(node)
        stack.append(node)
        for requirement in graph.get(node, []):
            if requirement not in graph:
                continue
            if cycle := walk(requirement):
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for node in graph:
        if cycle := walk(node):
            return cycle
    return []


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
