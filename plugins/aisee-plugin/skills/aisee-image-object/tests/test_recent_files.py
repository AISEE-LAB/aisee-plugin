from __future__ import annotations

import json

from gui.recent_files import load_recent_records, recent_path, save_recent_record


def test_recent_records_default_to_project_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    workspace = tmp_path / "aisee/docs/image-objects/product"
    workspace.mkdir(parents=True)
    save_recent_record(workspace=workspace, image="source.png")

    assert recent_path() == tmp_path / "aisee/cache/image-object/recent.json"
    assert recent_path().exists()
    assert load_recent_records()[0]["workspace"] == str(workspace)


def test_recent_records_respect_env_override(tmp_path, monkeypatch):
    custom_path = tmp_path / "custom/recent.json"
    monkeypatch.setenv("AISEE_IMAGE_OBJECT_RECENT_PATH", str(custom_path))

    custom_path.parent.mkdir(parents=True)
    custom_path.write_text(
        json.dumps([{"workspace": "workspace-a", "image": "image-a.png"}]),
        encoding="utf-8",
    )

    assert recent_path() == custom_path
    assert load_recent_records() == [{"workspace": "workspace-a", "image": "image-a.png"}]
