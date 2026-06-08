from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_json(root: Path, *args: str, env: dict[str, str] | None = None) -> dict:
    full_env = os.environ.copy()
    full_env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    if env:
        full_env.update(env)
    result = subprocess.run(
        [sys.executable, "-m", "aisee_cli.__main__", *args],
        cwd=root,
        env=full_env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def test_doctor_reports_marketplace_setup_hint_when_codex_config_lacks_aisee(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    (codex_home / "config.toml").write_text("[marketplaces.other]\nsource = \"other/repo\"\n", encoding="utf-8")

    data = run_json(tmp_path, "doctor", "--json", env={"CODEX_HOME": str(codex_home)})

    issue = next(item for item in data["issues"] if item["code"] == "AISEE_CODEX_MARKETPLACE_MISSING")
    assert issue["severity"] == "info"
    assert issue["setup_hint"]["writes_codex_state"] is False
    assert "codex plugin marketplace add AISEE-LAB/aisee-plugin" in issue["setup_hint"]["commands"][0]
    assert data["codex_marketplace"]["status"] == "missing"


def test_legacy_content_command_reports_marketplace_setup_hint(tmp_path: Path) -> None:
    data = run_json(tmp_path, "plugin", "export", "--target", "codex", "--dest", str(tmp_path / "bundle"), "--json")

    assert data["status"] == "blocked"
    assert data["setup_hint"]["writes_codex_state"] is False
    assert "codex plugin add aisee-plugin@aisee-plugin" in data["setup_hint"]["commands"][1]
