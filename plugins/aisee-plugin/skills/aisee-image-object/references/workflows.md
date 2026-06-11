# aisee:image-object 工作流

## 总体处理思路

所有图片处理都遵循同一条主线：`source` → `scope` → `mask` → `cutout/background` → `export/enhanced` → `source.json`。不要直接在原图上覆盖修改；不要绕过 workspace 输出临时文件；不要把多个对象混成一个无 scope 的结果。

执行前先判断输入来源：

- 已有图片、截图、海报、产品图或参考图中的对象：由本 skill 提取、去背景、修边、导出透明素材。
- `aisee:design-assets` 生成的纯色/绿幕主体图：由本 skill 继续做去背景、mask/cutout、边缘修正和透明导出。
- 从零生成新插画、banner、背景或素材 prompt：不属于本 skill，交给 `aisee:design-assets`。
- 通用 UI 图标：优先图标库，不走本 skill。

## 基于图片提取素材

通用素材提取流程见 `asset-extraction.md`。当用户从已有图片、截图、海报、参考图或产品图中提取可复用素材时，先建立单图 workspace，再按候选清单逐个生成 region、mask、cutout、export 或 enhanced，不把提取执行交给 `aisee:design-assets`。

## 去背景到透明素材

适用于已有图片主体，也适用于 `aisee:design-assets` 生成的绿幕/纯色背景主体图。

1. `init` 创建 workspace，复制原图为 `source.png`。
2. `remove-bg --profile quality` 通过 rembg 调用成熟模型，默认优先 BiRefNet 类模型。
3. 从 alpha 生成 mask，保存到 `masks/`，cutout 保存到 `cutouts/`。
4. `export-variant` 根据透明、背景、圆角、padding、裁切模式生成最终素材。
5. 更新 `source.json`，记录模型、参数、fallback 和产物路径。

质量门禁：

- 透明边缘不能有明显绿边、白边、黑边或背景残留。
- 半透明对象、毛发、玻璃、阴影和发光边缘需要人工复核或 mask refine。
- 导出前确认用途：透明 PNG/WebP、固定背景色版本、圆角/padding 版本或多尺寸变体。

## 已有 mask 修边

1. 把 mask 放入 workspace 或通过绝对路径传给 `refine-mask`。
2. 使用 expand/contract/feather/smooth/invert 做确定性修边。
3. 用修正后的 mask 执行 `extract-object`。
4. 导出变体时再决定透明、背景、圆角和 padding。

## 点选/框选分割

1. GUI 左侧原图画布收集前景点、背景点或 BBox。
2. 框选 region 后先展示裁切预览，并保存透明、圆角、留白、裁切模式和格式等导出默认值。
3. 选中 region 可调用 rembg profile 生成局部 Mask；Mask 会映射回原图同尺寸画布，便于背景修补和后续 Cutout 提取。
4. 选中 Mask 可提取 Cutout，也可在生成 Mask 时勾选同时提取 Cutout。
5. SAM/SAM2 backend 作为可选路径生成候选 mask。
6. 右侧同尺寸预览 mask overlay、cutout、alpha 和裁切结果。
7. 用户确认后写入 `source.json`。

## 背景修补

1. 使用 mask 指定要移除的对象区域。
2. 优先使用 LaMa / IOPaint 做本地模型修补。
3. LaMa backend 不可用时，可显式使用 `--fallback-opencv` 生成 OpenCV 候选，但它只作为低质量 fallback。
4. Image Gen 深度优化属于语义修补路径，由对话或 Codex CLI 触发；GUI 第一版不内置真实调用。

## Image Gen 深度优化

深度优化通过对话或 Codex CLI 触发，不作为 GUI MVP 的强依赖。它不是只消费最终导出图，也可以消费过程文件：region 裁切图、mask、cutout、背景修补图、导出变体和用户标记的局部抹除 mask 都可以作为局部编辑输入。

它可以与 `aisee:design-assets` 协作，但职责要分清：

- `aisee:image-object` 提供原图、mask、cutout、bbox、对象备注、品牌保留要求和输出目标。
- `aisee:design-assets` 负责把这些输入转成受控图片编辑提示词、参考约束和设计资产索引登记；候选图仍回写当前 image-object workspace。
- 深度优化后的候选图回写到当前 workspace 的 `enhanced/`，并记录到 `source.json.enhanced`。
- 如果候选图要进入项目素材库，再由 `aisee:design-assets` 更新 `aisee/docs/design-assets/` 索引。

handoff 原则：

- 优先传递最小必要输入，不把整个 workspace、全部缩略图或 `preview-cache/` 作为默认上下文。
- 局部优化必须带 mask/bbox/scope；没有明确 scope 时先让用户确认修改范围。
- 基于对话提炼区域描述时，必须同时写自然语言区域说明和可定位引用，例如 `region_id`、`mask_id`、`object_id` 或 bbox。
- 自然语言说明用于告诉 image gen “要优化什么”，可定位引用用于限制“只能改哪里”；两者缺一不可。
- region 本身可以直接作为素材输入；只有需要去背景、修边或重绘时才继续生成透明版本、mask 或 enhanced 候选。
- 同一张图的候选可以多轮生成，但每轮都产生新的 `enh_###`，不要覆盖上一轮候选。

调用时必须把以下约束写入提示：

- 保持原图风格、光照、透视、材质和边缘质量。
- 保留品牌元素、Logo、文字、产品比例和未遮罩区域。
- 只修改用户指定的对象或 mask 区域。
- 输出结果落到 `enhanced/`，并在 `source.json.enhanced` 中记录来源。

推荐 handoff 输入：

```json
{
  "task": "image-object-enhance",
  "workspace": "aisee/docs/image-objects/product-card-hero",
  "source": "source.png",
  "object": "cutouts/obj_001-product.png",
  "mask": "masks/mask_002-refined.png",
  "scope": {
    "description": "产品主体右侧边缘有半透明残留和轻微白边，需要只优化边缘过渡",
    "region_id": "region_002",
    "mask_id": "mask_002",
    "bbox": [412, 168, 734, 820]
  },
  "input_refs": [
    "cutouts/obj_001-product.png",
    "masks/mask_002-refined.png"
  ],
  "target": "enhanced/enh_001-product-edge-polish.png",
  "requirements": [
    "优化主体边缘半透明残留",
    "保持产品 Logo、比例、材质和光照",
    "未遮罩区域不得改变"
  ],
  "style_lock": {
    "preserve_brand": true,
    "preserve_unmasked_area": true,
    "preserve_lighting": true
  }
}
```
