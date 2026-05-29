from __future__ import annotations

from PIL import Image

from gui.asset_model import build_asset_records, find_first_object
from gui.main_window import MainWindow
from gui.preview_render import render_canvas_composite_preview, render_canvas_preview, render_preview, render_region_preview
from gui.task_runner import BatchUiBridge


def test_build_asset_records_keeps_collection_and_display():
    state = {
        "regions": [{"id": "region_001", "bbox": [1, 1, 5, 5], "label": "区域一"}],
        "masks": [{"id": "mask_001", "path": "masks/mask_001.png"}],
        "objects": [
            {
                "id": "obj_001",
                "path": "cutouts/obj_001-product.png",
                "name": "产品主体",
            }
        ],
        "backgrounds": [],
        "exports": [],
        "enhanced": [],
    }

    records = build_asset_records(state)

    assert [record.collection for record in records] == ["regions", "objects"]
    assert records[0].display.startswith("框选区域 region_001  区域一")
    assert records[1].display.startswith("透明素材 obj_001  产品主体")
    assert find_first_object(records).item_id == "obj_001"


def test_render_preview_alpha_and_checker_background(tmp_path):
    source = tmp_path / "cutout.png"
    image = Image.new("RGBA", (4, 4), (255, 0, 0, 0))
    image.putpixel((2, 2), (255, 0, 0, 255))
    image.save(source)

    alpha_output = tmp_path / "alpha.png"
    render_preview(source, alpha_output, mode="Alpha")
    with Image.open(alpha_output) as alpha:
        assert alpha.mode == "RGB"
        assert alpha.getpixel((0, 0)) == (0, 0, 0)
        assert alpha.getpixel((2, 2)) == (255, 255, 255)

    cutout_output = tmp_path / "cutout-preview.png"
    render_preview(source, cutout_output, mode="Cutout", background="黑底")
    with Image.open(cutout_output) as preview:
        assert preview.getpixel((0, 0)) == (0, 0, 0, 255)
        assert preview.getpixel((2, 2)) == (255, 0, 0, 255)


def test_render_canvas_preview_places_cutout_at_bbox(tmp_path):
    source = tmp_path / "source.png"
    cutout = tmp_path / "cutout.png"
    output = tmp_path / "canvas.png"
    Image.new("RGB", (20, 20), (200, 200, 200)).save(source)
    Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(cutout)

    render_canvas_preview(source, output, asset_path=cutout, bbox=[8, 6, 12, 10])

    with Image.open(output) as image:
        assert image.size == (20, 20)
        assert image.getpixel((8, 6)) == (255, 0, 0, 255)
        assert image.getpixel((7, 6)) != (255, 0, 0, 255)
        assert image.getpixel((0, 0)) != (200, 200, 200, 255)


def test_render_canvas_preview_overlays_mask(tmp_path):
    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    output = tmp_path / "mask-preview.png"
    Image.new("RGB", (8, 8), (200, 200, 200)).save(source)
    mask_image = Image.new("L", (8, 8), 0)
    mask_image.putpixel((4, 4), 255)
    mask_image.save(mask)

    render_canvas_preview(source, output, asset_path=mask, mode="Mask")

    with Image.open(output) as image:
        assert image.size == (8, 8)
        assert image.getpixel((4, 4)) != (200, 200, 200, 255)


def test_render_canvas_preview_highlights_region_bbox(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "region-preview.png"
    Image.new("RGB", (20, 20), (200, 200, 200)).save(source)

    render_canvas_preview(source, output, bbox=[4, 4, 12, 12])

    with Image.open(output) as image:
        assert image.size == (20, 20)
        assert image.getpixel((4, 4)) != (200, 200, 200, 255)


def test_render_canvas_composite_preview_layers_background_and_assets(tmp_path):
    source = tmp_path / "source.png"
    background = tmp_path / "background.png"
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    output = tmp_path / "composite.png"
    Image.new("RGB", (20, 20), (200, 200, 200)).save(source)
    Image.new("RGBA", (20, 20), (240, 240, 240, 255)).save(background)
    Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(first)
    Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(second)

    render_canvas_composite_preview(
        source,
        output,
        overlays=[
            {"kind": "background", "asset_path": background},
            {"kind": "asset", "asset_path": first, "bbox": [2, 2, 6, 6]},
            {"kind": "asset", "asset_path": second, "bbox": [10, 10, 14, 14]},
        ],
        show_boxes=False,
    )

    with Image.open(output) as image:
        assert image.getpixel((0, 0)) != (240, 240, 240, 255)
        assert image.getpixel((2, 2)) == (255, 0, 0, 255)
        assert image.getpixel((10, 10)) == (0, 255, 0, 255)


def test_render_canvas_composite_preview_can_hide_region_boxes(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "hidden-boxes.png"
    Image.new("RGB", (20, 20), (200, 200, 200)).save(source)

    render_canvas_composite_preview(
        source,
        output,
        overlays=[{"kind": "region", "bbox": [4, 4, 12, 12]}],
        show_boxes=False,
    )

    with Image.open(output) as image:
        assert image.getpixel((4, 4)) == (200, 200, 200, 255)


def test_render_region_preview_crops_bbox_on_checker_canvas(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "region-preview.png"
    image = Image.new("RGB", (20, 20), (200, 200, 200))
    for x in range(4, 12):
        for y in range(4, 12):
            image.putpixel((x, y), (255, 0, 0))
    image.save(source)

    render_region_preview(source, output, bbox=[4, 4, 12, 12], max_size=(12, 12))

    with Image.open(output) as preview:
        assert preview.size == (12, 12)
        assert preview.getpixel((2, 2)) == (255, 0, 0, 255)


def test_batch_ui_bridge_delegates_to_owner_slots():
    class Owner:
        def __init__(self):
            self.progress = None
            self.finished = None

        def _handle_task_progress(self, done, total, label):
            self.progress = (done, total, label)

        def _finish_background_batch(self, results):
            self.finished = results

    owner = Owner()
    bridge = BatchUiBridge(owner)

    bridge.handle_progress(1, 3, "正在处理 2/3：obj")
    bridge.handle_finished([{"status": "ok"}])

    assert owner.progress == (1, 3, "正在处理 2/3：obj")
    assert owner.finished == [{"status": "ok"}]


def test_task_progress_uses_busy_state_while_current_task_runs():
    class Progress:
        def __init__(self):
            self.range = None
            self.value = None

        def setRange(self, start, end):
            self.range = (start, end)

        def setValue(self, value):
            self.value = value

    class Label:
        def __init__(self):
            self.text = None

        def setText(self, text):
            self.text = text

    window = MainWindow.__new__(MainWindow)
    window.task_progress = Progress()
    window.task_status_label = Label()

    window._handle_task_progress(0, 2, "正在处理 1/2：region_001")
    assert window.task_progress.range == (0, 0)
    assert window.task_progress.value is None
    assert "剩余 2 个" in window.task_status_label.text

    window._handle_task_progress(1, 2, "已完成 1/2：region_001")
    assert window.task_progress.range == (0, 2)
    assert window.task_progress.value == 1
