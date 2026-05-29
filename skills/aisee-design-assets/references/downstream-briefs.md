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

只描述视觉实现输入：

- 视觉基调和设计 token 候选
- 素材路径、用途和裁切/叠加方式
- 背景图、图标、插画、装饰层使用方式
- 响应式视觉规则和 CSS 变量建议
- 与 UI 内容规格的关联

不要写业务逻辑、API endpoint、数据库字段、权限规则、路由设计或未确认页面内容。
