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
        "plugins/aisee-plugin/skills/aisee-ui-content/assets/ui-content-template-standard.md": [
            "**状态**：草稿",
            "**创建日期**：{date}",
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-ui-content/assets/ui-content-template-enhancement.md": [
            'doc_type: "ui-content"',
            "**状态**：草稿",
            "**创建日期**：{date}",
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-ui-content/assets/ui-content-template-inventory.md": [
            'doc_type: "ui-content"',
            "**状态**：草稿",
            "**创建日期**：{date}",
        ],
        "plugins/aisee-plugin/skills/aisee-ui-content/assets/ui-content-template-epic-index.md": [
            'doc_type: "ui-content"',
            "**状态**：草稿",
            "**创建日期**：{date}",
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-ui-content/assets/ui-content-template-epic-module.md": [
            'doc_type: "ui-content"',
            "**状态**：草稿",
            "**创建日期**：{date}",
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-architecture/assets/architecture-template-core.md": [
            "**状态**：草稿",
            "**创建日期**：{date}",
            "**ID Scope**：{scope}",
        ],
        "plugins/aisee-plugin/skills/aisee-design-spec/assets/design-spec-template-standard.md": [
            "**状态**：草稿",
            "**创建日期**：{date}",
        ],
        "plugins/aisee-plugin/skills/aisee-design-spec/assets/design-spec-template-light.md": [
            'doc_type: "design-spec"',
            "**状态**：草稿",
            "**创建日期**：{date}",
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


def test_architecture_skill_keeps_change_plan_hints_fact_based() -> None:
    expected_present = {
        "plugins/aisee-plugin/skills/aisee-architecture/assets/architecture-template-core.md": "## 14. 给 aisee:change-plan 的架构提示",
        "plugins/aisee-plugin/skills/aisee-architecture/references/workflow.md": "## Phase 3 — 生成给 change-plan 的技术提示",
    }
    forbidden_markers = [
        "### 14.3 可并行边界提示",
        "### 14.4 不应横切的能力",
        "可并行边界：哪些模块从技术上相互独立",
        "不应横切的能力：例如不要把同一状态机拆散",
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
    assert taxonomy["Project Setup / Adoption"] == ["aisee:orient", "aisee:init"]
    assert len(taxonomy["Core Workflow"]) == 9
    assert set(taxonomy["Core Workflow"]) == {
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
    assert "9 个核心迭代 skill" in readme
    assert "`aisee:init`" in readme
    assert "`aisee:orient`" in readme
    for skill in read_taxonomy()["Core Workflow"]:
        assert f"`{skill}`" in readme


def test_core_skills_document_auto_cli_consumption_and_lean_projection() -> None:
    expectations = {
        "plugins/aisee-plugin/skills/aisee-implementation-bridge/SKILL.md": "默认直接读取当前 change artifacts、schema、`tasks.md`、`source-map.md`（若当前 schema 生成）和 `AGENTS.md`。",
        "plugins/aisee-plugin/skills/aisee-verify/SKILL.md": "OpenSpec artifact 合法性以 `openspec validate` 和当前 schema 为准",
        "plugins/aisee-plugin/skills/aisee-archive-guard/SKILL.md": "OpenSpec artifact 合法性和 baseline merge 仍以 `openspec validate` / `openspec archive` 为准",
    }
    for relative_path, marker in expectations.items():
        assert marker in (ROOT / relative_path).read_text(encoding="utf-8")


def test_implementation_bridge_requires_apply_track_writeback_before_work_completion() -> None:
    skill = (ROOT / "plugins/aisee-plugin/skills/aisee-implementation-bridge/SKILL.md").read_text(encoding="utf-8")

    assert "CHECKPOINT: `ce-work` 完成前，必须先回写当前 schema 的 apply tracks。" in skill
    assert "如果代码已改但 apply tracks 仍未更新，不得把该批次报告为完成。" in skill


def test_change_plan_rules_and_templates_support_source_context_without_fake_refs() -> None:
    expected_markers = {
        "plugins/aisee-plugin/skills/aisee-change-plan/references/source-map-rules.md": "上游来源",
        "plugins/aisee-plugin/skills/aisee-change-plan/references/output-template.md": "Schema availability:",
        "plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/aisee-app-spec-driven/templates/source-map.md": "不要为了消除空值伪造",
        "plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/aisee-app-spec-driven/templates/proposal.md": "来源摘要放到 `source-map.md` 的“上游来源”",
    }
    for relative_path, marker in expected_markers.items():
        assert marker in (ROOT / relative_path).read_text(encoding="utf-8")
