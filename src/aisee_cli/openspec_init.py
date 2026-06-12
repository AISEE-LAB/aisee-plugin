"""OpenSpec initialization bridge for the Aisee CLI."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from aisee_cli.output import issue, summarize_issues


def run_openspec_init(
    project_root: Path,
    *,
    profile: str = "core",
    tools: str = "none",
    skip_profile: bool = False,
    skip_update: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    issues: list[dict[str, str]] = []
    operations: list[dict[str, Any]] = []

    openspec_bin = shutil.which("openspec")
    if not openspec_bin:
        issues.append(issue("OPENSPEC_CLI_NOT_FOUND", "blocker", "OpenSpec CLI was not found in PATH"))
        return build_response(root, profile, tools, skip_profile, skip_update, force, operations, issues)

    if profile != "core" and not skip_profile:
        issues.append(issue(
            "UNSUPPORTED_OPENSPEC_PROFILE",
            "blocker",
            "Only the non-interactive OpenSpec profile preset 'core' is supported by default",
        ))
        return build_response(root, profile, tools, skip_profile, skip_update, force, operations, issues)

    initialized = is_openspec_initialized(root)
    if initialized:
        operations.append({
            "kind": "skip",
            "command": "openspec init",
            "status": "skipped",
            "reason": "openspec/config.yaml and openspec/changes already exist",
        })
    else:
        init_command = [openspec_bin, "init", ".", "--tools", tools, "--profile", profile]
        if force:
            init_command.append("--force")
        init_result = run_command(init_command, root)
        operations.append(command_operation("openspec init", init_command, init_result))
        if init_result.returncode != 0:
            issues.append(issue("OPENSPEC_INIT_FAILED", "blocker", "openspec init failed"))
            return build_response(root, profile, tools, skip_profile, skip_update, force, operations, issues)

    if skip_profile:
        operations.append({
            "kind": "skip",
            "command": "openspec config profile",
            "status": "skipped",
            "reason": "--skip-profile was provided",
        })
    else:
        profile_command = [openspec_bin, "config", "profile", profile]
        profile_result = run_command(profile_command, root)
        operations.append(command_operation("openspec config profile", profile_command, profile_result))
        if profile_result.returncode != 0:
            issues.append(issue("OPENSPEC_PROFILE_FAILED", "blocker", f"openspec config profile {profile} failed"))
            return build_response(root, profile, tools, skip_profile, skip_update, force, operations, issues)

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

    return build_response(root, profile, tools, skip_profile, skip_update, force, operations, issues)


def is_openspec_initialized(root: Path) -> bool:
    return (root / "openspec" / "config.yaml").is_file() and (root / "openspec" / "changes").is_dir()


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
    tools: str,
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
            "profile_scope": "global",
            "profile_default_executes": not skip_profile,
            "update_default_executes": not skip_update,
            "tools": tools,
            "force": force,
            "skip_profile": skip_profile,
            "skip_update": skip_update,
        },
    }
