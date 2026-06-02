# PNG/JPG/WebP 转 SVG

## 适用范围

适合：

- 图标
- logo-like mark
- 扁平插画
- 装饰图形
- 简单多色图形
- 线稿或单色图

不适合：

- 复杂照片
- 细碎纹理
- 大量渐变和阴影
- 文字截图
- 完整 UI 页面截图

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

## 转换命令

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
