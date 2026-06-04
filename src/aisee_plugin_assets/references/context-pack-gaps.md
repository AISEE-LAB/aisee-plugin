# Context Pack Gaps

本文是 context pack gap 对象、severity 和常见 code 的维护源。

## Gap Object

所有 target 使用统一 gap 结构：

```json
{
  "code": "SOURCE_MAP_GAP",
  "severity": "blocker",
  "message": "tasks references auth:API-001 but source-map has no code path",
  "owner_artifact": "source-map.md",
  "related_ids": ["auth:API-001"],
  "suggested_fix": "Update source-map.md with code and test paths before ce-work"
}
```

Rules:

- `code`：稳定机器可读 code。
- `severity`：只能是 `blocker`、`risk` 或 `info`。
- `message`：人类可读说明。
- `owner_artifact`：应修复或确认的 artifact / 文件。
- `related_ids`：可为空，但涉及 ID trace 时必须使用完整 ID。
- `suggested_fix`：给出最小修复方向，不自动生成内容。

## Severity

- `blocker`：不能进入下一阶段。
- `risk`：可以继续，但必须记录接受理由或验证要求。
- `info`：提示，不阻断。

## Common Codes

- `MISSING_ARTIFACT`
- `SOURCE_MAP_GAP`
- `ID_REGISTRY_GAP`
- `TRACE_GAP`
- `TASK_GAP`
- `CONTRACT_GAP`
- `SPEC_DRIFT`
- `VALIDATE_FAILED`
- `REVIEW_BLOCKER`
- `TEST_EVIDENCE_MISSING`

## Gate Semantics

- `ce-work` 遇到 blocker 不应开始实现。
- `aisee-verify` 遇到 blocker 不应进入 archive guard。
- `aisee:archive-guard` 遇到 blocker 不应建议 `openspec archive`。
- risk 可以继续，但需要 owner、原因、影响和后续处理方式。
- info 不阻断，但应保留在 JSON 输出中供后续审查。
