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


def install_compound_skills(root: Path, *skills: str) -> Path:
    skills_dir = root / "compound" / "skills"
    for skill in skills:
        write(skills_dir / skill / "SKILL.md", f"# {skill}\n")
    return skills_dir


def create_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(
        root / "aisee" / "registry" / "sources.json",
        json.dumps(
            {
                "version": 1,
                "sources": [
                    {
                        "scope": "auth",
                        "type": "srs",
                        "path": "docs/requirements/auth-srs.md",
                        "alias": "srs:auth-login",
                        "template": "aisee-srs",
                        "parser": "srs",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    write(root / "docs" / "requirements" / "auth-srs.md", "# Auth SRS\n\n## 登录\n\n覆盖需求：FR-001\n")
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
    schema_templates = root / "openspec" / "schemas" / "aisee-app-spec-driven" / "templates"
    for template in ("proposal.md", "source-map.md", "spec.md", "change-context.md", "service-contract.md", "tasks.md"):
        write(schema_templates / template, f"# {template}\n")
    change = root / "openspec" / "changes" / "add-auth"
    write(change / ".openspec.yaml", "schema: aisee-app-spec-driven\n")
    write(
        change / "proposal.md",
        """# Proposal

## 变更范围

| 类型 | Ref | 说明 |
|---|---|---|
| 功能需求 | docs/requirements/auth-srs.md#FR-001 | 登录 |

## 不在范围

- 注册
""",
    )
    write(
        change / "source-map.md",
        """# Source Map

## Upstream Sources

| Source | Path / Description | Ref | Status | Notes |
|---|---|---|---|---|
| SRS | docs/requirements/auth-srs.md | docs/requirements/auth-srs.md#FR-001 | confirmed | |

## Anchor Trace

| Type | Ref | Title | Source | Handling | Artifact |
|---|---|---|---|---|---|
| FR | docs/requirements/auth-srs.md#FR-001 | 登录 | SRS | 覆盖 | specs / tasks |

## Artifact 适用性

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | docs/requirements/auth-srs.md#FR-001 | 需要后端接口 | tasks.md |

## Affected Paths Index

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |
| test | tests/auth/test_session.py | docs/requirements/auth-srs.md#FR-001 | add | |

## Contract Ownership / Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | |
| canonical_source | contracts/openapi.yaml | confirmed | |
| provider_repo | backend-api | confirmed | |
| consumer_repo | frontend-app | confirmed | |
| sync_mode | local-http | confirmed | |
| machine_readable_contract | contracts/openapi.yaml | confirmed | |
""",
    )
    write(
        change / "specs" / "auth.md",
        """## ADDED Requirements

### Requirement: SPEC-001 Login

系统 MUST allow login.
""",
    )
    write(change / "change-context.md", "# Change Context\n")
    write(
        change / "service-contract.md",
        """# Service Contract

docs/requirements/auth-srs.md#FR-001 uses src/auth/session.py and tests/auth/test_session.py.
""",
    )
    write(
        change / "tasks.md",
        """# Tasks

- [ ] TASK-001 Provider implementation: implement src/auth/session.py.
- [ ] TASK-001 Consumer integration: update frontend caller.
- [ ] TEST-001 Contract test: verify tests/auth/test_session.py.
- [ ] TEST-001 Backward compatibility check: confirm login contract compatibility.
""",
    )


def create_quick_fix_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: quick-fix\n")
    write(
        root / "openspec" / "schemas" / "quick-fix" / "schema.yaml",
        """name: quick-fix
version: 1
artifacts:
  - id: problem
    generates: problem.md
    template: problem.md
    requires: []
  - id: solution
    generates: solution.md
    template: solution.md
    requires: [problem]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [solution]
apply:
  requires: [tasks]
  tracks: tasks.md
""",
    )
    change = root / "openspec" / "changes" / "fix-login-copy"
    write(change / ".openspec.yaml", "schema: quick-fix\n")
    write(change / "problem.md", "# Problem\n\n登录按钮文案错误。\n")
    write(change / "solution.md", "# Solution\n\n修改 src/auth/login_view.py，并验证 tests/auth/test_login_view.py。\n")
    write(
        change / "tasks.md",
        """# Tasks

- [ ] 修改 src/auth/login_view.py 的按钮文案。
- [ ] 运行 tests/auth/test_login_view.py。
""",
    )


def test_ce_work_pack_contains_execution_context(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(install_compound_skills(tmp_path, "ce-work")))

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    assert pack["target"] == "ce-work"
    assert pack["change"]["schema"] == "aisee-app-spec-driven"
    assert "src/auth/session.py" in pack["facts"]["derived"]["code_paths"]
    assert "tests/auth/test_session.py" in pack["facts"]["derived"]["test_paths"]
    assert pack["facts"]["derived"]["task_state"]["total"] == 4
    assert pack["facts"]["derived"]["execution"]["requires_ce_plan"] is False
    assert pack["facts"]["derived"]["execution"]["allowed_paths"] == [
        "src/auth/session.py",
        "tests/auth/test_session.py",
    ]
    candidates = pack["facts"]["derived"]["execution"]["reusable_workflow_candidates"]
    assert all(set(candidate) == {"name", "kind", "status", "reason"} for candidate in candidates)
    candidates_by_name = {candidate["name"]: candidate for candidate in candidates}
    assert candidates_by_name["aisee:implementation-bridge"]["status"] == "recommended"
    assert candidates_by_name["ce-work"]["kind"] == "compound-skill"
    assert candidates_by_name["ce-work"]["status"] == "available"
    assert pack["facts"]["derived"]["implementation_references"]["unmapped_reference_paths"] == []
    assert pack["generated"] is None
    assert pack["facts"]["parsed"]["source_map"]["parse_level"] == "structured"
    assert pack["facts"]["parsed"]["source_map"]["implementation_paths"]


def test_ce_work_pack_does_not_allow_unmapped_task_paths(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md",
        """# Tasks

- [ ] TASK-001 Implement src/auth/session.py.
- [ ] TEST-001 Verify tests/auth/test_session.py.
- [ ] TASK-001 Investigate src/auth/side_effect.py.
""",
    )

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    execution = pack["facts"]["derived"]["execution"]
    references = pack["facts"]["derived"]["implementation_references"]
    assert "src/auth/side_effect.py" not in execution["allowed_paths"]
    assert references["unmapped_reference_paths"] == ["src/auth/side_effect.py"]
    assert "SOURCE_MAP_UNMAPPED_PATH" in {gap["code"] for gap in pack["gaps"]}


def test_ce_work_pack_reports_missing_ce_plan_as_limitation(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(tmp_path / "missing-compound"))
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        "docs/requirements/auth-srs.md#FR-001 is covered.\n",
    )

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    execution = pack["facts"]["derived"]["execution"]
    candidates = {candidate["name"]: candidate for candidate in execution["reusable_workflow_candidates"]}
    assert execution["requires_ce_plan"] is True
    assert candidates["ce-plan"]["status"] == "missing"
    assert candidates["aisee:implementation-bridge"]["status"] == "recommended"


def test_ce_work_pack_routes_blockers_to_change_author_not_ce_plan(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(install_compound_skills(tmp_path, "ce-plan", "ce-work")))
    (tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md").unlink()

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    execution = pack["facts"]["derived"]["execution"]
    candidates = execution["reusable_workflow_candidates"]
    assert execution["requires_ce_plan"] is True
    assert {gap["code"] for gap in pack["gaps"]} >= {"MISSING_ARTIFACT", "TASK_GAP"}
    assert candidates == [
        {
            "name": "aisee:change-author",
            "kind": "aisee-skill",
            "status": "required",
            "reason": "fix blocking artifact or traceability gaps before execution: MISSING_ARTIFACT, TASK_GAP",
        }
    ]


def test_quick_fix_pack_does_not_require_source_map(tmp_path: Path) -> None:
    create_quick_fix_project(tmp_path)

    pack = build_context_pack(tmp_path, "fix-login-copy", "ce-work")

    assert pack["change"]["schema"] == "quick-fix"
    assert pack["facts"]["parsed"]["schema"]["source_map_required"] is False
    assert pack["facts"]["parsed"]["source_map"]["status"] == "not_applicable"
    assert "SOURCE_MAP_MISSING" not in {gap["code"] for gap in pack["gaps"]}
    assert pack["facts"]["derived"]["implementation_references"]["source"] == "schema-artifacts"
    assert pack["facts"]["derived"]["code_paths"] == ["src/auth/login_view.py"]
    assert pack["facts"]["derived"]["test_paths"] == ["tests/auth/test_login_view.py"]
    assert pack["facts"]["derived"]["execution"]["requires_ce_plan"] is False
    assert pack["facts"]["derived"]["execution"]["allowed_paths"] == [
        "src/auth/login_view.py",
        "tests/auth/test_login_view.py",
    ]


def test_verify_pack_contains_check_groups(tmp_path: Path) -> None:
    create_project(tmp_path)

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    checks = pack["facts"]["derived"]["checks"]
    assert "schema_artifacts" in checks
    assert "traceability" in checks
    assert "review_and_tests" in checks
    contract_sync = pack["facts"]["parsed"]["source_map"]["contract_sync"]
    assert contract_sync["values"]["provider_repo"]["value"] == "backend-api"
    assert contract_sync["machine_readable_contracts"] == ["contracts/openapi.yaml"]
    contract_checks = checks["contracts"]
    assert {
        "artifact": "contract-sync",
        "status": "present",
        "owner": "backend",
        "canonical_source": "contracts/openapi.yaml",
        "provider_repo": "backend-api",
        "consumer_repo": "frontend-app",
        "sync_mode": "local-http",
        "machine_readable_contracts": ["contracts/openapi.yaml"],
    } in contract_checks
    assert pack["facts"]["derived"]["drift_candidates"] == []


def test_context_pack_reports_unregistered_change_ids(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md", "docs/requirements/missing.md#FR-999 is covered.\n")

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    gap_codes = {gap["code"] for gap in pack["gaps"]}
    assert "ANCHOR_RESOLUTION_MISSING" in gap_codes
    anchor_index = pack["facts"]["parsed"]["anchor_index"]
    assert "docs/requirements/missing.md#FR-999" in anchor_index["missing_references"]


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


def test_cli_gaps_outputs_summary(tmp_path: Path) -> None:
    create_project(tmp_path)
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "gaps",
            "--change",
            "add-auth",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert data["change"]["id"] == "add-auth"
    assert data["result"]["status"] == "clear"
    assert data["gaps"] == []


def test_cli_change_inspect_outputs_summary(tmp_path: Path) -> None:
    create_project(tmp_path)
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "change",
            "inspect",
            "add-auth",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert data["change"]["id"] == "add-auth"
    assert data["schema"]["name"] == "aisee-app-spec-driven"
    assert data["anchors"]["upstream_refs"] == ["docs/requirements/auth-srs.md#FR-001"]
    assert "SPEC-001" in data["anchors"]["produced_local_ids"]
    assert data["anchors"]["resolution"]["missing_references"] == []
    assert data["task_state"]["total"] == 4
    assert "src/auth/session.py" in data["paths"]["code"]


def test_cli_change_author_check_reports_ready_change(tmp_path: Path) -> None:
    create_project(tmp_path)
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "change",
            "author-check",
            "add-auth",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert data["status"] == "ready"
    assert data["schema"]["valid"] is True
    assert data["missing_artifacts"] == []
    assert data["anchors"]["actions"]["finalize_local_ids"] == []
    assert data["next_actions"] == ["continue authoring or run openspec validate"]


def test_cli_change_author_check_reports_missing_artifact(tmp_path: Path) -> None:
    create_project(tmp_path)
    (tmp_path / "openspec" / "changes" / "add-auth" / "service-contract.md").unlink()
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "change",
            "author-check",
            "add-auth",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert data["status"] == "needs-work"
    assert data["missing_artifacts"] == [
        {"id": "service-contract", "generates": "service-contract.md", "requires": ["source-map", "specs", "change-context"]}
    ]
    assert "create service-contract.md" in data["next_actions"]


def test_author_check_allows_missing_not_required_artifact(tmp_path: Path) -> None:
    create_project(tmp_path)
    (tmp_path / "openspec" / "changes" / "add-auth" / "service-contract.md").unlink()
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        """# Source Map

## Anchor Trace

| 类型 | Ref | 标题 | 来源 | 处理方式 | 后续 artifact |
|---|---|---|---|---|---|
| FR | docs/requirements/auth-srs.md#FR-001 | 登录 | SRS | 覆盖 | specs / tasks |

## Implementation Paths

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |
| test | tests/auth/test_session.py | docs/requirements/auth-srs.md#FR-001 | modify | |

## Artifact 适用性

| Artifact | Required | Refs | 原因 / N/A 说明 | 相关约束转交 |
|---|---|---|---|---|
| service-contract.md | no | N/A | 本 change 不涉及 API 或后端服务能力 | N/A |
""",
    )
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "change",
            "author-check",
            "add-auth",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert data["missing_artifacts"] == []
    assert "create service-contract.md" not in data["next_actions"]


def test_author_check_does_not_allow_missing_core_artifact_even_if_marked_not_required(tmp_path: Path) -> None:
    create_project(tmp_path)
    (tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md").unlink()
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        """# Source Map

## Artifact 适用性

| Artifact | Required | Refs | 原因 / N/A 说明 | 相关约束转交 |
|---|---|---|---|---|
| tasks.md | no | N/A | 错误地试图跳过核心 artifact | N/A |
""",
    )
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aisee_cli.__main__",
            "change",
            "author-check",
            "add-auth",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    data = json.loads(result.stdout)
    assert {
        "id": "tasks",
        "generates": "tasks.md",
        "requires": ["specs", "change-context", "service-contract"],
    } in data["missing_artifacts"]
