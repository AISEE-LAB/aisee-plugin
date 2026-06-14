from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_aisee(
    root: Path,
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_json(root: Path, *args: str, env: dict[str, str] | None = None) -> dict:
    return json.loads(run_aisee(root, *args, env_overrides=env).stdout)


def test_project_local_commands_remain_on_top_level_help(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "--help")

    for command in (
        "doctor",
        "bootstrap",
        "openspec",
        "knowledge",
        "memory",
    ):
        assert command in result.stdout


def test_removed_content_distribution_commands_are_not_public_subcommands(tmp_path: Path) -> None:
    env = {"AISEE_AGENT_RUNTIME": "none"}
    plugin_export = run_aisee(
        tmp_path,
        "plugin",
        "export",
        "--target",
        "codex",
        "--dest",
        str(tmp_path / "bundle"),
        "--json",
        check=False,
        env_overrides=env,
    )
    plugin_path = run_json(tmp_path, "plugin", "path", "--target", "codex", "--json", env=env)
    schema_install = run_aisee(tmp_path, "schemas", "install", "--all", "--json", check=False, env_overrides=env)
    knowledge_scaffold = run_aisee(
        tmp_path,
        "knowledge",
        "scaffold",
        "--dest",
        str(tmp_path / "team"),
        "--json",
        check=False,
        env_overrides=env,
    )

    assert plugin_export.returncode == 2
    assert "invalid choice" in plugin_export.stderr
    assert "export" in plugin_export.stderr
    assert plugin_path["status"] == "blocked"
    assert plugin_path["meta"]["writes"] is False
    assert schema_install.returncode == 2
    assert "invalid choice" in schema_install.stderr
    assert "install" in schema_install.stderr
    assert knowledge_scaffold.returncode == 2
    assert "invalid choice" in knowledge_scaffold.stderr
    assert "scaffold" in knowledge_scaffold.stderr


def test_knowledge_help_shows_init_repo_and_configure(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "knowledge", "--help")

    assert "init-repo" in result.stdout
    assert "configure" in result.stdout


def test_memory_help_shows_public_subcommands(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "memory", "--help")

    for command in ("inspect", "list", "search", "add", "update-index"):
        assert command in result.stdout


def test_schemas_help_shows_format_subcommand(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "schemas", "--help")

    assert "format" in result.stdout


def test_removed_change_and_contract_commands_are_not_public_subcommands(tmp_path: Path) -> None:
    removed_commands = [
        ("contract", "manifest", "--json"),
        ("flow", "inspect", "--json"),
        ("gaps", "--change", "add-auth", "--json"),
        ("change", "author-check", "add-auth", "--json"),
        ("change", "verify-check", "add-auth", "--json"),
        ("change", "archive-check", "add-auth", "--json"),
        ("change", "inspect", "add-auth", "--json"),
        ("sources", "list", "--json"),
        ("sources", "check", "--json"),
        ("index", "--json"),
        ("get", "docs/requirements/auth-srs.md#FR-001", "--json"),
        ("trace", "docs/requirements/auth-srs.md#FR-001", "--json"),
    ]

    for args in removed_commands:
        result = run_aisee(tmp_path, *args, check=False)
        assert result.returncode == 2
        assert "invalid choice" in result.stderr
