#!/usr/bin/env python3
"""Check dependencies for aisee:image-object."""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
from dataclasses import asdict, dataclass
from typing import Any

from runtime_config import load_runtime_config, resolve_lama_backend


@dataclass
class Dependency:
    name: str
    module: str
    group: str
    required: bool
    purpose: str
    install: str
    status: str = "missing"
    version: str | None = None
    error: str | None = None


DEPENDENCIES = [
    Dependency("Pillow", "PIL", "core", True, "读取图片、mask、cutout、导出与预览渲染", "python -m pip install pillow"),
    Dependency("numpy", "numpy", "core", True, "数组处理，OpenCV 和模型后端基础依赖", "python -m pip install numpy"),
    Dependency("OpenCV", "cv2", "core", True, "背景修补 fallback、图像处理辅助", "python -m pip install opencv-python"),
    Dependency("PySide6", "PySide6", "gui", False, "中文双画布 GUI", "python -m pip install PySide6"),
    Dependency("rembg", "rembg", "matting", False, "去背景主路径，调用 BiRefNet / U2-Net 等模型", "python -m pip install rembg"),
    Dependency("onnxruntime", "onnxruntime", "matting", False, "rembg ONNX 模型推理运行时", "python -m pip install onnxruntime"),
    Dependency("scikit-image", "skimage", "matting", False, "rembg 依赖，matting 质量辅助", "python -m pip install scikit-image"),
    Dependency("torch", "torch", "segmentation", False, "SAM2 推理依赖", "python -m pip install torch torchvision"),
    Dependency("torchvision", "torchvision", "segmentation", False, "SAM2 图像模型依赖", "python -m pip install torch torchvision"),
    Dependency("SAM2", "sam2", "segmentation", False, "点选/框选分割可选 backend，需要额外 checkpoint/model_cfg", "python -m pip install sam2"),
    Dependency("IOPaint", "iopaint", "inpainting", False, "LaMa 背景修补优先 backend", "python -m pip install iopaint"),
]


def check_dependency(dep: Dependency) -> Dependency:
    try:
        module = importlib.import_module(dep.module)
    except Exception as exc:
        dep.status = "missing"
        dep.error = f"{exc.__class__.__name__}: {exc}"
        return dep

    dep.status = "present"
    dep.version = getattr(module, "__version__", None)
    return dep


def run_checks() -> list[Dependency]:
    return [check_dependency(dep) for dep in DEPENDENCIES]


def check_runtime_backends(config_path: str | None = None) -> dict[str, Any]:
    config = load_runtime_config(config_path)
    lama = resolve_lama_backend(config=config)
    executable = lama["iopaint_bin"] or shutil.which("iopaint")
    if executable and (shutil.which(str(executable)) or __import__("pathlib").Path(executable).exists()):
        status = "present"
        message = "LaMa / IOPaint CLI 已配置"
    else:
        status = "missing"
        message = "未找到 IOPaint CLI；可通过配置文件或 AISEE_IMAGE_OBJECT_IOPAINT_BIN 指定独立环境路径"
    return {
        "lama_backend": {
            **lama,
            "resolved_iopaint_bin": str(executable) if executable else None,
            "status": status,
            "message": message,
        }
    }


def summary(checks: list[Dependency]) -> dict[str, Any]:
    missing_required = [dep.name for dep in checks if dep.required and dep.status != "present"]
    missing_optional = [dep.name for dep in checks if not dep.required and dep.status != "present"]
    return {
        "ok": not missing_required,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "counts": {
            "present": sum(1 for dep in checks if dep.status == "present"),
            "missing": sum(1 for dep in checks if dep.status != "present"),
        },
    }


def print_text(checks: list[Dependency], runtime: dict[str, Any]) -> None:
    data = summary(checks)
    print("aisee:image-object 依赖检查")
    print(f"核心依赖状态：{'通过' if data['ok'] else '缺失'}")
    print("")
    for dep in checks:
        marker = "OK" if dep.status == "present" else "缺失"
        required = "必需" if dep.required else "可选"
        version = f" {dep.version}" if dep.version else ""
        print(f"[{marker}] {dep.group} / {required} / {dep.name}{version}")
        print(f"  用途：{dep.purpose}")
        if dep.status != "present":
            print(f"  安装：{dep.install}")
            if dep.error:
                print(f"  错误：{dep.error}")
        print("")
    if data["missing_optional"]:
        print("说明：可选依赖缺失不会阻止 CLI 基础链路，但对应 GUI 或模型 backend 不可用。")
    lama = runtime["lama_backend"]
    print("")
    print(f"LaMa backend：{lama['status']}")
    print(f"  iopaint：{lama['resolved_iopaint_bin'] or '未配置'}")
    print(f"  device：{lama['device']}")
    print(f"  说明：{lama['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查 aisee:image-object 依赖")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--config", default=None, help="运行配置 JSON")
    args = parser.parse_args(argv)

    checks = run_checks()
    runtime = check_runtime_backends(args.config)
    if args.json:
        print(
            json.dumps(
                {
                    "summary": summary(checks),
                    "dependencies": [asdict(dep) for dep in checks],
                    "runtime": runtime,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(checks, runtime)
    return 0 if summary(checks)["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
