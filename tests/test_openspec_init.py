from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_aisee(root: Path, *args: str, path_prefix: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    env["PATH"] = f"{path_prefix}{os.pathsep}{env['PATH']}"
    env["HOME"] = str(root.parent / "home")
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def install_fake_openspec(bin_dir: Path) -> Path:
    script = bin_dir / "openspec"
    write(
        script,
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path.cwd()
calls = root / "openspec-calls.jsonl"
with calls.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(sys.argv[1:]) + "\\n")

if sys.argv[1:3] == ["config", "profile"]:
    if len(sys.argv) >= 4 and sys.argv[3] == "core":
        print("Configured profile: core")
        raise SystemExit(0)
    print("Available presets: core", file=sys.stderr)
    raise SystemExit(1)

if len(sys.argv) >= 2 and sys.argv[1] == "init":
    (root / "openspec" / "changes" / "archive").mkdir(parents=True, exist_ok=True)
    (root / "openspec" / "specs").mkdir(parents=True, exist_ok=True)
    print("Initialized OpenSpec")
    raise SystemExit(0)

if sys.argv[1:3] == ["update", "."]:
    print("Updated OpenSpec instructions")
    raise SystemExit(0)

print("unexpected openspec call", file=sys.stderr)
raise SystemExit(2)
""",
    )
    script.chmod(0o755)
    return script


def read_calls(root: Path) -> list[list[str]]:
    return [
        json.loads(line)
        for line in (root / "openspec-calls.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def read_global_config(root: Path) -> dict[str, object]:
    return json.loads((root.parent / "home" / ".config" / "openspec" / "config.json").read_text(encoding="utf-8"))


def test_openspec_ensure_runs_init_and_profile_by_default(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    project.mkdir()

    result = run_aisee(project, "openspec", "ensure", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 0
    assert data["status"] == "ok"
    assert data["writes"] is True
    assert data["meta"]["profile"] == "expanded"
    assert data["meta"]["openspec_profile"] == "custom"
    assert data["meta"]["profile_default_executes"] is True
    assert data["meta"]["update_default_executes"] is True
    assert data["meta"]["tools"] == "codex"
    assert data["meta"]["tools_source"] == "runtime-default"
    assert data["operations"][0]["label"] == "openspec custom profile alignment"
    assert data["operations"][1]["command"] == "openspec init . --tools codex --profile custom"
    assert data["operations"][2]["command"] == "openspec update ."
    assert read_calls(project) == [
        ["init", ".", "--tools", "codex", "--profile", "custom"],
        ["update", "."],
    ]
    assert read_global_config(project)["workflows"] == [
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


def test_openspec_ensure_replays_init_for_runtime_tools_on_initialized_project(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    (project / "openspec" / "changes").mkdir(parents=True)
    (project / "openspec" / "specs").mkdir(parents=True)

    result = run_aisee(project, "openspec", "ensure", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 0
    assert data["status"] == "ok"
    assert data["operations"][0]["label"] == "openspec custom profile alignment"
    assert data["operations"][1]["command"] == "openspec init . --tools codex --profile custom"
    assert data["operations"][2]["command"] == "openspec update ."
    assert read_calls(project) == [
        ["init", ".", "--tools", "codex", "--profile", "custom"],
        ["update", "."],
    ]


def test_openspec_ensure_can_skip_update(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    project.mkdir()

    result = run_aisee(project, "openspec", "ensure", "--tools", "none", "--skip-update", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 0
    assert data["status"] == "ok"
    assert data["meta"]["tools"] == "none"
    assert data["meta"]["tools_source"] == "explicit"
    assert data["meta"]["update_default_executes"] is False
    assert data["operations"][2]["command"] == "openspec update"
    assert data["operations"][2]["status"] == "skipped"
    assert read_calls(project) == [
        ["init", ".", "--tools", "none", "--profile", "custom"],
    ]


def test_openspec_ensure_accepts_legacy_config_yaml_marker(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    write(project / "openspec" / "config.yaml", "version: 1\n")
    (project / "openspec" / "changes").mkdir(parents=True)

    result = run_aisee(project, "openspec", "ensure", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 0
    assert data["status"] == "ok"
    assert data["operations"][1]["command"] == "openspec init . --tools codex --profile custom"
    assert read_calls(project) == [
        ["init", ".", "--tools", "codex", "--profile", "custom"],
        ["update", "."],
    ]


def test_openspec_ensure_can_skip_init_on_initialized_project_when_tools_none(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    (project / "openspec" / "changes").mkdir(parents=True)
    (project / "openspec" / "specs").mkdir(parents=True)

    result = run_aisee(project, "openspec", "ensure", "--tools", "none", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 0
    assert data["status"] == "ok"
    assert data["operations"][0]["status"] == "skipped"
    assert data["operations"][1]["label"] == "openspec custom profile alignment"
    assert read_calls(project) == [["update", "."]]


def test_openspec_ensure_blocks_unsupported_profile_before_running(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    project.mkdir()

    result = run_aisee(project, "openspec", "ensure", "--profile", "custom", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 1
    assert data["status"] == "blocked"
    assert data["issues"][0]["code"] == "UNSUPPORTED_OPENSPEC_PROFILE"
    assert not (project / "openspec-calls.jsonl").exists()


def test_openspec_ensure_core_profile_keeps_minimal_workflow(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    install_fake_openspec(bin_dir)
    project = tmp_path / "project"
    project.mkdir()

    result = run_aisee(project, "openspec", "ensure", "--profile", "core", "--json", path_prefix=bin_dir)
    data = json.loads(result.stdout)

    assert result.returncode == 0
    assert data["status"] == "ok"
    assert data["meta"]["profile"] == "core"
    assert data["meta"]["openspec_profile"] == "core"
    assert data["operations"][0]["command"] == "openspec init . --tools codex --profile core"
    assert data["operations"][1]["command"] == "openspec config profile core"
    assert read_calls(project) == [
        ["init", ".", "--tools", "codex", "--profile", "core"],
        ["config", "profile", "core"],
        ["update", "."],
    ]
