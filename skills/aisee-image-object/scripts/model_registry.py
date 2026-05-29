#!/usr/bin/env python3
"""Model profile registry for optional image-object backends."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    name: str
    backend: str
    models: tuple[str, ...]
    description: str


PROFILES: dict[str, ModelProfile] = {
    "quality": ModelProfile(
        "quality",
        "rembg",
        ("birefnet-general", "birefnet-general-lite", "isnet-general-use", "u2net"),
        "高质量通用去背景，优先 BiRefNet。",
    ),
    "fast": ModelProfile(
        "fast",
        "rembg",
        ("birefnet-general-lite", "u2netp", "u2net"),
        "速度优先，适合快速预览。",
    ),
    "product": ModelProfile(
        "product",
        "rembg",
        ("birefnet-general", "isnet-general-use", "u2net"),
        "产品图和通用物体优先。",
    ),
    "portrait": ModelProfile(
        "portrait",
        "rembg",
        ("birefnet-portrait", "u2net_human_seg", "u2net"),
        "人像优先。",
    ),
    "anime": ModelProfile(
        "anime",
        "rembg",
        ("isnet-anime", "u2net"),
        "动漫或插画图优先。",
    ),
    "compat": ModelProfile(
        "compat",
        "rembg",
        ("u2net", "u2netp"),
        "兼容路径，依赖最少。",
    ),
}


KNOWN_REMBG_MODELS = {
    "u2net",
    "u2netp",
    "u2net_human_seg",
    "silueta",
    "isnet-general-use",
    "isnet-anime",
    "birefnet-general",
    "birefnet-general-lite",
    "birefnet-portrait",
    "bria-rmbg",
}


def list_profiles() -> list[dict[str, object]]:
    return [
        {
            "name": profile.name,
            "backend": profile.backend,
            "models": list(profile.models),
            "description": profile.description,
        }
        for profile in PROFILES.values()
    ]


def resolve_profile(profile_or_model: str | None) -> ModelProfile:
    value = (profile_or_model or "quality").strip()
    if value in PROFILES:
        return PROFILES[value]
    if value in KNOWN_REMBG_MODELS:
        return ModelProfile(value, "rembg", (value,), "用户指定 rembg 模型。")
    raise ValueError(
        f"未知模型 profile 或 rembg 模型: {value}。可用 profile: {', '.join(sorted(PROFILES))}"
    )
