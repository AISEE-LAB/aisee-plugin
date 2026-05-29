"""User-level recent image project records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RECENT_PATH = Path.home() / ".aisee" / "image-object" / "recent.json"
MAX_RECENT = 12


def load_recent_records() -> list[dict[str, Any]]:
    if not RECENT_PATH.exists():
        return []
    try:
        data = json.loads(RECENT_PATH.read_text(encoding="utf-8"))
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
    RECENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECENT_PATH.write_text(
        json.dumps(records[:MAX_RECENT], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def last_recent_workspace() -> str | None:
    for item in load_recent_records():
        workspace = item.get("workspace")
        if workspace and Path(workspace).exists():
            return str(workspace)
    return None
