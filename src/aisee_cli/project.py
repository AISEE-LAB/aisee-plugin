"""Project-level discovery helpers for the Aisee CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def resolve_project_root(cwd: Path) -> Path:
    current = cwd.resolve()
    git_root = git_top_level(current)

    for candidate in ancestor_chain(current, stop=git_root):
        if has_project_markers(candidate):
            return candidate

    if git_root is not None:
        return git_root
    return current


def git_top_level(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return None
    output = result.stdout.strip()
    return Path(output).resolve() if output else None


def ancestor_chain(start: Path, *, stop: Path | None) -> list[Path]:
    current = start
    chain = [current]
    while current.parent != current:
        current = current.parent
        chain.append(current)
        if stop is not None and current == stop:
            break
    return chain


def has_project_markers(path: Path) -> bool:
    openspec_config = (path / "openspec" / "config.yaml").exists()
    openspec_changes = (path / "openspec" / "changes").exists()
    aisee_root = (path / "aisee").exists()
    agents = (path / "AGENTS.md").exists()
    return openspec_config or openspec_changes or (aisee_root and agents)


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
