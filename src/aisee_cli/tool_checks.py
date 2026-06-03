"""External tool and plugin checks for Aisee workflows."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


COMPOUND_REQUIRED_SKILLS = ["ce-plan", "ce-doc-review", "ce-work", "ce-code-review"]


def check_openspec_cli() -> dict[str, Any]:
    executable = shutil.which("openspec")
    if not executable:
        return {
            "available": False,
            "executable": None,
            "version": None,
            "status": "missing",
        }

    result = subprocess.run(
        [executable, "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    version = (result.stdout or result.stderr).strip() or None
    return {
        "available": result.returncode == 0,
        "executable": executable,
        "version": version,
        "status": "ok" if result.returncode == 0 else "error",
        "returncode": result.returncode,
    }


def check_compound_plugin() -> dict[str, Any]:
    skill_roots = find_compound_skill_roots()
    skills = {
        skill: any((root / skill / "SKILL.md").is_file() for root in skill_roots)
        for skill in COMPOUND_REQUIRED_SKILLS
    }
    missing = [skill for skill, available in skills.items() if not available]
    return {
        "plugin_available": bool(skill_roots),
        "status": "ok" if not missing else ("missing" if not skill_roots else "partial"),
        "skill_roots": [root.as_posix() for root in skill_roots],
        "skills": skills,
        "missing_skills": missing,
    }


def find_compound_skill_roots() -> list[Path]:
    roots: list[Path] = []
    env_value = os.environ.get("AISEE_COMPOUND_SKILLS_DIR", "")
    for item in env_value.split(os.pathsep):
        if item:
            add_skill_root(roots, Path(item).expanduser())
    if env_value:
        return roots

    home = Path.home()
    candidates = [
        home / ".codex" / "plugins" / "cache" / "compound-engineering-plugin",
        home / ".claude" / "plugins" / "cache" / "compound-engineering-plugin",
        home / ".agents" / "plugins" / "cache" / "compound-engineering-plugin",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        for skills_dir in candidate.glob("**/skills"):
            add_skill_root(roots, skills_dir)

    return roots


def add_skill_root(roots: list[Path], path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_dir():
        return
    if not any((resolved / skill / "SKILL.md").is_file() for skill in COMPOUND_REQUIRED_SKILLS):
        return
    if resolved not in roots:
        roots.append(resolved)
