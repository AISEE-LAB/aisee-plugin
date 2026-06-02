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

| Source | Path / Description | Source ID | Status | Notes |
|---|---|---|---|---|
| SRS | docs/requirements/auth-srs.md | SRC-001 | confirmed | |

## ID Trace

| Type | ID | Title | Source | Handling | Artifact |
|---|---|---|---|---|---|
| FR | auth:FR-001 | 登录 | SRS | covered | specs / tasks |

## Affected Paths Index

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | auth:API-001 | modify | |
| test | tests/auth/test_session.py | auth:TEST-001 | add | |

## Expected Evidence Index

| Type | Path / Command | Status | IDs | Notes |
|---|---|---|---|---|
| test | docs/verification/add-auth-test-results.md | passed | auth:TEST-001 | |

## Artifact Applicability

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| service-contract.md | yes | auth:API-001 | 需要接口 | tasks.md |
| data-model.md | no | N/A | 不涉及持久化 | N/A |

## Out of Scope

- auth:FR-002 注册
""",
    )

    parsed = parse_source_map(change)

    assert parsed["parse_level"] == "structured"
    assert parsed["upstream_sources"][0]["path"] == "docs/requirements/auth-srs.md"
    assert parsed["id_trace"][0]["ids"] == ["auth:FR-001"]
    assert parsed["implementation_paths"] == [
        {
            "kind": "code",
            "path": "src/auth/session.py",
            "ids": ["auth:API-001"],
            "mode": "modify",
            "notes": "",
        },
        {
            "kind": "test",
            "path": "tests/auth/test_session.py",
            "ids": ["auth:TEST-001"],
            "mode": "add",
            "notes": "",
        },
    ]
    assert parsed["verification_evidence"][0]["status"] == "passed"
    assert parsed["artifact_applicability"][1]["required"] == "no"
    assert parsed["out_of_scope"] == ["auth:FR-002 注册"]
    assert parsed["issues"] == []


def test_parse_source_map_falls_back_to_metadata_scan(tmp_path: Path) -> None:
    change = tmp_path / "openspec" / "changes" / "add-auth"
    write(change / "source-map.md", "auth:FR-001 uses src/auth/session.py and tests/auth/test_session.py.\n")

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

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/session.py | auth:API-001 | modify | |

## Verification Evidence

| Type | Path / Command | Status | IDs | Notes |
|---|---|---|---|---|
| test | docs/verification/add-auth-test-results.md | passed | auth:TEST-001 | |
""",
    )

    parsed = parse_source_map(change)

    assert parsed["implementation_paths"][0]["path"] == "src/auth/session.py"
    assert parsed["verification_evidence"][0]["path"] == "docs/verification/add-auth-test-results.md"
