from __future__ import annotations

from pathlib import Path

from test_knowledge_config import run_json


def test_knowledge_scaffold_returns_stable_blocker_without_writes(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"

    data = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--json")

    assert data["status"] == "blocked"
    assert data["destination"] == "team-knowledge"
    assert data["written"] == []
    assert data["config_update"] is None
    assert data["meta"]["writes"] is False
    assert data["meta"]["deprecated"] is True
    assert data["issues"][0]["code"] == "KNOWLEDGE_SCAFFOLD_DEPRECATED"
    assert "codex plugin marketplace add" in data["setup_hint"]["commands"][0]
    assert not destination.exists()


def test_knowledge_scaffold_does_not_overwrite_existing_paths(tmp_path: Path) -> None:
    destination = tmp_path / "ordinary"
    destination.mkdir()
    (destination / "keep.txt").write_text("keep", encoding="utf-8")

    data = run_json(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--force", "--json")

    assert data["status"] == "blocked"
    assert data["meta"]["writes"] is False
    assert (destination / "keep.txt").read_text(encoding="utf-8") == "keep"
