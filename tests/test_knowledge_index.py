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
