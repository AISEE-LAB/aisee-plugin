#!/usr/bin/env python3
"""source.json helpers for aisee:image-object workspaces."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
STATE_FILE = "source.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def empty_state(workspace: str | Path = ".") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace": str(workspace),
        "source": {
            "path": "source.png",
            "original_path": "",
            "width": 0,
            "height": 0,
            "mode": "",
            "format": "",
        },
        "regions": [],
        "models": [],
        "masks": [],
        "objects": [],
        "backgrounds": [],
        "exports": [],
        "enhanced": [],
        "operations": [],
    }


def state_path(workspace: str | Path) -> Path:
    path = Path(workspace)
    return path / STATE_FILE if path.is_dir() or path.suffix == "" else path


def load_state(workspace: str | Path) -> dict[str, Any]:
    path = state_path(workspace)
    if not path.exists():
        raise FileNotFoundError(f"source.json 不存在: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"source.json 必须是 JSON object: {path}")
    ensure_state_shape(data)
    return data


def save_state(workspace: str | Path, state: dict[str, Any]) -> Path:
    path = state_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_state_shape(state)
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def ensure_state_shape(state: dict[str, Any]) -> None:
    state.setdefault("schema_version", SCHEMA_VERSION)
    state.setdefault("workspace", ".")
    state.setdefault("source", {})
    source = state["source"]
    source.setdefault("path", "source.png")
    source.setdefault("original_path", "")
    source.setdefault("width", 0)
    source.setdefault("height", 0)
    source.setdefault("mode", "")
    source.setdefault("format", "")
    for key in ("regions", "models", "masks", "objects", "backgrounds", "exports", "enhanced", "operations"):
        state.setdefault(key, [])


def relpath(path: str | Path, workspace: str | Path) -> str:
    path_obj = Path(path)
    workspace_obj = Path(workspace)
    try:
        return str(path_obj.resolve().relative_to(workspace_obj.resolve()))
    except ValueError:
        return str(path_obj)


def workspace_path(workspace: str | Path, value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return Path(workspace) / path


def next_id(state: dict[str, Any], collection: str, prefix: str) -> str:
    ensure_state_shape(state)
    max_num = 0
    for item in state.get(collection, []):
        raw = str(item.get("id", ""))
        if raw.startswith(f"{prefix}_"):
            suffix = raw.rsplit("_", 1)[-1]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))
    return f"{prefix}_{max_num + 1:03d}"


def add_operation(
    state: dict[str, Any],
    kind: str,
    *,
    status: str = "success",
    params: dict[str, Any] | None = None,
    outputs: list[str] | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    operation = {
        "id": next_id(state, "operations", "op"),
        "kind": kind,
        "status": status,
        "created_at": utc_now(),
        "params": params or {},
        "outputs": outputs or [],
    }
    if message:
        operation["message"] = message
    state["operations"].append(operation)
    return operation


def upsert_model_record(
    state: dict[str, Any],
    *,
    backend: str,
    model: str,
    profile: str | None = None,
    status: str = "used",
    message: str | None = None,
) -> dict[str, Any]:
    record = {
        "backend": backend,
        "model": model,
        "profile": profile,
        "status": status,
        "used_at": utc_now(),
    }
    if message:
        record["message"] = message
    state["models"].append(record)
    return record


def find_by_id(state: dict[str, Any], collection: str, item_id: str) -> dict[str, Any]:
    for item in state.get(collection, []):
        if item.get("id") == item_id:
            return item
    raise KeyError(f"未找到 {collection} 中的 ID: {item_id}")
