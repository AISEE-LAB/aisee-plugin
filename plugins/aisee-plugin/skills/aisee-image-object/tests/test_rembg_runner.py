from __future__ import annotations

from io import BytesIO
import sys
import types

from PIL import Image

from rembg_runner import remove_background_region


def test_remove_background_region_pastes_mask_back_to_source_canvas(tmp_path, monkeypatch):
    def fake_new_session(model):
        return {"model": model}

    def fake_remove(input_bytes, session):
        with Image.open(BytesIO(input_bytes)).convert("RGBA") as image:
            cutout = Image.new("RGBA", image.size, (255, 0, 0, 0))
            for x in range(1, image.width - 1):
                for y in range(1, image.height - 1):
                    cutout.putpixel((x, y), (255, 0, 0, 255))
            output = BytesIO()
            cutout.save(output, format="PNG")
            return output.getvalue()

    monkeypatch.setitem(
        sys.modules,
        "rembg",
        types.SimpleNamespace(new_session=fake_new_session, remove=fake_remove),
    )

    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    Image.new("RGB", (10, 10), (200, 200, 200)).save(source)

    result = remove_background_region(source, mask, model="u2net", bbox=[2, 3, 8, 9])

    assert result["region_bbox"] == [2, 3, 8, 9]
    assert result["bbox"] == [3, 4, 7, 8]
    with Image.open(mask) as image:
        assert image.size == (10, 10)
        assert image.getpixel((2, 3)) == 0
        assert image.getpixel((3, 4)) == 255
