from __future__ import annotations

import json
import subprocess
from pathlib import Path

from test_memory_config import write_memory


ROOT = Path(__file__).resolve().parents[1]
SESSION_HOOK = ROOT / "plugins" / "aisee-plugin" / "skills" / "aisee-init" / "scripts" / "hooks" / "session-inject.js"
PROMPT_HOOK = ROOT / "plugins" / "aisee-plugin" / "skills" / "aisee-init" / "scripts" / "hooks" / "spec-drift.js"


def run_hook(script: Path, payload: dict) -> str:
    result = subprocess.run(
        ["node", str(script)],
        input=json.dumps(payload),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout


def hook_context(output: str) -> str:
    return json.loads(output)["hookSpecificOutput"]["additionalContext"]


def test_session_hook_does_not_emit_memory_block_when_memory_is_missing(tmp_path: Path) -> None:
    output = run_hook(SESSION_HOOK, {"cwd": str(tmp_path), "hook_event_name": "SessionStart"})

    assert output == ""


def test_session_hook_emits_bounded_memory_guidance(tmp_path: Path) -> None:
    write_memory(
        tmp_path,
        "aisee/memory/pref/commit.md",
        priority="high",
        summary="提交信息使用中文。",
        body="这段正文不应在 SessionStart 中完整注入。",
    )

    context = hook_context(run_hook(SESSION_HOOK, {"cwd": str(tmp_path), "hook_event_name": "SessionStart"}))

    assert "aisee memory inspect --json" in context
    assert 'aisee memory search --query "<当前任务>" --json' in context
    assert "提交信息使用中文。" in context
    assert "这段正文不应在 SessionStart 中完整注入" not in context
    assert "不是 OpenSpec 事实源" in context


def test_prompt_hook_memory_write_intent_only_emits_guidance(tmp_path: Path) -> None:
    context = hook_context(
        run_hook(
            PROMPT_HOOK,
            {
                "cwd": str(tmp_path),
                "hook_event_name": "UserPromptSubmit",
                "prompt": "以后本项目提交信息都用中文，记住这个偏好",
            },
        )
    )

    assert "Aisee 项目记忆写入提示" in context
    assert "不要由 hook 自动写文件" in context
    assert "aisee memory add" in context
    assert "aisee:reflect" in context
    assert not (tmp_path / "aisee" / "memory").exists()
