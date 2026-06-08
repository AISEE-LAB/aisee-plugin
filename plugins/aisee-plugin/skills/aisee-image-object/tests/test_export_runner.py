from __future__ import annotations

from PIL import Image, ImageDraw

from export_runner import create_package, export_region_variant, export_variant


def _cutout(path):
    image = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, 7, 7), fill=(255, 0, 0, 255))
    image.save(path)


def test_export_variant_padding_and_background(tmp_path):
    cutout = tmp_path / "cutout.png"
    _cutout(cutout)
    output = tmp_path / "export.png"

    result = export_variant(
        cutout,
        output,
        transparent="false",
        background="#000000",
        padding=2,
        crop_mode="bbox",
        output_format="png",
    )

    assert result["transparent"] is False
    assert result["size"] == [10, 10]
    with Image.open(output) as image:
        assert image.mode == "RGBA"
        assert image.size == (10, 10)
        assert image.getpixel((0, 0)) == (0, 0, 0, 255)


def test_export_variant_corner_radius_affects_alpha(tmp_path):
    cutout = tmp_path / "solid.png"
    Image.new("RGBA", (20, 20), (255, 0, 0, 255)).save(cutout)
    output = tmp_path / "rounded.png"

    export_variant(cutout, output, transparent=True, corner_radius=6)

    with Image.open(output) as image:
        assert image.getpixel((0, 0))[3] == 0
        assert image.getpixel((10, 10))[3] == 255


def test_export_region_variant_uses_bbox_and_corner_radius(tmp_path):
    source = tmp_path / "source.png"
    image = Image.new("RGB", (20, 20), (200, 200, 200))
    for x in range(4, 12):
        for y in range(4, 12):
            image.putpixel((x, y), (255, 0, 0))
    image.save(source)
    output = tmp_path / "region.png"

    result = export_region_variant(source, output, bbox=[4, 4, 12, 12], corner_radius=3)

    assert result["size"] == [8, 8]
    assert result["bbox"] == [4, 4, 12, 12]
    with Image.open(output) as exported:
        assert exported.size == (8, 8)
        assert exported.getpixel((0, 0))[3] == 0
        assert exported.getpixel((4, 4)) == (255, 0, 0, 255)


def test_create_package_includes_source_json(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "source.json").write_text('{"schema_version":"0.1"}\n', encoding="utf-8")
    (workspace / "exports").mkdir()
    (workspace / "exports" / "export_001.png").write_bytes(b"data")

    output = tmp_path / "package.zip"
    result = create_package(workspace, output)

    assert output.exists()
    assert result["size_bytes"] > 0
