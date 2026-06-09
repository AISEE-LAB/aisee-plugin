from __future__ import annotations

from pathlib import Path

from skill_contract_helpers import EXPECTED_TAXONOMY_SECTIONS, public_skill_names, read_taxonomy


ROOT = Path(__file__).resolve().parents[1]


def test_skills_do_not_reference_shared_cli_preflight() -> None:
    skill_files = sorted((ROOT / "plugins" / "aisee-plugin" / "skills").glob("*/SKILL.md"))
    offenders = []
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        if "references/cli-preflight.md" in text or "## CLI preflight" in text:
            offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_shared_cli_preflight_document_is_not_part_of_skill_context() -> None:
    assert not (ROOT / "plugins" / "aisee-plugin" / "references" / "cli-preflight.md").exists()


def test_planning_doc_frontmatter_contract_exists_and_representative_templates_reference_it() -> None:
    contract = ROOT / "plugins" / "aisee-plugin" / "references" / "planning-doc-frontmatter.md"
    assert contract.exists()
    assert "doc_type" in contract.read_text(encoding="utf-8")

    expected = {
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-standard.md": 'doc_type: "srs"',
        "plugins/aisee-plugin/skills/aisee-ui-content/assets/ui-content-template-standard.md": 'doc_type: "ui-content"',
        "plugins/aisee-plugin/skills/aisee-architecture/assets/architecture-template-core.md": 'doc_type: "architecture"',
        "plugins/aisee-plugin/skills/aisee-design-spec/assets/design-spec-template-standard.md": 'doc_type: "design-spec"',
        "plugins/aisee-plugin/skills/aisee-design-assets/assets/design-assets-index-template.md": 'doc_type: "design-assets"',
        "plugins/aisee-plugin/skills/aisee-implementation-bridge/references/brief-template.md": 'doc_type: "implementation-brief"',
        "plugins/aisee-plugin/skills/aisee-reflect/references/output-templates.md": 'doc_type: "reflect"',
    }
    for relative_path, marker in expected.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert marker in text
        assert "source_refs:" in text
        assert "change_refs:" in text
        assert "anchors:" in text


def test_cli_outputs_keep_marketplace_recovery_hints() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "src"))

    from aisee_cli.marketplace import MARKETPLACE_ADD_COMMAND, PLUGIN_ADD_COMMAND

    assert MARKETPLACE_ADD_COMMAND == "codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main"
    assert PLUGIN_ADD_COMMAND == "codex plugin add aisee-plugin@aisee-plugin"


def test_skill_taxonomy_contract_covers_all_public_skills() -> None:
    taxonomy = read_taxonomy()

    assert set(taxonomy) == EXPECTED_TAXONOMY_SECTIONS
    assert len(taxonomy["Core Workflow"]) == 11
    assert set(taxonomy["Core Workflow"]) == {
        "aisee:flow",
        "aisee:init",
        "aisee:srs",
        "aisee:ui-content",
        "aisee:architecture",
        "aisee:change-plan",
        "aisee:change-author",
        "aisee-schema-pack",
        "aisee:implementation-bridge",
        "aisee:verify",
        "aisee:archive-guard",
    }

    classified = {skill for skills in taxonomy.values() for skill in skills}
    assert classified == public_skill_names()


def test_readme_highlights_core_workflow_taxonomy() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Skill 分层" in readme
    assert "11 个核心主流程 skill" in readme
    for skill in read_taxonomy()["Core Workflow"]:
        assert f"`{skill}`" in readme
