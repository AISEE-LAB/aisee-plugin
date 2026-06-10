# Change Author Rules

本文件承接 `aisee:change-author` 的详细 authoring 规则。`SKILL.md` 只保留流程入口和强门禁；需要实际编写 artifacts 时读取本文件。

## 目录

- [无前置 planning docs 的 intake 路径](#无前置-planning-docs-的-intake-路径)
- [无 source-map schema 的缺口落点](#无-source-map-schema-的缺口落点)
- [Schema DAG 规则](#schema-dag-规则)
- [Artifact 编写边界](#artifact-编写边界)
- [App Schema v2 顺序](#app-schema-v2-顺序)
- [Artifact 适用性判断](#artifact-适用性判断)
- [ID Preflight](#id-preflight)

## 无前置 planning docs 的 intake 路径

当当前 change 没有 SRS / UI Content / Architecture 等前置 planning docs 时：

- `proposal.md` 只写范围摘要和来源类型，不复制原始长提示词。
- `source-map.md` 使用 `Intake 来源` 表记录 `type / external ref / summary / artifact`。
- `upstream_refs=[]` 是合法状态；不要为了满足模板创建假 `docs/...#FR-001`。
- 正式 local ID 仍由当前 change artifacts 产生，例如 `SPEC-001`、`API-001`、`TASK-001`。
- 如果输入无法压缩为摘要，写 `[SPEC-GAP]` 或 blocker，等待确认；不要把整段聊天记录写进 source-map。

## 无 source-map schema 的缺口落点

如果当前 schema 不生成 `source-map.md`，非阻塞缺口写入该 schema 的主 artifact：

| Schema | 缺口落点 |
|---|---|
| `quick-fix` | `problem.md` 或 `solution.md` |
| `quick-research` | `question.md` 或 `findings.md` |
| `opsx-collab-pr-loop` | `loop/intake.md` 或 `loop/research-plan.md` |
| `aisee-docsite-driven` | `doc-change.md` |
| `infra-change` | `impact-assessment.md` 或 `rollback-plan.md` |

## Schema DAG 规则

- 以 `author-check.artifact_order` 和当前 schema 的 `artifacts[].requires` 为唯一生成顺序来源。
- 不要因为某个模板常见就创建 schema 未声明的 artifact。
- 不要给 `quick-fix`、`quick-research`、`infra-change`、`aisee-docsite-driven` 等无 source-map schema 补 `source-map.md`。
- 对 app schema 的按需 artifacts，先读取 `source-map.md` 的 Artifact 适用性；Required=no 且有原因时不展开完整模板。
- schema metadata 缺失、不一致、未安装或找不到时，不继续 author；先回到 change creation / schema installation 修复。
- 如果项目要求保留 N/A 文件，只写状态和 N/A 原因；不要为了填模板而复制无关表格。
- 生成每个 artifact 前，读取它的 `instruction` 和 `template`。
- 发现 schema DAG 循环、模板缺失、requires 指向不存在 artifact 时，停止并输出 `[SCHEMA-INVALID]`；优先引用 `author-check.schema.issues`。

## Artifact 编写边界

`change-author` 按 schema 编排 artifacts，但每个 artifact 只能承接自己的信息层级：

| Artifact | 主要输入 | 可新增 ID | 禁止内容 |
|---|---|---|---|
| `proposal.md` | confirmed change-plan、上游来源 anchor、用户确认边界 | 无；只引用上游 anchor / local ID | 接口字段、数据库字段、实现步骤、重新拆 change |
| `source-map.md` | proposal、上游文档、sources index、schema artifact list | `SPEC / API / DATA / TASK / TEST` 的 local ID 记录 | 业务需求正文、契约细节、实现方案 |
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
| `security-audit` | `threat-model.md` 写 STRIDE 威胁、风险和缓解；`design.md` 写安全控制设计；`tasks.md` 写安全验收门控 | 不绕过 threat-model，不把安全 review 当普通实现任务 |

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

- `proposal.md`：只定义本 change 的目标、范围、非目标和成功标准；引用 anchor ref 或 local ID，不复制上游全文。
- `source-map.md`：先建立上游输入 anchor、产出 local ID、artifact 适用性和阻塞项。它是后续 artifact 的路由表。
- `specs/**/*.md`：只写用户可观察行为和验收场景，覆盖 FR / NFR / RULE / FLOW / STATE。
- `change-context.md`：只在 Required=yes 时承接本 change 相关的 ARCH / DEC / CONSTRAINT / RISK，不重写全局 Architecture。
- `ui-contract.md`：只在 Required=yes 且涉及页面、弹窗、交互、前端状态或前端数据需求时适用。
- `data-model.md`：只在 Required=yes 且涉及持久化数据、字段、关系、索引、迁移、审计或敏感数据时适用。
- `service-contract.md`：只在 Required=yes 且涉及 API、后端服务、异步任务、CLI / 工具命令或外部集成时适用。
- apply tracks：最后生成或补齐，是当前 schema 的唯一长期执行清单；常见是 `tasks.md`，也可能是其它 schema artifact 或 N/A。

app schema 的 `tasks.md` 只记录实现顺序、任务状态和验证证据，任务项必须引用 specs、source-map 和 Required=yes 的适用 artifacts，但不重复契约细节。轻量 schema 的任务追踪到该 schema 的 problem / solution / findings / doc-change / impact / rollback 等前置 artifact。

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

## Anchor / Local ID Preflight

优先使用当前 change、schema 模板和已存在 artifact 中的 anchor/local ID 信息。需要手动补查时使用：

```bash
aisee get <anchor-ref> --json
aisee trace <anchor-ref> --json
aisee index --json
```

只在当前 change 内生成实际需要的 local ID。上游已有的 FR / NFR / PAGE / FLOW / ARCH / DEC / CONSTRAINT / RISK 不重新分配；只在确实新增局部对象时写新的 local ID，并把跨文档追踪回写成 anchor ref。

工具不可用时：

- 继续生成草稿可以，但所有新增 ID 必须用 `TYPE-NEW-001`。
- 如果 schema 生成 `source-map.md`，必须在 `source-map.md` 写 `[ID-FINALIZATION-REQUIRED]`；否则写入当前 schema 的主 artifact。
- final / handoff 必须说明这些不是最终 local ID，后续需要完成 local ID 定稿并校验 anchor 解析。
