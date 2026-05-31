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
        root / ".aisee" / "id-registry.json",
        json.dumps(
            {
                "version": 1,
                "scopes": {
                    "auth": {
                        "counters": {"API": 1, "TEST": 1},
                        "ids": {
                            "auth:API-001": {
                                "type": "API",
                                "number": 1,
                                "status": "active",
                                "title": "登录接口",
                                "owner": "openspec/changes/add-auth/source-map.md",
                            },
                            "auth:TEST-001": {
                                "type": "TEST",
                                "number": 1,
                                "status": "active",
                                "title": "登录验证",
                                "owner": "openspec/changes/add-auth/source-map.md",
                            },
                        },
                    }
                },
            },
            ensure_ascii=False,
        )
        + "\n",
    )
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
  - id: service-contract
    generates: service-contract.md
    template: service-contract.md
    requires: [specs]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, service-contract]
apply:
  requires: [tasks]
  tracks: tasks.md
""",
    )
    change = root / "openspec" / "changes" / "add-auth"
    write(change / ".openspec.yaml", "schema: aisee-app-spec-driven\n")
    write(change / "proposal.md", "# Proposal\n")
    write(
        change / "source-map.md",
        """# Source Map

## Implementation Paths

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | auth:API-001 | modify | |
| test | tests/auth/test_session.py | auth:TEST-001 | add | |

## Artifact Applicability

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | auth:API-001 | 需要接口 | tasks.md |
""",
    )
    write(change / "specs" / "auth.md", "## ADDED Requirements\n")
    write(change / "service-contract.md", "src/auth/session.py\n")
    write(change / "tasks.md", f"# Tasks\n\n- [{task_mark}] Implement src/auth/session.py.\n")


def create_device_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-device-spec-driven\n")
    write(root / ".aisee" / "id-registry.json", '{"version":1,"scopes":{}}\n')
    write(
        root / "openspec" / "schemas" / "aisee-device-spec-driven" / "schema.yaml",
        """name: aisee-device-spec-driven
version: 3
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
  - id: design
    generates: design.md
    template: design.md
    requires: [specs]
  - id: hardware-contract
    generates: hardware-contract.md
    template: hardware-contract.md
    requires: [design]
  - id: firmware-contract
    generates: firmware-contract.md
    template: firmware-contract.md
    requires: [design, hardware-contract]
  - id: verification-contract
    generates: verification-contract.md
    template: verification-contract.md
    requires: [hardware-contract, firmware-contract]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs, design, hardware-contract, firmware-contract, verification-contract]
apply:
  requires: [tasks]
  tracks: tasks.md
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


def test_context_pack_adds_doc_review_focus_and_evidence(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "docs" / "reviews" / "add-auth-doc-review.md", "# Review\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "# Test\n")

    data = run_json(tmp_path, "context", "pack", "--change", "add-auth", "--for", "ce-doc-review", "--json")

    assert data["facts"]["derived"]["review"]["focus"][0] == "schema_artifacts"
    assert data["evidence"]["ce_doc_review"] == ["docs/reviews/add-auth-doc-review.md"]
    assert data["evidence"]["tests"] == ["docs/verification/add-auth-test-results.md"]


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
    write(tmp_path / "docs" / "reviews" / "add-auth-code-review.md", "- P1 accepted risk: legacy endpoint remains unchanged\n")
    write(tmp_path / "docs" / "verification" / "add-auth-openspec-validate.md", "passed\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "archive-check", "add-auth", "--json")

    assert data["status"] == "archive-ready"
    assert data["summary"]["blocker"] == 0
    assert data["evidence"]["details"]["accepted_risks"][0]["text"].startswith("- P1 accepted risk")


def test_na_artifact_without_reason_is_verify_risk(tmp_path: Path) -> None:
    create_change_project(tmp_path, task_mark="x")
    write(tmp_path / "openspec" / "changes" / "add-auth" / "service-contract.md", "N/A\n")
    write(tmp_path / "docs" / "verification" / "add-auth-test-results.md", "passed\n")

    data = run_json(tmp_path, "change", "verify-check", "add-auth", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "NA_REASON_MISSING" for item in data["warnings"])
