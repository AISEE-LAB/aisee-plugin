from __future__ import annotations

import json
from pathlib import Path

from skill_contract_helpers import public_skill_files, read_skill_name


EVAL_FILES = sorted(Path("plugins/aisee-plugin/skills").glob("*/evals/evals.json"))

REQUIRED_CASE_FIELDS = {
    "id",
    "name",
    "scenario",
    "prompt",
    "context",
    "expected_output",
    "expected_outputs",
    "must_ask",
    "must_include",
    "must_not",
    "quality_checks",
    "fact_source_constraints",
    "files",
}


def test_normalized_skill_eval_files_follow_schema() -> None:
    assert EVAL_FILES, "no skill eval files found"

    for path in EVAL_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))
        skill_file = path.parent.parent / "SKILL.md"

        assert data["schema_version"] == "aisee.skill-eval.v1"
        assert data["skill_name"] == read_skill_name(skill_file)
        assert data["harness"]["type"] == "skill-eval"
        assert data["harness"]["fact_source_policy"]
        assert data["evals"]

        ids = set()
        for case in data["evals"]:
            missing = REQUIRED_CASE_FIELDS - set(case)
            assert not missing, f"{path}:{case.get('name')} missing {sorted(missing)}"
            assert isinstance(case["id"], str)
            assert case["id"] not in ids
            ids.add(case["id"])
            assert case["prompt"]
            assert case["expected_output"]
            assert case["expected_outputs"]
            assert case["must_not"]
            assert isinstance(case["context"]["files"], list)
            assert case["files"] == case["context"]["files"]


def test_every_public_skill_has_eval_coverage() -> None:
    missing = []
    for skill_file in public_skill_files():
        eval_file = skill_file.parent / "evals" / "evals.json"
        if not eval_file.exists():
            missing.append(skill_file.parent.name)

    assert missing == []
