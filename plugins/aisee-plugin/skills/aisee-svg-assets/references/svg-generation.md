# SVG 直接生成

## 适用范围

直接生成 SVG 适合：

- 单色图标
- 线性图标
- filled icon
- duotone icon
- 几何装饰
- 简单插画
- 状态图
- logo-like mark 草案

不适合：

- 高复杂照片
- 精确品牌 Logo 复刻
- 大量文本排版
- 完整 UI 页面

## 生成原则

- 常见 UI 图标优先使用成熟图标库；只有库中没有合适语义、需要品牌/业务专属表达，或用户明确要求自定义 SVG 时才直接绘制。
- 如果使用图标库，交付和索引中记录库名、完整图标 ID、尺寸、线宽、颜色和适用状态，不需要重写 SVG。
- 如果环境中已有全局 `better-icons` CLI 或 MCP，可用它从 Iconify 生态搜索和获取候选图标；全局命令优先于每次 `npx` 调用。实现阶段缺少该工具时可按项目包管理器安装或一次性执行，并记录命令；规划阶段不可用时按项目依赖和常见库人工映射。
- 必须包含 `viewBox`
- 图形用途明确：`icon` 默认 24x24，装饰图和插画可使用 64、128、256 或自定义 viewBox
- 优先使用相对简洁的 `path`、`circle`、`rect`、`line`、`polyline`
- 图标默认使用 `currentColor`，多色图标使用少量明确颜色
- 不使用 `<script>`、事件属性、外链资源、`foreignObject`
- 不嵌入 base64 位图，除非用户明确要求
- 文件保存到 `aisee/docs/svg-assets/generated/`
- 文件名使用 kebab-case，例如 `settings-gear.svg`、`empty-state-search.svg`

## 质量门槛

直接生成的 SVG 在交付前必须自检：

- 小尺寸可识别：图标在 16px / 24px 不依赖细碎细节
- 可复用：单色图标优先 `currentColor`，不要硬编码业务无关颜色
- 可访问：有语义展示时包含 `<title>` 和 `<desc>`；纯装饰时使用 `aria-hidden="true"`
- 可维护：避免超长不可读 path，除非来自矢量化或已有工具输出
- 可安全内联：没有脚本、事件属性、外链和 `foreignObject`

## 自定义绘制步骤

直接绘制 SVG 时先写简短 brief，再动手：

1. 识别语义：这个图形代表什么对象、动作、状态或品牌含义。
2. 确定结构：画布、主轮廓、内部细节、装饰层、颜色层和状态变体。
3. 分步绘制：先主形，再细节，再颜色和可访问描述。
4. 对照需求复核：语义、比例、尺寸、颜色、可读性和可维护性。

如果输入来自参考图或位图，先读 `references/png-to-svg.md`，不要跳过识别和分解。

## 模板

读取 `assets/svg-icon-template.svg` 作为起点。

## 交付前校验

```bash
python <skill-dir>/scripts/validate_svg.py \
  --input aisee/docs/svg-assets/generated/icon.svg \
  --report aisee/docs/svg-assets/reports/icon.validate.json
```

校验有 warning 时可以交付，但要说明影响；有 error 或 risk 时不要标记为可直接 inline 使用。
