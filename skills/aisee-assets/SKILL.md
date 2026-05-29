---
name: aisee:assets
description: Aisee 视觉资产入口和路由器。用于判断是否需要 aisee:design-assets、aisee:svg-assets 或 aisee:image-object，并把视觉规范、SVG、位图素材通过 ui-contract、source-map 和 tasks 接入 OpenSpec change。它不生成 UI content，不负责需求或 change 边界规划。
---

# aisee:assets

`aisee:assets` 是视觉资产总入口。

## 路由

```text
aisee:design-assets
= 参考图、StyleSpec、设计规范、Figma brief、视觉素材计划

aisee:svg-assets
= SVG 图标、logo、线性图标、多色图形、SVG 校验和优化

aisee:image-object
= 图片对象分割、去背景、透明切图、素材变体、mask/inpaint
```

## OpenSpec 接入

- `ui-contract.md` 引用 StyleSpec 和关键视觉资产。
- `source-map.md` 记录 STYLE/ICON/IMG 与文件路径、tasks、页面的关系。
- `tasks.md` 记录资产接入和验证任务。

不要把完整视觉文档复制进 OpenSpec change。
