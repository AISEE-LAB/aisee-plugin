---
name: aisee:implementation-bridge
description: 将单个已确认且已 authored 的 OpenSpec change 转成给 Compound Engineering 执行的最小工程上下文。用于进入 ce-work 前运行 author-check、gaps 和 context pack，输出一次性的 Implementation Brief / context pack 摘要，明确当前 schema、事实源、读取顺序、schema/domain artifacts、apply tracks、source-map 适用性、禁止越界项、验证要求和 ce-plan 是否需要。它不创建平行任务清单，不默认落地新文档，不替代 ce-work，不修补缺失 artifacts。
---

# aisee:implementation-bridge

`aisee:implementation-bridge` 是 OpenSpec change 到工程实现阶段的交接器。

如需保存 Implementation Brief，frontmatter 字段合同统一遵循 `plugins/aisee-plugin/references/planning-doc-frontmatter.md`；这些 brief 仍是 generated handoff / cache，不是规范事实源。

## 复用优先

执行前必须优先复用当前 change 的机器可读上下文：

- 先读取 `aisee context pack --change <change> --for ce-work --json`。
- 优先使用 `facts.derived.execution.reusable_workflow_candidates`、`allowed_paths`、`requires_ce_plan` 和 `ce_plan_reason` 判断下一步。
- `requires_ce_plan=false` 且 paths/tasks 清楚时，推荐 `ce-work`，不要生成新的长期计划。
- `requires_ce_plan=true` 时，才按需建议 `ce-plan`；其结论必须回写当前 schema apply tracks，只有 source-map schema 才回写 `source-map.md`。
- 如果 CE skill 缺失，只说明限制和本地 guardrails，不创建 Aisee 替代 CE 的执行、代码审查或测试 agent。

## 职责

- 读取单个 OpenSpec change。
- 运行 `aisee change author-check <change> --json`、`aisee gaps --change <change> --json` 和 `aisee context pack --change <change> --for ce-work --json`。
- 输出给 `ce-work` 的一次性 Implementation Brief / context pack 摘要。
- 明确事实源、读取顺序、执行规则、禁止越界项和验证要求。
- 判断是否需要先用 `ce-plan` 细化，并要求有效结论回写当前 schema 的 apply tracks；只有 schema 生成 `source-map.md` 时才回写 source-map。
- 识别实现后是否建议 Tier 2 code review，并把审查代理授权提示写入 Brief。
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
- 如果用户明确要求保存，或当前 change 内容过大需要分批交接，优先写入 `aisee/cache/implementation-bridge/<change>/brief-part-NN.md`；如用户指定写入 change 目录，只能标注为 generated handoff / cache，且正文必须指向当前 schema artifacts 和 apply tracks；不得承载这些 artifact 中没有的新事实。
- 分批交接时必须先生成 `brief-index.md`，再生成 `brief-part-NN.md`；index 使用 `references/brief-index-template.md`，part 使用 `references/brief-template.md`。
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

CHECKPOINT: 推荐进入 `ce-work` 前，必须确认 `author-check` 无 blocker、`gaps` 无 blocker、context pack 可用、当前 change scope 清楚、apply tracks 存在或当前 schema 明确不需要、实现路径来自 context pack / schema artifacts。任一条件不满足时停止并输出 `[IMPLEMENTATION-BRIDGE-BLOCKED]`；不得生成可执行 Brief，不得建议 `ce-work`。

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
- `facts.derived.code_paths` / `test_paths`：允许读取和修改入口；source-map schema 优先来自 `Affected Paths Index`，缺表时只能使用 source-map metadata fallback 且必须保留 risk；轻量 schema 来自当前 schema artifacts 中明确引用的执行路径。
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

## Review Recommendation

## Blockers and Assumptions

## Recommended Compound Skill
```

## Brief 压缩与分批

Brief 只做执行索引，不复制 OpenSpec artifact 正文：

- `Read First` 只列路径、读取顺序和原因。
- `Artifact Map` 只写 artifact 角色、Required 状态、N/A 原因和关键风险。
- `Change Scope` 只写 in/out scope 摘要、关键 ID 和 follow-up candidates。
- `Task Execution` 只写当前批次的起点、允许路径、建议顺序和回写位置。
- `Verification` 只写必须运行的命令、人工检查和 evidence 写回位置。
- `Review Recommendation` 只写是否建议 Tier 2 code review、触发原因、授权提示和 evidence 写回位置，不启动审查代理。
- contracts、specs、source-map、tasks 的详细内容只能作为路径引用，不要复制全文。

当 change 很大或 context pack 指出任务过多时，不回到 `aisee:change-plan` 重新拆 change。改为在当前 change 内分批交接：

1. 先用 `references/brief-index-template.md` 生成 `brief-index.md`：批次数、每批目标、依赖顺序、允许路径、验证入口和 apply tracks 回写位置。
2. 再用 `references/brief-template.md` 生成 `brief-part-01.md`、`brief-part-02.md` 等分块 Brief；每个 part 只覆盖一组相关 tasks / allowed paths / verification。
3. 每个 part 都必须引用同一个 current change、schema、apply tracks 和相关 artifacts。
4. 分批执行后，结论必须回写当前 schema apply tracks；只有 schema 生成 `source-map.md` 时，才同步回写代码路径、测试路径和追踪关系。
5. 如果分批时发现 artifact 缺失、矛盾或不可实现，停止并回到 `aisee:change-author` 或对应 artifact 修补；不要在 implementation-bridge 内重拆 change。

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

## 实现后审查建议

Brief 必须根据当前 change 和 context pack 判断是否建议 Tier 2 code review。触发条件与 `aisee:verify` 保持一致：

- 公开 CLI 命令、参数、JSON 输出或退出码。
- HTTP endpoint、局域网/远程服务、API/service contract、OpenAPI/events/webhooks/proto 等机器可读契约。
- schema、artifact template、source-map parser、contract parser、ID registry、context pack 或 OpenSpec 衔接逻辑。
- 文件/路径读取、目录遍历、缓存、包安装、package assets、dependency manifest。
- 认证、权限、安全、隐私、敏感信息、生产配置或回滚策略。

规则：

- `aisee:implementation-bridge` 只把 review gate 写入 Brief，不自动启动 subagent。
- 如果用户已明确授权“使用审查代理做 Tier 2 code review”，执行阶段可调用可用的 CE / harness 审查能力。
- 如果尚未授权，Brief 中写：`Suggested authorization: 使用审查代理做 Tier 2 code review`。
- 审查结果应作为 evidence 供 `aisee:verify` 和 `aisee:archive-guard` 消费；不可写成新的规范事实源。

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

如果 `ce-plan` 需要新增需求、扩大范围、改变 contract 或重拆 change，停止当前实现交接。contract 或 artifact 缺口回到 `aisee:change-author` / 对应 artifact 修补；change 边界不可执行时只报告 blocker 并等待用户决策，不在 implementation-bridge 内重拆 change。

## Brief 输出模板

单批 Brief 读取 `references/brief-template.md`；多批次先读取 `references/brief-index-template.md` 生成 index，再按批次读取 `references/brief-template.md` 生成 part。按当前 schema 删除不适用项或标注 N/A。不得把模板中的空项当事实；所有字段必须来自当前 change、schema、context pack、apply tracks 或明确风险。
