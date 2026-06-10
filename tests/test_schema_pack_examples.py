from __future__ import annotations

import re
from pathlib import Path

from aisee_cli.context_pack import parse_schema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PACK_ROOT = ROOT / "plugins" / "aisee-plugin" / "skills" / "aisee-schema-pack" / "assets" / "schema-pack"
PACKAGED_SCHEMA_PACK_ROOT = ROOT / "src" / "aisee_plugin_assets" / "skills"
LOCAL_ID_PATTERN = re.compile(r"(?<![A-Za-z0-9_:-])[A-Z]+-(?:NEW-)?\d+\b")
ANCHOR_PATTERN = re.compile(r"(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+#[A-Z]+-(?:NEW-)?\d+\b")


def test_app_schema_sample_change_matches_schema_artifacts() -> None:
    schema_dir = SCHEMA_PACK_ROOT / "aisee-app-spec-driven"
    example = schema_dir / "examples" / "add-passwordless-login"
    schema = parse_schema(schema_dir / "schema.yaml")

    assert (example / ".openspec.yaml").read_text(encoding="utf-8").strip() == "schema: aisee-app-spec-driven"

    for artifact in schema["artifacts"]:
        generates = artifact.generates
        if generates == "specs/**/*.md":
            assert list((example / "specs").glob("*.md"))
        elif generates:
            assert (example / generates).exists(), f"missing sample artifact: {generates}"

    source_map = (example / "source-map.md").read_text(encoding="utf-8")
    tasks = (example / "tasks.md").read_text(encoding="utf-8")
    assert "Contract Ownership / Sync" in source_map
    assert "contracts/openapi.yaml" in source_map
    assert "Provider implementation" in tasks
    assert "Consumer integration" in tasks
    assert "Backward compatibility check" in tasks


def test_app_schema_sample_change_uses_anchor_refs_and_local_ids() -> None:
    example = SCHEMA_PACK_ROOT / "aisee-app-spec-driven" / "examples" / "add-passwordless-login"
    text = "\n".join(path.read_text(encoding="utf-8") for path in example.rglob("*.md"))
    local_ids = set(LOCAL_ID_PATTERN.findall(text))
    anchors = set(ANCHOR_PATTERN.findall(text))

    assert {
        "FR-001",
        "PAGE-001",
        "FLOW-001",
        "STATE-001",
        "ARCH-001",
        "DEC-001",
        "SPEC-001",
        "API-001",
        "DATA-001",
        "TASK-001",
        "TEST-001",
    } <= local_ids
    assert "aisee/docs/requirements/auth-srs.md#FR-001" in anchors
    assert not any("-NEW-" in item for item in local_ids)


def test_schema_examples_are_repository_plugin_content_not_packaged_assets() -> None:
    source = SCHEMA_PACK_ROOT / "aisee-app-spec-driven" / "examples" / "add-passwordless-login"

    assert source.exists()
    assert not PACKAGED_SCHEMA_PACK_ROOT.exists()


def test_app_schema_templates_allow_intake_without_fake_srs_anchor() -> None:
    source_map_template = (SCHEMA_PACK_ROOT / "aisee-app-spec-driven" / "templates" / "source-map.md").read_text(encoding="utf-8")
    proposal_template = (SCHEMA_PACK_ROOT / "aisee-app-spec-driven" / "templates" / "proposal.md").read_text(encoding="utf-8")

    assert "## Intake 来源" in source_map_template
    assert "FR | docs/requirements/...#FR-001 / N/A" in source_map_template
    assert "不要为了消除空值伪造" in source_map_template
    assert "Intake 来源" in proposal_template
