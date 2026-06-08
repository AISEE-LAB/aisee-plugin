from __future__ import annotations

from test_knowledge_config import configure_project, create_team_knowledge, run_json


def test_knowledge_index_writes_rebuildable_cache(tmp_path):
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)

    data = run_json(tmp_path, "knowledge", "index", "--json")

    assert data["status"] == "ok"
    assert data["meta"]["cache_is_fact_source"] is False
    assert data["index"]["path"] == "aisee/cache/knowledge-index.json"
    assert (tmp_path / "aisee" / "cache" / "knowledge-index.json").exists()
    ids = {item["id"] for item in data["cards"]}
    assert "cli-json-output-stability" in ids


def test_knowledge_index_can_write_team_scope_cache(tmp_path):
    team = create_team_knowledge(tmp_path)

    data = run_json(tmp_path, "knowledge", "index", "--team-path", str(team), "--json")

    assert data["status"] == "ok"
    assert data["meta"]["cache_is_fact_source"] is False
    assert data["index"]["scope"] == "team"
    assert data["index"]["path"].endswith("indexes/lexical-index.json")
    assert (team / "indexes" / "lexical-index.json").exists()
    ids = {item["id"] for item in data["cards"]}
    assert "cli-json-output-stability" in ids


def test_knowledge_index_does_not_create_missing_team_path(tmp_path):
    missing = tmp_path / "missing-team"

    data = run_json(tmp_path, "knowledge", "index", "--team-path", str(missing), "--json")

    assert data["status"] == "blocked"
    assert not missing.exists()
