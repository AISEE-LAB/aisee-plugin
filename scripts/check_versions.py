"""Check that package, CLI, and plugin metadata versions match."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]

VERSION_FILES = [
    ".agents/plugins/marketplace.json",
    "plugins/aisee-plugin/.codex-plugin/plugin.json",
    "plugins/aisee-plugin/.claude-plugin/plugin.json",
    "plugins/aisee-plugin/.cursor-plugin/plugin.json",
]


def pyproject_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def cli_version() -> str | None:
    tree = ast.parse((ROOT / "src" / "aisee_cli" / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    return ast.literal_eval(node.value)
    return None


def metadata_version(path: str) -> str | None:
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    value = data.get("version")
    return str(value) if value is not None else None


def is_semver(version: str) -> bool:
    return re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version) is not None


def main() -> int:
    expected = pyproject_version()
    errors: list[str] = []
    if not is_semver(expected):
        errors.append(f"pyproject.toml version is not SemVer-like: {expected}")

    observed = {"src/aisee_cli/__init__.py": cli_version()}
    observed.update({path: metadata_version(path) for path in VERSION_FILES})

    for path, version in observed.items():
        if version != expected:
            errors.append(f"{path} has version {version!r}, expected {expected!r}")

    if errors:
        print("Version check failed:")
        for item in errors:
            print(f"- {item}")
        print("\nRun: python scripts/sync_versions.py")
        return 1

    print(f"All versions match {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
