from __future__ import annotations

import json
from pathlib import Path


EVAL_FILES = [
    Path("skills/aisee-srs/evals/evals.json"),
    Path("skills/aisee-change-plan/evals/evals.json"),
    Path("skills/aisee-ui-content/evals/evals.json"),
    Path("skills/aisee-architecture/evals/evals.json"),
    Path("skills/aisee-init/evals/evals.json"),
    Path("skills/aisee-spec-migrate/evals/evals.json"),
]

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
    for path in EVAL_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))

        assert data["schema_version"] == "aisee.skill-eval.v1"
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
