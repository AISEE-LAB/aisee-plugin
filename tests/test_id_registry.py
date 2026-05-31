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


def test_cli_id_reserve_creates_registry_and_increments(tmp_path: Path) -> None:
    data = run_aisee(
        tmp_path,
        "id",
        "reserve",
        "--scope",
        "auth",
        "--type",
        "FR",
        "--count",
        "2",
        "--json",
    )

    assert data["status"] == "ok"
    assert [item["id"] for item in data["reserved"]] == ["auth:FR-001", "auth:FR-002"]

    registry = json.loads((tmp_path / ".aisee" / "id-registry.json").read_text(encoding="utf-8"))
    assert registry["scopes"]["auth"]["counters"]["FR"] == 2
    assert registry["scopes"]["auth"]["ids"]["auth:FR-001"]["status"] == "reserved"


def test_cli_id_activate_updates_reserved_id(tmp_path: Path) -> None:
    run_aisee(tmp_path, "id", "reserve", "--scope", "auth", "--type", "FR", "--count", "1", "--json")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "覆盖需求：auth:FR-001\n")

    data = run_aisee(
        tmp_path,
        "id",
        "activate",
        "auth:FR-001",
        "--owner",
        "docs/requirements/auth-srs.md",
        "--title",
        "用户登录",
        "--json",
    )

    assert data["status"] == "ok"
    assert data["entry"]["status"] == "active"
    assert data["entry"]["owner"] == "docs/requirements/auth-srs.md"
    assert data["entry"]["title"] == "用户登录"


def test_cli_id_check_reports_clean_registry(tmp_path: Path) -> None:
    run_aisee(tmp_path, "id", "reserve", "--scope", "auth", "--type", "FR", "--count", "1", "--json")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "覆盖需求：auth:FR-001\n")
    run_aisee(
        tmp_path,
        "id",
        "activate",
        "auth:FR-001",
        "--owner",
        "docs/requirements/auth-srs.md",
        "--title",
        "用户登录",
        "--json",
    )

    data = run_aisee(tmp_path, "id", "check", "--json")

    assert data["status"] == "ok"
    assert data["summary"] == {"blocker": 0, "risk": 0, "info": 0, "total": 0}


def test_cli_id_check_reports_unregistered_reference(tmp_path: Path) -> None:
    write(tmp_path / ".aisee" / "id-registry.json", "{}\n")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "覆盖需求：auth:FR-999\n")

    data = run_aisee(tmp_path, "id", "check", "--json")

    assert data["status"] == "risk"
    assert data["summary"]["risk"] == 1
    assert data["issues"][0]["code"] == "ID_UNREGISTERED_REFERENCE"
