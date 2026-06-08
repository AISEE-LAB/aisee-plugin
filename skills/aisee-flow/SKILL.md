---
name: aisee:flow
description: Aisee 工作流守门器。用于用户不知道下一步该走哪条 Aisee/OpenSpec/Compound 链路，或需要判断当前项目、需求、OpenSpec change、author-check、gaps、context pack、CE review/test 记录处于哪个 workflow stage 时使用。它只输出状态卡、缺口、阻断项、下一组推荐动作和 guardrails；不写 SRS、不拆 change、不生成 artifacts、不替代 validate/archive 或 CE work。
---

# aisee:flow

`aisee:flow` 是 workflow gatekeeper，不是讨论器、规划器、执行器、OpenSpec parser 或通用路由器。它只组合 OpenSpec、Aisee CLI 和 CE evidence 的状态；flow report 不是新事实源。

## CLI preflight

调用 `aisee ...` 前先按 `references/cli-preflight.md` 确认 CLI 可用；缺失时停止并提示用户通过 PyPI / pipx 安装 CLI。

## 复用优先

当用户要求创建任务、执行任务、增加审查角色或询问下一步时，先检查已有项目工作流和 skill，不要直接发明新路径：

- 无明确 change 时，先读取 `aisee flow inspect --json` 判断当前 stage。
- 有明确 change 时，优先读取 `aisee flow inspect --change <change> --json` 和对应 context pack。
- `ce-work` context pack 的 `reusable_workflow_candidates` 只作为路由提示，不是事实源。
- 接口、UI、硬件、固件、安全和验证差异作为 schema-aware check lenses，不单独推荐新的全能审查 agent。
- 如果需要 Aisee reviewer，只推荐 `aisee-change-architect`、`aisee-spec-reviewer`、`aisee-implementation-reviewer` 这三个只读一致性审查 role。

Reviewer 触发建议：

- `aisee-change-architect`：`change-planned` / `change-authored` 前后按需推荐；仅在 change 边界复杂、跨模块、跨 schema、依赖不清或粒度不确定时出现。
- `aisee-spec-reviewer`：`change-authored` 且准备进入 `implementation-ready` 前建议推荐；用于检查 artifacts、contracts、source-map 和 tasks 是否可执行。
- `aisee-implementation-reviewer`：`implemented` / `verified` 前建议推荐；用于检查实现、tasks、spec/source-map 和 evidence 是否一致。

`aisee:flow` 只输出触发建议，不自动启动 reviewer runtime。

## 职责

- 读取项目状态、OpenSpec change、`aisee/registry/sources.json`、`aisee/registry/id-registry.json`、schema artifacts、Aisee companion artifacts 和 CE review/test evidence。
- 优先调用 Aisee CLI 的 `doctor`、`flow inspect/next`、`change inspect`、`author-check`、`gaps`、`verify-check`、`archive-check` 和 `context pack` 获取当前事实。
- 展示当前 schema、source-map/tasks 是否必需、implementation references、verify/archive checks 和 required commands。
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
- 替代 OpenSpec schema / artifact 解析或 validate/archive。
- 替代 CE review/work/test。
- 替代 CE 的 `ideate`、`brainstorm`、`debug`、`plan` 等探索、诊断和工程规划 skill。
- 处理讨论内容本身；只能给出“下一步应进入哪个入口”的短建议。
- 把 `aisee flow inspect` 的输出写成长期状态文件。

## 下一步路由

遇到模糊请求时，`aisee:flow` 只判断下一步入口，不展开讨论内容，不做方案设计，不写文档。

- 只输出 1-3 个推荐入口和阻断原因。
- 不得创建 OpenSpec change、不得写 `tasks.md`、不得生成平行长期文档。
- 如果请求本身需要讨论、发散、诊断或工程规划，推荐对应 CE/Aisee 入口后结束。
- 如果用户已指定具体 change，优先读取 `aisee flow inspect --change <change> --json` 判断 gate 状态。

需要判断模糊请求应转向哪个入口时，按需读取 [route-hints.md](references/route-hints.md)。不要默认加载该引用。

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

优先使用以下命令读取当前事实。若 `aisee flow inspect --change <change> --json` 已返回 schema、inputs、checks 和 required_commands，可先使用它，不必重复跑全套命令；只有缺字段或需要定位问题时再展开调用下列命令：

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

## Flow 输出解释

CLI flow 的 JSON 只做状态汇总：

- `schema`：当前 change schema，以及 `source_map_required`、`tasks_required`、`archive_tracks`。
- `inputs`：source-map 状态、parse level、source-map issues、task_state、implementation references、execution、evidence 计数。
- `checks.author`：author-check 的状态、schema 有效性、blocker/warning codes。
- `checks.gaps`：context pack gaps 的 blocker/risk/info 计数和 issue codes。
- `checks.implementation_gaps`：过滤掉当前 schema 不适用的实现阶段 gap 后，用于判断能否进入 `implementation-bridge` / `ce-work`。
- `checks.verify`：verify-check 的状态、summary 和 issue codes。
- `checks.archive`：archive-check 的状态、summary 和 issue codes。
- `reuse.workflow_candidates`：来自 `ce-work` context pack 的 `facts.derived.execution.reusable_workflow_candidates`，只作为路由提示，不是事实源。
- `required_commands`：下一步排查或推进时建议运行的命令。

这些字段来自现有 artifacts、schema 和 evidence。不要把它们反写为新的规范事实；需要长期保存的结论必须进入当前 OpenSpec artifacts、schema apply tracks、source-map（如适用）或 evidence 文件。

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
-> review gate / ce-test-*（按需；命中公开接口、契约、schema、路径读取或安全表面时提示 Tier 2 review 授权）
-> aisee:verify
-> aisee:archive-guard
-> openspec archive
```

## 跳步保护

- 没有明确 change：不要进入 `aisee:change-author`、`implementation-bridge`、`verify` 或 `archive-guard`。
- `author-check.status=blocked`：推荐回到 `aisee:change-author` 或 schema artifact 修复。
- `gaps.result.status=blocked`：不要进入 `ce-work` 或 archive。
- 无 apply / no implementation schema 不应因为 `ce-work` context pack 的 `TASK_GAP` 或 `IMPLEMENTATION_PATHS_GAP` 被误导回实现阶段；以当前 schema 的 archive/verify gate 为准。
- `context pack --for ce-work` 中 `requires_ce_plan=true`：推荐先用 `aisee:implementation-bridge` 输出缺口，再用 `ce-plan` 临时细化；结论必须回写当前 schema 的 apply tracks，只有 schema 生成 `source-map.md` 时才要求回写 source-map。
- source-map schema 的执行路径优先来自 `Affected Paths Index`；metadata fallback 只能作为 risk，不应静默放行。
- `implementation-bridge` 或 `aisee:verify` 已建议 Tier 2 code review，且没有审查 evidence、本地重点自审 evidence 或正式 accepted risk：不要建议进入 archive-ready；先建议用户授权 `使用审查代理做 Tier 2 code review`，或记录可审查的 accepted risk。
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

## Checks

## Evidence Summary

## CE Gates

## Guardrails
```
