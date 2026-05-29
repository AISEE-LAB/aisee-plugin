from __future__ import annotations

from PIL import Image, ImageDraw

from mask_ops import create_bbox_mask_file, create_bboxes_mask_file, mask_bbox, refine_mask_file


def _mask(path):
    image = Image.new("L", (10, 10), 0)
    draw = ImageDraw.Draw(image)
    draw.rectangle((3, 3, 6, 6), fill=255)
    image.save(path)
    return image


def test_refine_mask_expand_changes_bbox(tmp_path):
    input_path = tmp_path / "mask.png"
    original = _mask(input_path)
    assert mask_bbox(original) == [3, 3, 7, 7]

    output_path = tmp_path / "expanded.png"
    result = refine_mask_file(input_path, output_path, expand=1)

    assert output_path.exists()
    assert result["bbox"] == [2, 2, 8, 8]


def test_create_bbox_mask_file_uses_source_size(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "mask.png"
    Image.new("RGB", (12, 10), (255, 255, 255)).save(source)

    result = create_bbox_mask_file(source, output, bbox=[2, 3, 7, 8], expand=1)

    assert output.exists()
    assert result["size"] == [12, 10]
    assert result["bbox"] == [1, 2, 8, 9]
    with Image.open(output).convert("L") as mask:
        assert mask.getbbox() == (1, 2, 8, 9)


def test_create_bboxes_mask_file_combines_regions(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "mask.png"
    Image.new("RGB", (12, 10), (255, 255, 255)).save(source)

    result = create_bboxes_mask_file(source, output, bboxes=[[1, 1, 3, 3], [8, 6, 11, 9]])

    assert output.exists()
    assert result["size"] == [12, 10]
    assert result["bbox"] == [1, 1, 11, 9]
    assert result["bboxes"] == [[1, 1, 3, 3], [8, 6, 11, 9]]
