from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_aisee(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    return subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=env,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_json(root: Path, *args: str) -> dict:
    return json.loads(run_aisee(root, *args).stdout)


def create_team_knowledge(root: Path) -> Path:
    team = root / ".aisee" / "team-knowledge"
    write(team / ".aisee-team-knowledge", "team_knowledge: true\n")
    write(
        team / "knowledge" / "packs" / "web-app.yaml",
        """id: web-app
version: 0.1.0
status: active
cards:
  - cli-json-output-stability
card_globs:
  - knowledge/cards/backend/*.md
disabled_cards: []
defaults:
  max_cards: 3
""",
    )
    write(
        team / "knowledge" / "cards" / "cli" / "json-output.md",
        """---
id: cli-json-output-stability
title: CLI JSON 输出必须保持字段稳定
status: active
applies_to:
  stacks: [python]
  phases: [implementation, verify]
  schemas: []
  surfaces: [cli, json-output]
trigger:
  - 修改 public CLI JSON 输出字段
recommended_action:
  - 补充 CLI contract test
boundaries:
  - 不适用于非 JSON 日志输出
tags: [cli, json-output]
---

Long body should not appear by default.
""",
    )
    write(
        team / "knowledge" / "cards" / "backend" / "http-contract.md",
        """---
id: http-contract-backward-compatibility
title: HTTP contract changes need compatibility checks
status: active
applies_to:
  stacks: [python]
  phases: [implementation, review]
  schemas: [aisee-app-spec-driven]
  surfaces: [contract, http-service]
trigger:
  - Changes service contract
recommended_action:
  - Add backward compatibility checks
boundaries:
  - Not for internal-only helpers
risk_types: [public-contract]
---
""",
    )
    write(
        team / "docs" / "ignored.md",
        """---
id: ignored-doc
title: Must not be scanned
status: active
applies_to:
  phases: [implementation]
trigger: [ignored]
recommended_action: [ignored]
boundaries: [ignored]
---
""",
    )
    return team


def configure_project(root: Path, team: Path) -> None:
    write(
        root / "aisee" / "knowledge.yaml",
        f"""repo: git@example.com:org/aisee-team-knowledge.git
path: {team.relative_to(root).as_posix()}
ref: v0.1.0
packs:
  - web-app
retrieval:
  max_cards: 3
  include_project_candidates: true
  vector: optional
""",
    )


def test_knowledge_inspect_missing_config_is_non_blocking(tmp_path: Path) -> None:
    data = run_json(tmp_path, "knowledge", "inspect", "--json")

    assert data["status"] == "missing"
    assert data["config"]["available"] is False
    assert data["issues"] == []


def test_knowledge_inspect_reads_configured_packs_and_cards(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)

    data = run_json(tmp_path, "knowledge", "inspect", "--json")

    assert data["status"] == "ok"
    assert data["config"]["local_path_exists"] is True
    assert [pack["id"] for pack in data["packs"]] == ["web-app"]
    ids = {item["id"] for item in data["cards"]["items"]}
    assert ids == {"cli-json-output-stability", "http-contract-backward-compatibility"}
    assert "ignored-doc" not in ids


def test_knowledge_doctor_reports_team_path_mismatch(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    other = tmp_path / ".aisee" / "other-team-knowledge"
    other.mkdir(parents=True)

    data = run_json(tmp_path, "knowledge", "doctor", "--team-path", str(other), "--json")

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_PATH_MISMATCH" in {item["code"] for item in data["issues"]}


def test_knowledge_doctor_blocks_missing_team_repo_marker(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    (team / ".aisee-team-knowledge").unlink()

    data = run_json(tmp_path, "knowledge", "doctor", "--json")

    assert data["status"] == "blocked"
    assert "KNOWLEDGE_SCAFFOLD_MARKER_MISSING" in {item["code"] for item in data["issues"]}


def test_knowledge_inspect_reports_missing_pack(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        f"""path: {team.relative_to(tmp_path).as_posix()}
packs:
  - missing-pack
""",
    )

    data = run_json(tmp_path, "knowledge", "inspect", "--json")

    assert data["status"] == "risk"
    assert data["issues"][0]["code"] == "KNOWLEDGE_PACK_MISSING"


def test_knowledge_query_excludes_cards_missing_required_fields(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        team / "knowledge" / "cards" / "backend" / "missing-required.md",
        """---
id: missing-required-card
title: Missing required card
status: active
applies_to:
  phases: [implementation]
  surfaces: [cli]
trigger: [missing-required]
recommended_action: [should not be returned]
---
""",
    )

    data = run_json(tmp_path, "knowledge", "query", "--phase", "implementation", "--surface", "cli", "--query", "missing-required", "--json")
    ids = {match["id"] for match in data["knowledge"]["matches"]}

    assert "missing-required-card" not in ids
    assert "KNOWLEDGE_CARD_FIELDS_MISSING" in {item["code"] for item in data["issues"]}


def test_knowledge_inspect_reports_invalid_card_glob_without_traceback(tmp_path: Path) -> None:
    team = create_team_knowledge(tmp_path)
    configure_project(tmp_path, team)
    write(
        team / "knowledge" / "packs" / "web-app.yaml",
        """id: web-app
version: 0.1.0
status: active
card_globs:
  - /tmp/**/*.md
""",
    )

    data = run_json(tmp_path, "knowledge", "inspect", "--json")

    assert data["status"] == "risk"
    assert "KNOWLEDGE_PACK_INVALID" in {item["code"] for item in data["issues"]}
