---
name: aisee:change-author
description: 将 aisee:change-plan 的结果转成单个 OpenSpec change artifacts 初稿。用于已确认 change 的 author preflight，并按当前 schema 编排 proposal、source-map、specs、tasks、quick-fix、research、docsite、infra、app 或 device 契约 artifacts。必须先运行 aisee change author-check；不拆 change 边界、不重新选择 schema、不写代码；仅当当前 schema 明确包含 design.md 时才按 schema 模板补齐 design artifact。
---

# aisee:change-author

`aisee:change-author` 是 OpenSpec change 产物编排器。

## 职责边界

- 读取 change-plan、所选 schema、当前 change 目录，以及该 schema 需要的上游事实。
- 通过 `aisee change author-check <change> --json` 识别 schema、artifact、ID 和 blocker 状态。
- 为单个 OpenSpec change 创建或补齐 artifacts 初稿。
- 当 schema 生成 `source-map.md` 时，通过 ID 和 `source-map.md` 串联上游产物、spec、tasks、代码路径和验证。
- 当 schema 不生成 `source-map.md` 时，不伪造 source-map；按 schema artifacts 自身承载问题、方案、调研、文档或运维信息。
- 需要新增正式 ID 时，先通过 `aisee id reserve` 获取；写入后用 `aisee id activate` 激活。
- 仅当 schema 明确包含 `design.md` 时，按该 schema 的官方模板直接补齐 design artifact；不要创建独立 design skill 流程。

不负责：

- 拆 change 边界。
- 为多个 change 规划 schema。
- 重新选择 schema 或把轻量 schema 升级成 app schema。
- 为不生成 `source-map.md` 的 schema 创建 source-map。
- 写代码。
- 让 `ce-plan` 生成长期任务清单。

## 必须先运行的检查

开始 author 前必须运行：

```bash
aisee change author-check <change> --json
```

处理规则：

- `status=blocked`：停止 author，向用户列出 `blockers`；不要创建或修改 artifacts。
- `schema.valid=false`：停止 author；不得自造 schema 未声明的 artifact 或模板。
- `missing_artifacts` 非空：只按 `artifact_order` 和 schema templates 补齐缺失项；不重排 schema。source-map.md 中 Required=no 且有原因的按需 artifact 不应进入补齐队列。
- `ids.actions.reserve` 非空：先运行对应 `aisee id reserve`，再写入正式 ID。
- `ids.actions.activate` 非空：写入 artifact 后运行 `aisee id activate`。
- `ids.registry.missing / inactive` 非空：先修复 registry 或替换引用；不要把断链 ID 写入新的 artifact。
- `next_actions` 是执行提示，不是新的事实源；所有结论必须回写到 OpenSpec artifacts。

如 CLI 不可用，允许继续草稿，但必须：

- 使用 `{{scope}}:<TYPE>-NEW-001` 临时 ID。
- 如果 schema 生成 `source-map.md`，在 `source-map.md` 标注 `[ID-RESERVATION-REQUIRED]`；否则在当前 schema 的主 artifact 中标注。
- 交付摘要说明尚未完成 `author-check / id reserve / id activate / id check`。

## Author 子阶段

```text
author-check -> blocker / schema / ID preflight
proposal.md -> change scope from confirmed change-plan
source-map.md -> only when schema generates it; upstream IDs + produced IDs + artifact applicability
specs/**/*.md -> only when schema generates it; observable behavior and acceptance
change-context.md -> app architecture context author, only when Required=yes
design.md -> only when schema generates design.md, author directly from schema template
ui-contract.md / service-contract.md / data-model.md -> app domain author, only when Required=yes
hardware-contract.md / firmware-contract.md / runtime-contract.md / verification-contract.md -> device domain author, when schema generates them
quick-fix artifacts -> problem.md / solution.md / tasks.md
research artifacts -> question.md / findings.md / recommendation.md or loop/* artifacts
docsite / infra artifacts -> only when selected schema generates them
tasks.md -> single durable implementation and verification checklist
final check -> aisee change author-check + aisee gaps
```

## ID 规则

- 正式 ID 必须来自 `.aisee/id-registry.json`，不得由 AI 直接发明。
- 生成或修改 artifacts 前，先读取 `author-check.ids.actions`。
- 新增 `FR / NFR / RULE / PAGE / FLOW / STATE / ARCH / DEC / CONSTRAINT / RISK / SPEC / API / DATA / TASK / TEST` 前，先使用 `aisee id reserve --scope <scope> --type <TYPE> --count <N> --json`。
- 写入 artifact 后，使用 `aisee id activate <full-id> --owner <path> --title "<title>"` 激活。
- 交付前运行或要求运行 `aisee id check --json` 和 `aisee change author-check <change> --json`。
- 如果 Aisee CLI 或 ID registry 不可用，只能写临时占位符，例如 `{{scope}}:API-NEW-001`，并在当前 schema 的追踪 artifact 标注 `[ID-RESERVATION-REQUIRED]`。schema 生成 `source-map.md` 时写入 `source-map.md`；否则写入主 artifact。不要声称占位符是正式 ID。

## 输入门禁

开始 author 前必须确认：

- 当前只处理一个 OpenSpec change；不要一次为多个 changes 生成 artifacts。
- change 已由 `aisee:change-plan` 或用户明确确认边界、schema 和依赖；不得在 author 阶段重新选择 schema。
- 能读取 `openspec/changes/<change>/`，或用户明确要求先输出补丁 / 草稿而不直接写文件。
- `aisee change author-check <change> --json` 已完成，且没有 blocker。
- 能读取当前 schema 的 `schema.yaml` 和所有 `templates/`；不得自造 artifact 顶层结构。
- 已收集与所选 schema 直接相关的上游输入：Change Plan、Issue / 用户输入；只有 app/device schema 需要读取对应 SRS、UI Content、Architecture 或设备上下文。
- 已读取项目规则：优先 `AGENTS.md`，`CLAUDE.md` 只作为 legacy fallback。
- 如涉及既有系统，先读取相关 existing specs、代码事实、路由/API/模型/测试；不要只按上游文档猜现状。

如果缺少阻塞输入，输出 `[CHANGE-AUTHOR-BLOCKED]` 并列出缺口。非阻塞缺口必须写入当前 schema 的追踪 artifact，不要静默补齐。

如果当前 schema 不生成 `source-map.md`，非阻塞缺口写入该 schema 的主 artifact：

- `quick-fix`：`problem.md` 或 `solution.md`
- `quick-research`：`question.md` 或 `findings.md`
- `opsx-collab-pr-loop`：`loop/intake.md` 或 `loop/research-plan.md`
- `aisee-docsite-driven`：`doc-change.md`
- `infra-change`：`impact-assessment.md` 或 `rollback-plan.md`

## Schema DAG 规则

- 以 `author-check.artifact_order` 和当前 schema 的 `artifacts[].requires` 为唯一生成顺序来源。
- 不要因为某个模板常见就创建 schema 未声明的 artifact。
- 不要创建 schema 未声明的 artifact，包括不要给 `quick-fix`、`quick-research`、`infra-change`、`aisee-docsite-driven` 补 `source-map.md`。
- 对 app schema 的按需 artifacts，先读取 source-map.md 的 Artifact 适用性；Required=no 且有原因时不展开完整模板。
- 如果项目要求保留 N/A 文件，只写状态和 N/A 原因；不要为了填模板而复制无关表格。
- 生成每个 artifact 前，读取它的 `instruction` 和 `template`。
- 发现 schema DAG 循环、模板缺失、requires 指向不存在 artifact 时，停止并输出 `[SCHEMA-INVALID]`；优先引用 `author-check.schema.issues`。

## Artifact 编写边界

`change-author` 按 schema 编排 artifacts，但每个 artifact 只能承接自己的信息层级：

| Artifact | 主要输入 | 可新增 ID | 禁止内容 |
|---|---|---|---|
| `proposal.md` | confirmed change-plan、上游来源 ID、用户确认边界 | 无；只引用上游 ID | 接口字段、数据库字段、实现步骤、重新拆 change |
| `source-map.md` | proposal、上游文档、ID registry、schema artifact list | `SPEC / API / DATA / TASK / TEST` 的预留记录 | 业务需求正文、契约细节、实现方案 |
| `specs/**/*.md` | source-map 中覆盖的 `FR / NFR / RULE / FLOW / STATE` | `SPEC` | UI 布局、API 字段、表字段、任务清单 |
| `change-context.md` | Architecture 中相关 `ARCH / DEC / CONSTRAINT / RISK` | 局部 `DEC / CONSTRAINT / RISK` | 重写全局 Architecture、展开服务 / 数据 / UI 契约 |
| `ui-contract.md` | UI Content、Design Spec / Assets、specs、change-context、source-map | 必要时新增局部 `PAGE / FLOW / STATE` | 重新制定或复制完整视觉规范、组件库选择、像素布局 |
| `data-model.md` | specs、change-context、service data needs | `DATA` | API 协议、UI 内容、迁移执行任务 |
| `service-contract.md` | specs、ui data needs、data-model、change-context | `API` | 代码实现步骤、数据库物理迁移脚本 |
| `tasks.md` | specs、source-map、Required=yes 的适用 artifacts / contracts | `TASK / TEST` | 新增需求、替代 source-map、ID 注册、来源追踪或归档判断 |

对于不生成 `source-map.md` 的轻量 schema，按 schema 模板写对应 artifact，不使用上表中的 app artifact 假设：

| Schema | Artifact 编写重点 | 不要做 |
|---|---|---|
| `quick-fix` | `problem.md` 写问题、影响、复现；`solution.md` 写根因、方案、风险；`tasks.md` 写修复和验证 | 不补 SRS、UI Content、Architecture 或 source-map |
| `quick-research` | `question.md` 写要回答的问题；`findings.md` 写依据；`recommendation.md` 写结论和下一步 | 不写生产实现任务 |
| `opsx-collab-pr-loop` | `loop/intake.md` 和 `loop/research-plan.md` 承接外部 PR / issue / 调研输入 | 不把 review 结论直接变成实现任务 |
| `aisee-docsite-driven` | `doc-change.md` 写文档差异、导航、结构和归档回写 | 不补 specs / UI / service / data contracts |
| `infra-change` | `impact-assessment.md` 和 `rollback-plan.md` 写影响、窗口、回滚和验证 | 不省略回滚风险 |

当 schema 生成 `source-map.md` 时，`source-map.md` 不是一次性文件。先用它建立初始路由，再在每个 artifact 写入或激活 ID 后回填：

- artifact 是否适用及 N/A 原因。
- 新增 ID 的 owner path、标题和上游追踪关系。
- 发现的 `[SPEC-GAP]`、`[ID-RESERVATION-REQUIRED]`、`[STACK-CONFLICT]` 或其他阻塞标签。
- 不覆盖的上游 ID 及原因。

## App Schema v2 顺序

`aisee-app-spec-driven` v2 使用同一个 schema，但分为最小闭环和按需 artifacts。

最小闭环：

```text
proposal.md
source-map.md
specs/**/*.md
tasks.md
```

按需 artifacts：

```text
change-context.md
ui-contract.md
data-model.md
service-contract.md
```

生成规则：

- `proposal.md`：只定义本 change 的目标、范围、非目标和成功标准；引用完整 ID，不复制上游全文。
- `source-map.md`：先建立上游输入 ID、产出 ID、artifact 适用性和阻塞项。它是后续 artifact 的路由表。
- `specs/**/*.md`：只写用户可观察行为和验收场景，覆盖 FR / NFR / RULE / FLOW / STATE。
- `change-context.md`：只在 Required=yes 时承接本 change 相关的 ARCH / DEC / CONSTRAINT / RISK，不重写全局 Architecture。
- `ui-contract.md`：只在 Required=yes 且涉及页面、弹窗、交互、前端状态或前端数据需求时适用。
- `data-model.md`：只在 Required=yes 且涉及持久化数据、字段、关系、索引、迁移、审计或敏感数据时适用。
- `service-contract.md`：只在 Required=yes 且涉及 API、后端服务、异步任务、CLI / 工具命令或外部集成时适用。
- apply tracks：最后生成或补齐，是当前 schema 的唯一长期执行清单；常见是 `tasks.md`，也可能是其它 schema artifact 或 N/A。app schema 的 `tasks.md` 只记录实现顺序、任务状态和验证证据，任务项必须引用 specs、source-map 和 Required=yes 的适用 artifacts，但不重复契约细节。轻量 schema 的任务追踪到该 schema 的 problem / solution / findings / doc-change / impact / rollback 等前置 artifact。

## Artifact 适用性判断

仅对生成 `source-map.md` 的 schema，先在 `source-map.md` 写适用性，再生成对应 artifact：

| Artifact | 适用信号 | N/A 合法原因 |
|---|---|---|
| `change-context.md` | 有 Architecture 约束、技术决策、平台限制、集成边界、风险或阻塞 | 纯文案 / 极小配置变更，且无技术约束影响 |
| `ui-contract.md` | 页面、弹窗、表单、导航、权限可见性、前端状态、前端数据需求 | backend-only / job-only / CLI-only 且无前端可见变更 |
| `data-model.md` | 持久化实体、字段、表、关系、索引、迁移、审计、敏感数据 | 无持久化数据变化，且不改变数据生命周期 |
| `service-contract.md` | API、后端能力、异步任务、定时任务、CLI、外部集成、权限、错误语义 | UI-only 静态展示或纯内容变更，无服务能力变化 |

Required=no 的 artifact 不能留空原因。生成 `source-map.md` 的 schema 必须在 source-map.md 写：

- N/A 原因。
- 哪些上游 ID 使它不适用。
- 是否有需要其他 artifact 承接的相关约束。

既有系统或二次开发场景下，Required=yes 的 artifact 应按 Existing / Changed / New / Deprecated / Unknown 标注影响。Existing 只引用现有来源，不重写完整规格；Changed / New 才补充本 change 的差异内容。

不生成 `source-map.md` 的 schema 应在当前主 artifact 或对应 artifact 中写 N/A 原因，不要补假 source-map。如果同时创建 N/A 文件，文件只需要包含状态和 N/A 原因，不需要填完整模板。

## ID Preflight

优先使用 `aisee change author-check <change> --json` 中的 `ids.actions`。需要手动补查时使用：

```bash
aisee change author-check <change> --json
aisee id check --json
aisee trace <upstream-id> --json
aisee id reserve --scope <scope> --type SPEC --count <n> --json
aisee id reserve --scope <scope> --type API --count <n> --json
aisee id reserve --scope <scope> --type DATA --count <n> --json
aisee id reserve --scope <scope> --type TASK --count <n> --json
aisee id reserve --scope <scope> --type TEST --count <n> --json
aisee id activate <full-id> --owner <artifact-path> --title "<title>"
```

只 reserve 实际需要的 ID 类型。上游已有的 FR / NFR / PAGE / FLOW / ARCH / DEC / CONSTRAINT / RISK 不重新分配；只在确实新增局部对象时 reserve。

工具不可用时：

- 继续生成草稿可以，但所有新增 ID 必须用 `{{scope}}:<TYPE>-NEW-001`。
- 如果 schema 生成 `source-map.md`，必须在 `source-map.md` 写 `[ID-RESERVATION-REQUIRED]`；否则写入当前 schema 的主 artifact。
- final / handoff 必须说明这些不是正式 ID，后续需要运行 `aisee id reserve / activate / check`。

## 写入与输出

如果用户要求直接写文件：

- 只写当前 change 目录内 schema 声明的 artifacts。
- 已存在 artifact 时先读取并增量补齐，避免覆盖用户内容。
- 不要删除用户已有内容，除非它与 schema 明确冲突且用户确认。

输出摘要必须包含：

- 生成 / 更新了哪些 artifacts。
- 哪些 artifacts 是 N/A 及原因。
- 当前 schema 是否生成 `source-map.md`；若不生成，说明没有创建 source-map。
- 是否存在临时 ID 或 `[ID-RESERVATION-REQUIRED]`。
- 需要用户确认的 blocker。
- 最后一次 `aisee change author-check <change> --json` 和 `aisee gaps --change <change> --json` 的状态。
- 建议下一步：`openspec validate`，再进入 `aisee:implementation-bridge`。
