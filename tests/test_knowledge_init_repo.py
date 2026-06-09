from __future__ import annotations

from pathlib import Path

from test_knowledge_config import run_json, write


def assert_base_result_shape(data: dict) -> None:
    assert set(data) >= {"schema_version", "status", "issues", "summary", "meta"}
    assert set(data["summary"]) == {"blocker", "risk", "info", "total"}


def test_knowledge_init_repo_creates_contract_valid_team_repo(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"

    data = run_json(tmp_path, "knowledge", "init-repo", "--dest", str(destination), "--json")

    assert_base_result_shape(data)
    assert data["status"] == "ok"
    assert data["meta"]["writes"] is True
    assert data["meta"]["command"].endswith("--json")
    assert len(data["next_commands"]) == 2
    assert (destination / ".aisee-team-knowledge").exists()
    assert (destination / "knowledge" / "packs" / "web-app.yaml").exists()
    assert (destination / "knowledge" / "cards" / "cli" / "cli-json-output-stability.md").exists()


def test_knowledge_init_repo_rejects_non_empty_destination_without_force(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"
    destination.mkdir()
    write(destination / "keep.txt", "keep")

    data = run_json(tmp_path, "knowledge", "init-repo", "--dest", str(destination), "--json")

    assert_base_result_shape(data)
    assert data["status"] == "blocked"
    assert data["issues"][0]["code"] == "KNOWLEDGE_DEST_NOT_EMPTY"
    assert data["meta"]["writes"] is False
    assert not (destination / ".aisee-team-knowledge").exists()
    assert (destination / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_knowledge_init_repo_allows_empty_existing_directory(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"
    destination.mkdir()

    data = run_json(tmp_path, "knowledge", "init-repo", "--dest", str(destination), "--initial-pack", "openspec", "--json")

    assert data["status"] == "ok"
    assert data["team_knowledge"]["initial_pack"] == "openspec"
    assert (destination / "knowledge" / "packs" / "openspec.yaml").exists()


def test_knowledge_init_repo_rejects_invalid_initial_pack(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"

    data = run_json(tmp_path, "knowledge", "init-repo", "--dest", str(destination), "--initial-pack", "bad-pack", "--json")

    assert_base_result_shape(data)
    assert data["status"] == "blocked"
    assert "KNOWLEDGE_PACK_INVALID" in {item["code"] for item in data["issues"]}
    assert not destination.exists()


def test_knowledge_init_repo_force_merges_managed_files(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"
    destination.mkdir()
    write(destination / "keep.txt", "keep")

    data = run_json(tmp_path, "knowledge", "init-repo", "--dest", str(destination), "--force", "--json")

    assert data["status"] == "ok"
    assert data["meta"]["force"] is True
    assert (destination / "keep.txt").read_text(encoding="utf-8") == "keep"
