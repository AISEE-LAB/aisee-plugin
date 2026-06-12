# SRS 工作流

本文是 `aisee:srs` 的详细执行流程。`SKILL.md` 只保留入口和核心规则；需求发现顺序、确认门禁、生成与保存细节维护在本文。

## Baseline-Aware 模式

出现以下任一情况时启用 baseline-aware 模式：

- 用户传入 `--baseline-aware`。
- 存在 `openspec/specs/`。
- 存在 active changes under `openspec/changes/`。
- 存在历史需求文档：`aisee/docs/requirements/` 或 `aisee/docs/spec-migration/`。
- 用户说明这是基于现有系统、二次开发、兼容、替换、迁移或改造现有行为。

Baseline-aware 模式必须：

- 从 baseline specs 或现有文档识别既有业务行为和术语。
- 将受影响需求标记为 `新增 / 修改 / 移除 / 兼容`。
- 在可用时记录受影响基线引用，例如 `openspec/specs/<domain>/spec.md`。
- 保留用户可观察的兼容性约束。
- 将未解决的基线冲突写入 Open Questions，并标注 `[SPEC-GAP]` 或 `[SPEC-CHANGE-REQUIRED]`。

Baseline-aware 模式不得：

- 设计 API、数据库表、迁移、服务、Job、UI 布局或代码模块。
- 把实现文件直接当作业务事实，除非它们是唯一可用来源；如果从代码推断行为，必须标注低可信度并要求确认。

## Phase 1 — 范围锚定

以简短回应开头，并只问 **一个** 锚定问题。

根据最不确定的维度选择问题：

| 不清楚的维度 | 询问方向 |
| --- | --- |
| 用户 | 谁使用这个功能？他们要完成什么结果？ |
| 替代关系 | 这是全新能力，还是替换 / 改进现有流程？ |
| 系统位置 | 它是独立系统、新模块，还是现有系统扩展？ |
| 触发原因 | 现在提出这个需求的业务痛点、事件或运营诉求是什么？ |
| 交付形态 | 主要交付形态是 App、小程序、Web、桌面 GUI、后端服务、CLI 还是 Job？ |

如果输入是纯硬件、嵌入式固件、PCB、BOM、驱动、RTOS 或制造相关工作，不要强行进入软件 SRS 主流程。说明当前 `aisee:srs` 只记录软件可见的设备约束，纯硬件工作应在后续专用硬件流程中处理。

## Phase 2 — 需求探讨

进入本阶段前读取：

- `references/question-bank.md`
- `references/domain-rules.md`

规则：

- 每轮最多问 3 个问题，按主题分组。
- 每轮开头显示：`[需求探讨 · 第 N 轮]`。
- 等待用户回答后再继续。
- 第 8 轮后展示 `question-bank.md` 中的过轮提醒。
- 将未解决但不阻塞的信息记录为 `[ASSUMPTION]`，然后继续推进。
- 对页面占比较高的需求，只追问理解用户任务路径所必需的功能性 UI 问题；详细页面清单和页面内容留给 `aisee:ui-content`。
- 进入确认门禁前，至少覆盖：目标用户、业务目标、范围 / 非目标、核心流程、业务对象与状态、关键规则、权限 / 数据范围、异常、验收方向和交付形态。

需求域处理：

- 当前主支持域：`app`、`web`、`mini-program`、`desktop`、`backend-service`、`cli-tool`、`job-async`。
- 对带设备的软件需求，只记录业务可见的设备能力、状态、告警、输入输出信号业务含义、安全可靠性约束和验收方向。
- 硬件架构、嵌入式固件设计、PCB/BOM、驱动、RTOS 任务、寄存器、引脚和制造细节属于后续专用硬件流程，不进入当前 SRS 主线。

## Phase 3 — 确认门禁

展示摘要前，先读取 `references/module-boundary-rules.md` 并审查模块候选。不要直接沿用输入材料章节、技术层、页面类型、架构主题、测试计划或任务阶段作为模块。

满足任一条件时进入 Epic 模式：

- 预计 FR 数量大于 10。
- 有效业务能力模块不少于 3 个。
- 存在 2 个以上复杂场景扩展块，例如工作流、外部集成或权限矩阵。

生成文档前展示结构化摘要，并等待用户明确确认：

```text
需求摘要（生成前确认）

- 系统 / 功能名称：{name}
- 核心用户：{users}
- 业务目标：{goals}
- 交付形态：{App / 小程序 / Web / 桌面 / 后端服务 / CLI / Job / 多端}
- 主流程数量：{N} 条
- 功能需求条数：约 {N} 条
- 非功能需求：{list or "暂无"}
- 业务对象 / 状态：{list or "暂无"}
- 关键业务规则：{list or "暂无"}
- 权限 / 数据范围：{list or "暂无"}
- 明确非目标：{list or "暂无"}
- 待确认假设：{list or "无"}
- 已识别风险：{list or "无"}
- 基线感知：启用 / 未启用（如启用，列出主要影响基线）
- 后续建议：UI Content 需要 / 不需要；Architecture 需要 / 不需要；仍待确认的关键问题
- 输出模式：标准模式 / Epic 模式

主流程预览：
1. {flow 1}
2. {flow 2}
```

如果进入 Epic 模式，补充：

```text
需求体量较大，将生成 1 份主文档 + {N} 份模块文档。
主文档：系统概述、跨模块约束、术语表和全局约束
模块文档：{模块 1} / {模块 2} / ...
```

要求用户回复 `确认，生成 SRS`。如果用户修正摘要，更新内部需求模型并重新展示摘要。

## Phase 4 — 生成 SRS

### 标准模式

当 FR 数量不超过 10、有效模块少于 3 个且不需要复杂场景拆分时，使用标准模式。

步骤：

1. 读取 `assets/srs-template.md` 确认模板路由。
2. 读取 `references/writing-rules.md`、`references/domain-rules.md` 和 `references/module-boundary-rules.md`。
3. 读取 `assets/srs-template-standard.md`。
4. 只读取 `references/scenario-extension-blocks.md` 中与当前场景相关的块。
5. 为 `FR / NFR / RULE / FLOW / STATE` 预留正式 ID，或在工具不可用时标注临时 ID。
6. 填写所有已确认需求、假设、Open Questions 和 baseline-aware 字段。
7. 仅在有价值时追加精简下游建议：是否建议进入 `aisee:ui-content`、`aisee:architecture`，以及仍待确认的关键问题；不得预写 `aisee:change-plan` 结果或实现级设计。

### Epic 模式

当范围过大、不适合单份 SRS 承载时，使用 Epic 模式。

Step 1：生成主文档。

- 读取 `assets/srs-template.md`、`references/writing-rules.md` 和 `assets/srs-template-epic-main.md`。
- 包含系统概述、全局上下文、非功能需求、约束、假设、Open Questions 和模块索引。
- 详细 FR 放入模块文档；主文档中每个 FR 都链接到对应模块文档。
- 如果启用 baseline-aware 模式，写明全局基线影响，并在可用时标注每个 FR 的变更类型和影响基线。

主文档生成后暂停并告知进度，再继续模块文档。

Step 2：逐个生成模块文档。

- 读取 `assets/srs-template-epic-module.md`。
- 只读取该模块需要的场景扩展块。
- 每份模块文档都必须包含足够的局部上下文，确保能单独传给 `aisee:change-plan`：模块目的、相关用户、业务对象 / 状态、关键规则、非目标、FR 详情、模块假设和 Open Questions；下游建议仅在确有价值时精简保留。
- 如果启用 baseline-aware 模式，每条 FR 都必须包含变更类型和影响基线。

每份模块文档生成后暂停，并询问是否继续。

## Phase 5 — 保存文档

标准模式路径：

```text
aisee/docs/requirements/<YYYY-MM-DD>-<requirement-slug>.md
```

Epic 模式路径：

```text
aisee/docs/requirements/<YYYY-MM-DD>-<slug>/
  ├── 00-main.md
  ├── 01-<module-a>.md
  ├── 02-<module-b>.md
  └── ...
```

`slug` 使用需求名称中前 3 到 5 个有意义词，转换为 kebab-case。

保存后报告：

- 生成路径
- `FR / NFR / RULE / Open Questions` 数量
- ID 状态：已激活正式 ID，或仍有临时占位符需要预留
- 建议下一步：`aisee:ui-content`、`aisee:architecture` 或 `aisee:change-plan`

当 UI Content、Architecture、contracts 或 change artifacts 仍缺失时，不要告诉用户可以只凭 SRS 直接开始实现。
