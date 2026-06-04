#!/usr/bin/env python3
"""Runtime configuration for optional aisee:image-object backends."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATHS = (
    "aisee/config/image-object/config.json",
    ".aisee/image-object/config.json",
    ".aisee-image-object.json",
)


def load_runtime_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = _resolve_config_path(config_path)
    if not path:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"运行配置 JSON 格式错误: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"运行配置必须是 JSON object: {path}")
    data["_config_path"] = str(path)
    return data


def _resolve_config_path(config_path: str | Path | None = None) -> Path | None:
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"运行配置不存在: {path}")
        return path
    env_path = os.getenv("AISEE_IMAGE_OBJECT_CONFIG")
    if env_path:
        path = Path(env_path)
        if not path.exists():
            raise FileNotFoundError(f"运行配置不存在: {path}")
        return path
    for candidate in DEFAULT_CONFIG_PATHS:
        path = Path(candidate)
        if path.exists():
            return path
    return None


def resolve_lama_backend(
    *,
    config: dict[str, Any] | None = None,
    iopaint_bin: str | None = None,
    device: str | None = None,
) -> dict[str, Any]:
    config = config or {}
    backend = config.get("lama_backend", {})
    if backend is None:
        backend = {}
    if not isinstance(backend, dict):
        raise ValueError("lama_backend 必须是 JSON object")

    resolved = {
        "enabled": bool(backend.get("enabled", True)),
        "iopaint_bin": iopaint_bin
        or os.getenv("AISEE_IMAGE_OBJECT_IOPAINT_BIN")
        or backend.get("iopaint_bin"),
        "device": device
        or os.getenv("AISEE_IMAGE_OBJECT_LAMA_DEVICE")
        or backend.get("device")
        or "cpu",
        "config_path": config.get("_config_path"),
    }
    return resolved
