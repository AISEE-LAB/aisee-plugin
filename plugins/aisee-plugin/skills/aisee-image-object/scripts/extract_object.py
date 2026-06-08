#!/usr/bin/env python3
"""Create RGBA cutouts from a source image and mask."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mask_ops import mask_bbox


def _load_pillow():
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("需要安装 Pillow 才能提取对象: pip install pillow") from exc
    return Image


def extract_object(
    source_path: str | Path,
    mask_path: str | Path,
    output_path: str | Path,
    *,
    crop: bool = True,
) -> dict[str, Any]:
    Image = _load_pillow()
    with Image.open(source_path).convert("RGBA") as source:
        with Image.open(mask_path).convert("L") as mask:
            if source.size != mask.size:
                raise ValueError(f"source 与 mask 尺寸不一致: {source.size} != {mask.size}")
            cutout = source.copy()
            cutout.putalpha(mask)
            bbox = mask_bbox(mask)
            if crop and bbox:
                cutout = cutout.crop(tuple(bbox))
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            cutout.save(output)
            return {
                "path": str(output),
                "bbox": bbox,
                "size": list(cutout.size),
                "source_size": list(source.size),
            }
