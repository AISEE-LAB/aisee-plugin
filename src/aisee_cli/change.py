"""Schema-aware OpenSpec change inspection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aisee_cli.context_pack import build_context_pack


def build_change_inspect(project_root: Path, change: str) -> dict[str, Any]:
    pack = build_context_pack(project_root, change, "aisee-verify")
    parsed = pack["facts"]["parsed"]
    derived = pack["facts"]["derived"]
    anchor_index = parsed["anchor_index"]
    traceability = derived["traceability"]
    return {
        "schema_version": pack["schema_version"],
        "change": pack["change"],
        "schema": parsed["schema"],
        "artifacts": parsed["schema"]["artifacts"],
        "anchors": {
            "upstream_refs": traceability["upstream_refs"],
            "produced_local_ids": traceability["produced_local_ids"],
            "resolution": {
                "available": anchor_index["available"],
                "path": anchor_index["path"],
                "resolved": anchor_index["resolved"],
                "missing_references": anchor_index["missing_references"],
                "temporary_local_ids": anchor_index["temporary_local_ids"],
                "legacy_full_ids": anchor_index["legacy_full_ids"],
            },
        },
        "task_state": derived["task_state"],
        "paths": {
            "code": derived["code_paths"],
            "tests": derived["test_paths"],
        },
        "gaps": summarize_gaps(pack["gaps"]),
        "artifact_applicability": derived["artifact_applicability"],
        "evidence": pack["evidence"],
        "meta": {
            "command": f"aisee change inspect {change} --json",
            "source_context_target": "aisee-verify",
        },
    }


def summarize_gaps(gaps: list[dict[str, object]]) -> dict[str, int | str]:
    blocker = sum(1 for gap in gaps if gap.get("severity") == "blocker")
    risk = sum(1 for gap in gaps if gap.get("severity") == "risk")
    info = sum(1 for gap in gaps if gap.get("severity") == "info")
    status = "blocked" if blocker else ("risk" if risk else "clear")
    return {
        "status": status,
        "blocker": blocker,
        "risk": risk,
        "info": info,
        "total": len(gaps),
    }
