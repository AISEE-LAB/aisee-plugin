#!/usr/bin/env python3
"""Export object variants with transparent/background/corner/padding options."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


def _load_pillow():
    try:
        from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageOps
    except ImportError as exc:
        raise RuntimeError("需要安装 Pillow 才能导出素材: pip install pillow") from exc
    return Image, ImageChops, ImageColor, ImageDraw, ImageOps


def _parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "是", "透明"}:
        return True
    if normalized in {"0", "false", "no", "n", "否", "不透明"}:
        return False
    raise ValueError(f"无法解析布尔值: {value}")


def _crop_bbox(image):
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    return image.crop(bbox) if bbox else image


def _square_canvas(image):
    Image, _, _, _, _ = _load_pillow()
    side = max(image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    offset = ((side - image.width) // 2, (side - image.height) // 2)
    canvas.alpha_composite(image, offset)
    return canvas


def _apply_padding(image, padding: int):
    Image, _, _, _, _ = _load_pillow()
    if padding <= 0:
        return image
    canvas = Image.new("RGBA", (image.width + padding * 2, image.height + padding * 2), (0, 0, 0, 0))
    canvas.alpha_composite(image, (padding, padding))
    return canvas


def _apply_corner_radius(image, radius: int):
    Image, ImageChops, _, ImageDraw, _ = _load_pillow()
    if radius <= 0:
        return image
    radius = min(radius, image.width // 2, image.height // 2)
    corner = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=255)

    alpha = Image.new("L", image.size, 255)
    alpha.paste(corner.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(corner.crop((radius, 0, radius * 2, radius)), (image.width - radius, 0))
    alpha.paste(corner.crop((0, radius, radius, radius * 2)), (0, image.height - radius))
    alpha.paste(corner.crop((radius, radius, radius * 2, radius * 2)), (image.width - radius, image.height - radius))

    result = image.copy()
    result.putalpha(ImageChops.multiply(result.getchannel("A"), alpha))
    return result


def _load_background(background: str | None, size: tuple[int, int]):
    Image, _, ImageColor, _, ImageOps = _load_pillow()
    if not background:
        return Image.new("RGBA", size, (255, 255, 255, 255))
    value = background.strip()
    if value.startswith("#") or value.lower() in {"white", "black", "transparent"}:
        color = ImageColor.getcolor(value, "RGBA")
        return Image.new("RGBA", size, color)
    path = Path(value)
    if not path.exists():
        raise FileNotFoundError(f"背景图不存在: {path}")
    with Image.open(path).convert("RGBA") as image:
        return ImageOps.fit(image, size)


def _save_variant_image(
    image,
    output_path: str | Path,
    *,
    transparent: str | bool = True,
    background: str | None = None,
    corner_radius: int = 0,
    padding: int = 0,
    crop_mode: str = "bbox",
    output_format: str | None = None,
) -> dict[str, Any]:
    is_transparent = _parse_bool(transparent)
    image = _apply_padding(image, int(padding))
    image = _apply_corner_radius(image, int(corner_radius))

    output = Path(output_path)
    suffix = (output_format or output.suffix.lstrip(".") or "png").lower()
    if suffix == "jpeg":
        suffix = "jpg"
    if suffix == "jpg":
        is_transparent = False
    if output.suffix.lower() != f".{suffix}":
        output = output.with_suffix(f".{suffix}")
    output.parent.mkdir(parents=True, exist_ok=True)

    if is_transparent:
        image.save(output)
    else:
        background_image = _load_background(background, image.size)
        background_image.alpha_composite(image)
        if suffix == "jpg":
            background_image = background_image.convert("RGB")
        background_image.save(output)

    return {
        "path": str(output),
        "size": list(image.size),
        "transparent": is_transparent,
        "background": background,
        "corner_radius": int(corner_radius),
        "padding": int(padding),
        "crop_mode": crop_mode,
        "format": suffix,
    }


def export_variant(
    cutout_path: str | Path,
    output_path: str | Path,
    *,
    transparent: str | bool = True,
    background: str | None = None,
    corner_radius: int = 0,
    padding: int = 0,
    crop_mode: str = "bbox",
    output_format: str | None = None,
) -> dict[str, Any]:
    Image, _, _, _, _ = _load_pillow()
    is_transparent = _parse_bool(transparent)
    with Image.open(cutout_path).convert("RGBA") as source:
        image = source.copy()

    if crop_mode == "bbox":
        image = _crop_bbox(image)
    elif crop_mode == "square":
        image = _square_canvas(_crop_bbox(image))
    elif crop_mode == "original-canvas":
        pass
    else:
        raise ValueError("--crop-mode 必须是 bbox、square 或 original-canvas")

    return _save_variant_image(
        image,
        output_path,
        transparent=is_transparent,
        background=background,
        corner_radius=corner_radius,
        padding=padding,
        crop_mode=crop_mode,
        output_format=output_format,
    )


def export_region_variant(
    source_path: str | Path,
    output_path: str | Path,
    *,
    bbox: list[int],
    transparent: str | bool = True,
    background: str | None = None,
    corner_radius: int = 0,
    padding: int = 0,
    crop_mode: str = "bbox",
    output_format: str | None = None,
) -> dict[str, Any]:
    Image, _, _, _, _ = _load_pillow()
    with Image.open(source_path).convert("RGBA") as source:
        x1, y1, x2, y2 = [int(value) for value in bbox]
        x1 = max(0, min(source.width, x1))
        y1 = max(0, min(source.height, y1))
        x2 = max(0, min(source.width, x2))
        y2 = max(0, min(source.height, y2))
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"区域 bbox 无效: {bbox}")

        if crop_mode == "bbox":
            image = source.crop((x1, y1, x2, y2))
        elif crop_mode == "square":
            image = _square_canvas(source.crop((x1, y1, x2, y2)))
        elif crop_mode == "original-canvas":
            image = Image.new("RGBA", source.size, (0, 0, 0, 0))
            image.alpha_composite(source.crop((x1, y1, x2, y2)), (x1, y1))
        else:
            raise ValueError("--crop-mode 必须是 bbox、square 或 original-canvas")

    result = _save_variant_image(
        image,
        output_path,
        transparent=transparent,
        background=background,
        corner_radius=corner_radius,
        padding=padding,
        crop_mode=crop_mode,
        output_format=output_format,
    )
    result["bbox"] = [x1, y1, x2, y2]
    return result


def create_package(workspace: str | Path, output_path: str | Path) -> dict[str, Any]:
    workspace_path = Path(workspace)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    include_dirs = ("masks", "cutouts", "backgrounds", "exports", "enhanced")
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        source_json = workspace_path / "source.json"
        if source_json.exists():
            archive.write(source_json, "source.json")
        for dirname in include_dirs:
            root = workspace_path / dirname
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file():
                    archive.write(path, str(path.relative_to(workspace_path)))
    return {"path": str(output), "size_bytes": output.stat().st_size}
