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
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(root / "openspec" / "changes" / ".gitkeep", "")
    write(
        root / "aisee" / "registry" / "sources.json",
        json.dumps(
            {
                "version": 1,
                "sources": [
                    {
                        "scope": "auth",
                        "type": "srs",
                        "path": "docs/requirements/auth-srs.md",
                        "alias": "srs:auth-login",
                        "template": "aisee-srs",
                        "parser": "srs",
                    },
                    {
                        "scope": "auth",
                        "type": "ui-content",
                        "path": "docs/ui-content/auth-ui.md",
                        "alias": "ui-content:auth-login",
                        "template": "aisee-ui-content",
                        "parser": "ui-content",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    write(
        root / "docs" / "requirements" / "auth-srs.md",
        """---
title: "Auth SRS"
doc_type: "srs"
status: "active"
date: "2026-06-09"
scope: "auth"
owner: "Aisee"
source_refs:
  - "ticket://auth"
change_refs:
  - "openspec/changes/add-auth"
anchors:
  - "docs/requirements/auth-srs.md#FR-001"
---

# Auth SRS

## 登录

覆盖需求：FR-001
关联页面：PAGE-001
""",
    )
    write(
        root / "docs" / "ui-content" / "auth-ui.md",
        """---
title: "Auth UI"
doc_type: "ui-content"
status: "active"
date: "2026-06-09"
scope: "auth"
owner: "Aisee"
source_refs:
  - "docs/requirements/auth-srs.md#FR-001"
change_refs:
  - "openspec/changes/add-auth"
anchors:
  - "docs/ui-content/auth-ui.md#PAGE-001"
---

# Auth UI

## 登录页

页面 ID：PAGE-001
覆盖需求：docs/requirements/auth-srs.md#FR-001
""",
    )
    write(
        root / "openspec" / "changes" / "add-auth" / "source-map.md",
        """## Upstream Sources

| Source | Path / Description | Ref | Status | Notes |
|---|---|---|---|---|
| SRS | docs/requirements/auth-srs.md | docs/requirements/auth-srs.md#FR-001 | confirmed | |

## Affected Paths Index

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |
| test | tests/auth/test_session.py | docs/requirements/auth-srs.md#FR-001 | add | |
""",
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
        "architecture",
        "--path",
        "docs/architecture/auth-brief.md",
        "--alias",
        "architecture:auth-login",
        "--template",
        "aisee-architecture",
        "--parser",
        "architecture",
        "--json",
    )
    checked = run_aisee(tmp_path, "sources", "check", "--json")

    assert added["status"] == "risk"
    assert added["changed"] is True
    assert checked["status"] == "risk"
    assert checked["sources"][0]["alias"] == "srs:auth-login"
    assert (tmp_path / "aisee" / "registry" / "sources.json").exists()


def test_index_writes_rebuildable_cache(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_aisee(tmp_path, "index", "--json")

    assert data["status"] == "ok"
    assert data["index"]["writes"] is True
    assert data["project_rules"]["primary"] == "AGENTS.md"
    assert "docs/requirements/auth-srs.md#FR-001" in data["anchors"]
    assert data["aliases"]["srs:auth-login"] == "docs/requirements/auth-srs.md"
    assert any(item["path"] == "docs/requirements/auth-srs.md" for item in data["documents"])
    assert data["planning_docs"]["count"] == 2
    assert any(item["path"] == "docs/requirements/auth-srs.md" and item["doc_type"] == "srs" for item in data["planning_docs"]["items"])
    cache = tmp_path / "aisee" / "cache" / "context-index.json"
    assert cache.exists()
    cached = json.loads(cache.read_text(encoding="utf-8"))
    assert cached["meta"]["cache_is_fact_source"] is False


def test_index_ignores_frontmatter_outside_planning_doc_roots(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "examples" / "sample.md",
        """---
title: "Example"
doc_type: "srs"
status: "active"
date: "2026-06-09"
scope: "example"
owner: "Aisee"
source_refs:
  - "ticket://example"
change_refs:
  - "openspec/changes/example"
anchors:
  - "examples/sample.md#FR-001"
---

# Example
""",
    )

    data = run_aisee(tmp_path, "index", "--json")

    assert all(item["path"] != "examples/sample.md" for item in data["planning_docs"]["items"])


def test_get_returns_anchor_source_and_relations(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_aisee(tmp_path, "get", "docs/requirements/auth-srs.md#FR-001", "--json")

    assert data["status"] == "linked"
    assert data["document"] == "docs/requirements/auth-srs.md"
    assert data["source"]["path"] == "docs/requirements/auth-srs.md"
    assert data["source"]["heading"]["title"] == "登录"
    assert data["relations"]["changes"] == ["add-auth"]
    assert data["relations"]["references"] == ["docs/requirements/auth-srs.md#PAGE-001"]
    assert data["relations"]["code_paths"] == ["src/auth/session.py"]
    assert data["relations"]["test_paths"] == ["tests/auth/test_session.py"]
    assert data["meta"]["source_index_written"] is False


def test_get_resolves_alias_anchor(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_aisee(tmp_path, "get", "srs:auth-login#FR-001", "--json")

    assert data["status"] == "linked"
    assert data["reference_type"] == "alias-anchor"
    assert data["canonical_reference"] == "docs/requirements/auth-srs.md#FR-001"


def test_get_reports_missing_local_id(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_aisee(tmp_path, "get", "docs/requirements/auth-srs.md#FR-999", "--json")

    assert data["status"] == "missing-local-id"
    assert data["issues"][0]["code"] == "ANCHOR_LOCAL_ID_MISSING"
