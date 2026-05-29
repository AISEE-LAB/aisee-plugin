---
name: aisee:verify
description: 验证当前 OpenSpec change 的文档、ID、source-map、tasks、contracts、CE review/test 结果和实现状态是否一致。用于实现前后检查缺口、断链、drift 和 schema artifact 完整性。它输出问题清单和修复建议，不负责 apply 放行审批。
---

# aisee:verify

## 职责

- 运行或建议运行 `openspec validate`。
- 检查 schema artifact DAG。
- 检查 ID、`source-map.md`、spec、tasks、contracts 的一致性。
- 检查实现后是否出现 spec drift。
- 消费 `ce-doc-review`、`ce-code-review`、`ce-test-*` 结果。
- 输出问题清单和修复建议。

## 输出

```md
# Aisee Verify Report

## Result

## Findings

## Required Fixes

## Suggested Next Step
```
