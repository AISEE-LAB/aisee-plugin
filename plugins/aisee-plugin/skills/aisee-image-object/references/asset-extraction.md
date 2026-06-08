# 基于图片的素材提取流程

当用户要求“从这张图里提取素材”“基于图片生成素材”“把截图里的图标/产品/人物/装饰层切出来”“做透明 PNG”“拆图层包”时，执行本流程。它属于 `aisee:image-object`，不是 `aisee:design-assets` 的生成型素材流程。

## 职责判断

| 用户意图 | 主责 skill | 说明 |
|---|---|---|
| 从已有图片中切出主体、图标、装饰元素、产品图或人物 | `aisee:image-object` | 需要 source、region、mask、cutout、export 追踪 |
| 去背景、生成透明 PNG、修 mask、处理边缘 | `aisee:image-object` | 属于对象级处理 |
| 移除对象并补背景 | `aisee:image-object` | 需要 mask 和背景修补记录 |
| 根据素材需求从零生成背景、插画、装饰层 | `aisee:design-assets` | 属于生成型视觉资产 |
| 把提取出的素材登记到项目素材清单 | `aisee:design-assets` | 只登记路径、用途、状态和来源，不执行提取 |

## 标准流程

1. **建立 workspace**
   - 为每张源图创建独立 `aisee/docs/image-objects/<image-slug>/`。
   - 复制源图为 `source.png`，初始化 `source.json`。

2. **素材候选清单**
   - 识别要提取的素材：对象、图标、产品、人物、装饰层、背景区域、局部纹理。
   - 为每个候选写用途、目标格式、是否透明、是否需要背景、是否需要保留阴影或边缘光。
   - 如果用户没有明确目标素材，先输出候选清单让用户确认。

3. **选择提取路径**
   - 边界清晰的单主体：`remove-bg` → `export-variant`。
   - 多对象或局部区域：`select --interactive` 或 `segment-box` / `segment-point` → `extract-object`。
   - 已有 mask：`refine-mask` → `extract-object`。
   - 只需要矩形素材且不透明：可用 region crop，不强制 mask。
   - 需要移除对象后的背景：`inpaint-background`。
   - 需要语义修边或局部重绘：生成 `enhanced/enh_###-brief.md`，再按 Image Gen handoff 处理。

4. **对话到区域描述**
   - 从用户对话中提取要优化或生成的区域描述，例如“右上角按钮旁的装饰光效”“产品边缘的白边”“卡片底部阴影太脏”。
   - 区域描述必须落到可定位引用：`source`、`region_id`、`object_id`、`mask_id`、`bbox` 或用户确认的标记区域。
   - 同时保留自然语言描述和机器可定位范围：自然语言用于 image gen 理解语义，mask/bbox/object 用于限制修改范围。
   - 如果只有自然语言、无法定位具体区域，先输出候选区域并让用户确认；不要直接让 image gen 自由判断整图。
   - 如果用户描述的是“生成一个类似图中某元素的新素材”，先提取或框定参考元素，再写生成型要求；不要把整张图作为无约束参考。

5. **导出变体**
   - 原始透明对象放 `cutouts/`。
   - 交付版放 `exports/`，按透明、背景、圆角、padding、尺寸和裁切模式生成。
   - 同一素材的不同用途导出多个 export ID，不覆盖旧版本。

6. **质量复核**
   - 检查边缘、透明残留、毛边、半透明材质、阴影、主体比例、品牌元素和文字。
   - 检查导出尺寸、padding、裁切范围和目标用途是否匹配。
   - 不合格时记录状态为 `needs-edit`，继续 refine mask、重提取或 enhanced。

7. **登记与交接**
   - 更新 `source.json`，记录候选、mask、cutout、export、background、enhanced 和操作历史。
   - 如果素材要作为项目级视觉资产复用，把最终 export/cutout/enhanced 路径、用途和状态交给 `aisee:design-assets` 更新 `aisee/docs/design-assets/` 索引。
   - OpenSpec change 只引用最终路径和使用范围，不复制完整 workspace。

## 输出字段

每个素材至少记录：

```text
Object ID:
Export ID:
Source image:
Region / BBox:
Mask:
Cutout:
Export:
区域描述:
生成/优化要求:
用途:
透明:
尺寸:
状态: candidate / usable / needs-edit / rejected
复核结论:
Design Assets handoff: yes / no
```

## 禁止事项

- 不把多张源图混在一个 workspace。
- 不把多个素材合并成一个 object ID。
- 不用 `aisee:design-assets` 的生成型 prompt 代替 mask、cutout 或 source.json。
- 不默认覆盖已有 mask、cutout、export 或 enhanced 候选。
- 不把 `preview-cache/` 或整个 workspace 复制进 OpenSpec artifacts。
