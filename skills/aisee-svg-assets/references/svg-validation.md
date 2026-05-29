# SVG 优化与校验

## 安全风险

必须检查并移除或阻止：

- `<script>`
- `onload=`, `onclick=`, `onerror=` 等事件属性
- `<foreignObject>`
- 外部 `http://` / `https://` 引用
- `<iframe>`, `<object>`, `<embed>`
- 不明字体或图片外链
- 巨大 base64 嵌入图，除非用户明确允许
- `javascript:` href
- CSS `url(http...)` 或 `@import`

## 结构要求

建议：

- 有 `viewBox`
- 不强依赖固定 `width` / `height`
- 图标可使用 `currentColor`
- 颜色数量适中
- 无无意义 metadata、注释和编辑器垃圾属性
- 语义图形包含 `<title>` 和 `<desc>`；纯装饰图明确 `aria-hidden="true"`
- `id` 和 `class` 命名稳定，不与页面全局样式产生明显冲突

## 校验命令

```bash
python <skill-dir>/scripts/validate_svg.py \
  --input path/to/file.svg \
  --report docs/svg-assets/reports/file.validate.json
```

## 优化命令

```bash
python <skill-dir>/scripts/optimize_svg.py \
  --input path/to/file.svg \
  --out docs/svg-assets/optimized/file.svg \
  --report docs/svg-assets/reports/file.optimize.json
```

`optimize_svg.py` 默认拒绝带已知安全风险的输入；如果用户明确要保留风险内容用于隔离分析，才使用 `--allow-unsafe`，并且不要把结果标记为可 inline。

如果项目已有 `svgo`，也可以使用，但不要强制新增依赖。使用 `svgo` 后仍要运行本 skill 的校验脚本形成统一报告。
