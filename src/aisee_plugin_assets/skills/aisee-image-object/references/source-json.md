# source.json 合同

`source.json` 是单图 workspace 的状态合同，GUI、CLI、模型后端和导出流程都读写它。

## 顶层字段

- `schema_version`：当前为 `0.1`
- `workspace`：workspace 相对或绝对路径
- `source`：原图信息，包含路径、原始路径、宽高、模式、格式
- `regions`：用户在原图上框选的区域，通常是 bbox
- `regions[].export_defaults`：该区域后续切图/导出时的默认属性，例如透明背景、圆角、留白、裁切模式和格式；GUI 框选时应先展示区域预览，再让用户确认这些属性。
- `models`：实际使用过的模型/backend
- `masks`：mask 产物
  - 从 region 生成的 mask 应记录 `region_id`、原始 `region_bbox`、实际 mask `bbox`、`model` 和 `source: "rembg-region"`。
- `objects`：cutout 或对象素材
  - 从 region mask 提取的对象应同时记录 `mask_id` 和 `region_id`。
- `backgrounds`：背景修补产物
- `exports`：最终导出变体
- `enhanced`：对话或外部图片生成工具产出的深度优化候选
  - `enhanced[].input_refs`：本次优化实际使用的过程文件引用，例如 source、mask、cutout、background 或 export。
  - `enhanced[].scope`：局部编辑范围，必须能指向 region、mask、object、background、bbox 或用户标记区域。
  - `enhanced[].prompt_ref`：写入 `enhanced/enh_###-brief.md` 的轻量 handoff brief，不把全量 `source.json` 直接塞给模型。
  - `enhanced[].style_lock`：风格、品牌、未遮罩区域和对象比例保护约束。
- `operations`：操作历史

## 路径规则

优先使用 workspace 相对路径，例如 `masks/mask_001.png`。跨 workspace 的外部输入可记录绝对路径，但最终产物必须写入 workspace。

每张输入图片必须对应一个独立 workspace，所有派生产物都保存在该 workspace 内。目录和命名规则见 `references/output-layout.md`。

## 对象备注

GUI 中用户给选中素材添加的要求文字写入对象的 `name`、`intent`、`notes` 或 export 的 `notes`。这些备注只描述对象用途和处理偏好，不自动变成全局图片生成提示词。

当备注用于大模型局部优化时，只能作为当前素材的局部要求参与 handoff，并且必须和明确的 `scope`、`input_refs`、保护约束一起使用。

## ID 规则

推荐使用稳定前缀：

- `mask_001`
- `region_001`
- `obj_001`
- `bg_001`
- `export_001`
- `enh_001`
- `op_001`

## 示例

```json
{
  "schema_version": "0.1",
  "workspace": "aisee/docs/image-objects/product-card-hero",
  "source": {
    "path": "source.png",
    "original_path": "assets/raw/product-card-hero.jpg",
    "width": 1536,
    "height": 1024,
    "mode": "RGB",
    "format": "JPEG"
  },
  "regions": [
    {
      "id": "region_001",
      "type": "bbox",
      "bbox": [214, 96, 1288, 938],
      "label": "产品主体区域",
      "notes": "用于生成主体 mask 和 cutout",
      "thumbnail": "preview-cache/thumb_region_001.png",
      "export_defaults": {
        "transparent": true,
        "corner_radius": 0,
        "padding": 0,
        "crop_mode": "bbox",
        "format": "png"
      }
    }
  ],
  "models": [
    {
      "backend": "rembg",
      "model": "birefnet-general",
      "profile": "quality",
      "status": "used",
      "used_at": "2026-05-24T12:00:00Z"
    }
  ],
  "masks": [
    {
      "id": "mask_001",
      "region_id": "region_001",
      "path": "masks/mask_001.png",
      "source": "rembg",
      "bbox": [214, 96, 1288, 938],
      "model": "birefnet-general",
      "notes": "主体产品 mask"
    },
    {
      "id": "mask_002",
      "region_id": "region_001",
      "path": "masks/mask_002-refined.png",
      "source": "refine",
      "bbox": [212, 94, 1290, 940],
      "model": null,
      "notes": "扩边 1px，羽化 0.8"
    }
  ],
  "objects": [
    {
      "id": "obj_001",
      "region_id": "region_001",
      "path": "cutouts/obj_001-product.png",
      "mask_id": "mask_002",
      "bbox": [212, 94, 1290, 940],
      "size": [1078, 846],
      "name": "产品主体",
      "intent": "用于 H5 首屏视觉素材",
      "notes": "保留原始高光和品牌标识"
    }
  ],
  "backgrounds": [
    {
      "id": "bg_001",
      "path": "backgrounds/bg_001.png",
      "mask": "mask_002",
      "scope": {
        "type": "masks",
        "ids": ["mask_002"]
      },
      "mask_ids": ["mask_002"],
      "method": "lama",
      "backend": "iopaint",
      "radius": null
    }
  ],
  "exports": [
    {
      "id": "export_001",
      "object_id": "obj_001",
      "path": "exports/export_001-product-transparent.png",
      "size": [1110, 878],
      "transparent": true,
      "background": null,
      "corner_radius": 0,
      "padding": 16,
      "crop_mode": "bbox",
      "format": "png",
      "notes": "透明交付版"
    },
    {
      "id": "export_002",
      "object_id": "obj_001",
      "path": "exports/export_002-product-white-web.webp",
      "size": [1200, 1200],
      "transparent": false,
      "background": "#ffffff",
      "corner_radius": 24,
      "padding": 48,
      "crop_mode": "square",
      "format": "webp",
      "notes": "白底方图"
    }
  ],
  "enhanced": [
    {
      "id": "enh_001",
      "source_object_id": "obj_001",
      "path": "enhanced/enh_001-product-edge-polish.png",
      "source": "aisee-design-assets",
      "method": "image-gen-edit",
      "input_refs": [
        "source.png",
        "cutouts/obj_001-product.png",
        "masks/mask_002-refined.png"
      ],
      "scope": {
        "type": "objects",
        "ids": ["obj_001"],
        "mask_ids": ["mask_002"]
      },
      "prompt_ref": "enhanced/enh_001-brief.md",
      "style_lock": {
        "preserve_brand": true,
        "preserve_unmasked_area": true,
        "preserve_lighting": true
      },
      "status": "candidate",
      "notes": "边缘与材质细节优化候选"
    }
  ],
  "operations": [
    {
      "id": "op_001",
      "kind": "init",
      "status": "success",
      "created_at": "2026-05-24T11:58:00Z",
      "params": {
        "input": "assets/raw/product-card-hero.jpg",
        "force": false
      },
      "outputs": ["source.png", "source.json"]
    },
    {
      "id": "op_002",
      "kind": "remove-bg",
      "status": "success",
      "created_at": "2026-05-24T12:00:00Z",
      "params": {
        "profile": "quality",
        "model": "birefnet-general"
      },
      "outputs": ["masks/mask_001.png", "cutouts/obj_001-product.png"]
    }
  ]
}
```
