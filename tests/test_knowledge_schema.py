from __future__ import annotations

from pathlib import Path

from test_knowledge_config import configure_project, create_team_knowledge, run_json, write


def test_knowledge_check_reports_duplicate_card_ids(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        team / "knowledge" / "cards" / "backend" / "duplicate.md",
        """---
id: cli-json-output-stability
title: Duplicate
status: active
applies_to:
  phases: [implementation]
trigger: [duplicate]
recommended_action: [fix duplicate]
boundaries: [test only]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--team-path", str(team), "--json")

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_CARD_DUPLICATE" in {item["code"] for item in data["issues"]}


def test_knowledge_check_reports_deprecated_replacement_issues(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(
        team / "knowledge" / "cards" / "backend" / "deprecated.md",
        """---
id: deprecated-card
title: Deprecated card
status: deprecated
deprecated_by: [missing-card]
applies_to:
  phases: [implementation]
trigger: [deprecated]
recommended_action: [use replacement]
boundaries: [test only]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--team-path", str(team), "--json")

    codes = {item["code"] for item in data["issues"]}
    assert data["status"] == "risk"
    assert "KNOWLEDGE_CARD_REPLACEMENT_MISSING" in codes


def test_knowledge_check_rejects_invalid_applies_to_shape(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(
        team / "knowledge" / "cards" / "backend" / "bad-applies.md",
        """---
id: bad-applies
title: Bad applies
status: active
applies_to: implementation
trigger: [bad]
recommended_action: [fix]
boundaries: [test only]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--team-path", str(team), "--json")

    assert "KNOWLEDGE_CARD_APPLIES_TO_INVALID" in {item["code"] for item in data["issues"]}


def test_knowledge_check_validates_unpacked_cards(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(
        team / "knowledge" / "cards" / "cli" / "unpacked-bad.md",
        """---
id: unpacked-bad
title: Unpacked bad card
status: active
applies_to: implementation
trigger: [bad]
recommended_action: [bad]
boundaries: [bad]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--team-path", str(team), "--json")

    assert "KNOWLEDGE_CARD_APPLIES_TO_INVALID" in {item["code"] for item in data["issues"]}


def test_knowledge_check_default_validates_unpacked_cards(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        team / "knowledge" / "cards" / "cli" / "default-unpacked-bad.md",
        """---
id: default-unpacked-bad
title: Default unpacked bad card
status: active
applies_to: implementation
trigger: [bad]
recommended_action: [bad]
boundaries: [bad]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--json")

    assert "KNOWLEDGE_CARD_APPLIES_TO_INVALID" in {item["code"] for item in data["issues"]}


def test_knowledge_check_rejects_scalar_list_fields(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(
        team / "knowledge" / "cards" / "cli" / "scalar-trigger.md",
        """---
id: scalar-trigger
title: Scalar trigger
status: active
applies_to:
  phases: [implementation]
trigger: bad
recommended_action: [bad]
boundaries: [bad]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--team-path", str(team), "--json")

    assert "KNOWLEDGE_CARD_FIELD_INVALID" in {item["code"] for item in data["issues"]}


def test_knowledge_check_reports_missing_pack_version(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    write(
        team / "knowledge" / "packs" / "web-app.yaml",
        """id: web-app
status: active
cards: []
""",
    )

    data = run_json(tmp_path, "knowledge", "check", "--team-path", str(team), "--json")

    assert "KNOWLEDGE_PACK_VERSION_MISSING" in {item["code"] for item in data["issues"]}
