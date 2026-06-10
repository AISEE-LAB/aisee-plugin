from __future__ import annotations

from pathlib import Path

from test_memory_config import run_json, write_memory


def test_memory_update_index_rebuilds_markdown_and_cache(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/commit.md", summary="提交信息使用中文。")

    data = run_json(tmp_path, "memory", "update-index", "--json")

    assert data["status"] == "ok"
    assert data["changed"] is True
    assert data["written"] == ["aisee/memory/index.md", "aisee/cache/memory-index.json"]
    assert "不是事实源" in (tmp_path / "aisee" / "memory" / "index.md").read_text(encoding="utf-8")
    assert '"cache_is_fact_source": false' in (tmp_path / "aisee" / "cache" / "memory-index.json").read_text(encoding="utf-8")


def test_memory_search_does_not_depend_on_cache(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/commit.md", summary="提交信息使用中文。")
    run_json(tmp_path, "memory", "update-index", "--json")
    (tmp_path / "aisee" / "cache" / "memory-index.json").unlink()

    data = run_json(tmp_path, "memory", "search", "--query", "commit", "--json")

    assert data["memory"]["matches"][0]["id"] == "commit"
    assert data["meta"]["cache_is_fact_source"] is False
