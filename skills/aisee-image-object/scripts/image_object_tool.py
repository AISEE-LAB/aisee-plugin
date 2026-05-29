#!/usr/bin/env python3
"""CLI for aisee:image-object workspaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from export_runner import create_package, export_variant
from extract_object import extract_object
from inpaint_runner import inpaint_background
from mask_ops import refine_mask_file
from model_registry import list_profiles, resolve_profile
from rembg_runner import remove_background, remove_background_region
from runtime_config import load_runtime_config, resolve_lama_backend
from sam_runner import segment_with_sam2
from source_state import (
    add_operation,
    find_by_id,
    load_state,
    next_id,
    relpath,
    save_state,
    upsert_model_record,
    workspace_path,
)
from workspace import init_workspace


def _json(data: dict[str, Any], *, code: int = 0) -> None:
    stream = sys.stdout if code == 0 else sys.stderr
    print(json.dumps(data, ensure_ascii=False, indent=2), file=stream)
    raise SystemExit(code)


def _handle_error(exc: Exception) -> None:
    _json({"ok": False, "error": str(exc), "type": exc.__class__.__name__}, code=2)


def _source_path(workspace: Path, state: dict[str, Any]) -> Path:
    return workspace_path(workspace, state["source"].get("path", "source.png"))


def _record_mask(
    state: dict[str, Any],
    workspace: Path,
    *,
    path: Path,
    source: str,
    bbox: list[int] | None = None,
    model: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    item = {
        "id": next_id(state, "masks", "mask"),
        "path": relpath(path, workspace),
        "source": source,
        "bbox": bbox,
        "model": model,
    }
    if notes:
        item["notes"] = notes
    state["masks"].append(item)
    return item


def _record_object(
    state: dict[str, Any],
    workspace: Path,
    *,
    path: Path,
    mask_id: str | None,
    bbox: list[int] | None,
    size: list[int],
    name: str | None = None,
    intent: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    item = {
        "id": next_id(state, "objects", "obj"),
        "path": relpath(path, workspace),
        "mask_id": mask_id,
        "bbox": bbox,
        "size": size,
        "name": name or "",
        "intent": intent or "",
        "notes": notes or "",
    }
    state["objects"].append(item)
    return item


def cmd_init(args: argparse.Namespace) -> None:
    state = init_workspace(args.input, args.output, force=args.force)
    _json({"ok": True, "workspace": str(Path(args.output)), "state": state})


def cmd_models(args: argparse.Namespace) -> None:
    _json({"ok": True, "profiles": list_profiles()})


def cmd_remove_bg(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    profile = resolve_profile(args.profile)
    source = _source_path(workspace, state)
    last_error: Exception | None = None

    for model in profile.models:
        mask_id = next_id(state, "masks", "mask")
        object_id = next_id(state, "objects", "obj")
        mask_path = workspace / "masks" / f"{mask_id}.png"
        cutout_path = workspace / "cutouts" / f"{object_id}.png"
        try:
            result = remove_background(source, cutout_path, mask_path, model=model)
        except Exception as exc:
            last_error = exc
            upsert_model_record(
                state,
                backend=profile.backend,
                model=model,
                profile=profile.name,
                status="failed",
                message=str(exc),
            )
            continue

        mask_item = {
            "id": mask_id,
            "path": relpath(mask_path, workspace),
            "source": "rembg",
            "bbox": result.get("bbox"),
            "model": model,
        }
        state["masks"].append(mask_item)
        object_item = {
            "id": object_id,
            "path": relpath(cutout_path, workspace),
            "mask_id": mask_id,
            "bbox": result.get("bbox"),
            "size": result.get("size"),
            "name": args.name or "",
            "intent": args.intent or "",
            "notes": args.notes or "",
        }
        state["objects"].append(object_item)
        upsert_model_record(state, backend=profile.backend, model=model, profile=profile.name)
        add_operation(
            state,
            "remove-bg",
            params={"profile": profile.name, "model": model},
            outputs=[mask_item["path"], object_item["path"]],
        )
        save_state(workspace, state)
        _json({"ok": True, "mask": mask_item, "object": object_item, "model": model})

    add_operation(
        state,
        "remove-bg",
        status="failed",
        params={"profile": profile.name},
        message=str(last_error) if last_error else "没有可用模型",
    )
    save_state(workspace, state)
    _json({"ok": False, "error": str(last_error) if last_error else "没有可用模型"}, code=2)


def cmd_remove_bg_region(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    profile = resolve_profile(args.profile)
    source = _source_path(workspace, state)
    region = find_by_id(state, "regions", args.region_id)
    last_error: Exception | None = None

    for model in profile.models:
        mask_id = next_id(state, "masks", "mask")
        mask_path = workspace / "masks" / f"{mask_id}.png"
        try:
            result = remove_background_region(source, mask_path, model=model, bbox=region["bbox"])
        except Exception as exc:
            last_error = exc
            upsert_model_record(
                state,
                backend=profile.backend,
                model=model,
                profile=profile.name,
                status="failed",
                message=str(exc),
            )
            continue

        mask_item = {
            "id": mask_id,
            "path": relpath(mask_path, workspace),
            "source": "rembg-region",
            "region_id": args.region_id,
            "bbox": result["bbox"],
            "region_bbox": result["region_bbox"],
            "model": model,
            "notes": args.notes or "",
        }
        state["masks"].append(mask_item)
        outputs = [mask_item["path"]]
        upsert_model_record(state, backend=profile.backend, model=model, profile=profile.name)
        add_operation(
            state,
            "remove-bg-region",
            params={"region_id": args.region_id, "profile": profile.name, "model": model, "bbox": region["bbox"]},
            outputs=outputs,
        )

        object_item = None
        if args.extract:
            object_id = next_id(state, "objects", "obj")
            output = workspace / "cutouts" / f"{object_id}.png"
            extract_result = extract_object(source, mask_path, output, crop=not args.no_crop)
            object_item = _record_object(
                state,
                workspace,
                path=output,
                mask_id=mask_id,
                bbox=extract_result["bbox"],
                size=extract_result["size"],
                name=args.name,
                intent=args.intent,
                notes=args.notes,
            )
            object_item["region_id"] = args.region_id
            add_operation(
                state,
                "extract-object",
                params={"mask": mask_id, "crop": not args.no_crop},
                outputs=[object_item["path"]],
            )

        save_state(workspace, state)
        _json({"ok": True, "mask": mask_item, "object": object_item, "model": model})

    add_operation(
        state,
        "remove-bg-region",
        status="failed",
        params={"region_id": args.region_id, "profile": profile.name, "bbox": region.get("bbox")},
        message=str(last_error) if last_error else "没有可用模型",
    )
    save_state(workspace, state)
    _json({"ok": False, "error": str(last_error) if last_error else "没有可用模型"}, code=2)


def cmd_refine_mask(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    if args.mask.startswith("mask_"):
        source_mask = find_by_id(state, "masks", args.mask)
        input_mask = workspace_path(workspace, source_mask["path"])
    else:
        input_mask = workspace_path(workspace, args.mask)
    mask_id = next_id(state, "masks", "mask")
    output = workspace / "masks" / f"{mask_id}.png"
    result = refine_mask_file(
        input_mask,
        output,
        expand=args.expand,
        contract=args.contract,
        feather=args.feather,
        smooth=args.smooth,
        invert=args.invert,
    )
    item = _record_mask(
        state,
        workspace,
        path=output,
        source="refine",
        bbox=result["bbox"],
        notes=args.notes,
    )
    add_operation(
        state,
        "refine-mask",
        params={
            "mask": args.mask,
            "expand": args.expand,
            "contract": args.contract,
            "feather": args.feather,
            "smooth": args.smooth,
            "invert": args.invert,
        },
        outputs=[item["path"]],
    )
    save_state(workspace, state)
    _json({"ok": True, "mask": item})


def cmd_extract_object(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    source = _source_path(workspace, state)
    mask_value = args.mask
    mask_id = None
    if mask_value.startswith("mask_"):
        mask_item = find_by_id(state, "masks", mask_value)
        mask_path = workspace_path(workspace, mask_item["path"])
        mask_id = mask_item["id"]
    else:
        mask_path = workspace_path(workspace, mask_value)
    object_id = next_id(state, "objects", "obj")
    output = workspace / "cutouts" / f"{object_id}.png"
    result = extract_object(source, mask_path, output, crop=not args.no_crop)
    item = _record_object(
        state,
        workspace,
        path=output,
        mask_id=mask_id,
        bbox=result["bbox"],
        size=result["size"],
        name=args.name,
        intent=args.intent,
        notes=args.notes,
    )
    add_operation(
        state,
        "extract-object",
        params={"mask": args.mask, "crop": not args.no_crop},
        outputs=[item["path"]],
    )
    save_state(workspace, state)
    _json({"ok": True, "object": item})


def cmd_export_variant(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    object_item = find_by_id(state, "objects", args.object_id)
    cutout = workspace_path(workspace, object_item["path"])
    export_id = next_id(state, "exports", "export")
    output_format = args.format.lower()
    output = workspace / "exports" / f"{export_id}.{output_format}"
    result = export_variant(
        cutout,
        output,
        transparent=args.transparent,
        background=args.background,
        corner_radius=args.corner_radius,
        padding=args.padding,
        crop_mode=args.crop_mode,
        output_format=output_format,
    )
    item = {
        "id": export_id,
        "object_id": args.object_id,
        "path": relpath(result["path"], workspace),
        "size": result["size"],
        "transparent": result["transparent"],
        "background": result["background"],
        "corner_radius": result["corner_radius"],
        "padding": result["padding"],
        "crop_mode": result["crop_mode"],
        "format": result["format"],
        "notes": args.notes or "",
    }
    state["exports"].append(item)
    add_operation(state, "export-variant", params=item, outputs=[item["path"]])
    save_state(workspace, state)
    _json({"ok": True, "export": item})


def cmd_inpaint_background(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    source = _source_path(workspace, state)
    mask_value = args.mask
    if mask_value.startswith("mask_"):
        mask_item = find_by_id(state, "masks", mask_value)
        mask_path = workspace_path(workspace, mask_item["path"])
    else:
        mask_path = workspace_path(workspace, mask_value)
    bg_id = next_id(state, "backgrounds", "bg")
    output = workspace / "backgrounds" / f"{bg_id}.png"
    try:
        result = inpaint_background(
            source,
            mask_path,
            output,
            method=args.method,
            radius=args.radius,
            device=args.device,
            iopaint_bin=args.iopaint_bin,
            config_path=args.config,
        )
    except Exception as exc:
        if args.method != "lama" or not args.fallback_opencv:
            raise
        result = inpaint_background(
            source,
            mask_path,
            output,
            method="opencv-telea",
            radius=args.radius,
            device=args.device,
            iopaint_bin=args.iopaint_bin,
            config_path=args.config,
        )
        result["fallback_from"] = "lama"
        result["fallback_reason"] = str(exc)
    item = {
        "id": bg_id,
        "path": relpath(output, workspace),
        "mask": args.mask,
        "scope": {"type": "masks", "ids": [args.mask]},
        "mask_ids": [args.mask],
        "method": result["method"],
        "backend": result.get("backend"),
        "device": result.get("device"),
        "iopaint_bin": result.get("iopaint_bin"),
        "config_path": result.get("config_path"),
        "radius": result["radius"],
    }
    if "fallback_from" in result:
        item["fallback_from"] = result["fallback_from"]
        item["fallback_reason"] = result["fallback_reason"]
    state["backgrounds"].append(item)
    add_operation(state, "inpaint-background", params=item, outputs=[item["path"]])
    save_state(workspace, state)
    _json({"ok": True, "background": item})


def cmd_segment_sam2(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    state = load_state(workspace)
    source = _source_path(workspace, state)
    mask_id = next_id(state, "masks", "mask")
    output = workspace / "masks" / f"{mask_id}.png"
    points = _parse_points(args.points)
    labels = [int(value) for value in args.labels.split(",")] if args.labels else None
    box = [float(value) for value in args.box.split(",")] if args.box else None
    result = segment_with_sam2(
        source,
        output,
        points=points,
        labels=labels,
        box=box,
        checkpoint=args.checkpoint,
        model_cfg=args.model_cfg,
    )
    item = _record_mask(state, workspace, path=output, source="sam2", model="sam2", notes=args.notes)
    item["score"] = result.get("score")
    upsert_model_record(state, backend="sam2", model="sam2", status="used")
    add_operation(state, "segment-sam2", params={"points": points, "labels": labels, "box": box}, outputs=[item["path"]])
    save_state(workspace, state)
    _json({"ok": True, "mask": item})


def _parse_points(raw: str | None) -> list[list[float]] | None:
    if not raw:
        return None
    points: list[list[float]] = []
    for pair in raw.split(";"):
        x, y = pair.split(",", 1)
        points.append([float(x), float(y)])
    return points


def cmd_package(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    output = Path(args.output) if args.output else workspace / "packages" / "image-object-package.zip"
    result = create_package(workspace, output)
    state = load_state(workspace)
    add_operation(state, "export-package", params={"output": str(output)}, outputs=[relpath(output, workspace)])
    save_state(workspace, state)
    _json({"ok": True, "package": result})


def cmd_select(args: argparse.Namespace) -> None:
    if not args.interactive:
        _json({"ok": False, "error": "select 目前需要 --interactive 启动 GUI。"}, code=2)
    try:
        from gui.app import run
    except ImportError as exc:
        _json(
            {
                "ok": False,
                "error": "PySide6 GUI 依赖未安装。请先安装 PySide6，或继续使用 CLI。",
                "detail": str(exc),
            },
            code=2,
        )
    raise SystemExit(run(workspace=args.workspace, image=args.image))


def cmd_config_preview(args: argparse.Namespace) -> None:
    config = load_runtime_config(args.config)
    lama_backend = resolve_lama_backend(
        config=config,
        iopaint_bin=args.iopaint_bin,
        device=args.device,
    )
    _json({"ok": True, "config": {"lama_backend": lama_backend}})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="aisee:image-object 对象级图片处理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="创建单图 workspace")
    init.add_argument("--input", required=True, help="输入图片路径")
    init.add_argument("--output", required=True, help="workspace 输出目录")
    init.add_argument("--force", action="store_true", help="覆盖已有 source.json")
    init.set_defaults(func=cmd_init)

    models = subparsers.add_parser("models", help="列出模型 profile")
    models.set_defaults(func=cmd_models)

    remove_bg = subparsers.add_parser("remove-bg", help="调用 rembg 去背景")
    remove_bg.add_argument("--workspace", required=True)
    remove_bg.add_argument("--profile", default="quality", help="profile 或具体 rembg 模型")
    remove_bg.add_argument("--name", default="")
    remove_bg.add_argument("--intent", default="")
    remove_bg.add_argument("--notes", default="")
    remove_bg.set_defaults(func=cmd_remove_bg)

    remove_bg_region = subparsers.add_parser("remove-bg-region", help="基于框选区域调用 rembg 生成局部 Mask")
    remove_bg_region.add_argument("--workspace", required=True)
    remove_bg_region.add_argument("--region-id", required=True)
    remove_bg_region.add_argument("--profile", default="quality", help="profile 或具体 rembg 模型")
    remove_bg_region.add_argument("--name", default="")
    remove_bg_region.add_argument("--intent", default="")
    remove_bg_region.add_argument("--notes", default="")
    remove_bg_region.add_argument("--extract", action="store_true", help="生成 Mask 后同时提取 Cutout")
    remove_bg_region.add_argument("--no-crop", action="store_true", help="提取 Cutout 时保持原图画布")
    remove_bg_region.set_defaults(func=cmd_remove_bg_region)

    refine = subparsers.add_parser("refine-mask", help="修正 mask 边缘")
    refine.add_argument("--workspace", required=True)
    refine.add_argument("--mask", required=True, help="mask ID 或路径")
    refine.add_argument("--expand", type=int, default=0)
    refine.add_argument("--contract", type=int, default=0)
    refine.add_argument("--feather", type=float, default=0.0)
    refine.add_argument("--smooth", type=int, default=0)
    refine.add_argument("--invert", action="store_true")
    refine.add_argument("--notes", default="")
    refine.set_defaults(func=cmd_refine_mask)

    extract = subparsers.add_parser("extract-object", help="基于 mask 提取对象 cutout")
    extract.add_argument("--workspace", required=True)
    extract.add_argument("--mask", required=True, help="mask ID 或路径")
    extract.add_argument("--name", default="")
    extract.add_argument("--intent", default="")
    extract.add_argument("--notes", default="")
    extract.add_argument("--no-crop", action="store_true", help="保持原图画布，不按 BBox 裁切")
    extract.set_defaults(func=cmd_extract_object)

    export = subparsers.add_parser("export-variant", help="导出透明/背景/圆角/padding 变体")
    export.add_argument("--workspace", required=True)
    export.add_argument("--object-id", required=True)
    export.add_argument("--transparent", default="true")
    export.add_argument("--background", default=None)
    export.add_argument("--corner-radius", type=int, default=0)
    export.add_argument("--padding", type=int, default=0)
    export.add_argument("--crop-mode", default="bbox", choices=["bbox", "original-canvas", "square"])
    export.add_argument("--format", default="png", choices=["png", "webp", "jpg", "jpeg"])
    export.add_argument("--notes", default="")
    export.set_defaults(func=cmd_export_variant)

    inpaint = subparsers.add_parser("inpaint-background", help="基于 mask 修补背景")
    inpaint.add_argument("--workspace", required=True)
    inpaint.add_argument("--mask", required=True)
    inpaint.add_argument("--method", default="lama", choices=["lama", "opencv-telea", "opencv-ns", "image-gen"])
    inpaint.add_argument("--radius", type=int, default=3)
    inpaint.add_argument("--device", default="cpu", help="LaMa/IOPaint 设备，如 cpu、mps、cuda")
    inpaint.add_argument("--iopaint-bin", default=None, help="独立 Python 3.10/3.11 环境中的 iopaint 可执行文件")
    inpaint.add_argument("--config", default=None, help="运行配置 JSON，默认查找 .aisee/image-object/config.json")
    inpaint.add_argument("--fallback-opencv", action="store_true", help="LaMa 不可用时自动 fallback 到 OpenCV")
    inpaint.set_defaults(func=cmd_inpaint_background)

    segment = subparsers.add_parser("segment-sam2", help="SAM2 点选/框选分割")
    segment.add_argument("--workspace", required=True)
    segment.add_argument("--points", default=None, help="点坐标，如 10,20;30,40")
    segment.add_argument("--labels", default=None, help="点标签，如 1,0")
    segment.add_argument("--box", default=None, help="BBox，如 x1,y1,x2,y2")
    segment.add_argument("--checkpoint", default=None)
    segment.add_argument("--model-cfg", default=None)
    segment.add_argument("--notes", default="")
    segment.set_defaults(func=cmd_segment_sam2)

    package = subparsers.add_parser("export-package", help="打包 workspace 产物")
    package.add_argument("--workspace", required=True)
    package.add_argument("--output", default=None)
    package.set_defaults(func=cmd_package)

    select = subparsers.add_parser("select", help="启动交互式 GUI")
    select.add_argument("--image", default=None, help="要打开的图片路径；推荐使用该参数启动 GUI")
    select.add_argument("--workspace", default=None, help="已有图片项目目录；兼容旧项目")
    select.add_argument("--interactive", action="store_true")
    select.set_defaults(func=cmd_select)

    config = subparsers.add_parser("config-preview", help="预览运行配置解析结果")
    config.add_argument("--config", default=None, help="运行配置 JSON")
    config.add_argument("--iopaint-bin", default=None, help="覆盖 LaMa backend 的 iopaint 路径")
    config.add_argument("--device", default=None, help="覆盖 LaMa backend 设备")
    config.set_defaults(func=cmd_config_preview)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception as exc:
        _handle_error(exc)


if __name__ == "__main__":
    main()
