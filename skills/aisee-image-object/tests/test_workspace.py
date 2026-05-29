from __future__ import annotations

import json

from PIL import Image

from workspace import init_workspace


def test_init_workspace_creates_source_json_and_dirs(tmp_path):
    input_path = tmp_path / "input.jpg"
    Image.new("RGB", (12, 8), (255, 0, 0)).save(input_path)

    workspace = tmp_path / "object"
    state = init_workspace(input_path, workspace)

    assert (workspace / "source.png").exists()
    assert (workspace / "source.json").exists()
    assert (workspace / "masks").is_dir()
    assert (workspace / "cutouts").is_dir()
    assert (workspace / "preview-cache").is_dir()
    assert state["source"]["width"] == 12
    assert state["source"]["height"] == 8

    data = json.loads((workspace / "source.json").read_text(encoding="utf-8"))
    assert data["operations"][0]["kind"] == "init"
