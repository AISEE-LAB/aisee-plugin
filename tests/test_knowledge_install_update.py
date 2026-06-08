from __future__ import annotations

import subprocess
from pathlib import Path

from test_knowledge_config import run_json, write


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def create_source_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "source-team"
    write(repo / "knowledge" / "packs" / "web-app.yaml", "id: web-app\nversion: 0.1.0\nstatus: active\ncards: []\n")
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "init")
    return repo


def current_branch(repo: Path) -> str:
    result = subprocess.run(["git", "branch", "--show-current"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def head(repo: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def test_knowledge_install_clones_configured_repo(tmp_path: Path) -> None:
    source = create_source_repo(tmp_path)
    branch = current_branch(source)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        f"""repo: {source.as_posix()}
path: .aisee/team-knowledge
ref: {branch}
packs: [web-app]
""",
    )

    data = run_json(tmp_path, "knowledge", "install", "--json")

    assert data["status"] == "ok"
    assert data["changed"] is True
    assert (tmp_path / ".aisee" / "team-knowledge" / ".git").exists()


def test_knowledge_install_refuses_existing_non_git_path(tmp_path: Path) -> None:
    source = create_source_repo(tmp_path)
    branch = current_branch(source)
    (tmp_path / ".aisee" / "team-knowledge").mkdir(parents=True)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        f"""repo: {source.as_posix()}
path: .aisee/team-knowledge
ref: {branch}
packs: [web-app]
""",
    )

    data = run_json(tmp_path, "knowledge", "install", "--json")

    assert data["status"] == "blocked"
    assert data["issues"][0]["code"] == "KNOWLEDGE_PATH_EXISTS"


def test_knowledge_update_refuses_dirty_checkout(tmp_path: Path) -> None:
    source = create_source_repo(tmp_path)
    branch = current_branch(source)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        f"""repo: {source.as_posix()}
path: .aisee/team-knowledge
ref: {branch}
packs: [web-app]
""",
    )
    run_json(tmp_path, "knowledge", "install", "--json")
    write(tmp_path / ".aisee" / "team-knowledge" / "dirty.txt", "dirty")

    data = run_json(tmp_path, "knowledge", "update", "--json")

    assert data["status"] == "blocked"
    assert data["issues"][0]["code"] == "KNOWLEDGE_REPO_DIRTY"


def test_knowledge_install_bad_ref_removes_partial_checkout(tmp_path: Path) -> None:
    source = create_source_repo(tmp_path)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        f"""repo: {source.as_posix()}
path: .aisee/team-knowledge
ref: missing-ref
packs: [web-app]
""",
    )

    data = run_json(tmp_path, "knowledge", "install", "--json")

    assert data["status"] == "blocked"
    assert not (tmp_path / ".aisee" / "team-knowledge").exists()


def test_knowledge_update_fast_forwards_branch_ref(tmp_path: Path) -> None:
    source = create_source_repo(tmp_path)
    branch = current_branch(source)
    write(
        tmp_path / "aisee" / "knowledge.yaml",
        f"""repo: {source.as_posix()}
path: .aisee/team-knowledge
ref: {branch}
packs: [web-app]
""",
    )
    run_json(tmp_path, "knowledge", "install", "--json")
    write(source / "knowledge" / "packs" / "extra.yaml", "id: extra\nversion: 0.1.0\nstatus: active\ncards: []\n")
    git(source, "add", ".")
    git(source, "commit", "-m", "add extra")
    expected = head(source)

    data = run_json(tmp_path, "knowledge", "update", "--json")

    assert data["status"] == "ok"
    assert data["changed"] is True
    assert head(tmp_path / ".aisee" / "team-knowledge") == expected
