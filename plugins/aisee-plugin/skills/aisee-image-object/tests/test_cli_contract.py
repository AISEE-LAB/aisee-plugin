from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "image_object_tool.py"


def _run(*args, cwd=None):
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_cli_init_extract_export_contract(tmp_path):
    source = tmp_path / "input.png"
    Image.new("RGB", (10, 10), (255, 0, 0)).save(source)
    mask = tmp_path / "mask.png"
    mask_image = Image.new("L", (10, 10), 0)
    draw = ImageDraw.Draw(mask_image)
    draw.rectangle((2, 2, 7, 7), fill=255)
    mask_image.save(mask)

    workspace = tmp_path / "workspace"
    init = _run("init", "--input", str(source), "--output", str(workspace))
    assert init["ok"] is True

    extract = _run(
        "extract-object",
        "--workspace",
        str(workspace),
        "--mask",
        str(mask),
        "--name",
        "按钮图标",
    )
    object_id = extract["object"]["id"]
    assert object_id == "obj_001"

    exported = _run(
        "export-variant",
        "--workspace",
        str(workspace),
        "--object-id",
        object_id,
        "--transparent",
        "true",
        "--padding",
        "1",
    )
    assert exported["export"]["id"] == "export_001"
    assert (workspace / exported["export"]["path"]).exists()


def test_cli_refine_accepts_mask_id(tmp_path):
    source = tmp_path / "input.png"
    Image.new("RGB", (10, 10), (255, 0, 0)).save(source)
    workspace = tmp_path / "workspace"
    _run("init", "--input", str(source), "--output", str(workspace))

    mask_dir = workspace / "masks"
    mask_dir.mkdir(exist_ok=True)
    mask_path = mask_dir / "mask_001.png"
    mask_image = Image.new("L", (10, 10), 0)
    draw = ImageDraw.Draw(mask_image)
    draw.rectangle((3, 3, 6, 6), fill=255)
    mask_image.save(mask_path)

    state_path = workspace / "source.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["masks"].append({"id": "mask_001", "path": "masks/mask_001.png", "source": "test"})
    state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    refined = _run(
        "refine-mask",
        "--workspace",
        str(workspace),
        "--mask",
        "mask_001",
        "--expand",
        "1",
    )

    assert refined["mask"]["id"] == "mask_002"
    assert (workspace / refined["mask"]["path"]).exists()
