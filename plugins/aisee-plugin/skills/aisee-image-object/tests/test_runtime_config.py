from __future__ import annotations

import json

from runtime_config import load_runtime_config, resolve_lama_backend


def test_resolve_lama_backend_prefers_cli_over_config(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "lama_backend": {
                    "enabled": True,
                    "iopaint_bin": "/config/bin/iopaint",
                    "device": "cpu",
                }
            }
        ),
        encoding="utf-8",
    )

    config = load_runtime_config(config_path)
    backend = resolve_lama_backend(
        config=config,
        iopaint_bin="/cli/bin/iopaint",
        device="mps",
    )

    assert backend["enabled"] is True
    assert backend["iopaint_bin"] == "/cli/bin/iopaint"
    assert backend["device"] == "mps"
    assert backend["config_path"] == str(config_path)


def test_resolve_lama_backend_uses_environment(monkeypatch):
    monkeypatch.setenv("AISEE_IMAGE_OBJECT_IOPAINT_BIN", "/env/bin/iopaint")
    monkeypatch.setenv("AISEE_IMAGE_OBJECT_LAMA_DEVICE", "cpu")

    backend = resolve_lama_backend()

    assert backend["iopaint_bin"] == "/env/bin/iopaint"
    assert backend["device"] == "cpu"
