#!/usr/bin/env python3
"""Workspace creation for aisee:image-object."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from source_state import add_operation, empty_state, save_state


WORKSPACE_DIRS = (
    "masks",
    "cutouts",
    "backgrounds",
    "exports",
    "enhanced",
    "packages",
    "preview-cache",
)


def _load_pillow():
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("需要安装 Pillow 才能读取图片尺寸: pip install pillow") from exc
    return Image


def init_workspace(input_path: str | Path, output_dir: str | Path, *, force: bool = False) -> dict[str, Any]:
    source_input = Path(input_path)
    if not source_input.exists():
        raise FileNotFoundError(f"输入图片不存在: {source_input}")

    workspace = Path(output_dir)
    state_file = workspace / "source.json"
    if state_file.exists() and not force:
        raise FileExistsError(f"workspace 已存在 source.json: {state_file}，如需覆盖请使用 --force")

    workspace.mkdir(parents=True, exist_ok=True)
    for name in WORKSPACE_DIRS:
        (workspace / name).mkdir(parents=True, exist_ok=True)

    Image = _load_pillow()
    with Image.open(source_input) as image:
        source_format = image.format or source_input.suffix.lstrip(".").upper()
        source_mode = image.mode
        width, height = image.size
        source_output = workspace / "source.png"
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")
        image.save(source_output)

    state = empty_state(workspace)
    state["source"] = {
        "path": "source.png",
        "original_path": str(source_input),
        "width": width,
        "height": height,
        "mode": source_mode,
        "format": source_format,
    }
    add_operation(
        state,
        "init",
        params={"input": str(source_input), "force": force},
        outputs=["source.png", "source.json"],
    )
    save_state(workspace, state)
    return state


def default_project_dir(input_path: str | Path) -> Path:
    source_input = Path(input_path)
    return source_input.with_name(f"{source_input.stem}.aisee-image-object")


def init_or_load_image_project(input_path: str | Path, *, force: bool = False) -> tuple[Path, dict[str, Any], bool]:
    from source_state import load_state

    workspace = default_project_dir(input_path)
    state_file = workspace / "source.json"
    if state_file.exists() and not force:
        return workspace, load_state(workspace), False
    return workspace, init_workspace(input_path, workspace, force=force), True
