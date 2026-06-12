"""OpenSpec initialization bridge for the Aisee CLI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from aisee_cli.assets import selected_agent_runtime
from aisee_cli.output import issue, summarize_issues

EXPANDED_WORKFLOWS = [
    "propose",
    "explore",
    "new",
    "continue",
    "apply",
    "ff",
    "sync",
    "archive",
    "bulk-archive",
    "verify",
    "onboard",
]


def run_openspec_init(
    project_root: Path,
    *,
    profile: str = "expanded",
    tools: str | None = None,
    skip_profile: bool = False,
    skip_update: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    issues: list[dict[str, str]] = []
    operations: list[dict[str, Any]] = []
    resolved_tools, tools_source = resolve_openspec_tools(tools)
    openspec_profile = resolve_openspec_profile(profile)

    openspec_bin = shutil.which("openspec")
    if not openspec_bin:
        issues.append(issue("OPENSPEC_CLI_NOT_FOUND", "blocker", "OpenSpec CLI was not found in PATH"))
        return build_response(
            root,
            profile,
            openspec_profile,
            resolved_tools,
            tools_source,
            skip_profile,
            skip_update,
            force,
            operations,
            issues,
        )

    if openspec_profile is None:
        issues.append(issue(
            "UNSUPPORTED_OPENSPEC_PROFILE",
            "blocker",
            "Only Aisee presets 'expanded' and 'core' are supported",
        ))
        return build_response(
            root,
            profile,
            "invalid",
            resolved_tools,
            tools_source,
            skip_profile,
            skip_update,
            force,
            operations,
            issues,
        )

    initialized = is_openspec_initialized(root)
    should_run_init = not initialized or resolved_tools != "none"
    if not should_run_init:
        operations.append({
            "kind": "skip",
            "command": "openspec init",
            "status": "skipped",
            "reason": "OpenSpec project markers already exist",
        })
    else:
        if not skip_profile and openspec_profile == "custom":
            profile_operation = ensure_profile_alignment(openspec_profile)
            operations.append(profile_operation)
            if profile_operation["status"] != "ok":
                issues.append(issue("OPENSPEC_PROFILE_FAILED", "blocker", f"OpenSpec profile alignment for {profile} failed"))
                return build_response(
                    root,
                    profile,
                    openspec_profile,
                    resolved_tools,
                    tools_source,
                    skip_profile,
                    skip_update,
                    force,
                    operations,
                    issues,
                )
        init_command = [openspec_bin, "init", ".", "--tools", resolved_tools, "--profile", openspec_profile]
        if force:
            init_command.append("--force")
        init_result = run_command(init_command, root)
        operations.append(command_operation("openspec init", init_command, init_result))
        if init_result.returncode != 0:
            issues.append(issue("OPENSPEC_INIT_FAILED", "blocker", "openspec init failed"))
            return build_response(
                root,
                profile,
                openspec_profile,
                resolved_tools,
                tools_source,
                skip_profile,
                skip_update,
                force,
                operations,
                issues,
            )

    if skip_profile:
        operations.append({
            "kind": "skip",
            "command": "openspec profile alignment",
            "status": "skipped",
            "reason": "--skip-profile was provided",
        })
    elif openspec_profile == "custom":
        if not should_run_init:
            profile_operation = ensure_profile_alignment(openspec_profile)
            operations.append(profile_operation)
            if profile_operation["status"] != "ok":
                issues.append(issue("OPENSPEC_PROFILE_FAILED", "blocker", f"OpenSpec profile alignment for {profile} failed"))
                return build_response(
                    root,
                    profile,
                    openspec_profile,
                    resolved_tools,
                    tools_source,
                    skip_profile,
                    skip_update,
                    force,
                    operations,
                    issues,
                )
    else:
        profile_command = [openspec_bin, "config", "profile", profile]
        profile_result = run_command(profile_command, root)
        operations.append(command_operation("openspec config profile", profile_command, profile_result))
        if profile_result.returncode != 0:
            issues.append(issue("OPENSPEC_PROFILE_FAILED", "blocker", f"OpenSpec profile alignment for {profile} failed"))
            return build_response(
                root,
                profile,
                openspec_profile,
                resolved_tools,
                tools_source,
                skip_profile,
                skip_update,
                force,
                operations,
                issues,
            )

    if skip_update:
        operations.append({
            "kind": "skip",
            "command": "openspec update",
            "status": "skipped",
            "reason": "--skip-update was provided",
        })
    else:
        update_command = [openspec_bin, "update", "."]
        update_result = run_command(update_command, root)
        operations.append(command_operation("openspec update", update_command, update_result))
        if update_result.returncode != 0:
            issues.append(issue("OPENSPEC_UPDATE_FAILED", "blocker", "openspec update failed"))

    return build_response(
        root,
        profile,
        openspec_profile,
        resolved_tools,
        tools_source,
        skip_profile,
        skip_update,
        force,
        operations,
        issues,
    )


def is_openspec_initialized(root: Path) -> bool:
    openspec_root = root / "openspec"
    return (openspec_root / "changes").is_dir() and (
        (openspec_root / "config.yaml").is_file() or (openspec_root / "specs").is_dir()
    )


def resolve_openspec_tools(requested: str | None) -> tuple[str, str]:
    value = (requested or "").strip()
    if value:
        return value, "explicit"
    runtime = selected_agent_runtime()
    if runtime in {"codex", "claude", "cursor"}:
        return runtime, "runtime-default"
    return "none", "runtime-default"


def resolve_openspec_profile(profile: str) -> str | None:
    value = profile.strip().lower()
    if value == "expanded":
        return "custom"
    if value == "core":
        return "core"
    return None


def ensure_profile_alignment(openspec_profile: str) -> dict[str, Any]:
    if openspec_profile == "core":
        return {
            "kind": "run",
            "command": "openspec config profile core",
            "label": "openspec config profile",
            "status": "pending",
        }

    config_path = openspec_global_config_path()
    existing = read_json_object(config_path)
    existing["profile"] = "custom"
    existing["delivery"] = "both"
    existing["workflows"] = list(EXPANDED_WORKFLOWS)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "kind": "write",
        "command": f"write {config_path.as_posix()}",
        "label": "openspec custom profile alignment",
        "status": "ok",
        "path": config_path.as_posix(),
        "profile": "custom",
        "delivery": "both",
        "workflows": list(EXPANDED_WORKFLOWS),
    }


def openspec_global_config_path() -> Path:
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home).expanduser() / "openspec" / "config.json"
    return Path.home() / ".config" / "openspec" / "config.json"


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def command_operation(label: str, command: list[str], result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "kind": "run",
        "command": printable_command(command),
        "label": label,
        "status": "ok" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "stdout": trim_output(result.stdout),
        "stderr": trim_output(result.stderr),
    }


def printable_command(command: list[str]) -> str:
    if command and command[0].endswith("/openspec"):
        return " ".join(["openspec", *command[1:]])
    return " ".join(command)


def trim_output(text: str, *, limit: int = 4000) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "\n...[truncated]"


def build_response(
    root: Path,
    profile: str,
    openspec_profile: str,
    tools: str,
    tools_source: str,
    skip_profile: bool,
    skip_update: bool,
    force: bool,
    operations: list[dict[str, Any]],
    issues: list[dict[str, str]],
) -> dict[str, Any]:
    summary = summarize_issues(issues)
    return {
        "status": "blocked" if summary["blocker"] else "ok",
        "writes": any(item.get("kind") == "run" for item in operations),
        "project_root": root.as_posix(),
        "operations": operations,
        "issues": issues,
        "summary": summary,
        "meta": {
            "command": "aisee openspec ensure --json",
            "profile": profile,
            "openspec_profile": openspec_profile,
            "profile_scope": "global",
            "profile_default_executes": not skip_profile,
            "update_default_executes": not skip_update,
            "tools": tools,
            "tools_source": tools_source,
            "force": force,
            "skip_profile": skip_profile,
            "skip_update": skip_update,
        },
    }
