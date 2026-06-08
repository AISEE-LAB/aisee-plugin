from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cli_dependent_skills_reference_shared_preflight() -> None:
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    missing = []
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        if "aisee " in text and "references/cli-preflight.md" not in text:
            missing.append(path.relative_to(ROOT).as_posix())

    assert missing == []


def test_cli_preflight_documents_cli_and_marketplace_boundary() -> None:
    text = (ROOT / "references" / "cli-preflight.md").read_text(encoding="utf-8")

    assert "pipx install aisee-plugin" in text
    assert "codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main" in text
    assert "Marketplace installation 不会安装 `aisee` CLI" in text
    assert "PyPI / pipx installation 不会安装 bundled skills" in text
