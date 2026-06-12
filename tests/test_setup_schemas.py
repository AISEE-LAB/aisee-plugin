from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "aisee-plugin" / "skills" / "aisee-schema-pack" / "scripts" / "setup-schemas.js"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_openspec_project(root: Path) -> None:
    write(root / "openspec" / "config.yaml", "schema: quick-fix\n")
    write(root / "openspec" / "changes" / ".gitkeep", "")


def test_setup_schemas_skips_examples_directory(tmp_path: Path) -> None:
    create_openspec_project(tmp_path)

    result = subprocess.run(
        ["node", str(SCRIPT), "--schema", "aisee-app-spec-driven", "--no-validate"],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    installed_schema = tmp_path / "openspec" / "schemas" / "aisee-app-spec-driven"

    assert "installed aisee-app-spec-driven" in result.stdout
    assert (installed_schema / "schema.yaml").exists()
    assert (installed_schema / "templates").is_dir()
    assert not (installed_schema / "examples").exists()
