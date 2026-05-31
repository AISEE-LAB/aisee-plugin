"""Project-level discovery helpers for the Aisee CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def resolve_project_root(cwd: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return Path(result.stdout.strip())
    except Exception:
        return cwd.resolve()


def rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def inspect_project_rules(root: Path) -> dict[str, Any]:
    primary = root / "AGENTS.md"
    legacy = root / "CLAUDE.md"
    return {
        "primary": rel(root, primary) if primary.exists() else None,
        "legacy_fallback": rel(root, legacy) if legacy.exists() else None,
    }


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")
