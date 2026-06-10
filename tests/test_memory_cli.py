from __future__ import annotations

from pathlib import Path

from test_memory_config import run_aisee, run_json, write_memory


def test_memory_list_filters_active_entries_by_default(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/commit.md", priority="high")
    write_memory(tmp_path, "aisee/memory/pref/stale.md", status="stale", summary="过期偏好")
    write_memory(tmp_path, "aisee/memory/stack/python.md", memory_type="stack", summary="Python 版本约束")

    data = run_json(tmp_path, "memory", "list", "--type", "pref", "--json")

    assert data["status"] == "ok"
    assert [entry["id"] for entry in data["entries"]] == ["commit"]
    assert data["entries"][0]["priority"] == "high"
    assert "body_excerpt" not in data["entries"][0]


def test_memory_list_include_body_returns_bounded_excerpt(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/commit.md", body="A" * 1000)

    data = run_json(tmp_path, "memory", "list", "--include-body", "--json")

    assert len(data["entries"][0]["body_excerpt"]) <= 800
    assert data["meta"]["full_body_read"] is True


def test_memory_add_writes_canonical_file_and_updates_index(tmp_path: Path) -> None:
    data = run_json(
        tmp_path,
        "memory",
        "add",
        "--type",
        "pref",
        "--title",
        "提交信息语言",
        "--summary",
        "提交信息必须使用中文。",
        "--body",
        "本项目 commit message 默认使用中文，并遵循当前 AGENTS.md。",
        "--source-ref",
        "AGENTS.md",
        "--priority",
        "high",
        "--json",
    )

    assert data["status"] == "ok"
    assert data["changed"] is True
    assert data["meta"]["writes"] is True
    assert any(path.startswith("aisee/memory/pref/memory-") for path in data["written"])
    assert "aisee/memory/index.md" in data["written"]
    assert "aisee/cache/memory-index.json" in data["written"]

    list_data = run_json(tmp_path, "memory", "list", "--json")
    assert list_data["entries"][0]["title"] == "提交信息语言"
    assert list_data["entries"][0]["summary"] == "提交信息必须使用中文。"


def test_memory_add_rejects_unsupported_type(tmp_path: Path) -> None:
    data = run_json(
        tmp_path,
        "memory",
        "add",
        "--type",
        "global",
        "--title",
        "Bad",
        "--summary",
        "Bad",
        "--body",
        "Bad",
        "--json",
    )

    assert data["status"] == "blocked"
    assert data["changed"] is False
    assert data["meta"]["writes"] is False
    assert "MEMORY_TYPE_INVALID" in {item["code"] for item in data["issues"]}


def test_memory_missing_subcommand_returns_json_error(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "memory", "--json", check=False)

    assert result.returncode == 2
    assert "MISSING_SUBCOMMAND" in result.stderr
