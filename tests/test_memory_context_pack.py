from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from test_context_pack import create_project
from test_memory_config import write_memory


ROOT = Path(__file__).resolve().parents[1]


def run_context_pack(root: Path, *extra_args: str) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "context",
            "pack",
            "--change",
            "add-auth",
            "--for",
            "ce-work",
            "--json",
            *extra_args,
        ],
        cwd=root,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def test_context_pack_excludes_project_memory_by_default(tmp_path: Path) -> None:
    create_project(tmp_path)
    write_memory(tmp_path, "aisee/memory/pref/auth.md", summary="add-auth 实现时保持登录兼容。")

    data = run_context_pack(tmp_path)

    assert "project_memory" not in data


def test_context_pack_includes_project_memory_only_with_flag(tmp_path: Path) -> None:
    create_project(tmp_path)
    write_memory(tmp_path, "aisee/memory/pref/auth.md", summary="add-auth 实现时保持登录兼容。")

    data = run_context_pack(tmp_path, "--project-memory")

    assert data["project_memory"]["status"] == "ok"
    assert data["project_memory"]["matches"][0]["id"] == "auth"
    assert "project_memory" not in data["facts"]["parsed"]
    assert data["project_memory"]["meta"]["cache_is_fact_source"] is False


def test_context_pack_project_memory_missing_does_not_fail(tmp_path: Path) -> None:
    create_project(tmp_path)

    data = run_context_pack(tmp_path, "--project-memory")

    assert data["project_memory"]["status"] == "ok"
    assert data["project_memory"]["matches"] == []
