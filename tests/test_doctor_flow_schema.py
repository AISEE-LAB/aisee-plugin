from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def install_compound_skills(root: Path, *skills: str) -> Path:
    skills_dir = root / "compound" / "skills"
    for skill in skills:
        write(skills_dir / skill / "SKILL.md", f"# {skill}\n")
    return skills_dir


def run_aisee(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(repo_src)
    if "CODEX_HOME" in os.environ:
        env["CODEX_HOME"] = os.environ["CODEX_HOME"]
    else:
        env["HOME"] = str(root / "home")
        env["CODEX_HOME"] = str(root / "home" / ".codex")
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
    write(root / "skills" / "aisee-srs" / "SKILL.md", "# Aisee SRS\n")
    write(root / "references" / "README.md", "# References\n")
    write(
        root / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix" / "schema.yaml",
        """name: quick-fix
version: 1
description: quick fixes
capabilities:
  - apply_execution
  - archive_authority
  - quick_fix_evidence
artifacts:
  - id: problem
    generates: problem.md
    template: problem.md
    requires: []
    requiredness: always
    capabilities: [problem_statement]
apply:
  requires: [problem]
  tracks: problem.md
archive:
  tracks:
    - problem.md
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
    write(
        root / "openspec" / "schemas" / "aisee-app-spec-driven" / "schema.yaml",
        """name: aisee-app-spec-driven
version: 2
description: app schema
capabilities:
  - source_map_routing
  - apply_execution
  - archive_authority
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
    requiredness: always
    capabilities: [primary_brief]
  - id: source-map
    generates: source-map.md
    template: source-map.md
    requires: [proposal]
    requiredness: always
    capabilities: [source_map]
  - id: specs
    generates: specs/**/*.md
    template: spec.md
    requires: [source-map]
    requiredness: always
    capabilities: [behavior_spec]
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [specs]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [tasks]
  tracks: tasks.md
archive:
  tracks:
    - tasks.md
    - source-map.md
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
    write(
        root / "openspec" / "schemas" / "quick-research" / "schema.yaml",
        """name: quick-research
version: 1
description: research schema
capabilities:
  - research_only
  - archive_authority
artifacts:
  - id: question
    generates: question.md
    template: question.md
    requires: []
    requiredness: always
    capabilities: [research_question]
  - id: findings
    generates: findings.md
    template: findings.md
    requires: [question]
    requiredness: always
    capabilities: [research_findings]
  - id: recommendation
    generates: recommendation.md
    template: recommendation.md
    requires: [findings]
    requiredness: always
    capabilities: [research_recommendation]
archive:
  tracks:
    - recommendation.md
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


def create_opsx_collab_project(root: Path) -> None:
    write(root / "AGENTS.md", "# Rules\n")
    write(root / "openspec" / "config.yaml", "schema: opsx-collab-pr-loop\n")
    write(root / "openspec" / "changes" / ".gitkeep", "")
    write(
        root / "openspec" / "schemas" / "opsx-collab-pr-loop" / "schema.yaml",
        """name: opsx-collab-pr-loop
version: 1
description: review loop
capabilities:
  - apply_execution
  - archive_authority
artifacts:
  - id: intake
    generates: loop/intake.md
    template: intake.md
    requires: []
    requiredness: always
    capabilities: [intake_brief]
  - id: research-plan
    generates: loop/research-plan.md
    template: research-plan.md
    requires: [intake]
    requiredness: always
    capabilities: [research_plan]
  - id: implementation
    generates: loop/implementation.md
    template: implementation.md
    requires: [research-plan]
    requiredness: always
    capabilities: [implementation_record]
  - id: checkpoints
    generates: loop/checkpoints.md
    template: checkpoints.md
    requires: [implementation]
    requiredness: always
    capabilities: [checkpoint_log]
apply:
  requires: [research-plan]
  tracks: loop/implementation.md
archive:
  tracks:
    - loop/implementation.md
    - loop/checkpoints.md
        """,
    )
    for template in ("intake.md", "research-plan.md", "implementation.md", "checkpoints.md"):
        write(root / "openspec" / "schemas" / "opsx-collab-pr-loop" / "templates" / template, f"# {template}\n")
    change = root / "openspec" / "changes" / "review-auth-pr"
    write(change / ".openspec.yaml", "schema: opsx-collab-pr-loop\n")
    write(change / "loop" / "intake.md", "# Intake\n")
    write(change / "loop" / "research-plan.md", "# Research Plan\n")
    write(change / "loop" / "implementation.md", "# Implementation\n")
    write(change / "loop" / "checkpoints.md", "# Checkpoints\n")
    write(root / "docs" / "verification" / "review-auth-pr-openspec-validate.md", "passed\n")


def test_doctor_reports_missing_openspec_as_blocked(tmp_path: Path) -> None:
    data = run_json(tmp_path, "doctor", "--json")

    assert data["status"] == "blocked"
    assert "cli" in data["openspec"]
    assert "compound" in data
    assert any(item["code"] == "OPENSPEC_CONFIG_MISSING" for item in data["issues"])
    assert data["meta"]["writes"] is False


def test_doctor_reports_planning_doc_lifecycle_risks_without_blocking_open_project(tmp_path: Path) -> None:
    create_open_project(tmp_path)
    write(
        tmp_path / "aisee" / "docs" / "requirements" / "legacy-auth.md",
        """---
title: "Legacy Auth SRS"
doc_type: "srs"
status: "active"
date: "2026-06-09"
scope: "auth"
owner: "Aisee"
source_refs:
  - "ticket://auth"
change_refs: []
---

# Legacy Auth
""",
    )

    data = run_json(tmp_path, "doctor", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "PLANNING_DOC_CHANGE_REFS_MISSING" for item in data["issues"])
    assert any(item["code"] == "PLANNING_DOC_STALE_ACTIVE" for item in data["issues"])
    assert data["aisee"]["planning_docs"]["count"] == 1


def test_doctor_reports_missing_frontmatter_as_risk_only(tmp_path: Path) -> None:
    create_open_project(tmp_path)
    write(tmp_path / "aisee" / "docs" / "requirements" / "legacy-auth.md", "# Legacy Auth\n")

    data = run_json(tmp_path, "doctor", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "PLANNING_DOC_FRONTMATTER_MISSING" for item in data["issues"])


def test_doctor_reports_invalid_change_refs_in_planning_docs(tmp_path: Path) -> None:
    create_open_project(tmp_path)
    write(
        tmp_path / "aisee" / "docs" / "requirements" / "legacy-auth.md",
        """---
title: "Legacy Auth SRS"
doc_type: "srs"
status: "active"
date: "2026-06-09"
scope: "auth"
owner: "Aisee"
source_refs:
  - "ticket://auth"
change_refs:
  - "README.md"
---

# Legacy Auth
""",
    )

    data = run_json(tmp_path, "doctor", "--json")

    assert data["status"] == "risk"
    assert any(item["code"] == "PLANNING_DOC_CHANGE_REF_INVALID" for item in data["issues"])
    assert any(item["code"] == "PLANNING_DOC_STALE_ACTIVE" for item in data["issues"])


def test_bootstrap_plan_is_read_only(tmp_path: Path) -> None:
    data = run_json(tmp_path, "bootstrap", "--plan", "--json")

    assert data["status"] == "ready"
    assert data["writes"] is False
    assert any(item["path"] == "AGENTS.md" for item in data["actions"])
    marketplace_action = next(item for item in data["actions"] if item["path"] == "aisee-plugin marketplace")
    assert "codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main" in marketplace_action["reason"]
    schema_action = next(item for item in data["actions"] if item["path"] == "openspec/schemas")
    assert schema_action["kind"] == "create"
    assert "aisee:schema-pack" in schema_action["reason"]
    assert "aisee schemas install" not in schema_action["reason"]
    assert not (tmp_path / "AGENTS.md").exists()


def test_bootstrap_plan_does_not_reinstall_marketplace_when_only_project_schemas_are_missing(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "AGENTS.md", "# Rules\n")
    write(tmp_path / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(tmp_path / "openspec" / "changes" / ".gitkeep", "")
    codex_home = tmp_path / "home" / ".codex"
    write(codex_home / "config.toml", """[marketplaces.aisee-plugin]\nsource = "AISEE-LAB/aisee-plugin"\n\n[plugins."aisee-plugin@aisee-plugin"]\nenabled = true\n""")
    create_schema_pack(codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin")
    write(
        codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin" / ".codex-plugin" / "plugin.json",
        '{"name":"aisee-plugin","version":"0.8.0"}\n',
    )
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    data = run_json(tmp_path, "bootstrap", "--plan", "--json")

    assert not any(item["path"] == "aisee-plugin marketplace" for item in data["actions"])
    schema_action = next(item for item in data["actions"] if item["path"] == "openspec/schemas")
    assert schema_action["kind"] == "create"


def test_doctor_and_bootstrap_report_legacy_aisee_layout(tmp_path: Path) -> None:
    write(tmp_path / "AGENTS.md", "# Rules\n")
    write(tmp_path / "openspec" / "config.yaml", "schema: aisee-app-spec-driven\n")
    write(tmp_path / "openspec" / "changes" / ".gitkeep", "")
    write(tmp_path / ".memory" / "index.md", "# Memory Index\n")

    doctor = run_json(tmp_path, "doctor", "--json")
    bootstrap = run_json(tmp_path, "bootstrap", "--plan", "--json")

    assert doctor["status"] == "risk"
    assert any(item["code"] == "AISEE_LEGACY_PATH" for item in doctor["issues"])
    assert {item["name"] for item in doctor["aisee"]["layout"]["legacy_only"]} >= {
        "memory_index",
    }
    assert any(item["kind"] == "migrate" and ".memory/index.md" in item["path"] for item in bootstrap["actions"])


def test_bootstrap_apply_is_not_a_public_flag(tmp_path: Path) -> None:
    result = run_aisee(tmp_path, "bootstrap", "--apply", "--json", check=False)

    assert result.returncode == 2
    assert "unrecognized arguments: --apply" in result.stderr


def test_schema_pack_list_and_check_use_explicit_dev_asset_root(tmp_path: Path, monkeypatch) -> None:
    create_schema_pack(tmp_path)
    monkeypatch.setenv("AISEE_PLUGIN_ASSET_ROOT", str(tmp_path))

    listed = run_json(tmp_path, "schemas", "list", "--json")
    checked = run_json(tmp_path, "schemas", "check", "--json")

    assert listed["schemas"][0]["name"] == "quick-fix"
    assert checked["status"] == "ok"
    assert not (tmp_path / "openspec" / "schemas" / "quick-fix" / "schema.yaml").exists()


def test_schema_check_validates_project_installed_schema_without_source_assets(tmp_path: Path) -> None:
    write(tmp_path / "openspec" / "schemas" / "broken" / "schema.yaml", "name: broken\nartifacts: [\n")

    result = run_aisee(tmp_path, "schemas", "check", "--json", "--fail-on-blocker", check=False)
    data = json.loads(result.stdout)

    assert result.returncode == 1
    assert data["status"] == "blocked"
    assert any(item["code"] == "SCHEMA_PARSE_FAILED" for item in data["issues"])


def test_schema_check_reports_structural_schema_contract_issues(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AISEE_AGENT_RUNTIME", "none")
    write(
        tmp_path / "openspec" / "schemas" / "broken" / "schema.yaml",
        """name: broken
capabilities:
  - apply_execution
artifacts:
  - id: proposal
    generates: proposal.md
    template: templates/proposal.md
    requires: [tasks]
    requiredness: always
    capabilities: [primary_brief]
  - id: proposal
    generates: tasks.md
    template: tasks.md
    requires: [proposal]
    requiredness: always
    capabilities: [apply_track]
apply:
  requires: [proposal]
  tracks: tasks.md
""",
    )
    write(tmp_path / "openspec" / "schemas" / "broken" / "templates" / "proposal.md", "# proposal\n")
    write(tmp_path / "openspec" / "schemas" / "broken" / "templates" / "tasks.md", "# tasks\n")

    data = run_json(tmp_path, "schemas", "check", "--json")

    assert data["status"] == "blocked"
    codes = {item["code"] for item in data["issues"]}
    assert "SCHEMA_ARTIFACT_DUPLICATE" in codes
    assert "SCHEMA_VERSION_MISSING" in codes
    assert "SCHEMA_DESCRIPTION_MISSING" in codes
    assert "SCHEMA_TEMPLATE_PATH_INVALID" in codes
    assert "SCHEMA_DAG_CYCLE" in codes


def test_doctor_reports_schema_pack_version_mismatch(tmp_path: Path, monkeypatch) -> None:
    create_open_project(tmp_path)
    codex_home = tmp_path / "home" / ".codex"
    write(codex_home / "config.toml", """[marketplaces.aisee-plugin]\nsource = "AISEE-LAB/aisee-plugin"\n\n[plugins."aisee-plugin@aisee-plugin"]\nenabled = true\n""")
    write(codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin" / "skills" / "aisee-srs" / "SKILL.md", "# aisee:srs\n")
    write(codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin" / "references" / "README.md", "# refs\n")
    write(
        codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin" / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix" / "schema.yaml",
        """name: quick-fix
version: 1
description: small fixes
capabilities:
  - apply_execution
  - archive_authority
artifacts:
  - id: problem
    generates: problem.md
    template: problem.md
    requires: []
    requiredness: always
    capabilities: [problem_statement]
apply:
  requires: [problem]
  tracks: problem.md
archive:
  tracks:
    - problem.md
""",
    )
    write(
        codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin" / "skills" / "aisee-schema-pack" / "assets" / "schema-pack" / "quick-fix" / "templates" / "problem.md",
        "# problem\n",
    )
    write(
        codex_home / ".tmp" / "marketplaces" / "aisee-plugin" / "plugins" / "aisee-plugin" / ".codex-plugin" / "plugin.json",
        '{"name":"aisee-plugin","version":"0.5.0"}\n',
    )
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    data = run_json(tmp_path, "doctor", "--json")

    assert any(item["code"] == "SCHEMA_PACK_VERSION_MISMATCH" for item in data["issues"])


def test_root_resolution_prefers_nearest_project_markers_inside_git_monorepo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_git_repo(repo)
    write(repo / "AGENTS.md", "# Monorepo Root\n")

    project = repo / "apps" / "billing"
    create_open_project(project)
    workdir = project / "nested" / "feature"
    workdir.mkdir(parents=True)

    doctor = run_json(workdir, "doctor", "--json")

    assert doctor["status"] == "ok"
    assert doctor["project_rules"]["primary"] == "AGENTS.md"
    assert doctor["openspec"]["config"] == "openspec/config.yaml"


def test_root_resolution_falls_back_to_git_root_without_aisee_markers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_git_repo(repo)
    write(repo / "AGENTS.md", "# Root Rules\n")

    nested = repo / "packages" / "web"
    nested.mkdir(parents=True)
    data = run_json(nested, "doctor", "--json")

    assert data["project_rules"]["primary"] == "AGENTS.md"
    assert data["status"] == "blocked"
    assert any(item["code"] == "OPENSPEC_CONFIG_MISSING" for item in data["issues"])
