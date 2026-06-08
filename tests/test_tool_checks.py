from __future__ import annotations

import os
from pathlib import Path

from aisee_cli.tool_checks import check_codex_aisee_marketplace, check_compound_plugin, check_openspec_cli


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_openspec_cli_check_reports_version(tmp_path: Path, monkeypatch) -> None:
    bin_dir = tmp_path / "bin"
    openspec = bin_dir / "openspec"
    write(openspec, "#!/bin/sh\nprintf '1.2.3\\n'\n")
    openspec.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")

    result = check_openspec_cli()

    assert result["available"] is True
    assert result["version"] == "1.2.3"
    assert result["status"] == "ok"


def test_compound_plugin_check_reports_required_skills(tmp_path: Path, monkeypatch) -> None:
    skills_dir = tmp_path / "compound" / "skills"
    for skill in ("ce-plan", "ce-doc-review", "ce-work", "ce-code-review"):
        write(skills_dir / skill / "SKILL.md", f"# {skill}\n")
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(skills_dir))

    result = check_compound_plugin()

    assert result["plugin_available"] is True
    assert result["status"] == "ok"
    assert all(result["skills"].values())


def test_compound_plugin_check_reports_partial_install(tmp_path: Path, monkeypatch) -> None:
    skills_dir = tmp_path / "compound" / "skills"
    write(skills_dir / "ce-work" / "SKILL.md", "# ce-work\n")
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(skills_dir))

    result = check_compound_plugin()

    assert result["plugin_available"] is True
    assert result["status"] == "partial"
    assert "ce-plan" in result["missing_skills"]


def test_codex_marketplace_check_reports_ok_from_config(tmp_path: Path, monkeypatch) -> None:
    codex_home = tmp_path / "codex-home"
    write(
        codex_home / "config.toml",
        """[marketplaces.aisee]
source = "AISEE-LAB/aisee-plugin"

[plugins."aisee-plugin@aisee"]
enabled = true
""",
    )
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    result = check_codex_aisee_marketplace()

    assert result["status"] == "ok"
    assert result["marketplace_configured"] is True
    assert result["plugin_enabled"] is True


def test_codex_marketplace_check_reports_missing_from_config(tmp_path: Path, monkeypatch) -> None:
    codex_home = tmp_path / "codex-home"
    write(codex_home / "config.toml", "[marketplaces.other]\nsource = \"other/repo\"\n")
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    result = check_codex_aisee_marketplace()

    assert result["status"] == "missing"
    assert result["setup_hint"]["writes_codex_state"] is False
    assert "codex plugin marketplace add" in result["setup_hint"]["commands"][0]


def test_codex_marketplace_check_reports_unknown_without_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "missing-codex-home"))

    result = check_codex_aisee_marketplace()

    assert result["status"] == "unknown"
    assert result["reason"] == "config-missing"
