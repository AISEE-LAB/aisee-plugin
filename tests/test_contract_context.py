from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from aisee_cli.contract import build_contract_get, build_contract_manifest, build_contract_summary


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


def create_contract_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(root / ".aisee" / "id-registry.json", '{"version":1,"scopes":{}}\n')
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
  - id: ui-contract
    generates: ui-contract.md
    template: ui-contract.md
    requires: [source-map, specs]
  - id: service-contract
    generates: service-contract.md
    template: service-contract.md
    requires: [source-map, specs]
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
    write(change / "specs" / "auth.md", "## ADDED Requirements\n")
    write(
        change / "source-map.md",
        """# Source Map

## Affected Paths Index

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | auth:API-001 | modify | |
| test | tests/auth/test_session.py | auth:TEST-001 | add | |

## Artifact Applicability

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | auth:API-001 | 需要接口 | tasks.md |
| ui-contract.md | yes | auth:PAGE-001 | 需要页面 | service-contract.md |

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
        change / "service-contract.md",
        """# Service Contract

## 契约归属与同步

Contract owner is backend.

## 能力契约

### auth:API-001 Login

- 方法 / 路径：POST /login
- 响应结构：token
""",
    )
    write(
        change / "ui-contract.md",
        """# UI Contract

## 前端数据需求

登录页需要 auth:API-001。
""",
    )
    write(
        change / "tasks.md",
        """# Tasks

- [ ] Implement src/auth/session.py.
- [ ] Verify tests/auth/test_session.py.
""",
    )


def test_contract_manifest_lists_change_contracts(tmp_path: Path) -> None:
    create_contract_project(tmp_path)

    manifest = build_contract_manifest(tmp_path)

    assert manifest["status"] == "ok"
    assert manifest["changes"][0]["id"] == "add-auth"
    assert manifest["changes"][0]["contract_sync"]["values"]["provider_repo"]["value"] == "backend-api"
    artifacts = {item["id"] for item in manifest["changes"][0]["contracts"]}
    assert {"service-contract", "ui-contract"} <= artifacts


def test_contract_manifest_marks_not_required_contracts(tmp_path: Path) -> None:
    create_contract_project(tmp_path)
    write(
        tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md",
        """# Source Map

## Artifact Applicability

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | no | N/A | 本 change 不涉及 API | N/A |
| ui-contract.md | yes | auth:PAGE-001 | 需要页面 | tasks.md |
""",
    )

    manifest = build_contract_manifest(tmp_path)
    service = next(item for item in manifest["changes"][0]["contracts"] if item["id"] == "service-contract")

    assert service["required"] is False
    assert service["status"] == "not_required"
    assert service["reason"] == "本 change 不涉及 API"


def test_contract_summary_returns_section_index_without_raw_dump(tmp_path: Path) -> None:
    create_contract_project(tmp_path)

    summary = build_contract_summary(tmp_path, "add-auth")

    service = next(item for item in summary["contracts"] if item["id"] == "service-contract")
    assert any(item["id"] == "契约归属与同步" for item in service["sections"])
    assert "POST /login" not in service["summary"]


def test_contract_get_returns_selected_section_with_etag(tmp_path: Path) -> None:
    create_contract_project(tmp_path)

    result = build_contract_get(
        tmp_path,
        "add-auth",
        "service-contract",
        section="能力契约",
        max_chars=30,
    )

    assert result["section"]["title"] == "能力契约"
    assert result["source_files"] == ["openspec/changes/add-auth/service-contract.md"]
    assert len(result["etag"]) == 64
    assert result["truncated"] is True
    assert result["max_chars"] == 30


def test_contract_cli_outputs_json(tmp_path: Path) -> None:
    create_contract_project(tmp_path)

    result = run_aisee(tmp_path, "contract", "get", "--change", "add-auth", "--artifact", "service-contract", "--section", "能力契约", "--json")
    data = json.loads(result.stdout)

    assert result.stderr == ""
    assert data["status"] == "ok"
    assert data["artifact"]["id"] == "service-contract"


def test_contract_cli_missing_section_returns_stable_error(tmp_path: Path) -> None:
    create_contract_project(tmp_path)

    result = run_aisee(
        tmp_path,
        "contract",
        "get",
        "--change",
        "add-auth",
        "--artifact",
        "service-contract",
        "--section",
        "missing",
        "--json",
        check=False,
    )
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert data["issues"][0]["code"] == "CONTRACT_CONTEXT_ERROR"


def test_contract_get_rejects_unsafe_change_name(tmp_path: Path) -> None:
    create_contract_project(tmp_path)

    result = run_aisee(
        tmp_path,
        "contract",
        "get",
        "--change",
        "../add-auth",
        "--artifact",
        "service-contract",
        "--json",
        check=False,
    )
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert data["issues"][0]["code"] == "CONTRACT_CONTEXT_ERROR"
    assert "unsafe change name" in data["message"]


def test_contract_get_rejects_artifact_path_outside_change(tmp_path: Path) -> None:
    create_contract_project(tmp_path)
    write(
        tmp_path / "openspec" / "schemas" / "aisee-app-spec-driven" / "schema.yaml",
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
  - id: service-contract
    generates: ../secret.md
    template: service-contract.md
    requires: [source-map]
apply:
  requires: []
""",
    )
    write(tmp_path / "openspec" / "changes" / "secret.md", "# Secret\n\nTOKEN=secret\n")

    result = run_aisee(
        tmp_path,
        "contract",
        "get",
        "--change",
        "add-auth",
        "--artifact",
        "service-contract",
        "--raw",
        "--json",
        check=False,
    )
    data = json.loads(result.stderr)

    assert result.returncode == 2
    assert data["issues"][0]["code"] == "CONTRACT_CONTEXT_ERROR"
    assert "escapes the change directory" in data["message"]
