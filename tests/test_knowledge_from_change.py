from __future__ import annotations

from pathlib import Path

from test_context_pack import create_project
from test_knowledge_config import configure_project, create_team_knowledge, run_json


def test_knowledge_query_from_change_extracts_features(tmp_path: Path) -> None:
    create_project(tmp_path)
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)

    data = run_json(tmp_path, "knowledge", "query", "--from-change", "add-auth", "--for", "ce-work", "--json")

    assert data["feature_source"] == "from-change"
    assert data["features"]["change"] == "add-auth"
    assert data["features"]["schema"] == "aisee-app-spec-driven"
    assert "contract" in data["features"]["surfaces"]
    assert any(match["id"] == "http-contract-backward-compatibility" for match in data["knowledge"]["matches"])


def test_context_pack_can_include_knowledge_matches(tmp_path: Path) -> None:
    create_project(tmp_path)
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)

    data = run_json(tmp_path, "context", "pack", "--change", "add-auth", "--for", "ce-work", "--knowledge", "--json")

    assert "knowledge" in data
    assert data["knowledge"]["enabled"] is True
    assert data["knowledge"]["matches"]
    assert "knowledge" not in data["facts"]["parsed"]
    assert "knowledge" not in data["facts"]["derived"]
