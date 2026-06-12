from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_change_plan_uses_mermaid_for_dependency_graph_contract() -> None:
    output_template = (ROOT / "plugins/aisee-plugin/skills/aisee-change-plan/references/output-template.md").read_text(encoding="utf-8")
    skill_text = (ROOT / "plugins/aisee-plugin/skills/aisee-change-plan/SKILL.md").read_text(encoding="utf-8")
    algorithm_text = (ROOT / "plugins/aisee-plugin/skills/aisee-change-plan/references/change-boundary-algorithm.md").read_text(encoding="utf-8")

    assert "## Mermaid 依赖图" in output_template
    assert "```mermaid" in output_template
    assert "flowchart TD" in output_template
    assert "简单依赖链使用 ASCII" not in output_template
    assert "| Change | 依赖 | 可并行 |" not in output_template
    assert "使用 Mermaid 语法块输出依赖顺序和并行关系" in skill_text
    assert "在 Mermaid 依赖图中用同一 phase 的 `subgraph` 明确标记并行组" in algorithm_text
