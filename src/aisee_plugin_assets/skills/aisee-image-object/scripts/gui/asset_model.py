"""GUI asset list model helpers without PySide dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AssetRecord:
    collection: str
    label: str
    item_id: str
    path: str
    display: str
    item: dict[str, Any]


ASSET_LABELS = {
    "regions": "框选区域",
    "objects": "透明素材",
    "backgrounds": "抹除结果",
    "exports": "导出结果",
    "enhanced": "优化",
}


def build_asset_records(state: dict[str, Any]) -> list[AssetRecord]:
    records: list[AssetRecord] = []
    for collection, label in ASSET_LABELS.items():
        for item in state.get(collection, []):
            item_id = str(item.get("id", ""))
            path = str(item.get("path", ""))
            name = str(item.get("name") or item.get("label") or "").strip()
            suffix = f"  {name}" if name else ""
            records.append(
                AssetRecord(
                    collection=collection,
                    label=label,
                    item_id=item_id,
                    path=path,
                    display=f"{label} {item_id}{suffix}  {path}",
                    item=item,
                )
            )
    return records


def find_first_object(records: list[AssetRecord]) -> AssetRecord | None:
    for record in records:
        if record.collection == "objects":
            return record
    return None
