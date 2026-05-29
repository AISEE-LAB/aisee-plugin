---
name: aisee:ui-content
description: 根据 SRS、模块需求文档或已确认的功能需求生成 UI 内容规格。用于回答“要开发哪些页面”“页面上有什么内容”“页面元素和操作是什么”“跨页面交互流程如何走”“PC/App/小程序/H5 有哪些内容差异”。当用户要求把 SRS 转成页面清单、前端页面内容、界面内容规格、UI content spec、页面交互说明、页面元素清单时使用。不要用于视觉设计、配色、布局稿、组件库选型或前端实现方案；这些属于后续设计或开发规划。
---

# aisee:ui-content — UI 内容规格

从已确认需求中推导页面清单、页面内容、页面元素、状态反馈、权限可见性、跨页面流程和多端差异，生成可交给前端、UI 设计或 `/ce:plan` 使用的 UI 内容规格。

## 输入

用户提供以下任意一种输入：
- `aisee:srs` 生成的 SRS 文件路径
- Epic 模式下的模块 SRS 文件路径
- 已确认的功能需求文本，且包含明确 FR / 用户流程 / 角色信息
- OpenSpec change 中的 `proposal.md` / `design.md` / `tasks.md` 路径

可选参数：
- `--platform pc|h5|app|wechat|multi` — 指定目标端；未指定且需求未说明时必须询问
- `--mode standard|epic|auto` — 输出模式，默认 `auto`
- `--split-by module|flow|platform|auto` — Epic 模式拆分策略，默认 `auto`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:ui-content` 产出的是 **UI 内容规格**，不是视觉设计规范，也不是实现方案。

必须覆盖：
- 页面清单、页面目标、页面类型、入口与完成后去向
- 页面内容区块、字段、列表列、筛选项、操作入口
- 页面状态：加载、空、无结果、错误、无权限、提交中、成功、失败、部分成功
- 表单规则：必填、默认值、校验、联动、只读、禁用、草稿、重复提交、未保存离开
- 危险操作：删除、撤销、批量操作、状态变更、支付、提交审批等的确认与恢复
- 角色与权限可见性：入口、字段、按钮、数据范围、操作权限
- 跨页面流程：起点、操作、目标页、携带信息、返回规则、中断恢复
- 平台范围与差异：PC Web、H5、App、微信小程序
- 文案占位：页面标题、按钮文案、空状态、错误提示、确认弹窗
- FR 到页面、元素、操作的追踪矩阵

禁止输出：
- 颜色、字体、间距、栅格、布局稿、视觉风格
- 组件库选择、具体组件实现、前端框架方案
- API endpoint、数据库字段、服务拆分、代码文件结构
- 未被 SRS / 用户确认的新增业务需求

如果输入缺少支撑某个页面或交互的需求依据，把它写入 Open Questions，不要自行补需求。

---

## Phase 0 — 读取来源上下文

先读取用户提供的输入文件或文本。若用户给的是文件路径，读取文件内容；若路径不存在，停止并说明无法继续。

同时静默收集项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat CLAUDE.md 2>/dev/null | head -120
cat AGENTS.md 2>/dev/null | head -120
ls docs/ui-content/ 2>/dev/null | head -20
```

使用这些信息识别已有平台、产品类型、命名习惯和文档路径。不要因为缺少 OpenSpec 上下文而停止；只要输入需求足够明确即可继续。

---

## Phase 1 — 输入门禁

判断输入是否足够生成 UI 内容规格。

可以继续的条件：
- 至少存在明确的用户角色或使用者
- 至少存在一个主流程或 FR
- 能判断功能是否需要用户可见页面、弹窗、通知、导入导出结果页等 UI 承载

必须先追问的情况：
- 没有目标平台，且无法从上下文判断
- 只有模糊想法，没有 SRS / FR / 主流程
- 页面内容会因角色、平台或业务范围不同而产生明显分歧
- 用户要求多端，但没有说明覆盖哪些端

追问规则：
- 每轮最多问 3 个问题
- 优先问影响页面清单和平台范围的问题
- 不追问视觉偏好
- 不超过 3 轮；仍不明确时，把未解决项写入 Open Questions

开始追问前读取 `references/question-bank.md`，从中选择必要问题。

---

## Phase 2 — 平台范围识别

识别目标端：
- `PC Web / Admin`
- `Mobile Web / H5`
- `Native App`
- `微信小程序`
- `多端共用`

如果 SRS 未说明目标端，必须询问用户；不要默认 PC 或移动端。

如果是多端：
1. 先生成跨端通用内容规格
2. 再生成平台差异补充
3. 只有平台差异足够复杂时，才拆出独立 `platform-diff` 文档

平台差异只记录内容、入口、操作、授权、反馈和能力限制，不写视觉布局。

---

## Phase 3 — 页面与交互对象识别

从需求中识别所有用户可见承载物：
- 页面：列表页、详情页、表单页、流程页、设置页、结果页、授权页、通知落地页
- 非完整页面：弹窗、抽屉、Bottom Sheet、Action Sheet、Popover、Toast、确认框
- 全局入口：导航、搜索、消息中心、待办中心、个人中心、设置、帮助、权限申请
- 非页面型交互结果：异步任务结果、导入导出结果、后台同步结果、审批待办、通知跳转

为每个对象分配稳定 ID：
- 页面：`PAGE-001`
- 流程：`FLOW-001`
- 弹窗/浮层：`MODAL-001`
- 全局入口：`NAV-001`

页面划分原则：
- 优先按用户任务和业务模块划分
- 不把每个弹窗机械拆成页面
- 不为未确认需求创建页面
- 同一业务流程不要拆散到多个无关文档

---

## Phase 4 — 输出模式选择

默认 `auto`，根据体量自动选择。

### 标准模式

满足以下条件时使用单文件：
- 页面详情数量 ≤ 8
- 模块数 ≤ 2
- 跨页面流程 ≤ 5 条
- 覆盖平台 ≤ 2 个
- 没有复杂权限矩阵或大量表单

### Epic 模式

满足任意条件时使用索引文档 + 多文档：
- 页面详情数量 > 8
- 模块数 ≥ 3
- 覆盖平台 ≥ 3 个
- 跨页面流程 > 5 条
- 存在复杂权限矩阵、复杂审批流、大量表单、批量导入导出、多端显著差异

Epic 拆分优先级：
1. 按业务模块拆
2. 跨模块流程单独拆为 `shared-flows`
3. 多端差异复杂时单独拆为 `platform-diff`
4. 不按页数机械切割，除非单个模块超过 8 个页面详情

硬性限制：
- 单个 UI 内容文档不超过 8 个页面详情
- 单个页面详情控制在 2 屏 Markdown 内
- 每份模块文档必须可独立交给前端或设计阅读
- 索引文档不写完整页面详情，只写总览、索引和追踪总表

---

## Phase 5 — 生成 UI 内容规格

读取 `assets/ui-content-template.md`，按输出模式选择模板。

### 标准模式

生成单文件，包含：
- 来源与范围
- 平台范围
- 信息架构
- 页面清单
- 用户路径
- 页面内容规格
- 全局状态与反馈
- 权限可见性
- 跨端差异
- 文案清单
- FR 追踪矩阵
- Open Questions

### Epic 模式

按顺序生成：
1. `00-index.md` — 来源、平台、模块索引、页面总览、流程总览、FR 追踪总表、全局 Open Questions
2. `01-<module>.md` — 模块页面清单、模块流程、页面内容规格、权限、状态、模块 FR 覆盖
3. `shared-flows.md` — 可选，仅当存在跨模块复杂流程
4. `platform-diff.md` — 可选，仅当多端差异复杂

每份文档生成后暂停并告知用户进度，等待确认继续。

---

## Phase 6 — 保存文档

标准模式：

```bash
mkdir -p docs/ui-content
```

文件名：

`docs/ui-content/<YYYY-MM-DD>-<slug>.md`

Epic 模式：

```bash
mkdir -p docs/ui-content/<YYYY-MM-DD>-<slug>
```

目录结构：

```text
docs/ui-content/<YYYY-MM-DD>-<slug>/
  ├── 00-index.md
  ├── 01-<module-a>.md
  ├── 02-<module-b>.md
  ├── shared-flows.md       # 可选
  └── platform-diff.md      # 可选
```

---

## 完成输出

标准模式完成后：

> UI 内容规格已生成：`docs/ui-content/{filename}.md`
>
> 覆盖 {N} 个页面、{M} 条流程、{K} 个平台差异、{Q} 个待确认事项。
>
> 下一步建议：将本文档与对应 SRS 一起交给 `/ce:plan` 或前端设计/实现流程。

Epic 模式完成后：

> UI 内容规格已生成（Epic 模式，共 {N} 份文档）：
>
> - 索引：`docs/ui-content/{slug}/00-index.md`
> - 模块文档：{list}
> - 跨模块流程：{path or "无"}
> - 平台差异：{path or "无"}
>
> 下一步建议：按模块将 UI 内容规格与对应 SRS 一起交给 `/ce:plan` 或前端设计/实现流程。

---

## Guardrails

- 不要在 UI 内容规格中新增业务需求；只映射和展开已确认需求。
- 不要写视觉设计规范、布局稿、组件库或实现方案。
- 不要默认目标端；平台不明确时先问。
- 不要生成超长单文件；触发 Epic 条件时必须拆分。
- 每个 FR 必须能追踪到页面、元素、操作或“非页面型系统行为”。无法追踪时写入 Open Questions。
- 每个页面都必须有入口、目标、完成后去向、状态反馈和关联 FR。
- 危险操作必须包含确认、取消、成功、失败和是否可恢复。
- 多角色页面必须写权限可见性差异。
- 多端页面必须写平台差异；无差异时写“无差异”。
- Open Questions 不得为空白占位；没有问题时写“无”。

---

## 与 OpenSpec 工作流集成

```text
aisee:srs                         ← 需求发现 → SRS
  ├─ aisee:ui-content              ← 页面清单、页面内容、元素、交互、平台差异
  ├─ aisee:tech-context            ← 技术事实、项目约束、共享前置
  └─ aisee:change-plan <inputs>          ← 基于 SRS + UI content + tech-context 规划 Change 边界
       └─ /opsx:new <change>
            └─ /opsx:continue      ← 创建 / 补 proposal.md
            └─ aisee:change-design ← 仅当 schema 包含 design.md；读取 SRS + UI 内容规格 + tech-context
            └─ /opsx:continue      ← 创建 / 补 specs 与 tasks
            └─ /opsx:apply
            └─ /ce:review
            └─ /opsx:archive
```

大 Epic 推荐：

```text
aisee:srs Epic
  └─ aisee:change-plan 按模块规划 change 边界
       └─ 针对每个模块运行 aisee:ui-content
```
