from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_aisee(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
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


def create_schema_pack(root: Path) -> None:
    write(
        root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix" / "schema.yaml",
        """name: quick-fix
version: 1
artifacts:
  - id: problem
    generates: problem.md
    template: problem.md
    requires: []
apply:
  requires: [problem]
  tracks: problem.md
""",
    )
    write(
        root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix" / "templates" / "problem.md",
        "# Problem\n",
    )


def create_open_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(root / "openspec" / "changes" / ".gitkeep", "")
    write(root / "aisee" / "registry" / "id-registry.json", '{"version":1,"scopes":{}}\n')
    write(root / "aisee" / "registry" / "sources.json", '{"version":1,"sources":[]}\n')
    write(
        root / "openspec" / "schemas" / "aisee-app-spec-driven" / "schema.yaml",
        """name: aisee-app-spec-driven
version: 2
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
  - id: source-map
    generates: source-map.md
    template: source-map.md
    requires: [proposal]
  - id: specs
    generates: specs/**/*.md
    template: spec.md
    requires: [source-map]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs]
apply:
  requires: [tasks]
  tracks: tasks.md
        """,
    )
    for template in ("proposal.md", "source-map.md", "spec.md", "tasks.md"):
        write(root / "openspec" / "schemas" / "aisee-app-spec-driven" / "templates" / template, f"# {template}\n")
    change = root / "openspec" / "changes" / "add-auth"
    write(change / ".openspec.yaml", "schema: aisee-app-spec-driven\n")
    write(change / "proposal.md", "# Proposal\n")
    write(change / "source-map.md", "src/auth/session.py tests/auth/test_session.py\n")
    write(change / "specs" / "auth.md", "## ADDED Requirements\n")
    write(change / "tasks.md", "# Tasks\n\n- [ ] Implement src/auth/session.py.\n")


def create_quick_research_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: quick-research\n")
    write(root / "openspec" / "changes" / ".gitkeep", "")
    write(root / "aisee" / "registry" / "id-registry.json", '{"version":1,"scopes":{}}\n')
    write(
        root / "openspec" / "schemas" / "quick-research" / "schema.yaml",
        """name: quick-research
version: 1
artifacts:
  - id: question
    generates: question.md
    template: question.md
    requires: []
  - id: findings
    generates: findings.md
    template: findings.md
    requires: [question]
  - id: recommendation
    generates: recommendation.md
    template: recommendation.md
    requires: [findings]
        """,
    )
    for template in ("question.md", "findings.md", "recommendation.md"):
        write(root / "openspec" / "schemas" / "quick-research" / "templates" / template, f"# {template}\n")
    change = root / "openspec" / "changes" / "research-cache"
    write(change / ".openspec.yaml", "schema: quick-research\n")
    write(change / "question.md", "# Question\n")
    write(change / "findings.md", "# Findings\n")
    write(change / "recommendation.md", "# Recommendation\n")
    write(root / "docs" / "verification" / "research-cache-openspec-validate.md", "passed\n")


def test_doctor_reports_missing_openspec_as_blocked(tmp_path: Path) -> None:
    data = run_json(tmp_path, "doctor", "--json")

    assert data["status"] == "blocked"
    assert any(item["code"] == "OPENSPEC_CONFIG_MISSING" for item in data["issues"])
    assert data["meta"]["writes"] is False


def test_bootstrap_plan_is_read_only(tmp_path: Path) -> None:
    data = run_json(tmp_path, "bootstrap", "--plan", "--json")

    assert data["status"] == "ready"
    assert data["writes"] is False
    assert any(item["path"] == "AGENTS.md" for item in data["actions"])
    assert not (tmp_path / "AGENTS.md").exists()


def test_doctor_and_bootstrap_report_legacy_aisee_layout(tmp_path: Path) -> None:
    write(tmp_path / "AGENTS.md", "# Rules\n")
    write(tmp_path / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(tmp_path / "openspec" / "changes" / ".gitkeep", "")
    write(tmp_path / ".aisee" / "id-registry.json", '{"version":1,"scopes":{}}\n')
    write(tmp_path / ".aisee" / "sources.json", '{"version":1,"sources":[]}\n')
    write(tmp_path / ".memory" / "index.md", "# Memory Index\n")

    doctor = run_json(tmp_path, "doctor", "--json")
    bootstrap = run_json(tmp_path, "bootstrap", "--plan", "--json")

    assert doctor["status"] == "risk"
    assert any(item["code"] == "AISEE_LEGACY_PATH" for item in doctor["issues"])
    assert {item["name"] for item in doctor["aisee"]["layout"]["legacy_only"]} >= {
        "sources",
        "id_registry",
        "memory_index",
    }
    assert any(item["kind"] == "migrate" and ".aisee/sources.json" in item["path"] for item in bootstrap["actions"])
    assert any(item["kind"] == "migrate" and ".memory/index.md" in item["path"] for item in bootstrap["actions"])


def test_bootstrap_apply_is_explicitly_blocked(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "bootstrap", "--apply", "--json", check=False)
    data = json.loads(result.stdout)

    assert result.returncode == 1
    assert data["status"] == "blocked"
    assert data["issues"][0]["code"] == "BOOTSTRAP_APPLY_NOT_IMPLEMENTED"


def test_schema_pack_list_check_and_install(tmp_path: Path) -> None:
    create_schema_pack(tmp_path)

    listed = run_json(tmp_path, "schemas", "list", "--json")
    checked = run_json(tmp_path, "schemas", "check", "--json")
    installed = run_json(tmp_path, "schemas", "install", "--schema", "quick-fix", "--json")

    assert listed["schemas"][0]["name"] == "quick-fix"
    assert checked["status"] == "ok"
    assert installed["installed"][0]["state"] == "installed"
    assert (tmp_path / "openspec" / "schemas" / "quick-fix" / "schema.yaml").exists()


def test_flow_inspect_recommends_implementation_for_authored_change(tmp_path: Path) -> None:
    create_open_project(tmp_path)

    data = run_json(tmp_path, "flow", "inspect", "--change", "add-auth", "--json")

    assert data["status"] == "risk"
    assert data["stage"] == "implementation-ready"
    assert "ce-work" in data["recommended_path"]
    assert data["doctor"]["status"] == "ok"
    assert data["schema"]["name"] == "aisee-app-spec-driven"
    assert data["schema"]["source_map_required"] is True
    assert data["schema"]["tasks_required"] is True
    assert data["inputs"]["source_map"] == "present"
    assert data["inputs"]["source_map_parse_level"] == "metadata"
    assert "SOURCE_MAP_UNSTRUCTURED" in data["inputs"]["source_map_issue_codes"]
    assert data["inputs"]["execution"]["requires_ce_plan"] is False
    assert data["checks"]["author"]["status"] == "needs-work"
    assert data["checks"]["gaps"]["status"] == "risk"
    assert data["checks"]["implementation_gaps"]["status"] == "risk"
    assert data["checks"]["verify"]["status"] == "risk"
    assert any("context pack --change add-auth --for ce-work" in item for item in data["required_commands"])


def test_flow_inspect_recommends_ce_plan_when_execution_paths_are_missing(tmp_path: Path) -> None:
    create_open_project(tmp_path)
    write(tmp_path / "openspec" / "changes" / "add-auth" / "source-map.md", "auth:FR-001 is covered.\n")

    data = run_json(tmp_path, "flow", "inspect", "--change", "add-auth", "--json")

    assert data["status"] == "risk"
    assert data["stage"] == "change-authored"
    assert data["recommended_path"] == ["aisee:implementation-bridge", "ce-plan"]
    assert data["inputs"]["execution"]["requires_ce_plan"] is True
    assert "SOURCE_MAP_PATHS_MISSING" in data["inputs"]["source_map_issue_codes"]
    assert "SOURCE_MAP_GAP" in data["checks"]["gaps"]["codes"]
    assert "SOURCE_MAP_GAP" in data["checks"]["implementation_gaps"]["codes"]
    assert any("context pack --change add-auth --for ce-work" in item for item in data["required_commands"])


def test_flow_ignores_ce_work_gaps_for_no_apply_schema(tmp_path: Path) -> None:
    create_quick_research_project(tmp_path)
    (tmp_path / "docs" / "verification" / "research-cache-openspec-validate.md").unlink()

    data = run_json(tmp_path, "flow", "inspect", "--change", "research-cache", "--json")

    assert data["status"] == "blocked"
    assert data["stage"] == "verified"
    assert data["recommended_path"] == ["aisee:archive-guard"]
    assert data["checks"]["gaps"]["status"] == "blocked"
    assert "TASK_GAP" in data["checks"]["gaps"]["codes"]
    assert data["checks"]["implementation_gaps"]["status"] == "clear"
    assert "TASK_GAP" not in data["checks"]["implementation_gaps"]["codes"]


def test_flow_status_is_blocked_when_author_check_blocks(tmp_path: Path) -> None:
    create_open_project(tmp_path)
    (tmp_path / "openspec" / "schemas" / "aisee-app-spec-driven" / "templates" / "tasks.md").unlink()

    data = run_json(tmp_path, "flow", "inspect", "--change", "add-auth", "--json")

    assert data["status"] == "blocked"
    assert data["stage"] == "change-authored"
    assert data["recommended_path"] == ["aisee:change-author"]
    assert "SCHEMA_TEMPLATE_MISSING" in data["checks"]["author"]["blocker_codes"]
    assert data["blocking"]


def test_flow_inspect_reports_archive_ready_for_quick_research(tmp_path: Path) -> None:
    create_quick_research_project(tmp_path)

    data = run_json(tmp_path, "flow", "inspect", "--change", "research-cache", "--json")

    assert data["status"] == "ok"
    assert data["stage"] == "archive-ready"
    assert data["schema"]["name"] == "quick-research"
    assert data["schema"]["source_map_required"] is False
    assert data["schema"]["tasks_required"] is False
    assert data["checks"]["archive"]["status"] == "archive-ready"
    assert data["recommended_path"] == ["openspec archive"]
