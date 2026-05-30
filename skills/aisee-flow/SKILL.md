---
name: aisee:flow
description: Aisee 工作流状态编排器。用于用户不知道下一步该走哪条 Aisee/OpenSpec/Compound 链路，或需要判断当前项目、需求、OpenSpec change、CE review/test 记录处于哪个 workflow stage 时使用。它输出状态卡、缺口、阻断项、下一组推荐动作和 guardrails；不写 SRS、不拆 change、不生成 design/tasks、不替代 validate/archive 或 CE work。
---

# aisee:flow

`aisee:flow` 是 workflow state orchestrator，不是简单路由器。

## 职责

- 读取项目状态、OpenSpec change、`.aisee/sources.json`、`.aisee/id-registry.json`、`source-map.md`、CE review/test 记录。
- 判断当前 workflow stage。
- 识别缺口、断链、过期和冲突。
- 编排下一组 Aisee skill、OpenSpec 操作和 CE gate。
- 阻止错误跳步。
- 输出工作流状态卡。

## 不负责

- 写 SRS 全文。
- 拆 change 边界。
- 为多个 change 决定最终 schema。
- 生成 `design.md`、`tasks.md` 或代码。
- 替代 `openspec validate/archive`。
- 替代 CE review/work/test。

## Stage

```text
uninitialized
idea
requirement-ready
context-ready
change-planned
change-authored
doc-reviewed
implementation-ready
implemented
verified
archive-ready
```

## 与 change-plan 的边界

```text
aisee:flow
= 判断是否应该进入 change-plan，以及进入前缺什么

aisee:change-plan
= 真正拆 change、定依赖、定粒度、定每个 change 的最终 schema
```

`aisee:flow` 只能给 domain hint 或 schema family hint。只有跳过 `change-plan` 的 quick-fix 等单 change 快路径，才可以推荐轻量 schema。

## 输出格式

输出一张状态卡：

```md
# Aisee Workflow State

## Current Stage

## Domain Hint

## Known Inputs

## Missing / Blocking

## Recommended Path

## CE Gates

## Guardrails
```
