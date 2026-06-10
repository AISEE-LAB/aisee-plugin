from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_aisee(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
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


def write_memory(
    root: Path,
    relative: str,
    *,
    title: str = "提交信息语言",
    memory_type: str = "pref",
    status: str = "active",
    priority: str = "normal",
    summary: str = "本项目提交信息使用中文。",
    body: str = "提交前检查变更范围，并使用中文 commit message。",
) -> None:
    write(
        root / relative,
        f"""---
id: {Path(relative).stem}
title: {title}
type: {memory_type}
status: {status}
priority: {priority}
summary: {summary}
source_refs:
  - AGENTS.md
tags:
  - commit
updated_at: 2026-06-10T00:00:00+00:00
---

# {title}

{body}
""",
    )


def test_memory_inspect_missing_layout_is_non_blocking(tmp_path: Path) -> None:
    data = run_json(tmp_path, "memory", "inspect", "--json")

    assert data["status"] == "missing"
    assert data["memory"]["available"] is False
    assert data["memory"]["canonical_root"] == "aisee/memory"
    assert data["issues"] == []
    assert data["meta"]["writes"] is False


def test_memory_inspect_prefers_canonical_over_legacy(tmp_path: Path) -> None:
    write_memory(tmp_path, ".memory/pref/legacy.md", summary="legacy should not win")
    write_memory(tmp_path, "aisee/memory/pref/canonical.md", summary="canonical wins")

    data = run_json(tmp_path, "memory", "inspect", "--json")

    assert data["memory"]["state"] == "dual"
    assert data["memory"]["root"] == "aisee/memory"
    assert [entry["summary"] for entry in data["entries"]] == ["canonical wins"]


def test_memory_inspect_reads_legacy_only_as_fallback(tmp_path: Path) -> None:
    write(
        tmp_path / ".memory" / "pref" / "legacy.md",
        """# 旧格式提交偏好

**日期：** 2026-06-10
**类型：** pref

## 摘要

旧格式仍可只读解析。
""",
    )

    data = run_json(tmp_path, "memory", "inspect", "--json")

    assert data["memory"]["state"] == "legacy-only"
    assert data["entries"][0]["legacy_format"] is True
    assert data["entries"][0]["summary"] == "旧格式仍可只读解析。"


def test_memory_invalid_metadata_reports_risk_without_crashing(tmp_path: Path) -> None:
    write_memory(tmp_path, "aisee/memory/pref/bad.md", memory_type="unknown", status="old", priority="urgent", summary="")

    data = run_json(tmp_path, "memory", "inspect", "--json")

    assert data["status"] == "risk"
    assert {item["code"] for item in data["issues"]} >= {
        "MEMORY_TYPE_INVALID",
        "MEMORY_STATUS_INVALID",
        "MEMORY_PRIORITY_INVALID",
        "MEMORY_SUMMARY_MISSING",
    }
