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


def create_anchor_project(root: Path) -> None:
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
                    }
                ],
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

覆盖需求：FR-001
旧规则提示：auth:FR-001
""",
    )
    write(
        root / "openspec" / "changes" / "add-auth" / "source-map.md",
        """## Upstream Sources

| Source | Path / Description | Ref | Status | Notes |
|---|---|---|---|---|
| SRS | docs/requirements/auth-srs.md | srs:auth-login#FR-001 | confirmed | |
""",
    )


def test_index_collects_anchor_and_alias_occurrences(tmp_path: Path) -> None:
    create_anchor_project(tmp_path)

    data = run_aisee(tmp_path, "index", "--json")

    assert data["status"] == "ok"
    assert "docs/requirements/auth-srs.md#FR-001" in data["anchors"]
    assert data["aliases"]["srs:auth-login"] == "docs/requirements/auth-srs.md"
    assert data["documents"][0]["local_ids"] == ["FR-001"]


def test_get_resolves_path_anchor(tmp_path: Path) -> None:
    create_anchor_project(tmp_path)

    data = run_aisee(tmp_path, "get", "docs/requirements/auth-srs.md#FR-001", "--json")

    assert data["status"] == "linked"
    assert data["canonical_reference"] == "docs/requirements/auth-srs.md#FR-001"
    assert data["source"]["path"] == "docs/requirements/auth-srs.md"


def test_get_resolves_alias_anchor(tmp_path: Path) -> None:
    create_anchor_project(tmp_path)

    data = run_aisee(tmp_path, "get", "srs:auth-login#FR-001", "--json")

    assert data["status"] == "linked"
    assert data["reference_type"] == "alias-anchor"
    assert data["canonical_reference"] == "docs/requirements/auth-srs.md#FR-001"


def test_get_reports_missing_alias(tmp_path: Path) -> None:
    create_anchor_project(tmp_path)

    data = run_aisee(tmp_path, "get", "srs:missing#FR-001", "--json")

    assert data["status"] == "missing-document"
    assert data["issues"][0]["code"] == "ANCHOR_ALIAS_NOT_FOUND"


def test_trace_reports_legacy_full_id_diagnostic(tmp_path: Path) -> None:
    create_anchor_project(tmp_path)

    data = run_aisee(tmp_path, "trace", "docs/requirements/auth-srs.md#FR-001", "--json")

    assert data["status"] == "linked"
    assert any(issue["code"] == "LEGACY_FULL_ID_REFERENCE" for issue in data["issues"])
