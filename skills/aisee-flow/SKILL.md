---
name: aisee:flow
description: Aisee 工作流状态编排器。用于用户不知道下一步该走哪条 Aisee/OpenSpec/Compound 链路，或需要判断当前项目、需求、OpenSpec change、author-check、gaps、context pack、CE review/test 记录处于哪个 workflow stage 时使用。它输出状态卡、缺口、阻断项、下一组推荐动作和 guardrails；不写 SRS、不拆 change、不生成 artifacts、不替代 validate/archive 或 CE work。
---

# aisee:flow

`aisee:flow` 是 workflow state orchestrator，不是简单路由器。

## 职责

- 读取项目状态、OpenSpec change、`.aisee/sources.json`、`.aisee/id-registry.json`、`source-map.md`、CE review/test 记录。
- 优先调用 Aisee CLI 的 `doctor`、`flow inspect/next`、`author-check`、`gaps`、`change inspect`、`verify-check`、`archive-check` 和 `context pack` 获取当前事实。
- 判断当前 workflow stage。
- 识别缺口、断链、过期和冲突。
- 编排下一组 Aisee skill、OpenSpec 操作和 CE gate。
- 阻止错误跳步。
- 输出工作流状态卡。

## 不负责

- 写 SRS 全文。
- 拆 change 边界。
- 为多个 change 决定最终 schema。
- 生成 change artifacts、`tasks.md` 或代码。
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

## Stage 判定入口

优先使用以下命令读取当前事实：

```bash
aisee doctor --json
aisee flow inspect --json
aisee flow inspect --change <change> --json
aisee flow next --change <change> --json
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee change inspect <change> --json
aisee change verify-check <change> --json
aisee change archive-check <change> --json
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for aisee-verify --json
```

如果还没有明确 change，则先判断是否已有 SRS、UI Content、Design Spec / Assets、Architecture 和 Change Plan 输入；不要凭空进入 change-author。

## 推荐路径

```text
idea
-> aisee:srs
-> aisee:ui-content / aisee:design-spec / aisee:architecture（按需）
-> aisee:change-plan
-> /opsx:new 或等效 OpenSpec change 创建
-> aisee:change-author
-> aisee change author-check
-> aisee:implementation-bridge
-> ce-work
-> ce-code-review / ce-test-*（按需）
-> aisee:verify
-> aisee:archive-guard
-> openspec archive
```

## 跳步保护

- 没有明确 change：不要进入 `aisee:change-author`、`implementation-bridge`、`verify` 或 `archive-guard`。
- `author-check.status=blocked`：推荐回到 `aisee:change-author` 或 schema artifact 修复。
- `gaps.result.status=blocked`：不要进入 `ce-work` 或 archive。
- `context pack --for ce-work` 中 `requires_ce_plan=true`：推荐先用 `ce-plan` 临时细化，但结论必须回写 `tasks.md` / `source-map.md`。
- `aisee:verify` 有 BLOCKER：不要进入 `aisee:archive-guard`。
- `aisee:archive-guard` 未给出“可以 archive”：不要建议执行 `openspec archive`。
- `ce-plan`、Implementation Brief、verify report 都不是长期事实源；长期结论必须回写 OpenSpec artifacts。

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

## Required Commands

## CE Gates

## Guardrails
```
