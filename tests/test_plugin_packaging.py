from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_aisee(
    root: Path,
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    env["HOME"] = str(root / "home")
    env["CODEX_HOME"] = str(root / "home" / ".codex")
    env.pop("AISEE_PLUGIN_ASSET_ROOT", None)
    env.pop("AISEE_AGENT_RUNTIME", None)
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
    result = run_aisee(root, *args, env_overrides=env)
    return json.loads(result.stdout)


def create_plugin_root(path: Path) -> Path:
    (path / "skills" / "aisee-srs").mkdir(parents=True)
    (path / "skills" / "aisee-srs" / "SKILL.md").write_text("# aisee:srs\n", encoding="utf-8")
    (path / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix").mkdir(parents=True)
    (path / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix" / "schema.yaml").write_text(
        "name: quick-fix\nartifacts:\n  - id: problem\n",
        encoding="utf-8",
    )
    (path / "references").mkdir()
    (path / ".codex-plugin").mkdir()
    (path / ".codex-plugin" / "plugin.json").write_text('{"name":"aisee-plugin"}\n', encoding="utf-8")
    return path


def test_schema_pack_does_not_fall_back_to_packaged_assets(tmp_path: Path) -> None:
    data = run_json(tmp_path, "schemas", "list", "--json")

    assert data["status"] == "ok"
    assert data["schemas"] == []
    assert data["source"] is None
    assert data["issues"][0]["code"] == "SCHEMA_PACK_SOURCE_UNAVAILABLE"
    assert "codex plugin marketplace add" in data["setup_hint"]["commands"][0]


def test_schema_pack_uses_default_codex_plugin_runtime(tmp_path: Path) -> None:
    codex_home = tmp_path / "home" / ".codex"
    create_plugin_root(codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin")
    (codex_home / "config.toml").parent.mkdir(parents=True, exist_ok=True)
    (codex_home / "config.toml").write_text(
        """[marketplaces.aisee-plugin]
source = "https://github.com/AISEE-LAB/aisee-plugin.git"

[plugins."aisee-plugin@aisee-plugin"]
enabled = true
""",
        encoding="utf-8",
    )

    data = run_json(tmp_path, "schemas", "list", "--json")

    assert data["source"].endswith(".codex/.tmp/marketplaces/aisee-plugin/plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack")
    assert data["issues"] == []
    assert data["setup_hint"] is None
    assert data["schemas"][0]["name"] == "quick-fix"


def test_agent_runtime_env_limits_asset_discovery(tmp_path: Path) -> None:
    create_plugin_root(tmp_path / "home" / ".codex" / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin")
    create_plugin_root(tmp_path / "home" / ".claude" / "plugins" / "cache" / "aisee-plugin" / "aisee-plugin" / "9.9.9")

    data = run_json(tmp_path, "schemas", "list", "--json", env={"AISEE_AGENT_RUNTIME": "claude"})

    assert data["source"].startswith("home/.claude/plugins/cache/aisee-plugin/aisee-plugin/9.9.9")


def test_agent_runtime_none_disables_installed_asset_discovery(tmp_path: Path) -> None:
    create_plugin_root(tmp_path / "home" / ".codex" / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin")

    data = run_json(tmp_path, "schemas", "list", "--json", env={"AISEE_AGENT_RUNTIME": "none"})

    assert data["source"] is None
    assert data["schemas"] == []
    assert data["issues"][0]["code"] == "SCHEMA_PACK_SOURCE_UNAVAILABLE"


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
