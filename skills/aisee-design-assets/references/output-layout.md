# 项目本地输出布局

## 默认目录

所有最终结果必须保存到目标项目本地：

```text
docs/design-assets/
├── index.md
├── index.json
├── references/
├── specs/
├── assets/
│   ├── backgrounds/
│   ├── icons/
│   ├── illustrations/
│   ├── overlays/
│   ├── layout-layers/
│   └── transparent/
├── edits/
├── briefs/
│   ├── figma-brief.md
│   ├── figma-brief.json
│   ├── dev-visual-brief.md
│   └── dev-visual-brief.json
└── manifests/
    └── asset-manifest.md
```

## 文件命名

参考图：

```text
reference-001.png
reference-002.png
reference-mobile-home-001.png
reference-pc-dashboard-001.png
```

设计规范：

```text
style-spec-001.md
style-spec-001.json
style-spec-mobile-home-001.md
style-spec-pc-dashboard-001.json
```

素材：

```text
background-hero-001.png
icon-entry-001.png
illustration-empty-state-001.png
overlay-light-001.png
layout-card-base-001.png
asset-transparent-001.png
```

编辑结果：

```text
reference-001-edit-001.png
background-hero-001-edit-001.png
```

## 索引原则

- `index.md` 给人读，记录主要结果和使用建议。
- `index.json` 给自动化流程读，记录路径、来源、状态和关联关系。
- 不把长 prompt 全量塞进索引；只保存摘要和必要参数。
- 结果文件路径使用项目相对路径。
- 不记录 API Key 或敏感原文。

## 下游 brief

Figma MCP 使用：

```text
docs/design-assets/briefs/figma-brief.md
docs/design-assets/briefs/figma-brief.json
```

前端开发使用：

```text
docs/design-assets/briefs/dev-visual-brief.md
docs/design-assets/briefs/dev-visual-brief.json
```

brief 文件只描述视觉交付输入和来源关系。页面内容、流程、字段、交互、权限和 API 仍以 `aisee:ui-content`、SRS 或实现需求为准。

## 来源关系

每个结果至少记录一种来源：

- `description`：用户描述
- `reference`：参考图路径
- `style_spec`：规范路径
- `edit_source`：被编辑图片路径
- `command`：CLI 命令摘要
