from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_aisee(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_json(root: Path, *args: str) -> dict:
    result = run_aisee(root, *args)
    return json.loads(result.stdout)


def test_schema_pack_does_not_fall_back_to_packaged_assets(tmp_path: Path) -> None:
    data = run_json(tmp_path, "schemas", "list", "--json")

    assert data["status"] == "ok"
    assert data["schemas"] == []
    assert data["source"] is None
    assert data["issues"][0]["code"] == "SCHEMA_PACK_SOURCE_UNAVAILABLE"
    assert "codex plugin marketplace add" in data["setup_hint"]["commands"][0]


def test_unrelated_project_skills_do_not_shadow_aisee_assets(tmp_path: Path) -> None:
    (tmp_path / "skills" / "custom-skill").mkdir(parents=True)
    (tmp_path / "skills" / "custom-skill" / "SKILL.md").write_text("# Custom\n", encoding="utf-8")

    data = run_json(tmp_path, "schemas", "list", "--json")

    assert data["status"] == "ok"
    assert data["schemas"] == []
    assert data["source"] is None
    assert data["issues"][0]["code"] == "SCHEMA_PACK_SOURCE_UNAVAILABLE"


def test_plugin_inspect_reports_cli_only_without_source_checkout(tmp_path: Path) -> None:
    data = run_json(tmp_path, "plugin", "inspect", "--json")

    assert data["status"] == "ok"
    assert data["mode"] == "cli-only"
    assert data["skills"] == []
    assert data["targets"] == []
    assert data["issues"][0]["code"] == "PLUGIN_CONTENT_UNAVAILABLE"


def test_plugin_export_returns_deprecation_blocker(tmp_path: Path) -> None:
    destination = tmp_path / "exported-plugin"
    data = run_json(tmp_path, "plugin", "export", "--target", "codex", "--dest", str(destination), "--json")

    assert data["status"] == "blocked"
    assert data["meta"]["writes"] is False
    assert data["issues"][0]["code"] == "PLUGIN_EXPORT_DEPRECATED"
    assert not destination.exists()


def test_team_knowledge_scaffold_returns_deprecation_blocker(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"
    data = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--json")

    assert data["status"] == "blocked"
    assert data["meta"]["writes"] is False
    assert data["issues"][0]["code"] == "KNOWLEDGE_SCAFFOLD_DEPRECATED"
    assert not destination.exists()
