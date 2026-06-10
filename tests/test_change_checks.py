from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_aisee(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_json(root: Path, *args: str) -> dict:
    result = run_aisee(root, *args)
    return json.loads(result.stdout)


def create_change_project(root: Path, *, task_mark: str = " ") -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(
        root / "aisee" / "registry" / "sources.json",
        json.dumps(
            {
                "version": 1,
                "sources": [],
            },
            ensure_ascii=False,
        )
        + "\n",
    )
    write(
        root / "openspec" / "schemas" / "aisee-app-spec-driven" / "schema.yaml",
        """name: aisee-app-spec-driven
version: 2
capabilities:
  - source_map_traceability
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
  - id: service-contract
    generates: service-contract.md
    template: service-contract.md
    requires: [specs]
    requiredness: conditional
    na_requires_reason: true
    capabilities: [contract_surface, contract_sync]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, service-contract]
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
    change = root / "openspec" / "changes" / "add-auth"
    write(change / ".openspec.yaml", "schema: aisee-app-spec-driven\n")
    write(change / "proposal.md", "# Proposal\n")
    write(
        change / "source-map.md",
        """# Source Map

## Implementation Paths

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |
| test | tests/auth/test_session.py | docs/requirements/auth-srs.md#FR-001 | add | |

## Artifact Applicability

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | docs/requirements/auth-srs.md#FR-001 | 需要接口 | tasks.md |

## Contract Ownership / Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | |
| canonical_source | service-contract.md | confirmed | |
| provider_repo | backend-api | confirmed | |
| consumer_repo | frontend-app | confirmed | |
| sync_mode | local-http | confirmed | |
| machine_readable_contract | contracts/openapi.yaml | confirmed | |
""",
    )
    write(root / "docs" / "requirements" / "auth-srs.md", "# Auth SRS\n\n## 登录\n\n覆盖需求：FR-001\n")
    write(change / "specs" / "auth.md", "## ADDED Requirements\n\n### Requirement: SPEC-001 Login\n")
    write(change / "service-contract.md", "src/auth/session.py\n")
    write(
        change / "tasks.md",
        f"""# Tasks

- [{task_mark}] Provider implementation: implement src/auth/session.py.
- [{task_mark}] Consumer integration: update frontend caller.
- [{task_mark}] Contract test: validate provider and consumer compatibility.
- [{task_mark}] Backward compatibility check: confirm login contract compatibility.
""",
    )


def create_device_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-device-spec-driven\n")
    write(
        root / "openspec" / "schemas" / "aisee-device-spec-driven" / "schema.yaml",
        """name: aisee-device-spec-driven
version: 3
capabilities:
  - source_map_traceability
  - apply_execution
  - archive_authority
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
  - id: design
    generates: design.md
    template: design.md
    requires: [specs]
    requiredness: always
    capabilities: [design_spec]
  - id: hardware-contract
    generates: hardware-contract.md
    template: hardware-contract.md
    requires: [design]
    requiredness: conditional
    na_requires_reason: true
    capabilities: [device_contract]
  - id: firmware-contract
    generates: firmware-contract.md
    template: firmware-contract.md
    requires: [design, hardware-contract]
    requiredness: conditional
    na_requires_reason: true
    capabilities: [device_contract]
  - id: verification-contract
    generates: verification-contract.md
    template: verification-contract.md
    requires: [hardware-contract, firmware-contract]
    requiredness: always
    capabilities: [device_contract, verification_contract]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, design, hardware-contract, firmware-contract, verification-contract]
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
    change = root / "openspec" / "changes" / "sample-sensor"
    write(change / ".openspec.yaml", "schema: aisee-device-spec-driven\n")
    for filename in (
        "proposal.md",
        "source-map.md",
        "design.md",
        "hardware-contract.md",
        "firmware-contract.md",
        "verification-contract.md",
        "tasks.md",
    ):
        write(change / filename, "# Artifact\n")
    write(change / "specs" / "sensor.md", "## ADDED Requirements\n")
    write(change / "tasks.md", "# Tasks\n\n- [x] Verify board behavior.\n")


def create_quick_fix_project(root: Path, *, task_mark: str = "x") -> None:
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
    write(change / "solution.md", "# Solution\n\n修改 src/auth/login_view.py。\n")
    write(change / "tasks.md", f"# Tasks\n\n- [{task_mark}] 修改 src/auth/login_view.py。\n- [{task_mark}] 运行 tests/auth/test_login_view.py。\n")


def create_quick_research_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: quick-research\n")
    write(
        root / "openspec" / "schemas" / "quick-research" / "schema.yaml",
        """name: quick-research
version: 1
capabilities:
  - research_only
  - archive_authority
artifacts:
  - id: question
    generates: question.md
    template: question.md
    requires: []
    requiredness: always
    capabilities: [research_question]
  - id: findings
    generates: findings.md
    template: findings.md
    requires: [question]
    requiredness: always
    capabilities: [research_findings]
  - id: recommendation
    generates: recommendation.md
    template: recommendation.md
    requires: [findings]
    requiredness: always
    capabilities: [research_recommendation]
archive:
  tracks:
    - recommendation.md
""",
    )
    change = root / "openspec" / "changes" / "research-cache"
    write(change / ".openspec.yaml", "schema: quick-research\n")
    write(change / "question.md", "# Question\n\n是否引入缓存？\n")
    write(change / "findings.md", "# Findings\n\n官方文档和现有代码分析表明可以引入本地缓存。\n")
    write(change / "recommendation.md", "# Recommendation\n\n有条件支持，后续另起实现 change。\n")


def create_opsx_collab_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: opsx-collab-pr-loop\n")
    write(
        root / "openspec" / "schemas" / "opsx-collab-pr-loop" / "schema.yaml",
        """name: opsx-collab-pr-loop
version: 1
capabilities:
  - apply_execution
  - archive_authority
artifacts:
  - id: intake
    generates: loop/intake.md
    template: intake.md
    requires: []
    requiredness: always
    capabilities: [intake_brief]
  - id: research-plan
    generates: loop/research-plan.md
    template: research-plan.md
    requires: [intake]
    requiredness: always
    capabilities: [research_plan]
  - id: implementation
    generates: loop/implementation.md
    template: implementation.md
    requires: [research-plan]
    requiredness: always
    capabilities: [implementation_record]
  - id: checkpoints
    generates: loop/checkpoints.md
    template: checkpoints.md
    requires: [implementation]
    requiredness: always
    capabilities: [checkpoint_log]
apply:
  requires: [research-plan]
  tracks: loop/implementation.md
archive:
  tracks:
    - loop/implementation.md
    - loop/checkpoints.md
""",
    )
    change = root / "openspec" / "changes" / "review-auth-pr"
    write(change / ".openspec.yaml", "schema: opsx-collab-pr-loop\n")
    write(change / "loop" / "intake.md", "# Intake\n\nPR review request.\n")
    write(change / "loop" / "research-plan.md", "# Research Plan\n\nCheck compatibility and correctness.\n")
    write(change / "loop" / "implementation.md", "# Implementation\n\nReview findings recorded.\n")
    write(change / "loop" / "checkpoints.md", "# Checkpoints\n\n本轮完成。\n")


def create_docsite_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-docsite-driven\n")
    write(
        root / "openspec" / "schemas" / "aisee-docsite-driven" / "schema.yaml",
        """name: aisee-docsite-driven
version: 1
capabilities:
  - apply_execution
  - archive_authority
  - docsite_evidence
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
    requiredness: always
    capabilities: [primary_brief]
  - id: doc-change
    generates: doc-change.md
    template: doc-change.md
    requires: [proposal]
    requiredness: always
    capabilities: [doc_change]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [doc-change]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
archive:
  tracks:
    - tasks.md
    - doc-change.md
""",
    )
    change = root / "openspec" / "changes" / "update-docs"
    write(change / ".openspec.yaml", "schema: aisee-docsite-driven\n")
    write(change / "proposal.md", "# Proposal\n")
    write(change / "doc-change.md", "# Doc Change\n")
    write(change / "tasks.md", "# Tasks\n\n- [x] 更新文档页面。\n- [x] 完成 Archive Gate。\n")


def create_infra_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: infra-change\n")
    write(
        root / "openspec" / "schemas" / "infra-change" / "schema.yaml",
        """name: infra-change
version: 1
capabilities:
  - apply_execution
  - archive_authority
  - infra_evidence
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
    requiredness: always
    capabilities: [primary_brief]
  - id: impact-assessment
    generates: impact-assessment.md
    template: impact-assessment.md
    requires: [proposal]
    requiredness: always
    capabilities: [infra_impact]
  - id: rollback-plan
    generates: rollback-plan.md
    template: rollback-plan.md
    requires: [proposal]
    requiredness: always
    capabilities: [infra_rollback]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [impact-assessment, rollback-plan]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
archive:
  tracks:
    - tasks.md
    - rollback-plan.md
""",
    )
    change = root / "openspec" / "changes" / "update-ci"
    write(change / ".openspec.yaml", "schema: infra-change\n")
    write(change / "proposal.md", "# Proposal\n")
    write(change / "impact-assessment.md", "# Impact\n")
    write(change / "rollback-plan.md", "# Rollback\n")
    write(change / "tasks.md", "# Tasks\n\n- [x] 更新 CI 配置。\n")


def create_security_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: security-audit\n")
    write(
        root / "openspec" / "schemas" / "security-audit" / "schema.yaml",
        """name: security-audit
version: 1
capabilities:
  - apply_execution
  - archive_authority
  - security_evidence
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
    requiredness: always
    capabilities: [primary_brief]
  - id: threat-model
    generates: threat-model.md
    template: threat-model.md
    requires: [proposal]
    requiredness: always
    capabilities: [threat_model]
  - id: specs
    generates: specs/**/*.md
    template: spec.md
    requires: [threat-model]
    requiredness: always
    capabilities: [behavior_spec]
  - id: design
    generates: design.md
    template: design.md
    requires: [proposal]
    requiredness: always
    capabilities: [design_spec]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, design]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
archive:
  tracks:
    - tasks.md
    - threat-model.md
""",
    )
    change = root / "openspec" / "changes" / "secure-login"
    write(change / ".openspec.yaml", "schema: security-audit\n")
    write(change / "proposal.md", "# Proposal\n")
    write(change / "threat-model.md", "# Threat Model\n")
    write(change / "specs" / "security.md", "## ADDED Requirements\n")
    write(change / "design.md", "# Design\n")
    write(change / "tasks.md", "# Tasks\n\n- [x] 修复认证风险。\n")


def test_change_inspect_uses_current_schema_artifacts(tmp_path: Path) -> None:
    create_device_project(tmp_path)

    data = run_json(tmp_path, "change", "inspect", "sample-sensor", "--json")

    artifact_ids = [item["id"] for item in data["artifacts"]]
    assert data["schema"]["name"] == "aisee-device-spec-driven"
    assert "hardware-contract" in artifact_ids
    assert "verification-contract" in artifact_ids
    assert "ui-contract" not in artifact_ids


def test_verify_check_reports_risk_when_evidence_missing(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")

    data = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "TEST_EVIDENCE_MISSING" for item in data["warnings"])


def test_verify_check_warns_when_required_service_contract_lacks_sync_metadata(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        """# Source Map

## Implementation Paths

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |
| test | tests/auth/test_session.py | docs/requirements/auth-srs.md#FR-001 | add | |

## Artifact Applicability

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | docs/requirements/auth-srs.md#FR-001 | 需要接口 | tasks.md |
""",
    )
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "CONTRACT_SYNC_METADATA_MISSING" for item in data["warnings"])


def test_verify_check_accepts_chinese_provider_consumer_task_terms(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "tasks.md",
        """# Tasks

- [x] 提供方实现：更新 src/auth/session.py。
- [x] 消费方接入：更新前端调用。
- [x] 契约测试：验证 provider / consumer 契约一致性。
- [x] 兼容性检查：确认登录契约兼容。
""",
    )
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")
    warning_codes = {item["code"] for item in data["warnings"]}

    assert "CONTRACT_PROVIDER_TASK_MISSING" not in warning_codes
    assert "CONTRACT_CONSUMER_TASK_MISSING" not in warning_codes
    assert "CONTRACT_TEST_TASK_MISSING" not in warning_codes


def test_archive_check_blocks_open_tasks_and_fail_flag(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark=" ")

    result = run_aisee(
        tmp_path,
        "change",
        "archive-check",
        "add-auth",
        "--json",
        "--fail-on-blocker",
        check=False,
    )
    data = json.loads(result.stdout)

    assert result.returncode == 1
    assert data["status"] == "blocked"
    assert any(item["code"] == "TASKS_OPEN" for item in data["blockers"])


def test_archive_check_blocks_missing_validate_evidence(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "archive-check", "add-auth", "--json")

    assert data["status"] == "blocked"
    assert any(item["code"] == "VALIDATE_EVIDENCE_MISSING" for item in data["blockers"])


def test_context_pack_adds_doc_review_focus_and_evidence(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "reviews" / "add-auth-doc-review.md", "# Review\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "# Test\n")

    data = run_json(tmp_path, "context", "pack", "--change", "add-auth", "--for", "ce-doc-review", "--json")

    assert data["facts"]["derived"]["review"]["focus"][0] == "schema_artifacts"
    assert data["evidence"]["ce_doc_review"] == ["docs/reviews/add-auth-doc-review.md"]
    assert data["evidence"]["tests"] == ["docs/verification/add-auth-test-results.md"]


def test_context_pack_separates_aisee_reviewer_lens_from_ce_review(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "reviews" / "add-auth-aisee-implementation-reviewer.md", "- P1 implementation drift remains open\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "# Test\n")

    data = run_json(tmp_path, "context", "pack", "--change", "add-auth", "--for", "aisee-verify", "--json")

    assert data["evidence"]["aisee_review_lens"] == ["docs/reviews/add-auth-aisee-implementation-reviewer.md"]
    assert data["evidence"]["ce_code_review"] == []
    assert data["evidence"]["details"]["aisee_review_lens"][0]["path"] == "docs/reviews/add-auth-aisee-implementation-reviewer.md"
    assert data["evidence"]["details"]["reviews"] == []


def test_verify_check_blocks_failed_validate_or_test_evidence(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "verification" / "add-auth-openspec-validate.md", "FAILED: spec error\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")

    assert data["status"] == "blocked"
    assert any(item["code"] == "VALIDATE_FAILED" for item in data["blockers"])
    assert data["evidence"]["details"]["openspec_validate"]["status"] == "failed"


def test_review_p1_is_risk_for_verify_and_blocker_for_archive(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "reviews" / "add-auth-code-review.md", "- P1 source-map missing test detail\n")
    write(tmp_path / "docs" / "verification" / "add-auth-openspec-validate.md", "passed\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    verify = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")
    archive = run_json(tmp_path, "change", "archive-check", "add-auth", "--json")

    assert verify["status"] == "risk"
    assert any(item["code"] == "REVIEW_P1_OPEN" for item in verify["warnings"])
    assert archive["status"] == "blocked"
    assert any(item["code"] == "REVIEW_P1_OPEN" for item in archive["blockers"])


def test_accepted_review_finding_allows_archive_ready(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(
        tmp_path / "docs" / "reviews" / "add-auth-code-review.md",
        "- P1 accepted risk: legacy endpoint remains unchanged; owner: platform; reason: backward compatibility; impact: existing endpoint only; follow-up: remove in next auth cleanup\n",
    )
    write(tmp_path / "docs" / "verification" / "add-auth-openspec-validate.md", "passed\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "archive-check", "add-auth", "--json")

    assert data["status"] == "archive-ready"
    assert data["summary"]["blocker"] == 0
    assert data["evidence"]["details"]["accepted_risks"][0]["text"].startswith("- P1 accepted risk")


def test_incomplete_accepted_risk_blocks_archive(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "reviews" / "add-auth-code-review.md", "- P1 accepted risk: legacy endpoint remains unchanged\n")
    write(tmp_path / "docs" / "verification" / "add-auth-openspec-validate.md", "passed\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "archive-check", "add-auth", "--json")

    assert data["status"] == "blocked"
    assert any(item["code"] == "ACCEPTED_RISK_INCOMPLETE" for item in data["blockers"])


def test_na_artifact_without_reason_is_verify_risk(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "openspec" / "changes" / "add-auth" / "service-contract.md", "N/A\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "NA_REASON_MISSING" for item in data["warnings"])


def test_quick_fix_archive_check_ignores_missing_source_map(tmp_path: Path) -> None:
    create_quick_fix_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "verification" / "fix-login-copy-openspec-validate.md", "passed\n")
    write(tmp_path / "docs" / "verification" / "fix-login-copy-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "archive-check", "fix-login-copy", "--json")

    assert data["status"] == "archive-ready"
    assert "SOURCE_MAP_MISSING" not in {item["code"] for item in data["issues"]}
    assert data["summary"]["blocker"] == 0


def test_quick_research_verify_and_archive_do_not_require_tasks_or_tests(tmp_path: Path) -> None:
    create_quick_research_project(tmp_path)
    write(tmp_path / "docs" / "verification" / "research-cache-openspec-validate.md", "passed\n")

    verify = run_json(tmp_path, "change", "verify-check", "research-cache", "--json")
    archive = run_json(tmp_path, "change", "archive-check", "research-cache", "--json")

    assert verify["status"] == "ready"
    assert "TASKS_MISSING" not in {item["code"] for item in verify["issues"]}
    assert "TEST_EVIDENCE_MISSING" not in {item["code"] for item in verify["issues"]}
    assert archive["status"] == "archive-ready"


def test_opsx_collab_verify_and_archive_do_not_require_tasks_md(tmp_path: Path) -> None:
    create_opsx_collab_project(tmp_path)
    write(tmp_path / "docs" / "verification" / "review-auth-pr-openspec-validate.md", "passed\n")

    verify = run_json(tmp_path, "change", "verify-check", "review-auth-pr", "--json")
    archive = run_json(tmp_path, "change", "archive-check", "review-auth-pr", "--json")

    assert verify["status"] == "ready"
    assert "TASKS_MISSING" not in {item["code"] for item in verify["issues"]}
    assert "TASK_GAP" not in {item["code"] for item in verify["issues"]}
    assert archive["status"] == "archive-ready"


def test_docsite_archive_requires_domain_evidence(tmp_path: Path) -> None:
    create_docsite_project(tmp_path)
    write(tmp_path / "docs" / "verification" / "update-docs-openspec-validate.md", "passed\n")

    missing = run_json(tmp_path, "change", "archive-check", "update-docs", "--json")
    assert missing["status"] == "blocked"
    assert any(item["code"] == "SCHEMA_EVIDENCE_MISSING" for item in missing["blockers"])

    write(tmp_path / "docs" / "verification" / "update-docs-build.md", "passed\n")
    ready = run_json(tmp_path, "change", "archive-check", "update-docs", "--json")
    assert ready["status"] == "archive-ready"


def test_infra_archive_requires_rollback_or_post_change_evidence(tmp_path: Path) -> None:
    create_infra_project(tmp_path)
    write(tmp_path / "docs" / "verification" / "update-ci-openspec-validate.md", "passed\n")

    data = run_json(tmp_path, "change", "archive-check", "update-ci", "--json")

    assert data["status"] == "blocked"
    assert any(item["code"] == "SCHEMA_EVIDENCE_MISSING" for item in data["blockers"])


def test_security_failed_schema_evidence_blocks_archive(tmp_path: Path) -> None:
    create_security_project(tmp_path)
    write(tmp_path / "docs" / "verification" / "secure-login-openspec-validate.md", "passed\n")
    write(tmp_path / "docs" / "verification" / "secure-login-sast.md", "FAILED: high risk finding\n")

    data = run_json(tmp_path, "change", "archive-check", "secure-login", "--json")

    assert data["status"] == "blocked"
    assert any(item["code"] == "SCHEMA_EVIDENCE_FAILED" for item in data["blockers"])
