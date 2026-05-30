from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from aisee_cli.context_pack import build_context_pack


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / ".aisee" / "id-registry.json", "{}\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(
        root / "openspec" / "schemas" / "aisee-app-spec-driven" / "schema.yaml",
        """name: aisee-app-spec-driven
version: 2
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
  - id: source-map
    generates: source-map.md
    template: source-map.md
    requires: [proposal]
  - id: specs
    generates: specs/**/*.md
    template: spec.md
    requires: [source-map]
  - id: change-context
    generates: change-context.md
    template: change-context.md
    requires: [specs]
  - id: service-contract
    generates: service-contract.md
    template: service-contract.md
    requires: [source-map, specs, change-context]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, change-context, service-contract]
apply:
  requires: [tasks]
  tracks: tasks.md
""",
    )
    change = root / "openspec" / "changes" / "add-auth"
    write(change / ".openspec.yaml", "schema: aisee-app-spec-driven\n")
    write(
        change / "proposal.md",
        """# Proposal

## 变更范围

| 类型 | 完整 ID | 说明 |
|---|---|---|
| 功能需求 | auth:FR-001 | 登录 |

## 不在范围

- 注册
""",
    )
    write(
        change / "source-map.md",
        """# Source Map

| 类型 | 完整 ID | 标题 | 来源 | 处理方式 | 后续 artifact |
|---|---|---|---|---|---|
| FR | auth:FR-001 | 登录 | SRS | 覆盖 | specs / tasks |
| API | auth:API-001 | 登录接口 | service-contract.md | 新增 | src/auth/session.py / tests/auth/test_session.py |

## Artifact 适用性

| service-contract.md | yes | auth:API-001 | 需要后端接口 | tasks.md |
""",
    )
    write(
        change / "specs" / "auth.md",
        """## ADDED Requirements

### Requirement: auth:SPEC-001 Login

系统 MUST allow login.
""",
    )
    write(change / "change-context.md", "# Change Context\n")
    write(
        change / "service-contract.md",
        """# Service Contract

auth:API-001 uses src/auth/session.py and tests/auth/test_session.py.
""",
    )
    write(
        change / "tasks.md",
        """# Tasks

- [ ] auth:TASK-001 Implement src/auth/session.py.
- [ ] auth:TEST-001 Verify tests/auth/test_session.py.
""",
    )


def test_ce_work_pack_contains_execution_context(tmp_path: Path) -> None:
    create_project(tmp_path)

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    assert pack["target"] == "ce-work"
    assert pack["change"]["schema"] == "aisee-app-spec-driven"
    assert "src/auth/session.py" in pack["facts"]["derived"]["code_paths"]
    assert "tests/auth/test_session.py" in pack["facts"]["derived"]["test_paths"]
    assert pack["facts"]["derived"]["task_state"]["total"] == 2
    assert pack["facts"]["derived"]["execution"]["requires_ce_plan"] is False
    assert pack["generated"] is None


def test_verify_pack_contains_check_groups(tmp_path: Path) -> None:
    create_project(tmp_path)

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    checks = pack["facts"]["derived"]["checks"]
    assert "schema_artifacts" in checks
    assert "traceability" in checks
    assert "review_and_tests" in checks
    assert pack["facts"]["derived"]["drift_candidates"] == []


def test_cli_context_pack_outputs_json(tmp_path: Path) -> None:
    create_project(tmp_path)
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

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
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert data["target"] == "ce-work"
    assert data["change"]["id"] == "add-auth"
