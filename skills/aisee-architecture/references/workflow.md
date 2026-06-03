# Architecture 工作流

本文维护 `aisee:architecture` 的详细执行流程。`SKILL.md` 只保留入口、边界、ID、上下文扫描和 reference 路由。

## Phase 1 — 技术域与技术栈状态判断

先判断软件技术域：

| Domain | 适用场景 |
| --- | --- |
| app / mini-program | App、小程序、H5、多端用户应用 |
| web / desktop | Web 应用、管理后台、门户、桌面 GUI、上位机软件 |
| backend-service | 后端服务、API 能力、内部平台服务 |
| cli-tool | CLI 工具、开发者工具、运维工具、本地处理工具 |
| job-async | 定时任务、异步任务、批处理、导入导出流水线、通知任务 |
| integration / data | 第三方集成、数据能力、迁移、报表、同步 |
| hybrid-software | 同一软件范围内同时包含 UI、服务、Job、数据、外部系统或设备协作 |

纯硬件、嵌入式、固件、RTOS、驱动或板级架构不进入当前主流程。若软件需求涉及设备，只记录软件可见的设备状态、数据上报、告警、上位机协作、运行环境和可靠性约束。

再判断项目级技术栈状态：

| 状态 | 条件 | 处理 |
| --- | --- | --- |
| 已确定 | `openspec/project.md`、项目文件或可信架构文档明确关键技术栈 | 记录来源并继续 |
| 部分确定 | 只确认部分层，例如前端 / 后端已定但队列 / 缓存 / 部署未定 | 标注缺口并继续生成上下文 |
| 未确定 | 没有可信来源确认关键技术栈 | 标注 `[STACK-CONTEXT-MISSING]`，不要替用户选型 |

关键技术栈包括：前端框架 / 客户端形态、后端框架 / 服务边界、数据库、ORM / 数据访问、鉴权与权限、队列 / 异步任务、缓存、文件存储、通知 / 消息、部署环境、测试和可观测性。

## Phase 1.5 — 缺口标签与处理动作

遇到缺口时先判断是否阻塞 change-plan，再写入风险、待确认决策或 Open Questions。不要把缺口补成推断结论。

| 标签 | 使用条件 | 处理动作 | 是否阻塞 change-plan |
|---|---|---|---|
| `[STACK-CONTEXT-MISSING]` | 技术栈或运行环境没有可信来源 | 列出缺失层级、已查来源、需要用户提供的项目文件/配置/文档；不做选型 | 影响 change 拆分时阻塞 |
| `[STACK-DECISION-REQUIRED]` | 已知有多个可行技术方向，但用户或项目未决策 | 写入待确认决策，说明影响范围和可选方向，不推荐单一结论 | 通常阻塞 |
| `[DOC-CONTEXT-MISSING]` | 框架、SDK、CLI、云服务、数据库能力无法从项目或官方文档确认 | 标注需要查证的版本、能力点和官方来源；不得靠记忆写事实 | 取决于影响范围 |
| `[ARCH-DECISION-REQUIRED]` | 架构边界、运行单元、集成方式、权限/数据归属等未决 | 写入待确认决策，说明对后续 contract 或 change-plan 的影响 | 通常阻塞 |
| `[TECH-CONVENTION-MISSING]` | API 响应、错误码、日志、配置、CLI 输出、Job 幂等等全局约定缺失 | 只记录缺口和影响，不创建新约定；提示后续 artifact 承接 | 通常为 risk |
| `[STACK-CONFLICT]` | 需求与现有技术栈、平台能力或运行环境冲突 | 写明冲突证据、影响范围和需要回到 SRS/change-plan 的原因 | 通常阻塞 |
| `[SPEC-GAP]` | 技术事实暴露需求缺口或验收缺口 | 写入风险和 Open Questions；不要在 Architecture 中补业务需求 | 取决于缺口 |
| `[SCHEMA-HINT-UNCLEAR]` | 后续契约类型不明确或 schema pack 可能不同 | 只写建议 artifact 类型和原因，不绑定文件名 | 不阻塞，但需提示 |

如果某标签涉及具体框架 / SDK / CLI / 云服务能力，先查项目文件；需要当前官方用法时使用 Context7 或官方文档。工具不可用或文档不可达时，保留 `[DOC-CONTEXT-MISSING]`，不要弱化为“应该可以”。

## Phase 2 — 技术架构事实与决策提取

需要追问时读取 `references/question-bank.md`，只问会影响技术架构判断的问题。每轮最多 3 个问题；超过 3 轮仍不明确时写入 Open Questions。

提取并标注来源：

- 技术栈事实
- 架构概览：系统分层、运行单元、端 / 服务 / 设备协作关系
- 全局工程约定
- 已确认架构决策与待确认架构决策
- 禁止假设项：没有可信来源时不能替用户决定的架构内容
- 模块边界
- 数据模型现状
- 权限体系现状
- API / 路由 / 服务边界
- 异步任务、队列、定时任务、通知现状
- 外部集成现状
- CLI / 工具入口、输出格式和分发现状
- 多端能力限制
- 设备协作软件中的设备状态、数据上报、告警、运行环境和可靠性约束
- 已有测试和验证方式

来源可信度：

- `high`：来自 `openspec/project.md`、代码、schema、配置、官方架构文档
- `medium`：来自 SRS、UI Content、Design Spec、用户明确说明
- `low`：从命名或上下文推断，必须标注为假设

对所有 `low` 来源的关键事实，必须给出后续动作：用户确认、补充项目文件、查官方文档、或降级为 Open Question。不能让 low 可信度事实直接影响 change-plan。

## Phase 3 — 生成给 change-plan 的技术提示

只写会影响 `aisee:change-plan` 的技术提示，不写 change 边界规划方案。

允许写：

- 共享技术前置：多个需求共同依赖的技术基础
- 技术耦合点：应被 change-plan 考虑的技术关联
- 可并行边界：哪些模块从技术上相互独立
- 不应横切的能力：例如不要把同一状态机拆散
- 阻塞性技术决策：缺队列、缺鉴权、缺数据库方案等
- Schema Artifact Hints：哪些后续契约类型需要承接，artifact 名称以 schema pack 为准
- 高风险区域：外部集成、迁移、权限、安全、性能、平台能力差异

禁止写：

- `Change 1 / Change 2`
- change 名称
- 阶段依赖图
- 具体 `/opsx:*` 命令
- 最终 change 边界规划结论
- 具体 artifact 文件名必须存在的断言

## Phase 4 — 生成与保存文档

先读取 `assets/architecture-template.md` 入口索引，再读取必要模板；每次生成都必须同时读取 `references/writing-rules.md`。

始终读取：

- `assets/architecture-template-core.md`
- `assets/architecture-template-software.md`
- `assets/architecture-template-artifact-hints.md`
- `references/writing-rules.md`

生成前先输出确认摘要：技术域、技术栈状态、关键来源、待确认决策、阻塞标签、将保留的 domain blocks、schema artifact hints 类型和 ID 状态。用户未确认时，只能输出草稿或 Open Questions，不直接写入长期 Architecture 文档。

默认保存：

```bash
mkdir -p aisee/docs/architecture
```

文件：

```text
aisee/docs/architecture/<YYYY-MM-DD>-<slug>-architecture.md
```

如果用户只要求分析，可以只在聊天中输出。

完成后报告：

- 生成路径
- 技术栈状态：已确定 / 部分确定 / 未确定
- 架构决策、架构边界、可复用能力、共享技术前置、风险和阻塞决策数量
- 下一步：将本文档与 SRS、UI Content、Design Spec 一起交给 `aisee:change-plan`

若存在阻塞项，说明阻塞项会影响 change 边界规划，但本技能不会直接规划 change 边界。
