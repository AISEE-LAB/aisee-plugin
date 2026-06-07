from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "scenarios" / "app-full-lifecycle"


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
    result = run_aisee(root, *args)
    return json.loads(result.stdout)


def copy_fixture(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project)
    return project


def test_app_full_lifecycle_fixture_reaches_archive_ready(tmp_path: Path) -> None:
    project = copy_fixture(tmp_path)
    change = "add-passwordless-login"

    installed = run_json(project, "schemas", "install", "--schema", "aisee-app-spec-driven", "--json")
    doctor = run_json(project, "doctor", "--json")
    sources = run_json(project, "sources", "check", "--json")
    ids = run_json(project, "id", "check", "--json")
    flow = run_json(project, "flow", "inspect", "--change", change, "--json")
    inspected = run_json(project, "change", "inspect", change, "--json")
    pack = run_json(project, "context", "pack", "--change", change, "--for", "ce-work", "--json")
    manifest = run_json(project, "contract", "manifest", "--json")
    summary = run_json(project, "contract", "summary", "--change", change, "--json")
    service = run_json(
        project,
        "contract",
        "get",
        "--change",
        change,
        "--artifact",
        "service-contract",
        "--section",
        "能力契约",
        "--json",
    )
    verify = run_json(project, "change", "verify-check", change, "--json")
    archive = run_json(project, "change", "archive-check", change, "--json")

    assert installed["installed"][0]["state"] == "installed"
    assert doctor["status"] == "ok"
    assert sources["status"] == "ok"
    assert ids["status"] == "ok"
    assert flow["stage"] == "archive-ready"
    assert flow["recommended_path"] == ["openspec archive"]
    assert inspected["schema"]["name"] == "aisee-app-spec-driven"
    assert pack["facts"]["derived"]["execution"]["requires_ce_plan"] is False
    assert "src/auth/passwordless.py" in pack["facts"]["derived"]["code_paths"]
    assert "tests/auth/test_passwordless.py" in pack["facts"]["derived"]["test_paths"]
    assert manifest["changes"][0]["id"] == change
    assert {item["id"] for item in summary["contracts"]} >= {"ui-contract", "service-contract", "data-model"}
    assert service["status"] == "ok"
    assert "Request login code" in service["content"]
    assert verify["status"] == "ready"
    assert archive["status"] == "archive-ready"


def test_app_full_lifecycle_fixture_context_pack_is_schema_aware(tmp_path: Path) -> None:
    project = copy_fixture(tmp_path)
    change = "add-passwordless-login"
    run_json(project, "schemas", "install", "--schema", "aisee-app-spec-driven", "--json")

    pack = run_json(project, "context", "pack", "--change", change, "--for", "aisee-verify", "--json")

    assert pack["facts"]["parsed"]["schema"]["source_map_required"] is True
    assert pack["facts"]["parsed"]["source_map"]["parse_level"] == "structured"
    assert pack["facts"]["parsed"]["source_map"]["contract_sync"]["values"]["provider_repo"]["value"] == "backend-api"
    assert pack["facts"]["parsed"]["source_map"]["contract_sync"]["machine_readable_contracts"] == ["contracts/openapi.yaml"]
    assert pack["facts"]["parsed"]["id_registry"]["missing_ids"] == []
    assert pack["facts"]["derived"]["implementation_references"]["unmapped_reference_paths"] == []
