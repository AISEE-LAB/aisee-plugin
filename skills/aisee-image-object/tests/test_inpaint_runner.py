from __future__ import annotations

from PIL import Image
import pytest

from inpaint_runner import inpaint_background, inpaint_background_isolated, inpaint_background_opencv


def test_lama_missing_does_not_silently_fallback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AISEE_IMAGE_OBJECT_CONFIG", raising=False)
    monkeypatch.delenv("AISEE_IMAGE_OBJECT_IOPAINT_BIN", raising=False)
    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (8, 8), (255, 255, 255)).save(source)
    Image.new("L", (8, 8), 0).save(mask)

    with pytest.raises(RuntimeError, match="LaMa backend"):
        inpaint_background(source, mask, output, method="lama")


def test_lama_missing_mentions_external_iopaint_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AISEE_IMAGE_OBJECT_CONFIG", raising=False)
    monkeypatch.delenv("AISEE_IMAGE_OBJECT_IOPAINT_BIN", raising=False)
    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (8, 8), (255, 255, 255)).save(source)
    Image.new("L", (8, 8), 0).save(mask)

    with pytest.raises(RuntimeError, match="--iopaint-bin"):
        inpaint_background(source, mask, output, method="lama")


def test_opencv_fallback_is_explicit(tmp_path):
    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (8, 8), (255, 255, 255)).save(source)
    mask_image = Image.new("L", (8, 8), 0)
    mask_image.putpixel((4, 4), 255)
    mask_image.save(mask)

    result = inpaint_background_opencv(source, mask, output)

    assert result["method"] == "opencv-telea"
    assert result["backend"] == "opencv"
    assert output.exists()


def test_isolated_inpaint_runs_backend_in_child_process(tmp_path):
    source = tmp_path / "source.png"
    mask = tmp_path / "mask.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (8, 8), (255, 255, 255)).save(source)
    mask_image = Image.new("L", (8, 8), 0)
    mask_image.putpixel((4, 4), 255)
    mask_image.save(mask)

    result = inpaint_background_isolated(source, mask, output, method="opencv-telea")

    assert result["method"] == "opencv-telea"
    assert result["backend"] == "opencv"
    assert output.exists()


def test_isolated_inpaint_reports_child_crash(tmp_path, monkeypatch):
    class Result:
        returncode = -11
        stdout = ""
        stderr = ""

    monkeypatch.setattr("inpaint_runner.subprocess.run", lambda *args, **kwargs: Result())

    with pytest.raises(RuntimeError, match="signal 11"):
        inpaint_background_isolated(tmp_path / "source.png", tmp_path / "mask.png", tmp_path / "output.png")
