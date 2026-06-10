from __future__ import annotations

from pathlib import Path

from aisee_cli.source_map import parse_source_map


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parse_source_map_structured_tables(tmp_path: Path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-auth"
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
| FR | docs/requirements/auth-srs.md#FR-001 | 登录 | SRS | covered | specs / tasks |

## Affected Paths Index

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |
| test | tests/auth/test_session.py | docs/requirements/auth-srs.md#FR-001 | add | |

## Expected Evidence Index

| Type | Path / Command | Status | Refs | Notes |
|---|---|---|---|---|
| test | docs/verification/add-auth-test-results.md | passed | docs/requirements/auth-srs.md#FR-001 | |

## Artifact Applicability

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | docs/requirements/auth-srs.md#FR-001 | 需要接口 | tasks.md |
| data-model.md | no | N/A | 不涉及持久化 | N/A |

## Contract Ownership / Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | |
| canonical_source | contracts/openapi.yaml | confirmed | |
| provider_repo | backend-api | confirmed | |
| consumer_repo | frontend-app | confirmed | |
| sync_mode | local-http | confirmed | |
| conflict_rule | canonical-source-wins | confirmed | |
| machine_readable_contract | contracts/openapi.yaml, contracts/events.yaml | confirmed | |
| version_ref | commit:abc123 | confirmed | |

## Out of Scope

- docs/requirements/auth-srs.md#FR-002 注册
""",
    )

    parsed = parse_source_map(change)

    assert parsed["parse_level"] == "structured"
    assert parsed["upstream_sources"][0]["ref"] == "docs/requirements/auth-srs.md#FR-001"
    assert parsed["source_context"][0]["refs"] == ["docs/requirements/auth-srs.md#FR-001"]
    assert parsed["implementation_paths"] == [
        {
            "kind": "code",
            "path": "src/auth/session.py",
            "refs": ["docs/requirements/auth-srs.md#FR-001"],
            "local_ids": ["FR-001"],
            "mode": "modify",
            "notes": "",
        },
        {
            "kind": "test",
            "path": "tests/auth/test_session.py",
            "refs": ["docs/requirements/auth-srs.md#FR-001"],
            "local_ids": ["FR-001"],
            "mode": "add",
            "notes": "",
        },
    ]
    assert parsed["verification_evidence"][0]["status"] == "passed"
    assert parsed["artifact_applicability"][1]["required"] == "no"
    assert parsed["contract_sync"]["values"]["contract_owner"]["value"] == "backend"
    assert parsed["contract_sync"]["values"]["canonical_source"]["value"] == "contracts/openapi.yaml"
    assert parsed["contract_sync"]["machine_readable_contracts"] == [
        "contracts/openapi.yaml",
        "contracts/events.yaml",
    ]
    assert parsed["out_of_scope"] == ["docs/requirements/auth-srs.md#FR-002 注册"]
    assert parsed["issues"] == []


def test_parse_source_map_falls_back_to_metadata_scan(tmp_path: Path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-auth"
    write(change / "source-map.md", "docs/requirements/auth-srs.md#FR-001 uses src/auth/session.py and tests/auth/test_session.py.\n")

    parsed = parse_source_map(change)

    assert parsed["parse_level"] == "metadata"
    assert parsed["implementation_paths"][0]["notes"] == "fallback path scan"
    assert "SOURCE_MAP_UNSTRUCTURED" in {item["code"] for item in parsed["issues"]}


def test_parse_source_map_keeps_legacy_section_heading_compatibility(tmp_path: Path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-auth"
    write(
        change / "source-map.md",
        """# Source Map

## Implementation Paths

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | docs/requirements/auth-srs.md#FR-001 | modify | |

## Verification Evidence

| Type | Path / Command | Status | Refs | Notes |
|---|---|---|---|---|
| test | docs/verification/add-auth-test-results.md | passed | docs/requirements/auth-srs.md#FR-001 | |
""",
    )

    parsed = parse_source_map(change)

    assert parsed["implementation_paths"][0]["path"] == "src/auth/session.py"
    assert parsed["verification_evidence"][0]["path"] == "docs/verification/add-auth-test-results.md"


def test_parse_source_map_contract_sync_legacy_labels(tmp_path: Path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-auth"
    write(
        change / "source-map.md",
        """# Source Map

## Contract Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| Contract Source | service-contract.md | confirmed | |
| Frontend Consumer | frontend-app | confirmed | |
| Backend Provider | backend-api | confirmed | |
| Sync Mode | package | confirmed | |
| External Repo / Package / Artifact Path | contracts/proto/auth.proto | confirmed | |
| Version / Commit / Tag | v1.2.3 | confirmed | |
""",
    )

    parsed = parse_source_map(change)

    values = parsed["contract_sync"]["values"]
    assert values["canonical_source"]["value"] == "service-contract.md"
    assert values["consumer_repo"]["value"] == "frontend-app"
    assert values["provider_repo"]["value"] == "backend-api"
    assert values["machine_readable_contract"]["value"] == "contracts/proto/auth.proto"
    assert values["version_ref"]["value"] == "v1.2.3"

