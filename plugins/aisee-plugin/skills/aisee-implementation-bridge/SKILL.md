---
name: aisee:implementation-bridge
description: 将单个已确认且已 authored 的 OpenSpec change 转成给 Compound Engineering 执行的最小工程交接。正常情况下直接进入 ce-work；只有在异常或明确要求 handoff 时才输出简短结果或人读 brief。它不创建平行任务清单，不默认落地新文档，不替代 ce-work，不修补缺失 artifacts。
---

# aisee:implementation-bridge

`aisee:implementation-bridge` 是 OpenSpec change 到工程实现阶段的交接器。

如需保存 Implementation Brief，frontmatter 字段合同统一遵循 `plugins/aisee-plugin/references/planning-doc-frontmatter.md`；这些 brief 仍是 generated handoff / cache，不是规范事实源。

## 复用优先

执行前必须优先复用当前 change 的事实源，而不是重新发明执行路由：

- 默认直接读取当前 change artifacts、schema、`tasks.md`、`source-map.md`（若当前 schema 生成）和 `AGENTS.md`。
- 如需项目记忆或团队知识，显式使用 `aisee memory search` 或 `aisee knowledge query --from-change <change> --for ce-work --json`。
- bridge 默认不把读取策略包装成公开 JSON 输出，也不搬运 artifact 正文，不代替 `ce-work` 读代码。
- 如果 CE skill 缺失，只说明限制和本地 guardrails，不创建 Aisee 替代 CE 的执行、代码审查或测试 agent。
- `design-spec`、`design-assets`、`reflect`、`knowledge-curate`、`hw:*` 等扩展能力只有在当前 change 明确引用，或用户显式要求附带注入时才读取；不要自动塞进默认实现交接路径。

## 职责

- 读取单个 OpenSpec change。
- 读取当前 change artifacts、schema、tasks、source-map（若适用）和 evidence 入口。
- 这些读取都是只读状态检查，由 skill 自动执行；不要求用户手工跑常规命令。
- 当前 change 已 ready 时，默认直接进入 `ce-work`。
- 仅在用户明确要求人读交接、保存 handoff 或分批执行索引时，生成人类可读的 Implementation Brief。
- 明确事实源、读取顺序、执行规则、禁止越界项和验证要求。
- 明确 `ce-work` 完成后必须先回写 `tasks.md` 或当前 schema 的 apply tracks，再记录验证证据。
- 识别实现后是否建议 Tier 2 code review，并把审查代理授权提示写入 Brief。
- 指出 blocker / risk / gap，但默认只做 advisory projection；除非当前 change 的关键读取入口本身失效，不替用户裁决是否继续实现。

## 不负责

- 创建、拆分或重新规划 change。
- 生成或补齐任何 OpenSpec change artifact 正文。
- 默认写入新的长期交接文档。
- 写代码或执行实现。
- 替代 `aisee:verify`、`ce-code-review`、`ce-test-*` 或 `aisee:archive-guard`。

## Change 入口规则

必须通过当前执行的 OpenSpec change 获取相关内容：

- 入口必须是明确的 `<change>`，例如 `openspec/changes/<change>/`。
- 只能读取当前 change artifacts、当前 change 的 schema、当前 change 明确引用的 evidence 入口，以及 `AGENTS.md` 这类执行规则。
- 可以读取当前 change 明确提到或当前 schema companion artifact 指向的内容；未提到但在实现或验证中发现的相关问题，可以报告出来。
- 不要绕过当前 change 去全项目搜索需求、页面、接口或代码后自行扩大实现上下文。
- 不要从其他未关联 change、历史草稿或泛项目文档推导实现范围；除非它们被当前 schema artifact、tasks 或用户显式要求的 memory/knowledge 注入明确引用。
- 如果实现需要的文件没有被当前 change artifacts、tasks 或当前 schema 指到，先把它作为 `[IMPLEMENTATION-PATH-GAP]`；schema 生成 `source-map.md` 时回写 source-map，否则回写当前 schema 的 apply tracks 或主 artifact。
- 未被当前 change 纳入范围的问题，只能进入 Brief 的 `Blockers and Assumptions`、`Follow-up candidates` 或验证风险；不得直接变成当前 change 的实现任务。

## 默认产物

默认不输出公开 JSON 判定结果，也不默认展开人读摘要。只有在异常、debug 或明确要求 handoff 时，结果才需要覆盖：

- 当前 change / schema / status。
- 是否存在 blocker 或关键风险；这些判定默认保留在 JSON 里作为 advisory，不自动转成停机。
- `read_first`：`ce-work` 开始前必须先读的 artifacts / supporting files。
- `apply_tracks` / 回写位置。
- `evidence_entrypoints`：验证、review、manual evidence 的读取与回写入口。
- `completion_gate`：完成当前批次前，必须先回写 `tasks.md` 或当前 schema apply tracks。
- 推荐下一步：直接进入 `ce-work`，必要时补充 artifact 修订 follow-up。

默认不写入 `openspec/changes/<change>/implementation-brief.md` 或其他长期文档，也不默认在会话里展开 `Implementation Brief` 各章节。

## Brief 产物形态

Implementation Brief 是按需的人读交接输出，不是新的规范事实源：

- 只有用户明确要求“生成 Brief / 交接摘要 / 保存 handoff”，或当前 change 内容过大需要分批交接时，才生成。
- 如果用户明确要求保存，优先写入 `aisee/cache/implementation-bridge/<change>/brief-part-NN.md`；如用户指定写入 change 目录，只能标注为 generated handoff / cache，且正文必须指向当前 schema artifacts 和 apply tracks；不得承载这些 artifact 中没有的新事实。
- 分批交接时必须先生成 `brief-index.md`，再生成 `brief-part-NN.md`；index 使用 `references/brief-index-template.md`，part 使用 `references/brief-template.md`。
- 发现 Brief 与 OpenSpec artifacts 不一致时，以 OpenSpec artifacts 为准，并回写对应 artifact，而不是修补 Brief。

## 输入门禁

开始前确认：

- 当前只处理一个 OpenSpec change。
- schema metadata、schema 安装状态和 artifact 缺口都要读取并原样保留在 `gaps`；默认作为 advisory 输出，而不是由 bridge 自动把流程打回上游。
- 不要把 Aisee 增强字段本身当成准入门槛：官方或轻量 schema 缺少顶层 `capabilities`、artifact `requiredness`、artifact `capabilities` 时，不因此阻塞实现交接；只要 OpenSpec schema 本身可解析，仍按该 schema 的实际 artifacts 和 apply tracks 继续 bridge。
- change 已经通过 `aisee:change-author` 补齐当前 schema 的必需 artifacts；只有 schema 生成 `source-map.md` 时才要求 source-map 说明按需 artifacts 的 Required=yes/no 与 N/A 原因。
- 当前 schema 的 apply tracks 存在；通常是 `tasks.md`，但 `quick-research` 等无 apply schema 可以没有 tasks。
- `source-map.md` 只在当前 schema 生成它时必需。
- `specs/**/*.md` 只在当前 schema 明确生成 specs 时必需。
- 当前 schema 的 Required=yes contracts 已存在并可读取；Required=no 的 app contract 只需要在 source-map schema 中写明原因。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。

只有当前 change 不存在、关键 artifact 无法读取，或入口本身失效时，才输出 `[IMPLEMENTATION-BRIDGE-BLOCKED]`。其它 schema / artifact / traceability 问题默认保留在 JSON `gaps` 与 Brief 风险段，交由用户或执行者决定是否先修补。

CHECKPOINT: 推荐进入 `ce-work` 前，必须确认当前 change artifacts 可用，且执行所需范围至少能从当前 change、tasks、source-map（若适用）和 supporting artifacts 推导出来。scope、apply tracks、实现路径或 schema 问题应进入 advisory JSON 与 Brief 风险段；只有读取入口本身失效时才停止并输出 `[IMPLEMENTATION-BRIDGE-BLOCKED]`。

## 推荐读取顺序

默认按以下顺序读取当前 change：

1. `AGENTS.md`
2. `openspec/changes/<change>/.openspec.yaml`
3. `openspec/changes/<change>/proposal.md`
4. 当前 schema 生成的追踪 artifact，例如 `source-map.md`、`problem.md`、`solution.md`、`doc-change.md`、`impact-assessment.md`、`rollback-plan.md`、`findings.md`
5. `openspec/changes/<change>/specs/**/*.md`，仅当当前 schema 生成 specs
6. schema 明确生成且当前 change Required=yes 的 supporting artifacts，例如 `change-context.md`、`design.md` 或其它 schema 专属 contract/document
7. 当前 schema 的 apply tracks，通常是 `tasks.md`
8. 当前 change 明确记录的 review / test / manual evidence 入口

如果用户明确要求附带项目记忆或团队知识，再额外读取：

```bash
aisee memory search --query "<当前实现任务>" --json
aisee knowledge query --from-change <change> --for ce-work --json
```

处理规则：

- `SCHEMA_METADATA_MISSING` / `SCHEMA_MISMATCH` / `SCHEMA_NOT_INSTALLED` / `SCHEMA_NOT_FOUND`：默认保留为 advisory gap，并在结果中明确风险；不要自动把实现交接打回上游。
- 如果当前 schema 是官方或轻量 schema，且缺少 Aisee 专属增强字段，不把这类缺口升级成 blocker；继续根据 schema 已声明的 artifacts、`apply.tracks`、`source-map.md` 是否存在来判断读取顺序。
- `ID_RESERVATION_REQUIRED`、`ID_UNREGISTERED_REFERENCE`、`ID_INACTIVE_REFERENCE` 只能作为阻塞或风险进入 Brief；不得在实现阶段由 `ce-work` 临时发明 ID。

如果 CLI 不可用，memory/knowledge 注入部分直接省略，不影响当前 change artifact 的默认读取路径。

## 默认 JSON 判定结果应包含

- 当前 change / schema / status。
- blocker / risk / gap 判定；默认只作为 advisory 投影，不自动改写路由候选。
- `read_first`、`required_supporting_artifacts`、`follow_up_candidates`。
- `apply_tracks`、completion gate、建议回写位置。
- `evidence_entrypoints`。
- 推荐下一步及仅针对读取入口失效的停止条件。

## 当明确要求生成人读 Brief 时，输出必须包含

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
- `Task Execution` 只写当前 change 下的必读 artifacts、apply tracks 回写位置和 evidence 入口。
- `Verification` 只写必须运行的命令、人工检查和 evidence 写回位置。
- `Review Recommendation` 只写是否建议 Tier 2 code review、触发原因、授权提示和 evidence 写回位置，不启动审查代理。
- contracts、specs、source-map、tasks 的详细内容只能作为路径引用，不要复制全文。

当 change 很大或当前 change 的任务 / artifacts 明显过多时，不回到 `aisee:change-plan` 重新拆 change。改为在当前 change 内分批交接：

1. 先用 `references/brief-index-template.md` 生成 `brief-index.md`：批次数、每批目标、依赖顺序、允许路径、验证入口和 apply tracks 回写位置。
2. 再用 `references/brief-template.md` 生成 `brief-part-01.md`、`brief-part-02.md` 等分块 Brief；每个 part 只覆盖一组相关 tasks / allowed paths / verification。
3. 每个 part 都必须引用同一个 current change、schema、apply tracks 和相关 artifacts。
4. 分批执行后，结论必须回写当前 schema apply tracks；只有 schema 生成 `source-map.md` 时，才同步回写代码路径、测试路径和追踪关系。
5. 如果分批时发现 artifact 缺失、矛盾或不可实现，停止并回到 `aisee:change-author` 或对应 artifact 修补；不要在 implementation-bridge 内重拆 change。

## 规则

- `specs/**/spec.md` 是行为契约。
- 当前 schema 的 apply tracks 是长期执行清单；app/device/quick-fix 通常是 `tasks.md`，无 apply schema 不强制 tasks。
- `source-map.md` 只在当前 schema 生成它时是代码定位入口；不生成 source-map 的 schema 只使用当前 schema artifacts 与 `tasks.md` 中明确给出的实现引用。
- `spec-driven`、`quick-fix`、`quick-research` 或其它轻量 schema 只要 OpenSpec 侧有效，就允许进入 bridge；不要要求它们补 Aisee app/device schema 才有的增强字段。
- app schema 中，按 `source-map.md` 的 Artifact Applicability 判断哪些 supporting artifacts 是 Required=yes；不要要求每个 change 都展开全部 contracts。
- device schema 中，`design.md` 和 hardware/firmware/runtime/verification contracts 是实现 contracts；不要把 app contract 假设套到设备项目。
- `ce-work` 的读取入口应来自当前 change artifacts、tasks、source-map（若适用）和 Required supporting artifacts。缺失时标记 `[SOURCE-MAP-GAP]` 或 `[IMPLEMENTATION-PATH-GAP]`，不要自行扩大实现范围。
- 实现中发现需求/spec/contract/code 事实不一致，先回写当前 OpenSpec change，再继续实现。
- 不创建新的长期计划文件；需要临时推理时，结论必须回写当前 schema 的 apply tracks 或追踪 artifact。
- 不扩大 change 范围；超出范围的发现记录为 follow-up 或新 change 候选。
- 完成实现后必须更新当前 schema 的 apply tracks 和验证证据；没有 apply tracks 的 schema 只记录必要 evidence。
- `ce-work` 只有在本轮实现涉及的 apply tracks 已同步回写后，才能声明当前批次完成；app/device/quick-fix 默认先更新 `tasks.md` checkbox、验证任务和 evidence 入口，再离开 `ce-work`。
- UI 实现涉及图标时，先复用项目已使用的组件库、图标包或设计系统图标；没有合适图标时允许使用 `better-icons` / Iconify 检索。优先使用全局安装的 `better-icons` 以减少冷启动；缺少时执行阶段应按项目包管理器安装或用 `npx -y better-icons` / `bunx better-icons` 完成一次性检索，并在 evidence 中记录命令、图标库和完整图标 ID。不要为了常见 UI 图标手写 SVG。

CHECKPOINT: `ce-work` 完成前，必须先回写当前 schema 的 apply tracks。对默认以 `tasks.md` 追踪的 schema，至少要同步当前批次已完成 / 未完成状态、验证任务和 evidence 入口；如果代码已改但 apply tracks 仍未更新，不得把该批次报告为完成。

## 实现后审查建议

Brief 必须根据当前 change、schema 和 evidence 入口判断是否建议 Tier 2 code review。触发条件与 `aisee:verify` 保持一致：

- 公开 CLI 命令、参数、JSON 输出或退出码。
- HTTP endpoint、局域网/远程服务、API/service contract、OpenAPI/events/webhooks/proto 等机器可读契约。
- schema、artifact template、source-map parser、contract parser、context pack 或 OpenSpec 衔接逻辑。
- 文件/路径读取、目录遍历、缓存、包安装、package assets、dependency manifest。
- 认证、权限、安全、隐私、敏感信息、生产配置或回滚策略。

规则：

- `aisee:implementation-bridge` 只把 review gate 写入 Brief，不自动启动 subagent。
- 如果用户已明确授权“使用审查代理做 Tier 2 code review”，执行阶段可调用可用的 CE / harness 审查能力。
- 如果尚未授权，Brief 中写：`Suggested authorization: 使用审查代理做 Tier 2 code review`。
- 审查结果应作为 evidence 供 `aisee:verify` 和 `aisee:archive-guard` 消费；不可写成新的规范事实源。

## Brief 输出模板

单批 Brief 读取 `references/brief-template.md`；多批次先读取 `references/brief-index-template.md` 生成 index，再按批次读取 `references/brief-template.md` 生成 part。按当前 schema 删除不适用项或标注 N/A。不得把模板中的空项当事实；所有字段必须来自当前 change、schema、apply tracks、evidence 入口或明确风险。
