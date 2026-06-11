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


def test_load_runtime_config_uses_global_config_after_project_paths(tmp_path, monkeypatch):
    project_config = tmp_path / "aisee/config/image-object/config.json"
    project_config.parent.mkdir(parents=True)
    project_config.write_text(
        json.dumps({"lama_backend": {"iopaint_bin": "/project/bin/iopaint"}}),
        encoding="utf-8",
    )
    global_config = tmp_path / ".config/aisee/image-object/config.json"
    global_config.parent.mkdir(parents=True)
    global_config.write_text(
        json.dumps({"lama_backend": {"iopaint_bin": "/global/bin/iopaint"}}),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    config = load_runtime_config()

    assert config["lama_backend"]["iopaint_bin"] == "/project/bin/iopaint"
    assert config["_config_path"] == "aisee/config/image-object/config.json"


def test_load_runtime_config_uses_global_config_when_project_missing(tmp_path, monkeypatch):
    global_config = tmp_path / ".config/aisee/image-object/config.json"
    global_config.parent.mkdir(parents=True)
    global_config.write_text(
        json.dumps({"lama_backend": {"iopaint_bin": "/global/bin/iopaint"}}),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    config = load_runtime_config()

    assert config["lama_backend"]["iopaint_bin"] == "/global/bin/iopaint"
    assert config["_config_path"] == str(global_config)
