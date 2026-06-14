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


def create_plugin_asset_root(root: Path, schema_name: str, schema_yaml: str, templates: tuple[str, ...]) -> Path:
    write(root / "skills" / "aisee-srs" / "SKILL.md", "# aisee:srs\n")
    write(root / "references" / "README.md", "# references\n")
    schema_dir = root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / schema_name
    write(schema_dir / "schema.yaml", schema_yaml)
    for template in templates:
        write(schema_dir / "templates" / template, f"# {template}\n")
    return root


def create_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "docs" / "requirements" / "auth-srs.md", "# Auth SRS\n\n## 登录\n\n覆盖需求：FR-001\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(
        root / "openspec" / "schemas" / "aisee-app-spec-driven" / "schema.yaml",
        """name: aisee-app-spec-driven
version: 2
capabilities:
  - source_map_routing
  - apply_execution
  - archive_authority
  - contract_helper
  - contract_sync
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
    requiredness: always
    capabilities: [primary_brief]
  - id: source-map
    generates: source-map.md
    template: source-map.md
    requires: [proposal]
    requiredness: always
    capabilities: [source_map]
  - id: specs
    generates: specs/**/*.md
    template: spec.md
    requires: [source-map]
    requiredness: always
    capabilities: [behavior_spec]
  - id: change-context
    generates: change-context.md
    template: change-context.md
    requires: [specs]
    requiredness: conditional
    na_requires_reason: true
    capabilities: [contract_surface]
  - id: service-contract
    generates: service-contract.md
    template: service-contract.md
    requires: [source-map, specs, change-context]
    requiredness: conditional
    na_requires_reason: true
    capabilities: [contract_surface, contract_sync]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, change-context, service-contract]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
archive:
  tracks:
    - tasks.md
    - source-map.md
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

## Source Context

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
capabilities:
  - apply_execution
  - archive_authority
  - quick_fix_evidence
artifacts:
  - id: problem
    generates: problem.md
    template: problem.md
    requires: []
    requiredness: always
    capabilities: [problem_statement]
  - id: solution
    generates: solution.md
    template: solution.md
    requires: [problem]
    requiredness: always
    capabilities: [solution_design]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [solution]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
archive:
  tracks:
    - tasks.md
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


def create_minimal_spec_driven_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: spec-driven\n")
    write(
        root / "openspec" / "schemas" / "spec-driven" / "schema.yaml",
        """name: spec-driven
version: 1
description: "官方轻量 schema 示例"
artifacts:
  - id: proposal
    generates: proposal.md
    template: templates/proposal.md
    requires: []
  - id: specs
    generates: specs/**/*.md
    template: templates/spec.md
    requires: [proposal]
  - id: tasks
    generates: tasks.md
    template: templates/tasks.md
    requires: [specs]
apply:
  requires: [tasks]
  tracks: tasks.md
""",
    )
    schema_templates = root / "openspec" / "schemas" / "spec-driven" / "templates"
    for template in ("proposal.md", "spec.md", "tasks.md"):
        write(schema_templates / template, f"# {template}\n")

    change = root / "openspec" / "changes" / "establish-database-migration-workflow"
    write(change / ".openspec.yaml", "schema: spec-driven\n")
    write(
        change / "proposal.md",
        """# Proposal

为数据库迁移建立稳定工作流，范围包含 src/db/migrations.py 与 tests/db/test_migrations.py。
""",
    )
    write(
        change / "specs" / "migration.md",
        """## ADDED Requirements

### Requirement: SPEC-001 Migration workflow

系统 MUST support repeatable database migrations.
""",
    )
    write(
        change / "tasks.md",
        """# Tasks

- [ ] TASK-001 在 src/db/migrations.py 中实现迁移执行入口。
- [ ] TEST-001 在 tests/db/test_migrations.py 中补充迁移验证。
""",
    )


def test_context_pack_contains_change_metadata_and_path_references(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(install_compound_skills(tmp_path, "ce-work")))

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    assert pack["target"] == "ce-work"
    assert pack["change"]["schema"] == "aisee-app-spec-driven"
    assert "src/auth/session.py" in pack["facts"]["derived"]["code_paths"]
    assert "tests/auth/test_session.py" in pack["facts"]["derived"]["test_paths"]
    assert pack["facts"]["derived"]["task_state"]["total"] == 4
    assert pack["facts"]["derived"]["implementation_references"]["unmapped_reference_paths"] == []
    assert pack["facts"]["derived"]["artifact_order"] == [
        "proposal",
        "source-map",
        "specs",
        "change-context",
        "service-contract",
        "tasks",
    ]
    assert [item["id"] for item in pack["facts"]["parsed"]["schema"]["artifacts"]] == [
        "proposal",
        "source-map",
        "specs",
        "change-context",
        "service-contract",
        "tasks",
    ]
    assert pack["generated"] is None
    assert pack["facts"]["parsed"]["source_map"]["parse_level"] == "structured"
    assert pack["facts"]["parsed"]["source_map"]["implementation_paths"]
    assert "text" not in pack["facts"]["parsed"]["artifacts"]["proposal"]
    assert "execution" not in pack["facts"]["derived"]


def test_context_pack_reports_unmapped_task_paths_without_execution_projection(tmp_path: Path) -> None:
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

    references = pack["facts"]["derived"]["implementation_references"]
    assert references["unmapped_reference_paths"] == ["src/auth/side_effect.py"]
    assert "SOURCE_MAP_UNMAPPED_PATH" in {gap["code"] for gap in pack["gaps"]}

def test_context_pack_accepts_intake_only_traceability_path(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        """# Source Map

## Upstream Sources

| Source | Path / Description | Ref | Status | Notes |
|---|---|---|---|---|
| user-input | 登录改造：摘要化输入，避免保存长提示词 | issue://AUTH-9 | confirmed | |

## Artifact 适用性

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | SPEC-001 | 需要服务接口 | tasks.md |

## Affected Paths Index

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | SPEC-001 | modify | |
| test | tests/auth/test_session.py | TEST-001 | add | |

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
        tmp_path / "openspec" / "changes" / "add-auth" / "specs" / "auth.md",
        """## ADDED Requirements

### Requirement: SPEC-001 Login

系统 MUST allow login by password.
""",
    )
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md",
        """# Tasks

- [ ] TASK-001 Provider implementation: implement src/auth/session.py for SPEC-001.
- [ ] TEST-001 Contract test: verify tests/auth/test_session.py.
""",
    )

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    traceability = pack["facts"]["derived"]["traceability"]
    assert traceability["upstream_refs"] == []
    assert traceability["mode"] == "numbered"
    assert "SPEC-001" in traceability["produced_local_ids"]
    assert pack["facts"]["parsed"]["source_reference_index"]["missing_references"] == []
    assert "SOURCE_CONTEXT_MISSING" not in {gap["code"] for gap in pack["gaps"]}


def test_context_pack_reports_source_context_missing_when_no_ref_or_number(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        """# Source Map

## Affected Paths Index

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | N/A | modify | |
""",
    )
    write(tmp_path / "openspec" / "changes" / "add-auth" / "specs" / "auth.md", "# Spec\n")
    write(tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md", "# Tasks\n\n- [ ] Implement src/auth/session.py.\n")

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    assert "SOURCE_CONTEXT_MISSING" in {gap["code"] for gap in pack["gaps"]}
    assert pack["facts"]["derived"]["traceability"]["mode"] == "empty"


def test_context_pack_blocks_when_change_schema_metadata_is_missing(tmp_path: Path) -> None:
    create_project(tmp_path)
    (tmp_path / "openspec" / "changes" / "add-auth" / ".openspec.yaml").unlink()

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    gap_codes = {gap["code"] for gap in pack["gaps"]}
    assert "SCHEMA_METADATA_MISSING" in gap_codes
    assert pack["facts"]["parsed"]["schema"]["metadata_present"] is False
    assert pack["facts"]["parsed"]["schema"]["resolved_from"] == "project-config"


def test_context_pack_blocks_when_schema_only_exists_in_plugin_assets(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    schema_dir = tmp_path / "openspec" / "schemas" / "aisee-app-spec-driven"
    schema_yaml = (schema_dir / "schema.yaml").read_text(encoding="utf-8")
    templates = tuple(path.name for path in (schema_dir / "templates").iterdir())
    plugin_root = create_plugin_asset_root(tmp_path / "mock-plugin", "aisee-app-spec-driven", schema_yaml, templates)
    monkeypatch.setenv("AISEE_PLUGIN_ASSET_ROOT", str(plugin_root))
    for path in reversed(sorted(schema_dir.rglob("*"))):
        if path.is_file():
            path.unlink()
        else:
            path.rmdir()

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    schema = pack["facts"]["parsed"]["schema"]
    blocker = next(gap for gap in pack["gaps"] if gap["code"] == "SCHEMA_NOT_INSTALLED")
    assert schema["installed"] is False
    assert schema["source_path"].endswith("mock-plugin/skills/aisee-schema-pack/assets/schema-pack/aisee-app-spec-driven/schema.yaml")
    assert blocker["suggested_fix"]["skill"] == "aisee-schema-pack"
    assert blocker["suggested_fix"]["command"].endswith("--schema aisee-app-spec-driven")


def test_context_pack_blocks_when_schema_hint_conflicts_with_metadata(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "proposal.md",
        """Schema: quick-fix

# Proposal
""",
    )

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    assert "SCHEMA_MISMATCH" in {gap["code"] for gap in pack["gaps"]}


def test_context_pack_omits_execution_routing_even_when_paths_are_unclear(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(tmp_path / "missing-compound"))
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        "docs/requirements/auth-srs.md#FR-001 is covered.\n",
    )

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    assert "execution" not in pack["facts"]["derived"]
    assert {gap["code"] for gap in pack["gaps"]} >= {"SOURCE_MAP_UNSTRUCTURED", "SOURCE_MAP_UNMAPPED_PATH"}


def test_context_pack_keeps_blocker_gaps_without_execution_projection(tmp_path: Path, monkeypatch) -> None:
    create_project(tmp_path)
    monkeypatch.setenv("AISEE_COMPOUND_SKILLS_DIR", str(install_compound_skills(tmp_path, "ce-plan", "ce-work")))
    (tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md").unlink()

    pack = build_context_pack(tmp_path, "add-auth", "ce-work")

    assert {gap["code"] for gap in pack["gaps"]} >= {"MISSING_ARTIFACT", "TASK_GAP"}
    assert "execution" not in pack["facts"]["derived"]


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
    assert "execution" not in pack["facts"]["derived"]


def test_minimal_spec_driven_schema_is_compatible_with_ce_work_pack(tmp_path: Path) -> None:
    create_minimal_spec_driven_project(tmp_path)

    pack = build_context_pack(tmp_path, "establish-database-migration-workflow", "ce-work")

    assert pack["change"]["schema"] == "spec-driven"
    assert pack["facts"]["parsed"]["schema"]["issues"] == []
    assert pack["facts"]["parsed"]["schema"]["source_map_required"] is False
    assert pack["facts"]["parsed"]["schema"]["tasks_required"] is True
    assert pack["facts"]["derived"]["implementation_references"]["source"] == "schema-artifacts"
    assert pack["facts"]["derived"]["code_paths"] == ["src/db/migrations.py"]
    assert pack["facts"]["derived"]["test_paths"] == ["tests/db/test_migrations.py"]
    assert "execution" not in pack["facts"]["derived"]
    gap_codes = {gap["code"] for gap in pack["gaps"]}
    assert "SCHEMA_CAPABILITIES_MISSING" not in gap_codes
    assert "SCHEMA_ARTIFACT_REQUIREDNESS_INVALID" not in gap_codes
    assert "SCHEMA_ARTIFACT_CAPABILITIES_MISSING" not in gap_codes


def test_artifact_order_keeps_apply_track_last_among_ready_artifacts(tmp_path: Path) -> None:
    write(tmp_path / "AGENTS.md", "# Rules\n")
    write(tmp_path / "openspec" / "config.yaml", "schema: demo\n")
    write(
        tmp_path / "openspec" / "schemas" / "demo" / "schema.yaml",
        """name: demo
version: 1
capabilities:
  - source_map_routing
  - apply_execution
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
    requiredness: always
    capabilities: [primary_brief]
  - id: source-map
    generates: source-map.md
    template: source-map.md
    requires: [proposal]
    requiredness: always
    capabilities: [source_map]
  - id: specs
    generates: specs/**/*.md
    template: spec.md
    requires: [source-map]
    requiredness: always
    capabilities: [behavior_spec]
  - id: ui-contract
    generates: ui-contract.md
    template: ui-contract.md
    requires: [source-map, specs]
    requiredness: conditional
    na_requires_reason: true
    capabilities: [contract_surface]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [source-map, specs]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
""",
    )
    schema_templates = tmp_path / "openspec" / "schemas" / "demo" / "templates"
    for template in ("proposal.md", "source-map.md", "spec.md", "ui-contract.md", "tasks.md"):
        write(schema_templates / template, f"# {template}\n")
    change = tmp_path / "openspec" / "changes" / "demo-change"
    write(change / ".openspec.yaml", "schema: demo\n")
    write(change / "proposal.md", "# Proposal\n")
    write(change / "source-map.md", "# Source Map\n")
    write(change / "specs" / "demo.md", "## ADDED Requirements\n")
    write(change / "ui-contract.md", "# UI Contract\n")
    write(change / "tasks.md", "# Tasks\n\n- [ ] TASK-001 demo\n")

    pack = build_context_pack(tmp_path, "demo-change", "aisee-verify")

    assert pack["facts"]["derived"]["artifact_order"] == [
        "proposal",
        "source-map",
        "specs",
        "ui-contract",
        "tasks",
    ]
    assert [item["id"] for item in pack["facts"]["parsed"]["schema"]["artifacts"]] == [
        "proposal",
        "source-map",
        "specs",
        "ui-contract",
        "tasks",
    ]


def test_verify_pack_keeps_schema_and_contract_metadata_without_check_groups(tmp_path: Path) -> None:
    create_project(tmp_path)

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    contract_sync = pack["facts"]["parsed"]["source_map"]["contract_sync"]
    assert contract_sync["values"]["provider_repo"]["value"] == "backend-api"
    assert contract_sync["machine_readable_contracts"] == ["contracts/openapi.yaml"]
    assert "checks" not in pack["facts"]["derived"]
    assert "drift_candidates" not in pack["facts"]["derived"]


def test_context_pack_flags_completion_evidence_without_apply_track_writeback(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "docs" / "verification" / "add-auth-test.md",
        """# Test Evidence

status: passed
""",
    )

    ce_work_pack = build_context_pack(tmp_path, "add-auth", "ce-work")
    verify_pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    assert "APPLY_TRACKS_WRITEBACK_REQUIRED" in {gap["code"] for gap in ce_work_pack["gaps"]}
    assert "APPLY_TRACKS_WRITEBACK_REQUIRED" in {gap["code"] for gap in verify_pack["gaps"]}
    assert ce_work_pack["facts"]["parsed"]["schema"]["apply_tracks"] == "tasks.md"
    assert verify_pack["facts"]["parsed"]["schema"]["apply_tracks"] == "tasks.md"
    assert ce_work_pack["evidence"]["tests"] == ["docs/verification/add-auth-test.md"]


def test_context_pack_does_not_flag_writeback_gap_after_task_sync(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md",
        """# Tasks

- [x] TASK-001 Provider implementation: implement src/auth/session.py.
- [ ] TASK-001 Consumer integration: update frontend caller.
- [ ] TEST-001 Contract test: verify tests/auth/test_session.py.
- [ ] TEST-001 Backward compatibility check: confirm login contract compatibility.
""",
    )
    write(
        tmp_path / "docs" / "verification" / "add-auth-test.md",
        """# Test Evidence

status: passed
""",
    )

    ce_work_pack = build_context_pack(tmp_path, "add-auth", "ce-work")
    verify_pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    assert "APPLY_TRACKS_WRITEBACK_REQUIRED" not in {gap["code"] for gap in ce_work_pack["gaps"]}
    assert ce_work_pack["facts"]["parsed"]["schema"]["apply_tracks"] == "tasks.md"
    assert "APPLY_TRACKS_WRITEBACK_REQUIRED" not in {gap["code"] for gap in verify_pack["gaps"]}
    assert verify_pack["facts"]["parsed"]["schema"]["apply_tracks"] == "tasks.md"


def test_context_pack_reports_missing_source_refs(tmp_path: Path) -> None:
    create_project(tmp_path)
    write(tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md", "docs/requirements/missing.md#FR-999 is covered.\n")

    pack = build_context_pack(tmp_path, "add-auth", "aisee-verify")

    gap_codes = {gap["code"] for gap in pack["gaps"]}
    assert "SOURCE_REF_RESOLUTION_MISSING" in gap_codes
    source_reference_index = pack["facts"]["parsed"]["source_reference_index"]
    assert "docs/requirements/missing.md#FR-999" in source_reference_index["missing_references"]


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
