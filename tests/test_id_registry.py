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


def run_aisee_error(root: Path, *args: str) -> dict:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    result = subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 2
    return json.loads(result.stderr)


def test_cli_id_reserve_creates_registry_and_increments(tmp_path: Path) -> None:
    next_data = run_aisee(tmp_path, "id", "next", "--scope", "auth", "--type", "FR", "--json")

    assert next_data["status"] == "ok"
    assert next_data["next"]["id"] == "auth:FR-001"
    assert next_data["writes"] is False
    assert not (tmp_path / ".aisee" / "id-registry.json").exists()

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


def test_cli_id_next_uses_existing_counter(tmp_path: Path) -> None:
    run_aisee(tmp_path, "id", "reserve", "--scope", "auth", "--type", "FR", "--count", "2", "--json")

    data = run_aisee(tmp_path, "id", "next", "--scope", "auth", "--type", "FR", "--json")

    assert data["next"]["id"] == "auth:FR-003"
    registry = json.loads((tmp_path / ".aisee" / "id-registry.json").read_text(encoding="utf-8"))
    assert registry["scopes"]["auth"]["counters"]["FR"] == 2


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


def test_cli_id_deprecate_marks_entry_and_check_reports_reference(tmp_path: Path) -> None:
    run_aisee(tmp_path, "id", "reserve", "--scope", "auth", "--type", "FR", "--count", "2", "--json")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "旧需求：auth:FR-001\n新需求：auth:FR-002\n")
    run_aisee(
        tmp_path,
        "id",
        "activate",
        "auth:FR-001",
        "--owner",
        "docs/requirements/auth-srs.md",
        "--title",
        "旧登录",
        "--json",
    )
    run_aisee(
        tmp_path,
        "id",
        "activate",
        "auth:FR-002",
        "--owner",
        "docs/requirements/auth-srs.md",
        "--title",
        "新登录",
        "--json",
    )

    deprecated = run_aisee(
        tmp_path,
        "id",
        "deprecate",
        "auth:FR-001",
        "--replaced-by",
        "auth:FR-002",
        "--reason",
        "登录方式拆分",
        "--json",
    )
    checked = run_aisee(tmp_path, "id", "check", "--json")
    traced = run_aisee(tmp_path, "trace", "auth:FR-001", "--json")

    assert deprecated["entry"]["status"] == "deprecated"
    assert deprecated["entry"]["replaced_by"] == ["auth:FR-002"]
    assert checked["status"] == "risk"
    assert any(issue["code"] == "ID_INACTIVE_REFERENCE" for issue in checked["issues"])
    assert traced["status"] == "deprecated"


def test_cli_id_deprecate_rejects_unregistered_replacement(tmp_path: Path) -> None:
    run_aisee(tmp_path, "id", "reserve", "--scope", "auth", "--type", "FR", "--count", "1", "--json")

    data = run_aisee_error(
        tmp_path,
        "id",
        "deprecate",
        "auth:FR-001",
        "--replaced-by",
        "auth:FR-999",
        "--reason",
        "登录方式拆分",
        "--json",
    )

    assert data["status"] == "error"
    assert "replacement ID is not registered" in data["message"]


def test_cli_id_check_reports_unregistered_reference(tmp_path: Path) -> None:
    write(tmp_path / ".aisee" / "id-registry.json", "{}\n")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "覆盖需求：auth:FR-999\n")

    data = run_aisee(tmp_path, "id", "check", "--json")

    assert data["status"] == "risk"
    assert data["summary"]["risk"] == 1
    assert data["issues"][0]["code"] == "ID_UNREGISTERED_REFERENCE"


def test_cli_trace_returns_registry_entry_and_change_relations(tmp_path: Path) -> None:
    run_aisee(tmp_path, "id", "reserve", "--scope", "auth", "--type", "FR", "--count", "1", "--json")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "覆盖需求：auth:FR-001\n")
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        "| FR | auth:FR-001 | 登录 | SRS | 覆盖 | specs / tasks |\n",
    )
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

    data = run_aisee(tmp_path, "trace", "auth:FR-001", "--json")

    assert data["status"] == "linked"
    assert data["registry"]["entry"]["status"] == "active"
    assert data["relations"]["changes"] == ["add-auth"]
    assert {reference["path"] for reference in data["references"]} == {
        "docs/requirements/auth-srs.md",
        "openspec/changes/add-auth/source-map.md",
    }


def test_cli_trace_reports_unregistered_reference(tmp_path: Path) -> None:
    write(tmp_path / ".aisee" / "id-registry.json", "{}\n")
    write(tmp_path / "docs" / "requirements" / "auth-srs.md", "覆盖需求：auth:FR-999\n")

    data = run_aisee(tmp_path, "trace", "auth:FR-999", "--json")

    assert data["status"] == "unregistered"
    assert data["issues"][0]["code"] == "ID_NOT_REGISTERED"
    assert data["references"][0]["path"] == "docs/requirements/auth-srs.md"
