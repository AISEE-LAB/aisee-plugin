from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_aisee(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_missing_openspec_subcommand_returns_json_error(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "openspec", "--json")
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert result.stdout == ""
    assert data["status"] == "error"
    assert data["issues"][0]["code"] == "MISSING_SUBCOMMAND"


def test_missing_change_subcommand_returns_json_error(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "change", "--json")
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert result.stdout == ""
    assert data["issues"][0]["code"] == "MISSING_SUBCOMMAND"


def test_removed_id_command_returns_argparse_error(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "id", "--json")

    assert result.returncode == 2
    assert result.stdout == ""
    assert "invalid choice" in result.stderr
    assert "id" in result.stderr


def test_missing_context_subcommand_returns_json_error(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "context", "--json")
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert result.stdout == ""
    assert data["issues"][0]["code"] == "MISSING_SUBCOMMAND"


def test_missing_knowledge_subcommand_returns_json_error(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "knowledge", "--json")
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert result.stdout == ""
    assert data["issues"][0]["code"] == "MISSING_SUBCOMMAND"
