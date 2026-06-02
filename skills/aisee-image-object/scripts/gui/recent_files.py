"""Recent image project records."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_RECENT_PATH = Path("aisee/cache/image-object/recent.json")
LEGACY_RECENT_PATH = Path.home() / ".aisee" / "image-object" / "recent.json"
MAX_RECENT = 12


def recent_path() -> Path:
    env_path = os.getenv("AISEE_IMAGE_OBJECT_RECENT_PATH")
    if env_path:
        return Path(env_path)
    return Path.cwd() / DEFAULT_RECENT_PATH


def load_recent_records() -> list[dict[str, Any]]:
    path = recent_path()
    if not path.exists() and not os.getenv("AISEE_IMAGE_OBJECT_RECENT_PATH"):
        path = LEGACY_RECENT_PATH
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    records = []
    for item in data:
        if not isinstance(item, dict):
            continue
        workspace = str(item.get("workspace") or "")
        image = str(item.get("image") or "")
        if workspace:
            records.append({"workspace": workspace, "image": image})
    return records[:MAX_RECENT]


def save_recent_record(*, workspace: str | Path, image: str | Path = "") -> None:
    workspace_text = str(workspace)
    image_text = str(image)
    records = [
        item
        for item in load_recent_records()
        if item.get("workspace") != workspace_text and item.get("image") != image_text
    ]
    records.insert(0, {"workspace": workspace_text, "image": image_text})
    path = recent_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(records[:MAX_RECENT], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def last_recent_workspace() -> str | None:
    for item in load_recent_records():
        workspace = item.get("workspace")
        if workspace and Path(workspace).exists():
            return str(workspace)
    return None
