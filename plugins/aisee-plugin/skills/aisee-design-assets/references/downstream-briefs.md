# 下游交付 Brief

`aisee:design-assets` 只提供视觉输入，不替代 UI 内容规格、Figma MCP 绘制或前端开发。按需生成：

- `figma-brief.md` / `figma-brief.json`
- `dev-visual-brief.md` / `dev-visual-brief.json`

## Figma Brief

应包含：

- 来源 UI 内容规格路径，可选
- 参考图、StyleSpec、素材路径和用途
- 画布尺寸、目标端、页面 / Frame 清单
- 页面区块、视觉层级和设计 token 候选
- Figma 资源库复用策略
- 不应绘制或不应新建的内容

不要补业务需求、接口、权限或未确认页面流程。缺少页面内容依据时，要求先运行 `aisee:ui-content` 或把缺口写入 Open Questions。

### Figma 资源库复用

使用 Figma MCP 绘制高保真稿时，先检索并复用目标 Figma 文件、Team Library 或 Design System 中已有的组件、变量、样式和 token。资源库缺失、组件不匹配或用户明确要求时，才创建新组件或自定义图层。

绘制前重点检索：

- 颜色、字体、间距变量
- 按钮、表单、卡片、导航、Tab、弹窗、Toast、Empty State、图标组件
- 既有页面布局模式

复用规则：

- 现有组件满足约 80% 以上需求时，优先复用实例并用 variant、props、override 调整。
- 不为贴合参考图而重造已有组件。
- 不把位图参考图机械描摹成不可维护图层。
- 新建组件必须说明原因。

## Dev Visual Brief

只描述视觉实现输入。它可以被 `ui-contract.md`、`implementation-bridge` 或 `ce-work` 引用，但不是代码方案，也不是 UI 内容规格。

- 视觉基调和设计 token 候选
- 来源参考图 / section / 状态清单，以及每张图的用途
- 从参考图提取的布局节奏、组件形态、圆角/阴影/边框/留白规律
- 素材路径、用途和裁切/叠加方式
- 背景图、图标、插画、装饰层使用方式
- 图标实现建议：优先复用项目已使用组件库 / 图标包；缺少合适图标时使用 `better-icons` / Iconify 检索，并记录完整 `prefix:name`
- 响应式视觉规则和 CSS 变量建议
- 视觉验收建议：实现后需要截图比对的页面、section、状态和风险点
- 与 UI 内容规格的关联

不要写业务逻辑、API endpoint、数据库字段、权限规则、路由设计或未确认页面内容。

### 前端图标实现规则

实现阶段处理图标时：

1. 先检查项目已使用的组件库、图标包、图标组件文件和设计系统约定。
2. 已有组件库提供合适图标时，直接复用并记录组件名或图标 ID。
3. 现有库没有合适语义或风格时，使用 `better-icons` / Iconify 搜索候选，保持同一界面内图标风格一致。
4. 优先使用已全局安装的 `better-icons`，避免每次 `npx` 冷启动；不可用时不要退回手写 SVG，按项目包管理器安装，或用 `npx -y better-icons ...` / `bunx better-icons ...` 执行一次性检索。
5. 安装或一次性执行命令后，在实现 evidence 中记录命令、图标库、图标 ID、尺寸和颜色策略。

如果来源是参考图或截图，brief 必须标注 extraction confidence：

- `high`：文字、层级、布局、组件形态和素材都清晰。
- `medium`：整体方向可用，但部分文字、间距或组件细节需要人工确认。
- `low`：只能作为视觉氛围，不应直接指导实现；建议重新生成 section/detail 参考图。
