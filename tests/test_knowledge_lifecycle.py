from __future__ import annotations

from pathlib import Path

from test_knowledge_config import configure_project, create_team_knowledge, run_json, write


def test_knowledge_query_excludes_deprecated_cards(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        team / "knowledge" / "cards" / "backend" / "deprecated.md",
        """---
id: deprecated-card
title: Deprecated card
status: deprecated
deprecated_by: [http-contract-backward-compatibility]
applies_to:
  phases: [implementation]
  surfaces: [cli]
trigger: [deprecated]
recommended_action: [use replacement]
boundaries: [test only]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "query", "--phase", "implementation", "--surface", "cli", "--query", "deprecated", "--json")

    assert "deprecated-card" not in {match["id"] for match in data["knowledge"]["matches"]}

