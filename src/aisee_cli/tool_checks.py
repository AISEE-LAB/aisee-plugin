"""External tool and plugin checks for Aisee workflows."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from aisee_cli.marketplace import MARKETPLACE_SOURCE, marketplace_setup_hint

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


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


def check_codex_aisee_marketplace() -> dict[str, Any]:
    executable = shutil.which("codex")
    config_path = codex_config_path()
    result: dict[str, Any] = {
        "runtime": "codex",
        "codex_cli_available": bool(executable),
        "codex_cli": executable,
        "config_path": config_path.as_posix(),
        "config_read": False,
        "marketplace_configured": False,
        "plugin_enabled": False,
        "status": "unknown",
        "setup_hint": marketplace_setup_hint(),
    }
    if not config_path.exists():
        result["reason"] = "config-missing"
        return result

    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except Exception as error:
        result["reason"] = f"config-unreadable: {error}"
        return result

    result["config_read"] = True
    marketplaces = config.get("marketplaces") if isinstance(config, dict) else None
    plugins = config.get("plugins") if isinstance(config, dict) else None
    if isinstance(marketplaces, dict):
        result["marketplace_configured"] = any(
            marketplace_matches_aisee(item)
            for item in marketplaces.values()
            if isinstance(item, dict)
        )
    if isinstance(plugins, dict):
        result["plugin_enabled"] = any(
            name.startswith("aisee-plugin@") and bool(item.get("enabled", True))
            for name, item in plugins.items()
            if isinstance(name, str) and isinstance(item, dict)
        )
    if result["marketplace_configured"] and result["plugin_enabled"]:
        result["status"] = "ok"
    else:
        result["status"] = "missing"
    return result


def marketplace_matches_aisee(item: dict[str, Any]) -> bool:
    values = [str(item.get(key) or "") for key in ("source", "repo", "url", "path")]
    return any(MARKETPLACE_SOURCE in value or "AISEE-LAB/aisee-plugin" in value for value in values)


def codex_config_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "config.toml"
    return Path.home() / ".codex" / "config.toml"


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
