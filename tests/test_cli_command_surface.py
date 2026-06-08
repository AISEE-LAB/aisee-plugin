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
        "sources",
        "change",
        "context",
        "knowledge",
        "contract",
        "id",
        "flow",
        "gaps",
        "trace",
        "get",
    ):
        assert command in result.stdout


def test_public_content_distribution_commands_return_json_blockers(tmp_path: Path) -> None:
    env = {"AISEE_AGENT_RUNTIME": "none"}
    plugin_export = run_json(tmp_path, "plugin", "export", "--target", "codex", "--dest", str(tmp_path / "bundle"), "--json", env=env)
    plugin_path = run_json(tmp_path, "plugin", "path", "--target", "codex", "--json", env=env)
    schema_install = run_json(tmp_path, "schemas", "install", "--all", "--json", env=env)
    knowledge_scaffold = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(tmp_path / "team"), "--json", env=env)

    assert plugin_export["status"] == "blocked"
    assert plugin_path["status"] == "blocked"
    assert schema_install["status"] == "blocked"
    assert knowledge_scaffold["status"] == "blocked"
    assert plugin_export["meta"]["writes"] is False
    assert plugin_path["meta"]["writes"] is False
    assert schema_install["meta"]["writes"] is False
    assert knowledge_scaffold["meta"]["writes"] is False
