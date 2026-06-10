from __future__ import annotations

from pathlib import Path

from test_memory_config import run_json, write_memory


def test_memory_search_returns_metadata_only_by_default(tmp_path: Path) -> None:
    write_memory(
        tmp_path,
        "aisee/memory/pref/commit-style.md",
        priority="high",
        summary="提交信息使用中文。",
        body="这里是较长正文，不应该默认返回。",
    )

    data = run_json(tmp_path, "memory", "search", "--query", "commit style", "--json")

    assert data["memory"]["matches"][0]["id"] == "commit-style"
    assert data["memory"]["matches"][0]["type"] == "pref"
    assert "body_excerpt" not in data["memory"]["matches"][0]
    assert data["meta"]["writes"] is False


def test_memory_search_include_body_returns_bounded_excerpt(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/commit-style.md", body="commit style " + ("A" * 1000))

    data = run_json(tmp_path, "memory", "search", "--query", "commit", "--include-body", "--json")

    assert "body_excerpt" in data["memory"]["matches"][0]
    assert len(data["memory"]["matches"][0]["body_excerpt"]) <= 800
    assert data["meta"]["full_body_read"] is True


def test_memory_search_excludes_stale_and_deprecated_by_default(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/active.md", summary="commit active")
    write_memory(tmp_path, "aisee/memory/pref/stale.md", status="stale", summary="commit stale")
    write_memory(tmp_path, "aisee/memory/pref/deprecated.md", status="deprecated", summary="commit deprecated")

    data = run_json(tmp_path, "memory", "search", "--query", "commit", "--json")
    included = {entry["id"] for entry in data["memory"]["matches"]}

    assert included == {"active"}

    with_stale = run_json(tmp_path, "memory", "search", "--query", "commit", "--include-stale", "--include-deprecated", "--json")
    assert {entry["id"] for entry in with_stale["memory"]["matches"]} == {"active", "deprecated", "stale"}


def test_memory_search_caps_limit_and_reports_conflicts(tmp_path: Path) -> None:
    for index in range(30):
        write_memory(tmp_path, f"aisee/memory/pref/item-{index}.md", title=f"偏好 {index}", summary="commit preference")
    write_memory(tmp_path, "aisee/memory/pref/conflict-a.md", title="重复偏好", summary="commit conflict a")
    write_memory(tmp_path, "aisee/memory/pref/conflict-b.md", title="重复偏好", summary="commit conflict b")

    data = run_json(tmp_path, "memory", "search", "--query", "commit", "--limit", "100", "--json")

    assert len(data["memory"]["matches"]) == 20
    assert data["memory"]["conflicts"]
    assert data["meta"]["command"].endswith("--limit 20 --json")
