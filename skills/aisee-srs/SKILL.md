---
name: aisee:srs
description: 通过结构化对话充分澄清软件类业务需求，并生成规划级详细的需求规格说明书（SRS）。当用户想写需求文档、澄清产品范围、整理业务目标/用户角色/业务能力/业务流程/业务规则/权限/非目标，或为 UI Content、Architecture、aisee:change-plan 准备稳定输入时使用。适用于 App、小程序、Web、桌面软件、后端/API 服务、CLI 工具、定时任务/异步任务等软件项目。SRS 应写到足够支持后续拆 change 和生成 UI/技术架构，但不要写成接口设计、数据库设计、技术方案、视觉设计、硬件架构、固件设计或开发任务。
---

# aisee:srs — OpenSpec 需求规格说明书

通过结构化对话挖掘软件需求，然后生成可交给 `aisee:ui-content`、`aisee:architecture` 和 `aisee:change-plan` 使用的需求规格说明书（SRS）。

当前主流程面向软件 / App / 后端 / CLI / Job 等场景。硬件、嵌入式和固件需求后续按专用流程整理；如果本次软件需求依赖设备，只记录软件可见的设备能力、状态、告警、操作环境、安全可靠性和验收约束，不展开硬件架构、固件设计或制造细节。

## 输入

用户提供以下任意一种输入：

- 原始需求或功能想法（自由文本）
- 模糊的产品目标或问题描述
- 已有但尚未成型的需求草稿
- 现有系统二次开发、改造、替换或兼容需求

可选参数：

- `--lang zh|en` — 输出语言，默认 `zh`
- `--depth shallow|standard|deep` — 对话深度，默认 `standard`
- `--baseline-aware` — 基于现有 OpenSpec baseline specs、active changes 和既有需求文档识别新增 / 修改 / 移除 / 兼容行为。若项目中存在 `openspec/specs/`、`openspec/changes/`、`aisee/docs/spec-migration/` 或历史 SRS，默认自动启用。

## 输出边界

`aisee:srs` 产出的是 **规划级需求契约**：它要足够详细，能支撑后续 UI 内容规格、技术架构和 change 边界规划；但它不是实现级接口设计、数据库设计、技术方案、UI 内容规格或设计系统。

必须覆盖：

- 目标用户、业务目标、范围和非目标
- 业务对象、业务状态、状态流转、业务流程和用户任务流
- 功能需求、非功能需求、业务规则、权限规则和数据范围
- 异常、失败、兼容、验收方向和待确认事项
- 交付形态信号，例如 App、小程序、Web 管理后台、桌面 GUI、后端服务、CLI、导入导出、通知、异步处理
- 现有项目二开时的新增 / 修改 / 移除 / 兼容行为，以及受影响 baseline 引用
- 后续是否需要 UI Content、Architecture 或特殊 change artifact 的提示

可以记录但不得展开设计：

- 页面相关的功能行为：必须采集或展示的数据字段、列表列、筛选条件、空状态、行操作、入口和完成后去向
- 外部系统交互的业务目的、触发条件、成功/失败处理和数据含义
- 设备参与的软件需求中，用户或系统可观察的设备能力、状态、告警、输入输出信号业务含义、安全可靠性和验收约束

禁止输出：

- 视觉布局、间距、颜色、字体、图标、组件库选择或逐页线框图
- API endpoint、数据库表字段、ORM、代码文件结构或迁移实现
- 具体技术栈选择、服务拆分、队列方案、任务拆解或代码实现计划
- 引脚表、寄存器表、RTOS 任务设计、驱动结构、BOM、PCB 布局、固件实现步骤或制造工艺
- 未由用户或现有 baseline 确认的新增需求

如果用户需要“开发哪些页面、页面上有什么内容、页面元素和交互流程”，先完成 SRS，再建议进入独立的 `aisee:ui-content`。如果用户需要接口、数据、任务或测试契约，应在 change artifacts 阶段处理。

## ID 规则

`aisee:srs` 负责需求侧上游 ID：

- `FR`：功能需求
- `NFR`：非功能需求
- `RULE`：业务规则
- `FLOW`：业务流程或用户任务流，只有在 SRS 阶段已经明确时分配
- `STATE`：业务状态或用户可感知状态，只有在 SRS 阶段已经明确时分配

正式 ID 必须来自 `aisee/registry/id-registry.json`。生成 SRS 前应确定 `scope`，并在需要新增 ID 时使用：

```bash
aisee id reserve --scope <scope> --type FR --count <N> --json
aisee id reserve --scope <scope> --type NFR --count <N> --json
aisee id reserve --scope <scope> --type RULE --count <N> --json
aisee id reserve --scope <scope> --type FLOW --count <N> --json
aisee id reserve --scope <scope> --type STATE --count <N> --json
```

写入文档后，使用 `aisee id activate <full-id> --owner <path> --title "<title>"` 激活；交付前运行或建议运行 `aisee id check --json`。

如果 Aisee CLI 或 ID registry 不可用，只能使用临时占位符，例如 `{{scope}}:FR-NEW-001`，并在文档 ID 状态中标注 `[ID-RESERVATION-REQUIRED]`。不要声称占位符是正式 ID。

SRS 不负责 `PAGE / API / DATA / TASK / TEST`。`PAGE` 以及 UI 细化由 `aisee:ui-content` 承接；`API / DATA / TASK / TEST` 由 change artifacts 承接。

## Phase 0 — 读取项目上下文

开始对话前，静默收集可用项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -120
cat aisee/registry/id-registry.json 2>/dev/null || true
rg --files openspec/specs 2>/dev/null | head -40
rg --files openspec/changes 2>/dev/null | rg '(^|/)(proposal\.md|source-map\.md)$|/specs/' | head -60
rg --files aisee/docs/spec-migration aisee/docs/requirements 2>/dev/null | head -60
rg --files aisee/docs/requirements 2>/dev/null | head -20
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，并只查 SRS 需要的文件类型。

用这些上下文理解项目边界、现有业务行为、术语和当前 specs，避免重复询问项目已经回答的问题。如果没有项目上下文，正常继续；`aisee:srs` 允许在 `openspec-init` 前运行。

## Workflow

先按 Phase 0 读取项目上下文，再按需读取 [workflow.md](references/workflow.md) 执行范围锚定、需求探讨、确认门禁、输出模式选择、SRS 生成和保存。

CHECKPOINT: 生成 SRS 前必须先输出需求摘要、范围、非目标、关键假设、Open Questions 和 ID 状态，等待用户确认。未确认时不得写入最终 SRS；如果用户要求继续但仍有缺口，把缺口写入 `[ASSUMPTION]` 或 Open Questions，不要静默补需求。

Reference loading：

- 需求追问前读取 `references/question-bank.md` 和 `references/domain-rules.md`。
- 模块划分或 Epic 判断前读取 `references/module-boundary-rules.md`。
- 生成前读取 `assets/srs-template.md` 入口索引和 `references/writing-rules.md`。
- 只读取当前输出模式需要的模板：标准模式读取 `assets/srs-template-standard.md`；Epic 模式读取 `assets/srs-template-epic-main.md` 和相关模块模板。
- 只读取当前场景需要的 `references/scenario-extension-blocks.md` 片段，不要一次性加载全部扩展块。

## Guardrails

- 用户在确认门禁前，不得生成 SRS。
- 每轮不得问超过 3 个问题；第一轮只问 1 个范围锚定问题。
- 功能需求不得包含实现决策，例如框架选择、具体 API endpoint、数据库 schema、服务拆分或代码文件结构。
- 不要把 SRS 写成 UI 设计文档。页面字段、列表列、操作和空状态只作为功能合约；视觉布局和详细页面构成留给 UI 内容 / 设计步骤。
- 不要把 baseline-aware 写成技术设计。已有基线只用于描述业务行为变化、兼容约束和影响范围。
- 不要把后续交接提示写成实现方案。Section 8 只能说明后续需要哪些上下文、哪些 FR/PAGE/业务对象值得关注。
- 单份 SRS 文档不得超过 20 条 FR；如果总范围超过 20 条 FR，标记为 Epic 并进入 Epic 模式。
- Epic 模式下，每份模块文档必须包含足够的模块上下文摘要，确保可被 `aisee:change-plan` 单独处理。
- 模块划分依据业务能力边界，不按输入材料章节、技术层、页面类型、设计规范、架构主题、测试计划或任务阶段直接划分。
- 每个 `[ASSUMPTION]` 必须进入主文档的 Section 5.2；Open Questions 不得为空白占位。
- 正式 `FR / NFR / RULE / FLOW / STATE` ID 必须来自 ID registry；工具不可用时使用 `{{scope}}:<TYPE>-NEW-001` 并标注 `[ID-RESERVATION-REQUIRED]`。
- 纯硬件、嵌入式或固件设计需求不在当前主流程展开；只在软件需求依赖设备时记录软件可见约束，并提示后续进入专用硬件流程。

## 与 OpenSpec 工作流集成

```text
aisee:srs                         ← 需求发现 → SRS 文档
  ├─ [conditional] aisee:ui-content       ← UI 型软件的页面清单、页面内容、页面元素、交互路径
  ├─ [recommended] aisee:architecture     ← 技术架构事实、决策、项目约束、共享前置
  └─ aisee:change-plan <srs-file>         ← 将 SRS 映射为独立 Change
       └─ /opsx:new <change>
            └─ aisee:change-author        ← 按 schema 创建 / 补 proposal、specs、contracts、tasks、source-map
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```
