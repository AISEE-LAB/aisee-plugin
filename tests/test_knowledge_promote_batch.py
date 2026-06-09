from __future__ import annotations

from pathlib import Path

from test_knowledge_config import create_team_knowledge, run_json, write


def test_knowledge_promote_batch_writes_card_and_updates_pack(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    curation = tmp_path / "aisee" / "docs" / "reflect" / "knowledge-curation" / "batch.md"
    write(
        curation,
        """# Batch

```yaml
id: new-guardrail
title: New guardrail
status: candidate
applies_to:
  phases: [implementation]
  surfaces: [cli]
trigger:
  - new trigger
recommended_action:
  - new action
boundaries:
  - test only
```
""",
    )

    data = run_json(
        tmp_path,
        "knowledge",
        "promote-batch",
        "--curation",
        str(curation),
        "--team-path",
        str(team),
        "--pack",
        "web-app",
        "--category",
        "cli",
        "--json",
    )

    assert data["status"] == "ok"
    assert data["meta"]["writes"] is True
    assert data["git_actions"] is False
    assert (team / "knowledge" / "cards" / "cli" / "new-guardrail.md").exists()
    pack = (team / "knowledge" / "packs" / "web-app.yaml").read_text(encoding="utf-8")
    assert "new-guardrail" in pack


def test_knowledge_promote_batch_rejects_bad_draft_without_writing(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: bad-draft
title: Bad draft
status: candidate
applies_to:
  phases: [implementation]
trigger:
  - bad
recommended_action:
  - bad
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--json")

    assert data["status"] == "blocked"
    assert not (team / "knowledge" / "cards" / "general" / "bad-draft.md").exists()


def test_knowledge_promote_batch_validates_all_drafts_before_writing(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: good-draft
title: Good draft
status: candidate
applies_to:
  phases: [implementation]
trigger:
  - good
recommended_action:
  - good
boundaries:
  - test only
```

```yaml
id: bad-draft
title: Bad draft
status: candidate
applies_to:
  phases: [implementation]
trigger:
  - bad
recommended_action:
  - bad
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--json")

    assert data["status"] == "blocked"
    assert not (team / "knowledge" / "cards" / "general" / "good-draft.md").exists()


def test_knowledge_promote_batch_rejects_pack_path_traversal(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    outside = team / "knowledge" / "outside.yaml"
    write(outside, "id: outside\nversion: 0.1.0\nstatus: active\ncards: []\n")
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: new-card
title: New card
status: candidate
applies_to:
  phases: [implementation]
trigger: [new]
recommended_action: [new]
boundaries: [test only]
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--pack", "../outside", "--json")

    assert data["status"] == "blocked"
    assert "new-card" not in outside.read_text(encoding="utf-8")
    assert not (team / "knowledge" / "cards" / "general" / "new-card.md").exists()


def test_knowledge_promote_batch_refuses_existing_card_body_overwrite(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    existing = team / "knowledge" / "cards" / "cli" / "existing.md"
    write(
        existing,
        """---
id: existing-card
title: Existing
status: active
applies_to:
  phases: [implementation]
trigger: [existing]
recommended_action: [existing]
boundaries: [test only]
---

Reviewed body must stay.
""",
    )
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: existing-card
title: Existing
status: candidate
applies_to:
  phases: [implementation]
trigger: [existing]
recommended_action: [existing]
boundaries: [test only]
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--category", "cli", "--json")

    assert data["status"] == "blocked"
    assert "Reviewed body must stay." in existing.read_text(encoding="utf-8")


def test_knowledge_promote_batch_refuses_duplicate_id_in_other_category(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: cli-json-output-stability
title: Duplicate existing
status: candidate
applies_to:
  phases: [implementation]
trigger: [duplicate]
recommended_action: [duplicate]
boundaries: [test only]
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--category", "backend", "--json")

    assert data["status"] == "blocked"
    assert not (team / "knowledge" / "cards" / "backend" / "cli-json-output-stability.md").exists()


def test_knowledge_promote_batch_rejects_duplicate_draft_ids(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: duplicate-draft
title: First duplicate
status: candidate
applies_to:
  phases: [implementation]
trigger: [first]
recommended_action: [first]
boundaries: [test only]
```

```yaml
id: duplicate-draft
title: Second duplicate
status: candidate
applies_to:
  phases: [implementation]
trigger: [second]
recommended_action: [second]
boundaries: [test only]
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--json")

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_CARD_DUPLICATE" in {item["code"] for item in data["issues"]}
    assert not (team / "knowledge" / "cards" / "general" / "duplicate-draft.md").exists()


def test_knowledge_promote_batch_requires_team_repo_marker(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    (team / ".aisee-team-knowledge").unlink()
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: marker-missing
title: Marker missing
status: candidate
applies_to:
  phases: [implementation]
trigger: [marker]
recommended_action: [marker]
boundaries: [test only]
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--json")

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_SCAFFOLD_MARKER_MISSING" in {item["code"] for item in data["issues"]}
    assert not (team / "knowledge" / "cards" / "general" / "marker-missing.md").exists()


def test_knowledge_promote_batch_rejects_missing_team_repo_structure(tmp_path: Path) -> None:
    team = tmp_path / "team"
    write(team / ".aisee-team-knowledge", "marker\n")
    curation = tmp_path / "curation.md"
    write(
        curation,
        """```yaml
id: structure-missing
title: Structure missing
status: candidate
applies_to:
  phases: [implementation]
trigger: [missing]
recommended_action: [missing]
boundaries: [test only]
```
""",
    )

    data = run_json(tmp_path, "knowledge", "promote-batch", "--curation", str(curation), "--team-path", str(team), "--json")

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_PACKS_MISSING" in {item["code"] for item in data["issues"]}
    assert "KNOWLEDGE_CARDS_MISSING" in {item["code"] for item in data["issues"]}
