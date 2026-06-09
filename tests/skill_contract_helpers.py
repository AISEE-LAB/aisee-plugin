from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "plugins" / "aisee-plugin" / "skills"
TAXONOMY_PATH = ROOT / "plugins" / "aisee-plugin" / "references" / "skill-taxonomy.md"
EXPECTED_TAXONOMY_SECTIONS = {
    "Core Workflow",
    "Optional Extensions",
    "Knowledge Loop",
    "Hardware / Experimental",
}


def split_frontmatter(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return ""
    collected: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return "".join(collected).strip()
        collected.append(line)
    return ""


def read_skill_name(path: Path) -> str:
    frontmatter = split_frontmatter(path.read_text(encoding="utf-8"))
    assert frontmatter, f"missing frontmatter in {path}"
    data = yaml.safe_load(frontmatter) or {}
    assert isinstance(data, dict) and isinstance(data.get("name"), str) and data["name"], f"missing skill name in {path}"
    return data["name"].strip()


def public_skill_files() -> list[Path]:
    return sorted(SKILLS_ROOT.glob("*/SKILL.md"))


def public_skill_names() -> set[str]:
    return {read_skill_name(path) for path in public_skill_files()}


def read_taxonomy() -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in TAXONOMY_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            heading = line[3:].strip()
            current = heading if heading in EXPECTED_TAXONOMY_SECTIONS else None
            if current:
                sections.setdefault(current, [])
            continue
        if current and line.startswith("- `") and line.endswith("`"):
            sections[current].append(line[3:-1])
    return sections
