from __future__ import annotations

from pathlib import Path

from test_knowledge_config import run_aisee, run_json


def test_knowledge_scaffold_writes_packaged_team_repo(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"

    data = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--json")

    assert data["status"] == "ok"
    assert data["meta"]["writes"] is True
    assert (destination / "knowledge" / "packs" / "web-app.yaml").exists()
    assert (destination / "schemas" / "knowledge-card.schema.json").exists()

    check = run_json(tmp_path, "knowledge", "check", "--team-path", str(destination), "--json")
    assert check["status"] == "ok"
    assert {item["id"] for item in check["cards"]["items"]} >= {
        "cli-json-output-stability",
        "openspec-source-map-is-routing",
    }


def test_knowledge_scaffold_update_config_writes_matching_path(tmp_path: Path) -> None:
    destination = tmp_path / ".aisee" / "team-knowledge"

    data = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--update-config", "--pack", "openspec", "--json")

    assert data["status"] == "ok"
    assert data["config_update"]["changed"] is True
    config = (tmp_path / "aisee" / "knowledge.yaml").read_text(encoding="utf-8")
    assert "path: .aisee/team-knowledge" in config
    assert "openspec" in config
    doctor = run_json(tmp_path, "knowledge", "doctor", "--json")
    assert doctor["status"] == "ok"
    assert doctor["team_knowledge"]["configured_path"] == ".aisee/team-knowledge"


def test_knowledge_scaffold_refuses_existing_destination_without_force(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"
    destination.mkdir()

    result = run_aisee(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--json", check=False)

    assert result.returncode == 2
    assert "destination already exists" in result.stderr


def test_knowledge_scaffold_force_rebuilds_destination(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"
    run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--json")
    (destination / "old.txt").write_text("old", encoding="utf-8")

    data = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--force", "--json")

    assert data["status"] == "ok"
    assert not (destination / "old.txt").exists()
    assert (destination / "README.md").exists()


def test_knowledge_scaffold_force_refuses_non_scaffold_directory(tmp_path: Path) -> None:
    destination = tmp_path / "ordinary"
    destination.mkdir()
    (destination / "keep.txt").write_text("keep", encoding="utf-8")

    result = run_aisee(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--force", "--json", check=False)

    assert result.returncode == 2
    assert "refusing to overwrite non-scaffold directory" in result.stderr
    assert (destination / "keep.txt").exists()


def test_knowledge_scaffold_force_refuses_project_root(tmp_path: Path) -> None:
    (tmp_path / ".aisee-team-knowledge").write_text("marker", encoding="utf-8")

    result = run_aisee(tmp_path, "knowledge", "scaffold", "--dest", str(tmp_path), "--force", "--json", check=False)

    assert result.returncode == 2
    assert "refusing to overwrite protected path" in result.stderr
