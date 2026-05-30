---
name: aisee:design-spec
description: 在 aisee:change-plan 之前生成项目级或模块级 UI 设计规范。用于根据 SRS、UI Content、Architecture、Design Assets、Logo、参考图、截图、既有组件库、主题和代码事实，沉淀设计原则、组件库采用/扩展/重写策略、Design Tokens、界面模式、交互模式、响应式规则、可访问性规则和 Do/Don't。适用于用户要求“生成设计规范”“设计系统规则”“组件库使用规范”“从参考图/Logo 提取 UI 规范”“基于组件库定设计规范”“DESIGN.md 类文档”“change-plan 前补设计约束”。不要用于生成图片素材、写 UI 内容规格、前端实现、Figma 写入或具体页面像素稿。
---

# aisee:design-spec — UI 设计规范

在 `aisee:change-plan` 前运行，归纳项目级或模块级 UI 设计规范。它和 `aisee:design-assets` 共享设计上下文，但职责不同：`design-assets` 管视觉证据和资产，`design-spec` 管从证据中抽象出的长期设计规则。

## 输入

用户提供以下任意一种输入：
- `aisee:srs` 输出的 SRS 文件
- `aisee:ui-content` 输出的 UI 内容规格
- `aisee:architecture` 输出的技术架构文档
- `docs/design-assets/` 索引、Logo、参考图、截图、StyleSpec 草稿、素材清单或 visual brief
- 既有组件库、设计系统、主题 token、CSS 变量、Figma brief、页面截图或代码事实
- 已确认的设计方向文本

可选参数：
- `--strategy adopt|extend|rewrite|auto` — 设计策略，默认 `auto`
- `--scope project|module|feature|auto` — 规范范围，默认 `auto`
- `--platform pc|h5|app|wechat|desktop|multi|auto` — 目标端，默认 `auto`
- `--format md|md+json|auto` — 输出格式，默认 `auto`
- `--lang zh|en` — 输出语言，默认 `zh`

---

## 输出边界

`aisee:design-spec` 产出的是 **设计规范事实源**，不是参考图集合、UI 内容规格或实现方案。

必须覆盖：
- 设计来源：SRS、UI Content、Architecture、Design Assets、Logo、参考图、截图、组件库、主题或代码事实
- 设计策略：`adopt` / `extend` / `rewrite`
- 设计原则：信息密度、视觉层级、品牌表达、任务效率、平台一致性
- Design Tokens：色彩、字体、间距、圆角、阴影、状态色、动效节奏
- 组件策略：基础组件库、可直接使用组件、需要业务封装组件、禁止魔改组件、组件状态规则
- 界面模式 / Screen Patterns：从 UI Content 页面和流程归纳实际模式，不预设固定页面类型
- 交互模式 / Interaction Patterns：导航、表单、列表/表格、搜索筛选、弹窗/抽屉/浮层、危险操作、状态反馈
- 响应式与多端规则
- 可访问性规则
- Do / Don't
- 追踪关系与 Open Questions

禁止输出：
- SRS 或 UI 内容规格；分别交给 `aisee:srs` 和 `aisee:ui-content`
- 图片、图标、插画、背景或素材生成；交给 `aisee:design-assets`
- 具体页面像素稿、Figma 节点结构、截图式设计稿
- 前端代码、CSS 实现、组件 props、文件结构或开发任务
- API endpoint、数据库字段、服务拆分
- 未经来源支撑的品牌、文案、业务字段或视觉假设

如果缺少设计来源，把缺口写入 Open Questions，不要凭空创造品牌或视觉体系。若用户只想要视觉参考图或素材，转交 `aisee:design-assets`。

---

## Phase 0 — 读取来源上下文

先读取用户提供的输入文件或文本。若路径不存在，停止并说明无法继续。

同时静默收集项目上下文：

```bash
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -160
find docs/design-spec -maxdepth 3 -type f 2>/dev/null | head -80
find docs/design-assets -maxdepth 4 -type f 2>/dev/null | head -120
find docs/ui-content -maxdepth 4 -type f 2>/dev/null | head -80
find docs/architecture -maxdepth 3 -type f 2>/dev/null | head -40
find . -maxdepth 4 \( -iname '*theme*' -o -iname '*token*' -o -iname '*design*system*' -o -iname '*style*spec*' -o -iname '*.module.css' -o -iname 'tailwind.config.*' -o -iname 'package.json' \) 2>/dev/null | head -120
```

使用这些信息识别已有设计资产、组件库、主题、命名习惯和规范路径。不要因为缺少某类上下文而停止；只要输入足够明确即可继续。

---

## Phase 1 — 输入门禁

判断输入是否足够生成设计规范。

可以继续的条件：
- 能判断目标平台或产品形态
- 至少有 UI Content、页面/流程描述、参考图/Logo/截图、组件库事实或明确设计方向中的一种
- 能判断规范是项目级、模块级还是功能级

必须先追问的情况：
- 完全无法判断目标端或产品形态
- 用户要求采用/扩展组件库，但组件库或既有主题不明确
- 用户要求从参考图、Logo 或截图提取规范，但没有提供来源或路径
- 设计策略会明显影响范围，但无法判断是 `adopt`、`extend` 还是 `rewrite`

追问规则：
- 每轮最多问 3 个问题
- 优先问影响设计策略、组件库来源、平台范围和参考来源的问题
- 不超过 3 轮；仍不明确时，把未解决项写入 Open Questions

开始追问前读取 `references/question-bank.md`，从中选择必要问题。

---

## Phase 2 — 设计策略识别

默认 `auto`，按来源判断设计策略：

| 策略 | 条件 | 输出重点 |
|------|------|----------|
| `adopt` | 已有组件库 / 设计系统 / theme，且用户希望遵循现有规范 | 组件库使用规则、token 来源、禁止自定义范围、页面密度和模式约束 |
| `extend` | 使用组件库作为基础，但需要品牌化、业务化或局部重塑 | token 覆盖、业务组件策略、改造边界、典型界面模式 |
| `rewrite` | 新产品、重大 redesign、品牌体系重建，或组件库不适合作为视觉基线 | 设计语言、token、组件原则、界面模式、响应式、a11y、Do/Don't |

不要替用户做不可逆的设计策略决策。证据不足时标注 `[DESIGN-DECISION-REQUIRED]`。

---

## Phase 3 — 设计来源映射

建立来源表，优先沿用 `design-assets` 索引里的 ID；没有 ID 时分配临时 Source ID：

- `DA-xxx`：来自 design-assets 的资产或索引
- `DSRC-xxx`：本次 design-spec 临时来源
- `UIC-xxx` / `PAGE-xxx` / `FLOW-xxx`：来自 UI Content 的页面和流程
- `ARCH-xxx`：来自 Architecture 的技术事实或约束

来源可信度：
- `high`：来自项目文件、组件库配置、theme/token、代码、设计资产索引、用户明确提供的 Logo/截图
- `medium`：来自 SRS、UI Content、Architecture、用户明确说明
- `low`：从参考图风格或上下文推断，必须标注为假设

`design-spec` 可以引用 `design-assets`，但不要复制资产说明、生成参数或素材清单。

---

## Phase 4 — 归纳界面模式

从 UI Content 的页面、流程、角色、平台和信息密度中归纳开放式 Screen Patterns，不使用固定页面类型枚举。

每个 Screen Pattern 必须说明：
- 适用页面 / 流程
- 用户任务
- 信息密度
- 内容组织
- 主操作区与次操作区
- 状态反馈
- 响应式变化
- 禁止事项

如果没有 UI Content，只能基于已确认页面/流程或参考材料生成初版，并把缺口写入 Open Questions。

---

## Phase 5 — 生成设计规范

读取 `assets/design-spec-template.md` 和 `references/writing-rules.md`，生成文档。

默认保存：

```bash
mkdir -p docs/design-spec
```

文件：

`docs/design-spec/<YYYY-MM-DD>-<slug>.md`

可选文件：
- `docs/design-spec/<YYYY-MM-DD>-<slug>.tokens.json`
- `docs/design-spec/<YYYY-MM-DD>-<slug>.component-policy.md`

只有用户明确需要机器可读 token，或项目已有 token 消费链路时，才生成 JSON。大项目组件策略过长时，才拆 `component-policy.md`。

---

## 完成输出

完成后输出：

> 设计规范已生成：`docs/design-spec/{filename}.md`
>
> 设计策略：adopt / extend / rewrite
> 覆盖：{N} 个来源、{P} 个界面模式、{C} 类组件策略、{Q} 个待确认事项。
>
> 下一步：将本文档与 SRS、UI Content、Architecture 以及必要的 Design Assets 一起交给 `aisee:change-plan`。

如果存在缺口：

> 存在设计决策缺口：{tags}
> 这些缺口会影响视觉一致性或组件策略，但本技能不会生成图片或实现代码。

---

## Guardrails

- 不要生成图片、素材或参考图；交给 `aisee:design-assets`。
- 不要把 `design-assets` 的索引内容复制成规范；只引用来源并归纳设计规则。
- 不要替代 UI Content，不要重新定义页面字段、页面操作或业务流程。
- 不要写具体页面像素稿、Figma 节点结构或前端实现代码。
- 不要预设固定页面模式；Screen Patterns 必须来自当前项目上下文。
- 不要把组件库采用策略写成技术选型；技术事实不足时标注 `[ARCHITECTURE-CONTEXT-MISSING]`。
- 不要从参考图照抄第三方品牌、Logo、文案或专有视觉元素。
- 所有关键设计规则都应能追踪到来源、用户决策或明确假设。

---

## 与 OpenSpec 工作流集成

```text
aisee:srs
  ├─ aisee:ui-content
  ├─ aisee:design-assets      ← 可选：Logo、参考图、截图、素材、visual brief
  ├─ aisee:design-spec        ← 本技能：设计规范事实源
  ├─ aisee:architecture
  └─ aisee:change-plan        ← 基于 SRS + UI content + design-spec + architecture 拆 change
       └─ /opsx:new <change>
            └─ aisee:change-author
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```

`design-assets` 与 `design-spec` 不要求固定先后：有视觉证据时先登记/引用资产再沉淀规范；已有规范时也可以反向指导资产生成。
