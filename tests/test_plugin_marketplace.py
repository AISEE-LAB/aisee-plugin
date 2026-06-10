from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def package_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def test_codex_marketplace_listing_points_to_repository_plugin_root() -> None:
    marketplace = read_json(".agents/plugins/marketplace.json")

    assert marketplace["name"] == "aisee-plugin"
    assert marketplace["version"] == package_version()
    assert len(marketplace["plugins"]) == 1

    plugin = marketplace["plugins"][0]
    assert plugin["name"] == "aisee-plugin"
    assert plugin["source"] == {"source": "local", "path": "./plugins/aisee-plugin"}
    assert plugin["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
    assert plugin["category"] == "Coding"


def test_codex_manifest_is_loadable_from_marketplace_plugin_root() -> None:
    marketplace = read_json(".agents/plugins/marketplace.json")
    plugin_root = ROOT / marketplace["plugins"][0]["source"]["path"]
    manifest = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "aisee-plugin"
    assert manifest["version"] == marketplace["version"]
    assert manifest["skills"] == "./skills/"
    assert (plugin_root / "skills" / "aisee-srs" / "SKILL.md").exists()
    assert (plugin_root / "skills" / "aisee-knowledge-curate" / "assets" / "team-knowledge" / "README.md").exists()


def test_plugin_skill_directories_are_loadable_skills() -> None:
    marketplace = read_json(".agents/plugins/marketplace.json")
    plugin_root = ROOT / marketplace["plugins"][0]["source"]["path"]

    skill_dirs = [path for path in (plugin_root / "skills").iterdir() if path.is_dir()]
    assert skill_dirs
    assert all((path / "SKILL.md").exists() for path in skill_dirs)


def test_codex_default_prompts_reference_existing_skills() -> None:
    marketplace = read_json(".agents/plugins/marketplace.json")
    plugin_root = ROOT / marketplace["plugins"][0]["source"]["path"]
    manifest = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    prompts = manifest["interface"]["defaultPrompt"]
    assert prompts

    for prompt in prompts:
        match = re.search(r"\baisee:([a-z0-9-]+)\b", prompt)
        assert match, f"default prompt should name an aisee skill: {prompt}"
        assert (plugin_root / "skills" / f"aisee-{match.group(1)}" / "SKILL.md").exists()
