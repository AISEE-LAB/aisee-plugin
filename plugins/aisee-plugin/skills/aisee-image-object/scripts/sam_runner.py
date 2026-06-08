#!/usr/bin/env python3
"""SAM/SAM2 optional backend boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def segment_with_sam2(
    image_path: str | Path,
    output_mask: str | Path,
    *,
    points: list[list[float]] | None = None,
    labels: list[int] | None = None,
    box: list[float] | None = None,
    checkpoint: str | None = None,
    model_cfg: str | None = None,
) -> dict[str, Any]:
    try:
        import numpy as np
        from PIL import Image
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        from sam2.build_sam import build_sam2
    except ImportError as exc:
        raise RuntimeError("SAM2 backend 未安装。请先安装 sam2，并配置 checkpoint/model_cfg。") from exc

    if not checkpoint or not model_cfg:
        raise RuntimeError("SAM2 需要 checkpoint 和 model_cfg，当前未配置。")

    sam_model = build_sam2(model_cfg, checkpoint)
    predictor = SAM2ImagePredictor(sam_model)
    with Image.open(image_path).convert("RGB") as image:
        predictor.set_image(np.array(image))

    point_coords = np.array(points, dtype=np.float32) if points else None
    point_labels = np.array(labels, dtype=np.int32) if labels else None
    box_array = np.array(box, dtype=np.float32) if box else None
    masks, scores, _ = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        box=box_array,
        multimask_output=True,
    )
    best_index = int(np.argmax(scores))
    mask = (masks[best_index] * 255).astype("uint8")
    output = Path(output_mask)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask, mode="L").save(output)
    return {"path": str(output), "score": float(scores[best_index])}
