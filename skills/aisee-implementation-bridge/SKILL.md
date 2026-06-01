---
name: aisee:implementation-bridge
description: 将单个已确认且已 authored 的 OpenSpec change 转成给 Compound Engineering 执行的最小工程上下文。用于进入 ce-work 前运行 author-check、gaps 和 context pack，输出一次性的 Implementation Brief / context pack 摘要，明确当前 schema、事实源、读取顺序、schema/domain artifacts、apply tracks、source-map 适用性、禁止越界项、验证要求和 ce-plan 是否需要。它不创建平行任务清单，不默认落地新文档，不替代 ce-work，不修补缺失 artifacts。
---

# aisee:implementation-bridge

`aisee:implementation-bridge` 是 OpenSpec change 到工程实现阶段的交接器。

## 职责

- 读取单个 OpenSpec change。
- 运行 `aisee change author-check <change> --json`、`aisee gaps --change <change> --json` 和 `aisee context pack --change <change> --for ce-work --json`。
- 输出给 `ce-work` 的一次性 Implementation Brief / context pack 摘要。
- 明确事实源、读取顺序、执行规则、禁止越界项和验证要求。
- 判断是否需要先用 `ce-plan` 细化，并要求有效结论回写当前 schema 的 apply tracks；只有 schema 生成 `source-map.md` 时才回写 source-map。
- 指出不能进入实现的阻塞项。

## 不负责

- 创建、拆分或重新规划 change。
- 生成或补齐 `proposal.md`、`specs/**`、`change-context.md`、contracts、`source-map.md` 或 `tasks.md`。
- 让 `ce-plan` 生成长期任务清单。
- 默认写入新的长期交接文档。
- 写代码或执行实现。
- 替代 `aisee:verify`、`ce-code-review`、`ce-test-*` 或 `aisee:archive-guard`。

## Change 入口规则

必须通过当前执行的 OpenSpec change 获取相关内容：

- 入口必须是明确的 `<change>`，例如 `openspec/changes/<change>/` 或 `aisee context pack --change <change> --for ce-work --json`。
- 只能读取当前 change artifacts、当前 change 的 schema、context pack 给出的 implementation references，以及 `AGENTS.md` 这类执行规则。
- 可以读取当前 change 明确提到、context pack `read_order` 给出或当前 schema companion artifact 指向的内容；未提到但在实现或验证中发现的相关问题，可以报告出来。
- 不要绕过当前 change 去全项目搜索需求、页面、接口或代码后自行扩大实现上下文。
- 不要从其他未关联 change、历史草稿或泛项目文档推导实现范围；除非它们被 context pack 或当前 schema artifact 明确引用。
- 如果实现需要的文件没有被当前 change 或 context pack 指到，先把它作为 `[IMPLEMENTATION-PATH-GAP]`；schema 生成 `source-map.md` 时回写 source-map，否则回写当前 schema 的 apply tracks 或主 artifact。
- 未被当前 change 纳入范围的问题，只能进入 Brief 的 `Blockers and Assumptions`、`Follow-up candidates` 或验证风险；不得直接变成当前 change 的实现任务。

## 产物形态

Implementation Brief 是实现阶段的交接输出，不是新的规范事实源：

- 默认作为当前会话输出，或由 `aisee context pack --change <change> --for ce-work --json` 返回给执行方。
- 不默认写入 `openspec/changes/<change>/implementation-brief.md` 或其他长期文档。
- 如果用户明确要求保存，只能标注为 generated handoff / cache，且正文必须指向当前 schema artifacts 和 apply tracks；不得承载这些 artifact 中没有的新事实。
- 发现 Brief 与 OpenSpec artifacts 不一致时，以 OpenSpec artifacts 为准，并回写对应 artifact，而不是修补 Brief。

## 输入门禁

开始前确认：

- 当前只处理一个 OpenSpec change。
- `aisee change author-check <change> --json` 无 blocker；如果 `status=blocked`，停止并回到 `aisee:change-author`。
- `aisee gaps --change <change> --json` 无 blocker；risk 可以进入 Brief，但不能被写成已解决。
- change 已经通过 `aisee:change-author` 补齐当前 schema 的必需 artifacts；只有 schema 生成 `source-map.md` 时才要求 source-map 说明按需 artifacts 的 Required=yes/no 与 N/A 原因。
- 当前 schema 的 apply tracks 存在；通常是 `tasks.md`，但 `quick-research` 等无 apply schema 可以没有 tasks。
- `source-map.md` 只在当前 schema 生成它时必需。
- `specs/**/*.md` 只在当前 schema 明确生成 specs 时必需。
- 当前 schema 的 Required=yes contracts 已存在并可读取；Required=no 的 app contract 只需要在 source-map schema 中写明原因。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。

如果门禁不满足，输出 `[IMPLEMENTATION-BRIDGE-BLOCKED]`，列出 `author-check.blockers`、`gaps` 和缺失 artifact，并建议回到 `aisee:change-author` 或对应 schema artifact，而不是进入 `ce-work`。

## 推荐读取顺序

优先使用 Aisee CLI 基于当前 change 生成最小上下文包。按顺序运行：

```bash
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee context pack --change <change> --for ce-work --json
```

读取 pack 时只消费：

- `facts.parsed`：当前 change artifacts、schema、sources、ID registry 状态。
- `facts.derived.read_order`：实现前读取顺序。
- `facts.derived.scope`：in/out scope 与 follow-up candidates。
- `facts.derived.traceability`：上游 ID、产出 ID、ID links。
- `facts.parsed.schema.source_map_required` / `tasks_required` / `archive_tracks`：当前 schema 的实现前置。
- `facts.derived.code_paths` / `test_paths`：允许读取和修改入口；source-map schema 来自 Implementation Paths，轻量 schema 来自当前 schema artifacts 中明确引用的执行路径。
- `facts.derived.implementation_references.source`：路径来源，可能是 `source-map` 或 `schema-artifacts`。
- `facts.derived.implementation_references.unmapped_reference_paths`：source-map schema 中 artifacts 提到但未在 source-map 声明的路径，只能作为缺口处理，不能交给 `ce-work` 自动修改。
- `facts.derived.execution`：执行顺序、是否需要先 ce-plan、禁止越界项。
- `gaps` 和 `guardrails`：阻塞项、风险和执行限制。

处理规则：

- `author-check.status=blocked`：停止，不输出可执行 Brief。
- `gaps.result.status=blocked`：停止，不进入 `ce-work`。
- `context pack.facts.derived.execution.requires_ce_plan=true`：Brief 中推荐先用 `ce-plan`，但结论必须回写当前 schema 的 apply tracks；只有 schema 生成 `source-map.md` 时才回写 source-map。
- `ID_RESERVATION_REQUIRED`、`ID_UNREGISTERED_REFERENCE`、`ID_INACTIVE_REFERENCE` 只能作为阻塞或风险进入 Brief；不得在实现阶段由 `ce-work` 临时发明 ID。

如果 CLI 不可用，仍然只能从当前 change 出发，按以下顺序读取：

1. `AGENTS.md`
2. `openspec/changes/<change>/proposal.md`
3. 当前 schema 生成的追踪 artifact，例如 `source-map.md`、`problem.md`、`solution.md`、`doc-change.md`、`impact-assessment.md`、`rollback-plan.md`、`findings.md`
4. `openspec/changes/<change>/specs/**/*.md`，仅当当前 schema 生成 specs
5. Required=yes 的 `openspec/changes/<change>/change-context.md` 或 schema 明确生成的 `design.md`
6. Required=yes 的 contracts：`ui-contract.md`、`service-contract.md`、`data-model.md`、device contracts
7. 当前 schema 的 apply tracks，通常是 `tasks.md`
8. context pack 明确给出的相关代码路径、测试路径、路由、API、模型和配置

## Implementation Brief 输出必须包含

```md
# Implementation Brief

## Preflight

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
- 当前 schema 的 apply tracks 是长期执行清单；app/device/quick-fix 通常是 `tasks.md`，无 apply schema 不强制 tasks。
- `source-map.md` 只在当前 schema 生成它时是代码定位入口；不生成 source-map 的 schema 使用 context pack 从 schema artifacts 中提取的 implementation references。
- app schema 中，`ui-contract.md`、`service-contract.md`、`data-model.md` 和 `change-context.md` 只有在 `source-map.md` 标记 Required=yes 时才是实现 contracts；不要要求每个 change 都展开全部 contracts。
- device schema 中，`design.md` 和 hardware/firmware/runtime/verification contracts 是实现 contracts；不要把 app contract 假设套到设备项目。
- `ce-work` 的允许路径应来自 context pack 的 `allowed_paths`、`code_paths` 和 `test_paths`。缺失时标记 `[SOURCE-MAP-GAP]` 或 `[IMPLEMENTATION-PATH-GAP]`，不要自行扩大实现范围。
- 实现中发现需求/spec/contract/code 事实不一致，先回写当前 OpenSpec change，再继续实现。
- 不创建新的长期计划文件；需要临时推理时，结论必须回写当前 schema 的 apply tracks 或追踪 artifact。
- 不扩大 change 范围；超出范围的发现记录为 follow-up 或新 change 候选。
- 完成实现后必须更新当前 schema 的 apply tracks 和验证证据；没有 apply tracks 的 schema 只记录必要 evidence。

## ce-plan 使用边界

默认推荐直接进入 `ce-work`。只有在以下情况才建议先用 `ce-plan`：

- `tasks.md` 的任务粒度过粗，无法指导实现顺序。
- context pack 指向的代码位置不足，无法定位入口。
- contracts 之间存在需要拆解的技术依赖，但不改变需求和 change 边界。
- 需要把已有任务细化为更小执行步骤。

`ce-plan` 的输出不是事实源。有效结论必须回写：

- 当前 schema apply tracks：细化任务、执行顺序、验证任务。
- `source-map.md`：仅当 schema 生成 source-map 时，回写代码路径、测试路径、追踪关系。
- 相关 contract：如果发现契约缺口或冲突。

如果 `ce-plan` 需要新增需求、扩大范围、改变 contract 或拆分 change，停止并回到 `aisee:change-plan` / `aisee:change-author`。

## Brief 输出模板

按以下格式输出给实现阶段：

```md
# Implementation Brief

## Preflight

- Author check:
- Gaps:
- Context pack:
- Blocked:

## Authoritative Source

- Change: `openspec/changes/<change>`
- Schema:
- Source-map required:
- Apply tracks:
- Specs:
- Tasks / apply tracks:
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
| specs/**/*.md | Behavior contract | yes / no | 仅当 schema 生成 |
| source-map.md | ID and code routing | yes / no | 仅当 schema 生成 |
| tasks.md / apply tracks | Durable execution list | yes / no | 以 schema 为准 |
| change-context.md / design.md | Architecture / design constraints | yes / no | app change-context Required=no 时写 source-map N/A 原因；design.md 只在 schema 生成时出现 |
| ui-contract.md | UI implementation contract | yes / no | Required=no 时写 source-map N/A 原因 |
| service-contract.md | API / service contract | yes / no | Required=no 时写 source-map N/A 原因 |
| data-model.md | Data contract | yes / no | Required=no 时写 source-map N/A 原因 |

## Execution Rules

- Follow current schema apply tracks; do not create a parallel durable plan.
- Preserve traceability when touching code or tests; source-map schema 回写 `source-map.md`，轻量 schema 回写对应主 artifact / apply tracks。
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
- Implementation path source:

## Verification

- Required commands:
- Required manual checks:
- Evidence to record:

## Blockers and Assumptions

- Blockers:
- Assumptions:
- Temporary IDs / unresolved source-map entries:

## Recommended Compound Skill

- Recommended: `ce-work`
- Use `ce-plan` first only if:
- After implementation: `ce-code-review`, relevant `ce-test-*`, then `aisee:verify`
```
