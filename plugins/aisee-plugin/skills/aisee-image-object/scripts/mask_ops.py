#!/usr/bin/env python3
"""Deterministic mask operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_pillow():
    try:
        from PIL import Image, ImageChops, ImageFilter
    except ImportError as exc:
        raise RuntimeError("需要安装 Pillow 才能处理 mask: pip install pillow") from exc
    return Image, ImageChops, ImageFilter


def load_mask(path: str | Path):
    Image, _, _ = _load_pillow()
    return Image.open(path).convert("L")


def save_mask(mask, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    mask.convert("L").save(path)
    return path


def mask_bbox(mask) -> list[int] | None:
    bbox = mask.convert("L").getbbox()
    return list(bbox) if bbox else None


def refine_mask_image(
    mask,
    *,
    expand: int = 0,
    contract: int = 0,
    feather: float = 0.0,
    smooth: int = 0,
    invert: bool = False,
):
    Image, ImageChops, ImageFilter = _load_pillow()
    result = mask.convert("L")
    if invert:
        result = ImageChops.invert(result)
    if contract > 0:
        size = contract * 2 + 1
        result = result.filter(ImageFilter.MinFilter(size))
    if expand > 0:
        size = expand * 2 + 1
        result = result.filter(ImageFilter.MaxFilter(size))
    if smooth > 0:
        size = smooth * 2 + 1
        result = result.filter(ImageFilter.MedianFilter(size))
    if feather > 0:
        result = result.filter(ImageFilter.GaussianBlur(float(feather)))
    return result


def refine_mask_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    expand: int = 0,
    contract: int = 0,
    feather: float = 0.0,
    smooth: int = 0,
    invert: bool = False,
) -> dict[str, Any]:
    mask = load_mask(input_path)
    refined = refine_mask_image(
        mask,
        expand=expand,
        contract=contract,
        feather=feather,
        smooth=smooth,
        invert=invert,
    )
    output = save_mask(refined, output_path)
    return {"path": str(output), "bbox": mask_bbox(refined), "size": list(refined.size)}


def alpha_to_mask(rgba_image):
    if rgba_image.mode != "RGBA":
        rgba_image = rgba_image.convert("RGBA")
    return rgba_image.getchannel("A")


def create_bbox_mask_file(
    source_path: str | Path,
    output_path: str | Path,
    *,
    bbox: list[int],
    expand: int = 0,
) -> dict[str, Any]:
    Image, _, _ = _load_pillow()
    with Image.open(source_path) as source:
        width, height = source.size
    x1, y1, x2, y2 = [int(value) for value in bbox]
    x1 = max(0, min(width, x1 - int(expand)))
    y1 = max(0, min(height, y1 - int(expand)))
    x2 = max(0, min(width, x2 + int(expand)))
    y2 = max(0, min(height, y2 + int(expand)))
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"无效框选区域: {bbox}")
    mask = Image.new("L", (width, height), 0)
    mask.paste(255, (x1, y1, x2, y2))
    output = save_mask(mask, output_path)
    return {"path": str(output), "bbox": [x1, y1, x2, y2], "size": [width, height]}


def create_bboxes_mask_file(
    source_path: str | Path,
    output_path: str | Path,
    *,
    bboxes: list[list[int]],
    expand: int = 0,
) -> dict[str, Any]:
    Image, _, _ = _load_pillow()
    with Image.open(source_path) as source:
        width, height = source.size
    if not bboxes:
        raise ValueError("至少需要一个抹除区域")
    mask = Image.new("L", (width, height), 0)
    normalized = []
    for bbox in bboxes:
        x1, y1, x2, y2 = [int(value) for value in bbox]
        x1 = max(0, min(width, x1 - int(expand)))
        y1 = max(0, min(height, y1 - int(expand)))
        x2 = max(0, min(width, x2 + int(expand)))
        y2 = max(0, min(height, y2 + int(expand)))
        if x2 <= x1 or y2 <= y1:
            continue
        mask.paste(255, (x1, y1, x2, y2))
        normalized.append([x1, y1, x2, y2])
    if not normalized:
        raise ValueError(f"无效抹除区域: {bboxes}")
    output = save_mask(mask, output_path)
    return {"path": str(output), "bbox": mask_bbox(mask), "bboxes": normalized, "size": [width, height]}
