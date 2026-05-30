---
name: aisee:implementation-bridge
description: 将单个已确认且已 authored 的 OpenSpec change 转成给 Compound Engineering 执行的最小工程上下文。用于进入 ce-work 前输出一次性的 Implementation Brief / context pack 摘要，明确事实源、读取顺序、schema/domain contracts、tasks.md、source-map.md、禁止越界项、测试要求和 ce-plan 是否需要。它不创建平行任务清单，不默认落地新文档，不替代 ce-work，不修补缺失 artifacts。
---

# aisee:implementation-bridge

`aisee:implementation-bridge` 是 OpenSpec change 到工程实现阶段的交接器。

## 职责

- 读取单个 OpenSpec change。
- 输出给 `ce-work` 的一次性 Implementation Brief / context pack 摘要。
- 明确事实源、读取顺序、执行规则、禁止越界项和验证要求。
- 判断是否需要先用 `ce-plan` 细化，并要求有效结论回写 `tasks.md` / `source-map.md`。
- 指出不能进入实现的阻塞项。

## 不负责

- 创建、拆分或重新规划 change。
- 生成或补齐 `proposal.md`、`specs/**`、`change-context.md`、contracts、`source-map.md` 或 `tasks.md`。
- 让 `ce-plan` 生成长期任务清单。
- 默认写入新的长期交接文档。
- 写代码或执行实现。
- 替代 `aisee:verify`、`ce-code-review`、`ce-test-*` 或 `aisee:apply-guard`。

## Change 入口规则

必须通过当前执行的 OpenSpec change 获取相关内容：

- 入口必须是明确的 `<change>`，例如 `openspec/changes/<change>/` 或 `aisee context pack --change <change> --for ce-work --json`。
- 只能读取当前 change artifacts、当前 change 的 schema、`source-map.md` 指向的上游文档 / 代码 / 测试路径，以及 `AGENTS.md` 这类执行规则。
- 可以读取当前 change 明确提到或 `source-map.md` 指向的内容；未提到但在实现或验证中发现的相关问题，可以报告出来。
- 不要绕过当前 change 去全项目搜索需求、页面、接口或代码后自行扩大实现上下文。
- 不要从其他未关联 change、历史草稿或泛项目文档推导实现范围；除非它们被当前 `source-map.md` 或 context pack 明确引用。
- 如果实现需要的文件没有被当前 change 或 `source-map.md` 指到，先把它作为 `[SOURCE-MAP-GAP]`，回写 `source-map.md` 或要求 `aisee:change-author` 补齐。
- 未被当前 change 纳入范围的问题，只能进入 Brief 的 `Blockers and Assumptions`、`Follow-up candidates` 或验证风险；不得直接变成当前 change 的实现任务。

## 产物形态

Implementation Brief 是实现阶段的交接输出，不是新的规范事实源：

- 默认作为当前会话输出，或由 `aisee context pack --change <change> --for ce-work --json` 返回给执行方。
- 不默认写入 `openspec/changes/<change>/implementation-brief.md` 或其他长期文档。
- 如果用户明确要求保存，只能标注为 generated handoff / cache，且正文必须指向 `proposal.md`、`source-map.md`、`specs/**`、contracts 和 `tasks.md`；不得承载这些 artifact 中没有的新事实。
- 发现 Brief 与 OpenSpec artifacts 不一致时，以 OpenSpec artifacts 为准，并回写对应 artifact，而不是修补 Brief。

## 输入门禁

开始前确认：

- 当前只处理一个 OpenSpec change。
- change 已经通过 `aisee:change-author` 补齐当前 schema 声明的 artifacts，或明确标出 N/A 原因。
- `openspec/changes/<change>/tasks.md` 存在，且是唯一长期任务清单。
- `openspec/changes/<change>/source-map.md` 存在，且能说明上游 ID、产出 ID、artifact 适用性和阻塞项。
- `specs/**/*.md` 存在，除非当前 schema 明确不生成 specs。
- 当前 schema 的关键 contracts 已存在：app schema 通常包括 `change-context.md`、`ui-contract.md`、`service-contract.md`、`data-model.md`；device schema 通常包括 `design.md` 和设备侧 contracts。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。

如果门禁不满足，输出 `[IMPLEMENTATION-BRIDGE-BLOCKED]`，列出缺口，并建议回到 `aisee:change-author` 或对应 schema artifact，而不是进入 `ce-work`。

## 推荐读取顺序

优先使用 Aisee CLI 基于当前 change 生成最小上下文包：

```bash
aisee context pack --change <change> --for ce-work --json
```

如果 CLI 不可用，仍然只能从当前 change 出发，按以下顺序读取：

1. `AGENTS.md`
2. `openspec/changes/<change>/proposal.md`
3. `openspec/changes/<change>/source-map.md`
4. `openspec/changes/<change>/specs/**/*.md`
5. `openspec/changes/<change>/change-context.md` 或 `design.md`
6. 适用 contracts：`ui-contract.md`、`service-contract.md`、`data-model.md`、device contracts
7. `openspec/changes/<change>/tasks.md`
8. `source-map.md` 明确指向的相关代码路径、测试路径、路由、API、模型和配置

## Implementation Brief 输出必须包含

```md
# Implementation Brief

## Authoritative Source

## Change Scope

## Read First

## Artifact Map

## Execution Rules

## Scope Guardrails

## Task Execution

## Verification

## Blockers and Assumptions

## Recommended Compound Skill
```

## 规则

- `specs/**/spec.md` 是行为契约。
- `tasks.md` 是唯一长期任务清单。
- `source-map.md` 是代码定位入口。
- app schema 中，`ui-contract.md`、`service-contract.md`、`data-model.md` 和 `change-context.md` 是实现 contracts；不要只读 specs 就开始写代码。
- device schema 中，`design.md` 和 hardware/firmware/runtime/verification contracts 是实现 contracts；不要把 app contract 假设套到设备项目。
- 实现中发现需求/spec/contract/code 事实不一致，先回写当前 OpenSpec change，再继续实现。
- 不创建新的长期计划文件；需要临时推理时，结论必须回写 `tasks.md` 或 `source-map.md`。
- 不扩大 change 范围；超出范围的发现记录为 follow-up 或新 change 候选。
- 完成实现后必须更新 `tasks.md` 勾选状态和验证证据。

## ce-plan 使用边界

默认推荐直接进入 `ce-work`。只有在以下情况才建议先用 `ce-plan`：

- `tasks.md` 的任务粒度过粗，无法指导实现顺序。
- `source-map.md` 指向的代码位置不足，无法定位入口。
- contracts 之间存在需要拆解的技术依赖，但不改变需求和 change 边界。
- 需要把已有任务细化为更小执行步骤。

`ce-plan` 的输出不是事实源。有效结论必须回写：

- `tasks.md`：细化任务、执行顺序、验证任务。
- `source-map.md`：代码路径、测试路径、追踪关系。
- 相关 contract：如果发现契约缺口或冲突。

如果 `ce-plan` 需要新增需求、扩大范围、改变 contract 或拆分 change，停止并回到 `aisee:change-plan` / `aisee:change-author`。

## Brief 输出模板

按以下格式输出给实现阶段：

```md
# Implementation Brief

## Authoritative Source

- Change: `openspec/changes/<change>`
- Schema:
- Specs:
- Tasks:
- Source Map:
- Contracts:

## Change Scope

- In scope:
- Out of scope:
- Upstream IDs:
- Produced IDs:

## Read First

1. （待填）
2. （待填）
3. （待填）

## Artifact Map

| Artifact | Role in implementation | Required | Notes |
|---|---|---:|---|
| specs/**/*.md | Behavior contract | yes / no | |
| source-map.md | ID and code routing | yes | |
| tasks.md | Durable task list | yes | |
| change-context.md / design.md | Architecture / design constraints | yes / no | |
| ui-contract.md | UI implementation contract | yes / no | |
| service-contract.md | API / service contract | yes / no | |
| data-model.md | Data contract | yes / no | |

## Execution Rules

- Follow `tasks.md`; do not create a parallel durable plan.
- Preserve `source-map.md` traceability when touching code or tests.
- If implementation facts conflict with specs or contracts, pause and update the current OpenSpec change first.

## Scope Guardrails

- Do not implement:
- Follow-up candidates:
- Accepted assumptions:

## Task Execution

- Start from:
- Suggested order:
- Code paths:
- Test paths:

## Verification

- Required commands:
- Required manual checks:
- Evidence to record in `tasks.md`:

## Blockers and Assumptions

- Blockers:
- Assumptions:
- Temporary IDs / unresolved source-map entries:

## Recommended Compound Skill

- Recommended: `ce-work`
- Use `ce-plan` first only if:
- After implementation: `ce-code-review`, relevant `ce-test-*`, then `aisee:verify`
```
