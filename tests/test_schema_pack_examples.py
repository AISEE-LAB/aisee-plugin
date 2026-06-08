from __future__ import annotations

import re
from pathlib import Path

from aisee_cli.context_pack import parse_schema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PACK_ROOT = ROOT / "plugins" / "aisee-plugin" / "skills" / "aisee-schema-pack" / "assets" / "schema-pack"
PACKAGED_SCHEMA_PACK_ROOT = ROOT / "src" / "aisee_plugin_assets" / "skills"
ID_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]*:[A-Z]+-\d+\b")


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


def test_app_schema_sample_change_has_registered_style_ids() -> None:
    example = SCHEMA_PACK_ROOT / "aisee-app-spec-driven" / "examples" / "add-passwordless-login"
    text = "\n".join(path.read_text(encoding="utf-8") for path in example.rglob("*.md"))
    ids = set(ID_PATTERN.findall(text))

    assert {
        "auth:FR-001",
        "auth:PAGE-001",
        "auth:FLOW-001",
        "auth:STATE-001",
        "auth:ARCH-001",
        "auth:DEC-001",
        "auth:SPEC-001",
        "auth:API-001",
        "auth:DATA-001",
        "auth:TASK-001",
        "auth:TEST-001",
    } <= ids
    assert not any("-NEW-" in item for item in ids)


def test_schema_examples_are_repository_plugin_content_not_packaged_assets() -> None:
    source = SCHEMA_PACK_ROOT / "aisee-app-spec-driven" / "examples" / "add-passwordless-login"

    assert source.exists()
    assert not PACKAGED_SCHEMA_PACK_ROOT.exists()
