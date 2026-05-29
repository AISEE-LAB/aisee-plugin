"""Render preview images for the GUI without PySide dependencies."""

from __future__ import annotations

from pathlib import Path


def _load_pillow():
    try:
        from PIL import Image, ImageColor, ImageDraw
    except ImportError as exc:
        raise RuntimeError("需要安装 Pillow 才能渲染预览图: pip install pillow") from exc
    return Image, ImageColor, ImageDraw


def checkerboard(size: tuple[int, int], *, cell: int = 16):
    Image, _, _ = _load_pillow()
    width, height = size
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    pixels = image.load()
    light = (238, 238, 238, 255)
    dark = (198, 198, 198, 255)
    for y in range(height):
        for x in range(width):
            pixels[x, y] = light if ((x // cell) + (y // cell)) % 2 == 0 else dark
    return image


def render_preview(
    input_path: str | Path,
    output_path: str | Path,
    *,
    mode: str = "自动",
    background: str = "棋盘格",
) -> Path:
    Image, ImageColor, _ = _load_pillow()
    path = Path(input_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(path) as raw:
        if mode == "Alpha":
            image = raw.convert("RGBA").getchannel("A").convert("RGB")
        elif mode == "Mask":
            image = raw.convert("L").convert("RGB")
        else:
            image = raw.convert("RGBA")

    if image.mode == "RGBA":
        base = _preview_background(image.size, background, ImageColor)
        base.alpha_composite(image)
        image = base

    image.save(output)
    return output


def render_canvas_preview(
    source_path: str | Path,
    output_path: str | Path,
    *,
    asset_path: str | Path | None = None,
    bbox: list[int] | None = None,
    mode: str = "画布定位",
    background: str = "棋盘格",
    mask_tint: tuple[int, int, int, int] = (0, 102, 204, 96),
    show_box: bool = True,
) -> Path:
    Image, ImageColor, ImageDraw = _load_pillow()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source_path).convert("RGBA") as source:
        canvas = source.copy()
        if not asset_path:
            if bbox:
                x1, y1, x2, y2 = [int(value) for value in bbox]
                overlay = Image.new("RGBA", source.size, (255, 255, 255, 120))
                canvas.alpha_composite(overlay)
                if show_box:
                    draw = ImageDraw.Draw(canvas)
                    draw.rectangle((x1, y1, x2, y2), outline=(0, 102, 204, 255), width=1)
            canvas.save(output)
            return output

        with Image.open(asset_path) as raw_asset:
            asset = raw_asset.convert("RGBA")
            if mode == "Mask":
                mask = raw_asset.convert("L")
                overlay = Image.new("RGBA", source.size, (0, 0, 0, 0))
                tint = Image.new("RGBA", source.size, mask_tint)
                overlay.alpha_composite(tint)
                overlay.putalpha(mask.point(lambda value: int(value * (mask_tint[3] / 255))))
                canvas.alpha_composite(overlay)
            elif _is_full_canvas(asset.size, source.size):
                canvas = _compose_full_canvas_asset(asset, background, ImageColor)
            elif bbox:
                x1, y1, x2, y2 = [int(value) for value in bbox]
                target_size = (max(1, x2 - x1), max(1, y2 - y1))
                if asset.size != target_size:
                    asset = asset.resize(target_size)
                overlay = source.copy()
                dim = Image.new("RGBA", source.size, (247, 248, 250, 172))
                overlay.alpha_composite(dim)
                overlay.alpha_composite(asset, (x1, y1))
                canvas = overlay
            else:
                canvas = _compose_full_canvas_asset(asset, background, ImageColor)

    canvas.save(output)
    return output


def render_canvas_composite_preview(
    source_path: str | Path,
    output_path: str | Path,
    *,
    overlays: list[dict],
    background: str = "棋盘格",
    show_boxes: bool = True,
) -> Path:
    Image, ImageColor, ImageDraw = _load_pillow()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source_path).convert("RGBA") as source:
        canvas = source.copy()
        boxes: list[list[int]] = []
        background_overlays = [overlay for overlay in overlays if overlay.get("kind") == "background"]
        focus_overlays = [overlay for overlay in overlays if overlay.get("kind") != "background"]
        for overlay in overlays:
            bbox = overlay.get("bbox")
            if bbox:
                boxes.append([int(value) for value in bbox])

        for overlay in background_overlays:
            bbox = overlay.get("bbox")
            asset_path = overlay.get("asset_path")
            if not asset_path:
                continue
            with Image.open(asset_path).convert("RGBA") as raw_asset:
                canvas = _place_canvas_asset(canvas, source.size, raw_asset.copy(), bbox, background, ImageColor)

        should_focus = bool(focus_overlays) and (show_boxes or any(overlay.get("asset_path") for overlay in focus_overlays))
        if should_focus:
            dim = Image.new("RGBA", source.size, (247, 248, 250, 172))
            canvas.alpha_composite(dim)

        for overlay in focus_overlays:
            bbox = overlay.get("bbox")
            asset_path = overlay.get("asset_path")
            kind = overlay.get("kind", "asset")
            if not asset_path:
                continue

            with Image.open(asset_path) as raw_asset:
                if kind == "mask":
                    mask = raw_asset.convert("L")
                    tint = Image.new("RGBA", source.size, (0, 102, 204, 96))
                    tint.putalpha(mask.point(lambda value: int(value * (96 / 255))))
                    canvas.alpha_composite(tint)
                    continue
                asset_image = raw_asset.convert("RGBA").copy()
            canvas = _place_overlay_asset(canvas, source.size, asset_image, bbox, background, ImageColor)

        if show_boxes and boxes:
            draw = ImageDraw.Draw(canvas)
            for x1, y1, x2, y2 in boxes:
                draw.rectangle((x1, y1, x2, y2), outline=(0, 102, 204, 255), width=2)

    canvas.save(output)
    return output


def _place_canvas_asset(canvas, source_size, asset, bbox, background, ImageColor):
    if _is_full_canvas(asset.size, source_size):
        return asset.copy()
    if bbox:
        x1, y1, x2, y2 = [int(value) for value in bbox]
        target_size = (max(1, x2 - x1), max(1, y2 - y1))
        if asset.size != target_size:
            asset = asset.resize(target_size)
        canvas.alpha_composite(asset, (x1, y1))
        return canvas
    return _compose_full_canvas_asset(asset, background, ImageColor)


def _place_overlay_asset(canvas, source_size, asset, bbox, background, ImageColor):
    if bbox:
        x1, y1, x2, y2 = [int(value) for value in bbox]
        target_size = (max(1, x2 - x1), max(1, y2 - y1))
        if asset.size != target_size:
            asset = asset.resize(target_size)
        canvas.alpha_composite(asset, (x1, y1))
        return canvas
    if _is_full_canvas(asset.size, source_size):
        canvas.alpha_composite(asset)
        return canvas
    return _compose_full_canvas_asset(asset, background, ImageColor)


def render_thumbnail(
    input_path: str | Path,
    output_path: str | Path,
    *,
    size: tuple[int, int] = (96, 72),
    background: str = "棋盘格",
) -> Path:
    Image, ImageColor, _ = _load_pillow()
    path = Path(input_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(path).convert("RGBA") as raw:
        image = raw.copy()
    image.thumbnail(size)
    canvas = _preview_background(size, background, ImageColor)
    offset = ((size[0] - image.width) // 2, (size[1] - image.height) // 2)
    canvas.alpha_composite(image, offset)
    canvas.save(output)
    return output


def render_region_thumbnail(
    source_path: str | Path,
    output_path: str | Path,
    *,
    bbox: list[int],
    size: tuple[int, int] = (96, 72),
) -> Path:
    Image, ImageColor, _ = _load_pillow()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path).convert("RGBA") as source:
        x1, y1, x2, y2 = [int(value) for value in bbox]
        crop = source.crop((x1, y1, x2, y2))
    crop.thumbnail(size)
    canvas = _preview_background(size, "棋盘格", ImageColor)
    offset = ((size[0] - crop.width) // 2, (size[1] - crop.height) // 2)
    canvas.alpha_composite(crop, offset)
    canvas.save(output)
    return output


def render_region_preview(
    source_path: str | Path,
    output_path: str | Path,
    *,
    bbox: list[int],
    max_size: tuple[int, int] = (520, 360),
) -> Path:
    Image, ImageColor, _ = _load_pillow()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path).convert("RGBA") as source:
        x1, y1, x2, y2 = [int(value) for value in bbox]
        crop = source.crop((x1, y1, x2, y2))
    crop.thumbnail(max_size)
    canvas = _preview_background(max_size, "棋盘格", ImageColor)
    offset = ((max_size[0] - crop.width) // 2, (max_size[1] - crop.height) // 2)
    canvas.alpha_composite(crop, offset)
    canvas.save(output)
    return output


def _preview_background(size: tuple[int, int], background: str, ImageColor):
    Image, _, _ = _load_pillow()
    if background == "黑底":
        return Image.new("RGBA", size, (0, 0, 0, 255))
    if background == "白底":
        return Image.new("RGBA", size, (255, 255, 255, 255))
    if background.startswith("#"):
        return Image.new("RGBA", size, ImageColor.getcolor(background, "RGBA"))
    return checkerboard(size)


def _is_full_canvas(asset_size: tuple[int, int], source_size: tuple[int, int]) -> bool:
    return asset_size == source_size


def _compose_full_canvas_asset(asset, background: str, ImageColor):
    if asset.mode == "RGBA":
        base = _preview_background(asset.size, background, ImageColor)
        base.alpha_composite(asset)
        return base
    return asset.convert("RGBA")
