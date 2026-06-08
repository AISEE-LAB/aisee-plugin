#!/usr/bin/env python3
"""Background inpainting backends."""

from __future__ import annotations

import shutil
import subprocess
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from runtime_config import load_runtime_config, resolve_lama_backend


def inpaint_background(
    source_path: str | Path,
    mask_path: str | Path,
    output_path: str | Path,
    *,
    method: str = "lama",
    radius: int = 3,
    device: str = "cpu",
    iopaint_bin: str | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    if method == "lama":
        return inpaint_background_lama(
            source_path,
            mask_path,
            output_path,
            device=device,
            iopaint_bin=iopaint_bin,
            config_path=config_path,
        )
    if method not in {"opencv-telea", "opencv-ns"}:
        raise RuntimeError(f"{method} 是可选 backend，当前脚本支持 lama 和 OpenCV fallback。")
    return inpaint_background_opencv(
        source_path,
        mask_path,
        output_path,
        method=method,
        radius=radius,
    )


def inpaint_background_isolated(
    source_path: str | Path,
    mask_path: str | Path,
    output_path: str | Path,
    *,
    method: str = "lama",
    radius: int = 3,
    device: str = "cpu",
    iopaint_bin: str | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run native inpainting backends in a child process to protect the GUI."""

    payload = {
        "source_path": str(source_path),
        "mask_path": str(mask_path),
        "output_path": str(output_path),
        "method": method,
        "radius": int(radius),
        "device": device,
        "iopaint_bin": iopaint_bin,
        "config_path": str(config_path) if config_path else None,
    }
    child_code = r"""
import json
import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path(sys.argv[0]).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from inpaint_runner import inpaint_background

payload = json.loads(sys.stdin.read())
try:
    result = inpaint_background(**payload)
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc), "type": exc.__class__.__name__}, ensure_ascii=False))
    raise SystemExit(2)
print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
"""
    result = subprocess.run(
        [sys.executable, "-c", child_code],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        cwd=str(Path(__file__).resolve().parent),
        check=False,
    )
    if result.returncode != 0:
        try:
            error_payload = json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            error_payload = {}
        message = (
            error_payload.get("error")
            or result.stderr.strip()
            or result.stdout.strip()
            or f"子进程退出码 {result.returncode}"
        )
        if result.returncode < 0:
            message = f"修补 backend 子进程异常退出（signal {-result.returncode}）：{message}"
        raise RuntimeError(message)
    try:
        output_payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError("修补 backend 子进程没有返回有效 JSON。") from exc
    if not output_payload.get("ok"):
        raise RuntimeError(output_payload.get("error", "修补 backend 执行失败。"))
    return output_payload["result"]


def inpaint_background_lama(
    source_path: str | Path,
    mask_path: str | Path,
    output_path: str | Path,
    *,
    device: str = "cpu",
    iopaint_bin: str | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    config = load_runtime_config(config_path)
    backend = resolve_lama_backend(config=config, iopaint_bin=iopaint_bin, device=device)
    if not backend["enabled"]:
        raise RuntimeError("LaMa backend 已在运行配置中禁用。")

    executable = backend["iopaint_bin"] or shutil.which("iopaint")
    if not executable:
        raise RuntimeError(
            "LaMa backend 需要 IOPaint CLI。请在兼容环境安装 `iopaint`，"
            "推荐 Python 3.10/3.11；当前环境若是 Python 3.13，IOPaint 可能因 Pillow 9.5.0 构建失败。"
            "可通过 --iopaint-bin、AISEE_IMAGE_OBJECT_IOPAINT_BIN 或 aisee/config/image-object/config.json 指定独立环境中的 iopaint。"
        )
    if not Path(executable).exists() and shutil.which(str(executable)) is None:
        raise FileNotFoundError(f"IOPaint CLI 不存在或不可执行: {executable}")

    source = Path(source_path)
    mask = Path(mask_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="aisee-lama-") as tmp:
        tmp_path = Path(tmp)
        image_dir = tmp_path / "image"
        mask_dir = tmp_path / "mask"
        result_dir = tmp_path / "output"
        image_dir.mkdir()
        mask_dir.mkdir()
        result_dir.mkdir()
        image_input = image_dir / "input.png"
        mask_input = mask_dir / "input.png"
        _normalize_image_for_lama(source, image_input, mode="RGB")
        _normalize_image_for_lama(mask, mask_input, mode="L")

        command = [
            executable,
            "run",
            "--model=lama",
            f"--device={backend['device']}",
            f"--image={image_dir}",
            f"--mask={mask_dir}",
            f"--output={result_dir}",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(
                "LaMa / IOPaint 执行失败: "
                + (result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")
            )

        candidates = sorted(path for path in result_dir.rglob("*") if path.is_file())
        if not candidates:
            raise RuntimeError("LaMa / IOPaint 没有生成输出文件。")
        shutil.copyfile(candidates[0], output)
        return {
            "path": str(output),
            "method": "lama",
            "backend": "iopaint",
            "device": backend["device"],
            "iopaint_bin": str(executable),
            "config_path": backend.get("config_path"),
            "radius": None,
        }


def _normalize_image_for_lama(input_path: Path, output_path: Path, *, mode: str) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("需要安装 Pillow 才能准备 LaMa 输入。") from exc

    with Image.open(input_path) as image:
        image.convert(mode).save(output_path)


def inpaint_background_opencv(
    source_path: str | Path,
    mask_path: str | Path,
    output_path: str | Path,
    *,
    method: str = "opencv-telea",
    radius: int = 3,
) -> dict[str, Any]:
    try:
        import cv2
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("需要安装 opencv-python、numpy 和 Pillow 才能执行 OpenCV 背景修补。") from exc

    with Image.open(source_path).convert("RGB") as source:
        source_array = cv2.cvtColor(np.array(source), cv2.COLOR_RGB2BGR)
    with Image.open(mask_path).convert("L") as mask:
        mask_array = np.array(mask)

    flag = cv2.INPAINT_TELEA if method == "opencv-telea" else cv2.INPAINT_NS
    result = cv2.inpaint(source_array, mask_array, int(radius), flag)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result).save(output)
    return {"path": str(output), "method": method, "backend": "opencv", "radius": int(radius)}
