---
name: aisee:design-spec
description: 在 aisee:change-plan 之前生成项目级或模块级 UI 设计规范。用于根据 SRS、UI Content、Architecture、Design Assets、Logo、参考图、截图、既有组件库、主题和代码事实，沉淀设计原则、组件库采用/扩展/重写策略、Design Tokens、界面模式、交互模式、响应式规则、可访问性规则和 Do/Don't。适用于用户要求“生成设计规范”“设计系统规则”“组件库使用规范”“从参考图/Logo 提取 UI 规范”“基于组件库定设计规范”“DESIGN.md 类文档”“change-plan 前补设计约束”。不要用于生成图片素材、写 UI 内容规格、前端实现、Figma 写入或具体页面像素稿。
---

# aisee:design-spec — UI 设计规范

在 `aisee:change-plan` 前运行，归纳项目级或模块级 UI 设计规范。它和 `aisee:design-assets` 共享设计上下文，但职责不同：`design-assets` 管视觉证据和资产，`design-spec` 管从证据中抽象出的长期设计规则。

生成或改写 planning doc 时，frontmatter 字段合同统一遵循 `plugins/aisee-plugin/references/planning-doc-frontmatter.md`；它只服务索引和追踪，不替代 OpenSpec 事实源。

## 输入

用户提供以下任意一种输入：
- `aisee:srs` 输出的 SRS 文件
- `aisee:ui-content` 输出的 UI 内容规格
- `aisee:architecture` 输出的技术架构文档
- `aisee/docs/design-assets/` 索引、Logo、参考图、截图、StyleSpec 草稿、素材清单或 visual brief
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

`aisee:design-spec` 产出的是 **project / module 级 design spec 或 delta planning doc**，不是参考图集合、长期规范事实源、UI 内容规格或实现方案。

必须覆盖：
- 设计来源：SRS、UI Content、Architecture、Design Assets、Logo、参考图、截图、组件库、主题或代码事实
- 设计策略：`adopt` / `extend` / `rewrite`
- Design Read：产品类型、目标受众、平台、设计气质和应避免的默认审美
- 设计参数：信息密度、品牌表达、动效强度、组件定制程度、内容密度
- 设计原则：信息密度、视觉层级、品牌表达、任务效率、平台一致性
- Design Tokens：色彩、字体、间距、圆角、阴影、状态色、动效节奏
- 组件策略：基础组件库、可直接使用组件、需要业务封装组件、禁止魔改组件、组件状态规则
- 界面模式 / Screen Patterns：从 UI Content 页面和流程归纳实际模式，不预设固定页面类型
- 交互模式 / Interaction Patterns：导航、表单、列表/表格、搜索筛选、弹窗/抽屉/浮层、危险操作、状态反馈
- 响应式与多端规则
- 可访问性规则
- Do / Don't
- 视觉验收规则：截图比对、移动端溢出、对比度、状态完整性和参考图/brief 匹配点
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
rg --files aisee/docs/design-spec 2>/dev/null | head -80
rg --files aisee/docs/design-assets 2>/dev/null | head -120
rg --files aisee/docs/ui-content 2>/dev/null | head -80
rg --files aisee/docs/architecture 2>/dev/null | head -40
rg --files | rg '(theme|token|design.*system|style.*spec|\.module\.css$|(^|/)tailwind\.config\.|(^|/)package\.json$)' | head -120
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，并只查设计规范需要的文件类型。

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

读取 `references/design-rules.md` 中的设计策略规则，识别 `adopt / extend / rewrite`。不要替用户做不可逆的设计策略决策；证据不足时标注 `[DESIGN-DECISION-REQUIRED]`。

CHECKPOINT: 在生成设计规范前，必须确认或显式标注设计策略 `adopt / extend / rewrite`、规范范围、目标平台、设计来源和关键假设。策略会影响组件库采用、token、视觉语言或重写范围时，先暂停让用户确认；用户要求继续但证据不足时，只能写 `[DESIGN-DECISION-REQUIRED]`，不得把推断写成既定规范。

---

## Phase 3 — Design Read 与设计参数

读取 `references/design-rules.md` 中的 Design Read 和设计参数规则。Design Read 必须来自来源或明确假设；设计参数使用 1-5 档，并写明理由和来源。

---

## Phase 4 — 设计来源映射

读取 `references/design-rules.md` 中的来源映射规则。优先沿用 `design-assets` 索引 ID；没有 ID 时使用临时 Source ID。引用 `design-assets` 时只引用来源并归纳设计规则，不复制资产说明、生成参数或素材清单。

---

## Phase 5 — 归纳界面模式

读取 `references/design-rules.md` 中的 Screen Patterns 规则。从 UI Content 的页面、流程、角色、平台和信息密度归纳开放式模式，不使用固定页面类型枚举。没有 UI Content 时，只能基于已确认页面/流程或参考材料生成初版，并把缺口写入 Open Questions。

---

## Phase 6 — 生成设计规范

读取 `assets/design-spec-template.md` 入口索引、`references/design-rules.md` 和 `references/writing-rules.md`，再按范围选择模板：

- 功能级或局部约束：读取 `assets/design-spec-template-light.md`。
- 项目级、模块级、跨页面或多端规范：读取 `assets/design-spec-template-standard.md`。
- 需要 token、组件库采用/扩展、状态规则时，再读取 `assets/design-spec-template-tokens.md`，并用详细章节替换标准模板中的 token / 组件摘要。
- UI Content 页面/流程复杂，需要 Screen Patterns / Interaction Patterns 时，再读取 `assets/design-spec-template-patterns.md`，并用详细章节替换标准模板中的模式摘要。

默认保存：

```bash
mkdir -p aisee/docs/design-spec
```

文件：

`aisee/docs/design-spec/<YYYY-MM-DD>-<slug>.md`

可选文件：
- `aisee/docs/design-spec/<YYYY-MM-DD>-<slug>.tokens.json`
- `aisee/docs/design-spec/<YYYY-MM-DD>-<slug>.component-policy.md`

只有用户明确需要机器可读 token，或项目已有 token 消费链路时，才生成 JSON。大项目组件策略过长时，才拆 `component-policy.md`。

---

## 完成输出

完成后输出：

> 设计规范已生成：`aisee/docs/design-spec/{filename}.md`
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
  ├─ aisee:design-spec        ← 本技能：design spec / delta planning doc
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
