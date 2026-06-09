---
name: aisee:ui-content
description: 根据 SRS、模块需求文档、已确认功能需求或现有系统 UI 事实生成 UI 内容规格。用于回答“要开发哪些页面”“已有页面怎么改”“页面上有什么内容”“页面元素和操作是什么”“跨页面交互流程如何走”“PC/App/小程序/H5 有哪些内容差异”。当用户要求把 SRS 转成页面清单、前端页面内容、界面内容规格、UI content spec、页面交互说明、页面元素清单，或基于现有系统做 UI 二次开发差异说明时使用。不要用于视觉设计、配色、布局稿、组件库选型或前端实现方案；这些属于后续设计或开发规划。
---

# aisee:ui-content — UI 内容规格

从已确认需求中推导页面清单、页面内容、页面元素、状态反馈、权限可见性、跨页面流程和多端差异，生成可交给 `aisee:change-plan`、UI 设计规范阶段或后续实现规划使用的 UI 内容规格。

## 输入

用户提供以下任意一种输入：
- `aisee:srs` 生成的 SRS 文件路径
- Epic 模式下的模块 SRS 文件路径
- 已确认的功能需求文本，且包含明确 FR / 用户流程 / 角色信息
- 现有系统的 UI 事实来源，例如历史 `aisee/docs/ui-content/`、OpenSpec baseline specs、`source-map.md`、路由、页面代码、截图或产品说明

OpenSpec change 中的 `proposal.md` / `design.md` / `tasks.md` 只能作为补充上下文，不作为生成 UI 内容规格的主输入；如果用户需要为单个 change 补实现级 UI 契约，应转入 change 内 artifact 编写流程。

可选参数：
- `--platform pc|h5|app|wechat|multi` — 指定目标端；未指定且需求未说明时必须询问
- `--scenario new-build|enhancement|inventory|auto` — 指定场景；默认 `auto`
- `--mode standard|epic|auto` — 输出模式，默认 `auto`
- `--split-by module|flow|platform|auto` — Epic 模式拆分策略，默认 `auto`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:ui-content` 产出的是 **UI 内容规格**，不是视觉设计规范，也不是实现方案。

必须覆盖：
- 场景模式：新建系统 / 现有系统二开 / 现有 UI 盘点
- 二开场景的受影响 UI 范围：Existing、Changed、New、Deprecated、Unknown
- 页面清单、页面目标、页面类型、入口与完成后去向
- 页面内容区块、字段、列表列、筛选项、操作入口
- 页面状态：加载、空、无结果、错误、无权限、提交中、成功、失败、部分成功
- 表单规则：必填、默认值、校验、联动、只读、禁用、草稿、重复提交、未保存离开
- 危险操作：删除、撤销、批量操作、状态变更、支付、提交审批等的确认与恢复
- 角色与权限可见性：入口、字段、按钮、数据范围、操作权限
- 页面内流程语境：入口来源、用户在本页面完成什么、完成后去向、返回规则、参与流程
- 跨页面流程汇总：起点、操作、目标页、携带信息、返回规则、中断恢复
- 平台范围与差异：PC Web、H5、App、微信小程序
- 文案占位：页面标题、按钮文案、空状态、错误提示、确认弹窗
- FR 到页面、元素、操作的追踪矩阵

禁止输出：
- 颜色、字体、间距、栅格、布局稿、视觉风格
- 组件库选择、具体组件实现、前端框架方案
- API endpoint、数据库字段、服务拆分、代码文件结构
- 未被 SRS / 用户确认的新增业务需求

如果输入缺少支撑某个页面或交互的需求依据，把它写入 Open Questions，不要自行补需求。现有系统二开时，不要重写未变化的既有页面内容；只引用事实来源并展开本次新增、变更、下线或未知部分。

---

## ID 规则

`aisee:ui-content` 负责 UI 内容侧上游 ID：

- 复用 SRS 中已有的 `FR / NFR / RULE`，不得重新分配。
- 负责新增或确认 `PAGE / FLOW / STATE`。
- 可以继续沿用既有系统或历史 UI 文档中的稳定 `PAGE / FLOW / STATE`。
- 不负责 `API / DATA / TASK / TEST`，这些由 change artifacts 承接。

正式写法只使用文档内 local ID，例如 `PAGE-001`、`FLOW-001`、`STATE-001`。跨文档引用由后续 `source-map.md`、`aisee get`、`aisee trace` 或 alias anchor 处理。不要再要求 `aisee id reserve/activate/check` 或 full ID lifecycle。

如果当前轮次还不能确定最终编号，可以使用 `PAGE-NEW-001`、`FLOW-NEW-001`、`STATE-NEW-001`，并显式标注 `[ID-FINALIZATION-REQUIRED]`。不要把占位符当正式稳定 ID。

---

## Phase 0 — 读取来源上下文

先读取用户提供的输入文件或文本。若用户给的是文件路径，读取文件内容；若路径不存在，停止并说明无法继续。

同时静默收集项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -120
ls aisee/docs/ui-content/ 2>/dev/null | head -20
rg --files openspec/specs 2>/dev/null | head -40
rg --files openspec/changes 2>/dev/null | rg '(^|/)source-map\.md$' | head -20
cat aisee/registry/sources.json 2>/dev/null || true
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，并只查 UI 内容规格需要的文件类型。

使用这些信息识别已有平台、产品类型、命名习惯、现有 UI 事实来源和文档路径。不要因为缺少 OpenSpec 上下文而停止；只要输入需求足够明确即可继续。

---

## Workflow

先按 Phase 0 读取来源上下文，再按需读取 [workflow.md](references/workflow.md) 执行输入门禁、平台识别、场景识别、对象识别、输出模式选择、生成和保存。

CHECKPOINT: 生成 UI 内容规格前必须确认目标平台、场景模式、输出模式、主要页面/流程范围和来源依据。平台或页面范围不明确时先问；用户要求继续时，把未确认项写入 Open Questions，不要自行补页面或交互。

Reference loading：

- 需要追问时读取 `references/question-bank.md`。
- 生成前读取 `assets/ui-content-template.md` 入口索引。
- 每次生成 UI 内容规格都读取 `references/writing-rules.md`。
- 只读取当前场景和输出模式需要的模板，不要一次性加载所有模板。

---

## Guardrails

- 不要在 UI 内容规格中新增业务需求；只映射和展开已确认需求。
- 不要在二开场景重写未变化的既有 UI；引用来源并只写本次差异。
- 不要写视觉设计规范、布局稿、组件库或实现方案。
- 不要默认目标端；平台不明确时先问。
- 不要生成超长单文件；触发 Epic 条件时必须拆分。
- 每个 FR 必须能追踪到页面、元素、操作或“非页面型系统行为”。无法追踪时写入 Open Questions。
- 每个页面都必须有入口、目标、完成后去向、返回规则、参与流程、状态反馈和关联 FR。
- 危险操作必须包含确认、取消、成功、失败和是否可恢复。
- 多角色页面必须写权限可见性差异。
- 多端页面必须写平台差异；无差异时写“无差异”。
- Open Questions 不得为空白占位；没有问题时写“无”。
- 正式 PAGE / FLOW / STATE 只使用文档内 local ID；工具不可用时使用 `TYPE-NEW-001` 并标注 `[ID-FINALIZATION-REQUIRED]`。

---

## 与 OpenSpec 工作流集成

```text
aisee:srs                         ← 需求发现 → SRS
  ├─ aisee:ui-content              ← 页面清单、页面内容、元素、交互、平台差异
  ├─ aisee:design-assets            ← 可选：参考图、StyleSpec、视觉规范
  ├─ aisee:architecture            ← 技术架构事实、决策、项目约束、共享前置
  └─ aisee:change-plan <inputs>          ← 基于 SRS + UI content + architecture 规划 Change 边界
       └─ /opsx:new <change>
            └─ aisee:change-author ← 按 schema 创建 / 补 proposal、specs、contracts、tasks、source-map
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```

大 Epic 推荐：

```text
aisee:srs Epic
  ├─ 按模块运行 aisee:ui-content，生成模块 UI 内容规格
  ├─ 必要时补充 aisee:design-assets 和 aisee:architecture
  └─ aisee:change-plan 按模块规划 change 边界
```
