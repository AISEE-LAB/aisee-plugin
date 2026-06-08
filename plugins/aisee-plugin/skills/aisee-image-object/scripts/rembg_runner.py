#!/usr/bin/env python3
"""rembg backend wrapper."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from mask_ops import alpha_to_mask, mask_bbox


def remove_background(
    input_path: str | Path,
    cutout_path: str | Path,
    mask_path: str | Path,
    *,
    model: str,
) -> dict[str, Any]:
    try:
        from PIL import Image
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError("需要安装 rembg 和 Pillow 才能调用去背景模型: pip install rembg pillow") from exc

    session = new_session(model)
    input_bytes = Path(input_path).read_bytes()
    output_bytes = remove(input_bytes, session=session)
    with Image.open(BytesIO(output_bytes)).convert("RGBA") as cutout:
        cutout_output = Path(cutout_path)
        mask_output = Path(mask_path)
        cutout_output.parent.mkdir(parents=True, exist_ok=True)
        mask_output.parent.mkdir(parents=True, exist_ok=True)
        cutout.save(cutout_output)
        mask = alpha_to_mask(cutout)
        mask.save(mask_output)
        return {
            "cutout_path": str(cutout_output),
            "mask_path": str(mask_output),
            "model": model,
            "bbox": mask_bbox(mask),
            "size": list(cutout.size),
        }


def remove_background_region(
    input_path: str | Path,
    mask_path: str | Path,
    *,
    model: str,
    bbox: list[int],
) -> dict[str, Any]:
    try:
        from PIL import Image
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError("需要安装 rembg 和 Pillow 才能调用区域去背景模型: pip install rembg pillow") from exc

    session = new_session(model)
    with Image.open(input_path).convert("RGBA") as source:
        x1, y1, x2, y2 = _clamp_bbox(bbox, source.size)
        crop = source.crop((x1, y1, x2, y2))
        input_buffer = BytesIO()
        crop.save(input_buffer, format="PNG")

        output_bytes = remove(input_buffer.getvalue(), session=session)
        with Image.open(BytesIO(output_bytes)).convert("RGBA") as cutout:
            region_mask = alpha_to_mask(cutout)
            full_mask = Image.new("L", source.size, 0)
            if region_mask.size != crop.size:
                region_mask = region_mask.resize(crop.size)
            full_mask.paste(region_mask, (x1, y1))

    mask_output = Path(mask_path)
    mask_output.parent.mkdir(parents=True, exist_ok=True)
    full_mask.save(mask_output)
    return {
        "mask_path": str(mask_output),
        "model": model,
        "bbox": mask_bbox(full_mask),
        "region_bbox": [x1, y1, x2, y2],
        "size": list(full_mask.size),
    }


def _clamp_bbox(bbox: list[int], size: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = size
    x1, y1, x2, y2 = [int(value) for value in bbox]
    x1 = max(0, min(width, x1))
    y1 = max(0, min(height, y1))
    x2 = max(0, min(width, x2))
    y2 = max(0, min(height, y2))
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"区域 bbox 无效: {bbox}")
    return x1, y1, x2, y2
