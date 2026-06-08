from __future__ import annotations

import pytest

from model_registry import resolve_profile


def test_resolve_known_profile_prefers_birefnet():
    profile = resolve_profile("quality")
    assert profile.backend == "rembg"
    assert profile.models[0] == "birefnet-general"
    assert "u2net" in profile.models


def test_resolve_specific_rembg_model():
    profile = resolve_profile("u2net")
    assert profile.name == "u2net"
    assert profile.models == ("u2net",)


def test_unknown_profile_rejected():
    with pytest.raises(ValueError):
        resolve_profile("unknown-model")
