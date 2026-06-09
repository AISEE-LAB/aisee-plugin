from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_removed_command(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_knowledge_scaffold_is_not_a_public_subcommand(tmp_path: Path) -> None:
    destination = tmp_path / "team-knowledge"

    result = run_removed_command(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--json")

    assert result.returncode == 2
    assert "invalid choice" in result.stderr
    assert "scaffold" in result.stderr
    assert not destination.exists()


def test_knowledge_scaffold_does_not_overwrite_existing_paths(tmp_path: Path) -> None:
    destination = tmp_path / "ordinary"
    destination.mkdir()
    (destination / "keep.txt").write_text("keep", encoding="utf-8")

    result = run_removed_command(tmp_path, "knowledge", "scaffold", "--dest", str(destination), "--force", "--json")

    assert result.returncode == 2
    assert (destination / "keep.txt").read_text(encoding="utf-8") == "keep"
