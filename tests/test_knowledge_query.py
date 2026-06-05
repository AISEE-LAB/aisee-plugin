from __future__ import annotations

import json
from pathlib import Path

from test_knowledge_config import configure_project, create_team_knowledge, run_json, write


def test_knowledge_query_filters_and_scores_active_cards(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)

    data = run_json(
        tmp_path,
        "knowledge",
        "query",
        "--phase",
        "implementation",
        "--surface",
        "cli",
        "--stack",
        "python",
        "--query",
        "public CLI JSON output",
        "--json",
    )

    assert data["status"] == "ok"
    assert [match["id"] for match in data["knowledge"]["matches"]] == ["cli-json-output-stability"]
    match = data["knowledge"]["matches"][0]
    assert match["recommended_action"] == ["补充 CLI contract test"]
    assert "Long body" not in json.dumps(match, ensure_ascii=False)


def test_knowledge_query_does_not_return_candidate_or_unpacked_docs(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        team / "knowledge" / "cards" / "cli" / "candidate.md",
        """---
id: candidate-card
title: Candidate
status: candidate
applies_to:
  phases: [implementation]
  surfaces: [cli]
trigger: [candidate]
recommended_action: [candidate]
boundaries: [candidate]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "query", "--phase", "implementation", "--surface", "cli", "--json")
    ids = {match["id"] for match in data["knowledge"]["matches"]}

    assert "candidate-card" not in ids
    assert "ignored-doc" not in ids


def test_knowledge_query_dedupes_project_candidate(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        tmp_path / "aisee" / "docs" / "reflect" / "knowledge-candidates" / "cli-json.md",
        """# Reusable Knowledge Candidate: CLI JSON 输出必须保持字段稳定

## Card Draft

```yaml
id: cli-json-output-stability
title: CLI JSON 输出必须保持字段稳定
status: candidate
applies_to:
  phases: [implementation]
  surfaces: [cli]
trigger:
  - 修改 public CLI JSON 输出字段
recommended_action:
  - 补充 CLI contract test
boundaries:
  - 不适用于非 JSON 日志输出
```
""",
    )

    data = run_json(tmp_path, "knowledge", "query", "--phase", "implementation", "--surface", "cli", "--json")
    match = data["knowledge"]["matches"][0]

    assert match["id"] == "cli-json-output-stability"
    assert match["dedupe"]["status"] == "deduped_project_candidate"


def test_knowledge_query_missing_config_returns_empty_matches(tmp_path: Path) -> None:
    data = run_json(tmp_path, "knowledge", "query", "--phase", "implementation", "--surface", "cli", "--json")

    assert data["status"] == "ok"
    assert data["knowledge"]["enabled"] is False
    assert data["knowledge"]["matches"] == []
    assert data["issues"][0]["code"] == "KNOWLEDGE_CONFIG_MISSING"
