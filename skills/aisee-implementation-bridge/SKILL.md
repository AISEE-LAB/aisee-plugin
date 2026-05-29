---
name: aisee:implementation-bridge
description: 将单个已确认 OpenSpec change 转成给 Compound Engineering 执行的最小工程上下文。用于进入 ce-work 前生成 Implementation Brief，明确 specs、tasks.md、source-map.md、design/contracts、禁止越界项和测试要求。它不创建平行任务清单，不替代 ce-work。
---

# aisee:implementation-bridge

## 职责

- 读取单个 OpenSpec change。
- 生成给 `ce-work` 的 Implementation Brief。
- 明确事实源和执行规则。
- 判断是否需要先用 `ce-plan` 细化，并要求结论回写 `tasks.md` / `source-map.md`。

## Implementation Brief 必须包含

```md
# Implementation Brief

## Authoritative Source

## Read First

## Execution Rules

## Scope Guardrails

## Verification

## Recommended Compound Skill
```

## 规则

- `specs/**/spec.md` 是行为契约。
- `tasks.md` 是唯一长期任务清单。
- `source-map.md` 是代码定位入口。
- 实现中发现需求/spec 不一致，先回写当前 OpenSpec change。
