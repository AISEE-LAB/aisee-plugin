# PNG/JPG/WebP 转 SVG 或按参考图重绘 SVG

## 适用范围

适合：

- 图标
- logo-like mark
- 扁平插画
- 装饰图形
- 简单多色图形
- 线稿或单色图
- 需要把位图作为参考，准确重绘成可维护 SVG 的简单图形

不适合：

- 复杂照片
- 细碎纹理
- 大量渐变和阴影
- 文字截图
- 完整 UI 页面截图
- 对象分离、去背景、mask、背景修补

## 先识别，再选择 trace 或 redraw

不要只因为用户给了 PNG/JPG/WebP 就直接运行 VTracer。先形成一个简短重建 brief：

- 原图内容：主体是什么，图形表达什么语义。
- 结构分解：外轮廓、内部形状、装饰、文字、阴影、背景分别是什么。
- 几何关系：viewBox、对齐、比例、留白、圆角、描边、对称关系。
- 色彩和透明：主色、辅色、渐变/阴影是否必须保留，背景是否透明。
- 可还原性：哪些部分能准确 SVG 化，哪些纹理、模糊或文字需要简化或人工复核。

选择方式：

- `trace`：原图是扁平、边界清晰、颜色较少的图标、logo-like mark、线稿或简单多色图形。
- `redraw`：用户要求准确、可维护、可编辑，或原图结构清楚但自动 trace 会产生大量不可读 path。
- `handoff-to-image-object`：需要先抠出主体、去背景、mask 或局部修图。
- `handoff-to-design-assets`：用户要的是新位图素材、参考图、插画、banner 或视觉变体。

## 依赖策略

只在需要位图矢量化时安装或检查依赖。优先使用 Python 包：

```bash
pip install vtracer
```

备用 CLI：

```bash
cargo install vtracer
```

运行时检测：

```bash
python -c "import vtracer; print('python-vtracer=present')" 2>/dev/null || true
command -v vtracer >/dev/null && echo "vtracer-cli=present" || true
```

CHECKPOINT: 如果本机没有 VTracer，不要静默安装。先说明需要安装 `vtracer` 的原因、安装方式和影响，等待用户确认后再执行 `pip install vtracer` 或 `cargo install vtracer`。

如果用户真正要的是对象抠图、去背景、mask 或修图，不进入 trace；应转 `aisee:image-object`。如果用户要基于图片生成新的位图素材或参考图，应转 `aisee:design-assets`。

## trace 转换命令

```bash
python <skill-dir>/scripts/trace_bitmap.py \
  --input input.png \
  --out aisee/docs/svg-assets/traced/input.svg \
  --preset icon-color \
  --report aisee/docs/svg-assets/reports/input.trace.json
```

常用 preset：

- `icon-color`：多色扁平图标
- `icon-bw`：单色图标、线稿
- `logo`：logo-like mark
- `illustration`：简单插画

## 转换后必须校验

```bash
python <skill-dir>/scripts/validate_svg.py \
  --input aisee/docs/svg-assets/traced/input.svg \
  --report aisee/docs/svg-assets/reports/input.validate.json
```

必要时优化：

```bash
python <skill-dir>/scripts/optimize_svg.py \
  --input aisee/docs/svg-assets/traced/input.svg \
  --out aisee/docs/svg-assets/optimized/input.svg \
  --report aisee/docs/svg-assets/reports/input.optimize.json
```

## 结果判断

- `python-vtracer` 和 `vtracer-cli` 都是可接受路径，交付时说明实际使用了哪个。
- 复杂照片、纹理和截图可能生成体积很大的 SVG；这种结果只能作为草稿或进一步设计输入。
- 如果输出缺少 `viewBox`、含外链、含 base64 或 XML 不合法，不要进入索引的 `passed` 状态。
- 对含文字的位图，不承诺转成可编辑文字；必要时建议手工重建文字层。
- 对疑似商标、付费素材、个人头像或敏感图片，只能在用户确认有权处理后继续；不要在报告中记录敏感来源细节。

## redraw 分步骤绘制

当目标是准确重绘，而不是机械矢量化时：

1. 根据重建 brief 确定 `viewBox`、画布比例和安全留白。
2. 先绘制主轮廓和大色块，确认比例与位置。
3. 再绘制内部结构、装饰、阴影或高光，避免一开始生成不可读长 path。
4. 最后处理文字：短文字可用 SVG text 或 path，但必须说明字体替代；复杂文字建议作为可编辑前端/设计工具文本另行处理。
5. 运行 `validate_svg.py`，并在报告或索引中记录 `reconstruction_brief` 与 `accuracy_check`。

准确性检查至少覆盖：

- 语义是否一致：图形是否仍表达原图对象或动作。
- 比例是否一致：主体、留白、圆角、描边和内部细节是否接近原图。
- 色彩是否一致：主色、辅色、明暗关系是否接近原图。
- 小尺寸是否可读：图标类资产在 16px / 24px 仍可识别。
- 可维护性是否合格：SVG 结构能看出图层意图，没有无意义的大量碎片 path。
