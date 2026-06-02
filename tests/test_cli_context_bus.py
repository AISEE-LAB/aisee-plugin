from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_aisee(root: Path, *args: str) -> dict:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    result = subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def create_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(
        root / ".aisee" / "id-registry.json",
        json.dumps(
            {
                "version": 1,
                "scopes": {
                    "auth": {
                        "counters": {"FR": 1, "PAGE": 1},
                        "ids": {
                            "auth:FR-001": {
                                "type": "FR",
                                "number": 1,
                                "status": "active",
                                "title": "用户登录",
                                "owner": "docs/requirements/auth-srs.md",
                            },
                            "auth:PAGE-001": {
                                "type": "PAGE",
                                "number": 1,
                                "status": "active",
                                "title": "登录页",
                                "owner": "docs/ui-content/auth-ui.md",
                            },
                        },
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    write(
        root / "docs" / "requirements" / "auth-srs.md",
        """# Auth SRS

## 登录

覆盖需求：auth:FR-001
关联页面：auth:PAGE-001
""",
    )
    write(
        root / "docs" / "ui-content" / "auth-ui.md",
        """# Auth UI

## 登录页

页面 ID：auth:PAGE-001
覆盖需求：auth:FR-001
""",
    )
    write(
        root / "openspec" / "changes" / "add-auth" / "source-map.md",
        "| FR | auth:FR-001 | 登录 | docs/requirements/auth-srs.md | 覆盖 | src/auth/session.py / tests/auth/test_session.py |\n",
    )


def test_sources_add_and_check(tmp_path: Path) -> None:
    create_project(tmp_path)

    added = run_aisee(
        tmp_path,
        "sources",
        "add",
        "--scope",
        "auth",
        "--type",
        "srs",
        "--path",
        "docs/requirements/auth-srs.md",
        "--template",
        "aisee-srs",
        "--parser",
        "srs",
        "--json",
    )
    checked = run_aisee(tmp_path, "sources", "check", "--json")

    assert added["status"] == "ok"
    assert added["changed"] is True
    assert checked["status"] == "ok"
    assert checked["sources"][0]["path"] == "docs/requirements/auth-srs.md"
    assert (tmp_path / "aisee" / "registry" / "sources.json").exists()


def test_index_writes_rebuildable_cache(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_aisee(tmp_path, "index", "--json")

    assert data["status"] == "ok"
    assert data["index"]["writes"] is True
    assert data["project_rules"]["primary"] == "AGENTS.md"
    assert "auth:FR-001" in data["ids"]
    assert any(item["path"] == "docs/requirements/auth-srs.md" for item in data["documents"])
    cache = tmp_path / "aisee" / "cache" / "context-index.json"
    assert cache.exists()
    cached = json.loads(cache.read_text(encoding="utf-8"))
    assert cached["meta"]["cache_is_fact_source"] is False


def test_get_returns_registry_source_and_relations(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_aisee(tmp_path, "get", "auth:FR-001", "--json")

    assert data["status"] == "linked"
    assert data["registry"]["entry"]["title"] == "用户登录"
    assert data["source"]["path"] == "docs/requirements/auth-srs.md"
    assert data["source"]["heading"]["title"] == "登录"
    assert data["relations"]["changes"] == ["add-auth"]
    assert data["relations"]["ids"] == ["auth:PAGE-001"]
    assert data["relations"]["code_paths"] == ["src/auth/session.py"]
    assert data["relations"]["test_paths"] == ["tests/auth/test_session.py"]
    assert data["meta"]["source_index_written"] is False


def test_get_reports_unregistered_reference(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "遗漏注册：auth:FR-999\n")

    data = run_aisee(tmp_path, "get", "auth:FR-999", "--json")

    assert data["status"] == "unregistered"
    assert data["issues"][0]["code"] == "ID_NOT_REGISTERED"
    assert data["references"][0]["path"] == "docs/requirements/auth-srs.md"
