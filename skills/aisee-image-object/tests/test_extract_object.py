from __future__ import annotations

from PIL import Image, ImageDraw

from extract_object import extract_object


def test_extract_object_applies_mask_and_crops(tmp_path):
    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    output = tmp_path / "cutout.png"

    Image.new("RGB", (10, 10), (255, 0, 0)).save(source)
    mask_image = Image.new("L", (10, 10), 0)
    draw = ImageDraw.Draw(mask_image)
    draw.rectangle((3, 3, 6, 6), fill=255)
    mask_image.save(mask)

    result = extract_object(source, mask, output)

    assert output.exists()
    assert result["bbox"] == [3, 3, 7, 7]
    assert result["size"] == [4, 4]
    with Image.open(output) as image:
        assert image.mode == "RGBA"
        assert image.size == (4, 4)
