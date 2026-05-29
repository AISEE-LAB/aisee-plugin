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

- 必须包含 `viewBox`
- 图形用途明确：`icon` 默认 24x24，装饰图和插画可使用 64、128、256 或自定义 viewBox
- 优先使用相对简洁的 `path`、`circle`、`rect`、`line`、`polyline`
- 图标默认使用 `currentColor`，多色图标使用少量明确颜色
- 不使用 `<script>`、事件属性、外链资源、`foreignObject`
- 不嵌入 base64 位图，除非用户明确要求
- 文件保存到 `docs/svg-assets/generated/`
- 文件名使用 kebab-case，例如 `settings-gear.svg`、`empty-state-search.svg`

## 质量门槛

直接生成的 SVG 在交付前必须自检：

- 小尺寸可识别：图标在 16px / 24px 不依赖细碎细节
- 可复用：单色图标优先 `currentColor`，不要硬编码业务无关颜色
- 可访问：有语义展示时包含 `<title>` 和 `<desc>`；纯装饰时使用 `aria-hidden="true"`
- 可维护：避免超长不可读 path，除非来自矢量化或已有工具输出
- 可安全内联：没有脚本、事件属性、外链和 `foreignObject`

## 模板

读取 `assets/svg-icon-template.svg` 作为起点。

## 交付前校验

```bash
python <skill-dir>/scripts/validate_svg.py \
  --input docs/svg-assets/generated/icon.svg \
  --report docs/svg-assets/reports/icon.validate.json
```

校验有 warning 时可以交付，但要说明影响；有 error 或 risk 时不要标记为可直接 inline 使用。
