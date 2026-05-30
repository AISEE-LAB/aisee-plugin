# StyleSpec 草稿 / 视觉线索

## 目的

StyleSpec 是可复用的视觉线索，用于基于参考图继续生成新参考图、素材或下游 Figma AI 提示。它不是长期 UI 设计规范事实源、品牌手册全文，也不是前端实现方案；需要沉淀为项目级或模块级设计规范时，交给 `aisee:design-spec`。

## 何时输出 Markdown

- 用户阅读和人工复核为主
- 需要给 Figma AI 或设计师继续使用
- 初次沉淀视觉线索，后续可交给 `aisee:design-spec` 归纳为长期规范

## 何时同时输出 JSON

- 需要被脚本、MCP 管线或后续自动化读取
- 项目会维护多份 StyleSpec 草稿并索引
- 用户明确要求结构化存储

## 提取维度

必须覆盖：

- 来源：参考图、用户描述、已有规范、版本
- 适用范围：平台、页面类型、业务场景
- 视觉定位：关键词、气质、适合/不适合方向
- 色彩：主色、辅助色、背景色、高光、禁用色
- 构图：画布比例、视觉重心、留白、层级、背景/前景关系
- 图形语言：形状、线条、光影、材质、图标/插画风格
- 素材需求：背景、图标、插画、装饰、透明素材
- 禁止项：文字、Logo、水印、过强具象主体、平台不合适元素
- 下游提示：基于该规范生成新图时应保留和避免什么

## 文件命名

```text
docs/design-assets/specs/style-spec-001.md
docs/design-assets/specs/style-spec-001.json
```

多份规范并存时，不覆盖旧文件；通过索引标记 `active`、`candidate`、`archived`。

## JSON 最小结构

```json
{
  "id": "style-spec-001",
  "title": "",
  "status": "active",
  "platforms": ["pc"],
  "source": {
    "type": "reference-image",
    "paths": ["docs/design-assets/references/reference-001.png"],
    "notes": ""
  },
  "visualPositioning": {
    "keywords": [],
    "tone": "",
    "avoid": []
  },
  "colors": {
    "primary": [],
    "secondary": [],
    "background": [],
    "accent": [],
    "avoid": []
  },
  "composition": {
    "canvas": "",
    "focus": "",
    "spacing": "",
    "layers": []
  },
  "graphicLanguage": {
    "shapes": "",
    "lighting": "",
    "materials": "",
    "icons": "",
    "illustrations": ""
  },
  "assetNeeds": [],
  "downstreamPromptNotes": {
    "preserve": [],
    "emphasize": [],
    "avoid": []
  }
}
```
