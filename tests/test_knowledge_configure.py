from __future__ import annotations

from pathlib import Path

import yaml

from test_knowledge_config import create_team_knowledge, run_json, write


def assert_configure_result_shape(data: dict) -> None:
    assert set(data) >= {"schema_version", "status", "config", "written", "issues", "summary", "next_commands", "meta"}
    assert set(data["summary"]) == {"blocker", "risk", "info", "total"}


def test_knowledge_configure_writes_path_only_config(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)

    data = run_json(
        tmp_path,
        "knowledge",
        "configure",
        "--path",
        str(team),
        "--enable-pack",
        "web-app",
        "--json",
    )

    payload = yaml.safe_load((tmp_path / "aisee" / "knowledge.yaml").read_text(encoding="utf-8"))
    assert_configure_result_shape(data)
    assert data["status"] == "ok"
    assert data["meta"]["writes"] is True
    assert data["config"]["local_path_exists"] is True
    assert data["meta"]["command"].endswith("--json")
    assert payload["path"] == ".aisee/team-knowledge"
    assert payload["packs"] == ["web-app"]


def test_knowledge_configure_supports_repo_ref_and_dedupes_enabled_packs(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)

    data = run_json(
        tmp_path,
        "knowledge",
        "configure",
        "--path",
        str(team),
        "--repo",
        "git@example.com:org/aisee-team-knowledge.git",
        "--ref",
        "main",
        "--enable-pack",
        "web-app",
        "--enable-pack",
        "web-app",
        "--enable-pack",
        "openspec",
        "--max-cards",
        "5",
        "--include-project-candidates",
        "false",
        "--json",
    )

    assert_configure_result_shape(data)
    assert data["status"] == "ok"
    inspect = run_json(tmp_path, "knowledge", "inspect", "--json")
    assert inspect["config"]["repo"] == "git@example.com:org/aisee-team-knowledge.git"
    assert inspect["config"]["ref"] == "main"
    assert inspect["config"]["packs"] == ["web-app", "openspec"]
    assert inspect["config"]["retrieval"]["max_cards"] == 5
    assert inspect["config"]["retrieval"]["include_project_candidates"] is False


def test_knowledge_configure_preserves_untouched_fields(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        """repo: git@example.com:org/aisee-team-knowledge.git
path: old/path
ref: v1
packs:
  - openspec
retrieval:
  max_cards: 4
  include_project_candidates: true
  vector: required
""",
    )

    run_json(tmp_path, "knowledge", "configure", "--path", str(team), "--enable-pack", "web-app", "--json")

    payload = yaml.safe_load((tmp_path / "aisee" / "knowledge.yaml").read_text(encoding="utf-8"))
    assert payload["repo"] == "git@example.com:org/aisee-team-knowledge.git"
    assert payload["ref"] == "v1"
    assert payload["packs"] == ["openspec", "web-app"]
    assert payload["retrieval"]["vector"] == "required"


def test_knowledge_configure_allows_doctor_to_pass_for_valid_local_team_repo(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(team / ".aisee-team-knowledge", "marker\n")

    run_json(tmp_path, "knowledge", "configure", "--path", str(team), "--enable-pack", "web-app", "--json")
    data = run_json(tmp_path, "knowledge", "doctor", "--json")

    assert data["status"] == "ok"


def test_knowledge_configure_rejects_missing_path_without_repo(tmp_path: Path) -> None:
    missing = tmp_path / "missing-team"

    data = run_json(
        tmp_path,
        "knowledge",
        "configure",
        "--path",
        str(missing),
        "--enable-pack",
        "web-app",
        "--json",
    )

    assert_configure_result_shape(data)
    assert data["status"] == "blocked"
    assert "KNOWLEDGE_REPO_MISSING" in {item["code"] for item in data["issues"]}
    assert not (tmp_path / "aisee" / "knowledge.yaml").exists()


def test_knowledge_configure_allows_missing_path_when_repo_is_provided(tmp_path: Path) -> None:
    missing = tmp_path / "future-checkout"

    data = run_json(
        tmp_path,
        "knowledge",
        "configure",
        "--path",
        str(missing),
        "--repo",
        "git@example.com:org/aisee-team-knowledge.git",
        "--enable-pack",
        "web-app",
        "--json",
    )

    assert data["status"] == "ok"
    assert data["config"]["local_path_exists"] is False
    assert data["config"]["repo"] == "git@example.com:org/aisee-team-knowledge.git"


def test_knowledge_configure_rejects_existing_path_without_marker(tmp_path: Path) -> None:
    team = tmp_path / "team-without-marker"
    write(team / "knowledge" / "packs" / "web-app.yaml", "id: web-app\nversion: 0.1.0\nstatus: active\ncards: []\n")
    write(team / "knowledge" / "cards" / "cli" / "dummy.md", "---\nid: dummy\ntitle: dummy\nstatus: active\napplies_to:\n  phases: [implementation]\ntrigger: [dummy]\nrecommended_action: [dummy]\nboundaries: [dummy]\n---\n")

    data = run_json(
        tmp_path,
        "knowledge",
        "configure",
        "--path",
        str(team),
        "--enable-pack",
        "web-app",
        "--json",
    )

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_SCAFFOLD_MARKER_MISSING" in {item["code"] for item in data["issues"]}
