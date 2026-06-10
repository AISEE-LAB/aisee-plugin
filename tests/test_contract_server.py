from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

from aisee_cli.contract_server import create_contract_http_server, lan_warning


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_contract_project(root: Path) -> Path:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
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
    requires: [source-map, specs]
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
    write(change / "specs" / "auth.md", "## ADDED Requirements\n")
    write(
        change / "source-map.md",
        """# Source Map

## Affected Paths Index

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | auth:API-001 | modify | |

## Artifact Applicability

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | auth:API-001 | 需要接口 | tasks.md |

## Contract Ownership / Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | |
| provider_repo | backend-api | confirmed | |
| consumer_repo | frontend-app | confirmed | |
| sync_mode | local-http | confirmed | |
""",
    )
    write(
        change / "service-contract.md",
        """# Service Contract

## 能力契约

### auth:API-001 Login

- 方法 / 路径：POST /login
""",
    )
    write(change / "tasks.md", "# Tasks\n\n- [ ] Implement src/auth/session.py.\n")
    return change


def create_non_contract_project(root: Path) -> None:
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
    write(change / "problem.md", "# Problem\n")
    write(change / "solution.md", "# Solution\n")
    write(change / "tasks.md", "# Tasks\n\n- [ ] Fix copy.\n")


def get_json(base_url: str, path: str) -> dict:
    with urlopen(f"{base_url}{path}", timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def test_contract_server_health_manifest_and_section(tmp_path: Path) -> None:
    create_contract_project(tmp_path)
    server = create_contract_http_server(tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        health = get_json(base_url, "/health")
        manifest = get_json(base_url, "/manifest")
        section = get_json(base_url, f"/changes/add-auth/contracts/service-contract/sections/{quote('能力契约')}?max_chars=20")

        assert health["status"] == "ok"
        assert manifest["changes"][0]["id"] == "add-auth"
        assert section["section"]["title"] == "能力契约"
        assert section["truncated"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_contract_server_reflects_file_changes_without_restart(tmp_path: Path) -> None:
    change = create_contract_project(tmp_path)
    server = create_contract_http_server(tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        section_path = f"/changes/add-auth/contracts/service-contract/sections/{quote('能力契约')}"
        before = get_json(base_url, section_path)
        write(
            change / "service-contract.md",
            """# Service Contract

## 能力契约

### auth:API-001 Login

- 方法 / 路径：POST /sessions
""",
        )
        after = get_json(base_url, section_path)

        assert "POST /login" in before["content"]
        assert "POST /sessions" in after["content"]
        assert before["etag"] != after["etag"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_contract_server_unknown_endpoint_returns_json_404(tmp_path: Path) -> None:
    create_contract_project(tmp_path)
    server = create_contract_http_server(tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        try:
            get_json(base_url, "/missing")
        except HTTPError as error:
            data = json.loads(error.read().decode("utf-8"))
            assert error.code == 404
            assert data["issues"][0]["code"] == "CONTRACT_HTTP_NOT_FOUND"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_contract_server_bad_max_chars_returns_json_400(tmp_path: Path) -> None:
    create_contract_project(tmp_path)
    server = create_contract_http_server(tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        try:
            get_json(base_url, "/manifest?max_chars=abc")
        except HTTPError as error:
            data = json.loads(error.read().decode("utf-8"))
            assert error.code == 400
            assert data["issues"][0]["code"] == "CONTRACT_HTTP_BAD_REQUEST"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_contract_server_lan_warning_for_non_local_hosts() -> None:
    assert lan_warning("127.0.0.1") is None
    assert lan_warning("localhost") is None
    assert lan_warning("::1") is None
    assert "LAN exposure" in str(lan_warning("0.0.0.0"))
    assert "LAN exposure" in str(lan_warning(""))


def test_contract_server_returns_not_applicable_for_non_contract_schema(tmp_path: Path) -> None:
    create_non_contract_project(tmp_path)
    server = create_contract_http_server(tmp_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        contracts = get_json(base_url, "/changes/fix-login-copy/contracts")
        sections = get_json(base_url, f"/changes/fix-login-copy/contracts/{quote('service-contract')}/sections")

        assert contracts["status"] == "not_applicable"
        assert "contract_helper capability" in contracts["reason"]
        assert sections["status"] == "not_applicable"
        assert "contract_helper capability" in sections["reason"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
