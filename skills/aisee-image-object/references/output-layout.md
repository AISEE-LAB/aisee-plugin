# 输出目录与命名规范

每张输入图片必须对应一个独立 workspace。不要把多张图片的 mask、cutout、导出变体混放到同一个目录。

## Workspace 位置

默认位置：

```text
docs/image-objects/<image-slug>/
```

`<image-slug>` 使用源图文件名规范化得到：

- 小写英文、数字和连字符。
- 空格、下划线和中文标点转为连字符。
- 去掉扩展名。
- 同名冲突时追加 `-02`、`-03`。

示例：

```text
assets/raw/Product Card Hero.jpg
→ docs/image-objects/product-card-hero/
```

如果用户指定输出目录，仍然要求该目录只对应一张源图。

## 标准目录

```text
docs/image-objects/product-card-hero/
├── source.png
├── source.json
├── masks/
├── cutouts/
├── backgrounds/
├── exports/
├── enhanced/
├── packages/
└── preview-cache/
```

目录含义：

- `source.png`：workspace 内标准源图，所有处理以它为基准。
- `source.json`：唯一结构化状态来源。
- `masks/`：模型、人工或后处理生成的 mask。
- `cutouts/`：由 source + mask 得到的原始对象切图。
- `backgrounds/`：移除对象后的背景修补图。
- `exports/`：透明、背景、圆角、padding、尺寸等最终导出变体。
- `enhanced/`：Image Gen 或外部工具深度优化候选，以及与候选同 ID 的 handoff brief。
- `packages/`：zip 或交付包。
- `preview-cache/`：GUI 预览缓存，可删除，不进入正式交付包。

## 文件命名

统一使用稳定 ID 前缀，后面可追加短 slug 说明用途。

```text
masks/mask_001.png
masks/mask_002-refined.png
cutouts/obj_001-product.png
backgrounds/bg_001-inpaint-opencv.png
exports/export_001-product-transparent.png
exports/export_002-product-white-square.webp
enhanced/enh_001-product-edge-polish.png
enhanced/enh_001-brief.md
packages/image-object-package.zip
```

命名规则：

- ID 由 `source.json` 分配并保持稳定。
- 文件名可带用途 slug，但不要改变 ID。
- 重新生成同一语义产物时创建新 ID，不覆盖旧文件，除非用户明确要求覆盖。
- 透明原始对象优先放 `cutouts/`；带背景、圆角、padding、尺寸处理的交付版放 `exports/`。
- Image Gen 深度优化的提示词、输入说明或 handoff brief 放在 `enhanced/`，并用同一个 `enh_###` 前缀关联候选图。
- 过程文件可以作为大模型输入，但不要复制到 `enhanced/`；在 `enh_###-brief.md` 或 `source.json.enhanced[].input_refs` 中引用原路径即可。

## 大模型 handoff 文件

当需要把过程文件交给 Image Gen 或多模态模型继续处理时，为每个候选创建一个简短 brief：

```text
enhanced/enh_001-brief.md
enhanced/enh_001-product-edge-polish.png
```

brief 只写本次任务需要的内容：

- 输入引用：`source.png`、相关 `region`/`mask`/`cutout`/`background`/`export` 路径。
- 编辑范围：bbox、mask 或用户标记区域。
- 保护约束：品牌元素、文字、未遮罩区域、光照、透视、对象比例。
- 输出目标：目标路径、尺寸、透明/背景要求、候选状态。

`preview-cache/` 只用于 GUI 展示，默认不进入 handoff；除非用户明确要求把某张预览图作为视觉参考。

## 单图隔离原则

同一 workspace 内只能有一张 `source.png`。如果用户一次处理多张图片，为每张图片创建独立目录：

```text
docs/image-objects/product-card-hero/
docs/image-objects/product-card-detail/
docs/image-objects/product-card-icon/
```

跨图复用或进入项目级素材库时，不在本 workspace 内混放；由 `aisee:design-assets` 把最终产物登记到 `docs/design-assets/` 索引。
