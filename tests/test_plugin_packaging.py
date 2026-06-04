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


def test_schema_pack_falls_back_to_packaged_assets(tmp_path: Path) -> None:
    data = run_json(tmp_path, "schemas", "list", "--json")

    names = {schema["name"] for schema in data["schemas"]}
    assert data["status"] == "ok"
    assert "aisee-app-spec-driven" in names
    assert "quick-fix" in names
    assert "src/aisee_plugin_assets" in data["source"]


def test_unrelated_project_skills_do_not_shadow_packaged_assets(tmp_path: Path) -> None:
    (tmp_path / "skills" / "custom-skill").mkdir(parents=True)
    (tmp_path / "skills" / "custom-skill" / "SKILL.md").write_text("# Custom\n", encoding="utf-8")

    data = run_json(tmp_path, "schemas", "list", "--json")

    names = {schema["name"] for schema in data["schemas"]}
    assert data["status"] == "ok"
    assert "aisee-app-spec-driven" in names
    assert "src/aisee_plugin_assets" in data["source"]


def test_plugin_inspect_lists_packaged_skills_without_source_checkout(tmp_path: Path) -> None:
    data = run_json(tmp_path, "plugin", "inspect", "--json")

    assert data["status"] == "ok"
    assert "aisee-srs" in data["skills"]
    assert "aisee-change-plan" in data["skills"]
    assert {target["target"] for target in data["targets"]} == {"codex", "claude", "cursor"}


def test_plugin_export_writes_codex_bundle(tmp_path: Path) -> None:
    destination = tmp_path / "exported-plugin"
    data = run_json(tmp_path, "plugin", "export", "--target", "codex", "--dest", str(destination), "--json")

    assert data["status"] == "ok"
    assert (destination / ".codex-plugin" / "plugin.json").exists()
    assert (destination / "skills" / "aisee-srs" / "SKILL.md").exists()
    metadata = json.loads((destination / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert metadata["skills"] == "./skills/"
