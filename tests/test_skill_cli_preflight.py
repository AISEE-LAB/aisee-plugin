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
        "plugins/aisee-plugin/skills/aisee-spec-migrate/assets/migration-index-template.md": 'doc_type: "spec-migration"',
        "plugins/aisee-plugin/skills/aisee-reflect/references/output-templates.md": 'doc_type: "reflect"',
    }
    for relative_path, marker in expected.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert marker in text
        assert "source_refs:" in text
        assert "change_refs:" in text


def test_planning_doc_output_templates_use_frontmatter_without_duplicate_header_metadata() -> None:
    expected = {
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-standard.md": [
            "**状态**：草稿",
            "**创建日期**：{date}",
            '**作者**：{从 AGENTS.md 或项目上下文提取，或填"待填写"}',
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-epic-main.md": [
            'doc_type: "srs"',
            "**状态**：草稿",
            "**创建日期**：{date}",
            '**作者**：{从 AGENTS.md 或项目上下文提取，或填"待填写"}',
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-epic-module.md": [
            'doc_type: "srs"',
            "**状态**：草稿",
            "**创建日期**：{date}",
            "**ID Scope**：{scope}",
        ],
    }

    for relative_path, forbidden_markers in expected.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for marker in forbidden_markers:
            if marker.startswith("doc_type:"):
                assert marker in text
            else:
                assert marker not in text


def test_srs_skill_keeps_downstream_hints_minimal() -> None:
    expected_present = {
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-standard.md": "## 7. 下游建议（可选）",
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-epic-main.md": "## 7. 下游建议（可选）",
        "plugins/aisee-plugin/skills/aisee-srs/assets/srs-template-epic-module.md": "## 7. 本模块下游建议（可选）",
        "plugins/aisee-plugin/skills/aisee-srs/references/writing-rules.md": "### Section 7：下游建议（可选）",
    }
    forbidden_markers = [
        "变更候选清单",
        "Change Plan 输入提示",
        "change-plan 输入是否已充足",
        "规模估算是粗估",
    ]

    for relative_path, required_marker in expected_present.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert required_marker in text
        for marker in forbidden_markers:
            assert marker not in text

def test_spec_migrate_template_uses_frontmatter_without_duplicate_header_metadata() -> None:
    text = (ROOT / "plugins/aisee-plugin/skills/aisee-spec-migrate/assets/migration-index-template.md").read_text(encoding="utf-8")

    assert 'doc_type: "spec-migration"' in text
    assert "source_refs:" in text
    assert "change_refs:" in text
    assert "**状态**：" not in text
    assert "**创建日期**：" not in text


def test_cli_outputs_keep_marketplace_recovery_hints() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "src"))

    from aisee_cli.marketplace import MARKETPLACE_ADD_COMMAND, PLUGIN_ADD_COMMAND

    assert MARKETPLACE_ADD_COMMAND == "codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main"
    assert PLUGIN_ADD_COMMAND == "codex plugin add aisee-plugin@aisee-plugin"


def test_skill_taxonomy_contract_covers_all_public_skills() -> None:
    taxonomy = read_taxonomy()

    assert set(taxonomy) == EXPECTED_TAXONOMY_SECTIONS
    assert taxonomy["Project Setup / Adoption"] == ["aisee:init"]
    assert taxonomy["OpenSpec Core"] == [
        "aisee:spec-migrate",
        "aisee:srs",
        "aisee:change-plan",
        "aisee:change-author",
    ]
    assert taxonomy["Memory And Knowledge"] == [
        "aisee:reflect",
        "aisee:memory",
        "aisee:knowledge",
        "aisee:knowledge-curate",
    ]
    assert set(taxonomy["Legacy / Transitional"]) == {
        "aisee:image-object",
    }

    classified = {skill for skills in taxonomy.values() for skill in skills}
    assert classified == public_skill_names()


def test_readme_highlights_core_workflow_taxonomy() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "## Skill 分层" in readme
    assert "OpenSpec companion 主推能力" in readme
    assert "`aisee:init`" in readme
    assert "`aisee:spec-migrate`" in readme
    for skill in read_taxonomy()["OpenSpec Core"]:
        assert f"`{skill}`" in readme

def test_change_plan_rules_and_templates_support_source_context_without_fake_refs() -> None:
    expected_markers = {
        "plugins/aisee-plugin/skills/aisee-change-plan/references/source-map-rules.md": "上游来源",
        "plugins/aisee-plugin/skills/aisee-change-plan/references/output-template.md": "Schema availability:",
        "plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/aisee-app-spec-driven/templates/source-map.md": "不要为了消除空值伪造",
        "plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/aisee-app-spec-driven/templates/proposal.md": "来源摘要放到 `source-map.md` 的“上游来源”",
    }
    for relative_path, marker in expected_markers.items():
        assert marker in (ROOT / relative_path).read_text(encoding="utf-8")
