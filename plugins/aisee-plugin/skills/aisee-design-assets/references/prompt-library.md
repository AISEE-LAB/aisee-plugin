# 内置 GPT Image 2 中文提示词库

内置中文原始提示词库用于生成参考图、视觉方向、海报、电商图、社媒图、信息图、角色、插画、图标或素材前的 prompt 写法参考。只借鉴结构、描述密度和视觉约束写法，不直接照抄，不引入无关品牌、人物、Logo、文案或业务字段。

路径：

```text
aisee-design-assets/prompt-library/gpt-image-2/
├── catalogs/
│   ├── prompts.jsonl
│   ├── prompts.csv
│   ├── prompts.xlsx
│   ├── excluded.jsonl
│   └── summary.json
├── raw-index/
└── sources.md
```

日常读取方式：

```bash
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py search --intent ui --limit 5
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py search --query "电商 主图" --no-risk --limit 5
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py read-excel --query "UI 设计系统" --limit 5
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py categories
```

支持的 `--intent`：`asset`、`character`、`ecommerce`、`infographic`、`poster`、`social`、`style`、`ui`。

入库约束：

- 只保留原始语言为中文或 prompt 正文本身为中文的条目。
- 不把英文、日文、韩文等非中文 prompt 翻译后入库；正文含日文假名或韩文时必须排除。
- EvoLinkAI 作为默认种子来源，从 canonical cases 中按中文正文筛选。
- YouMind 作为补充来源，默认通过 sitemap 发现 detail 页，并只保留 detail 页原始 `language/originalLanguage == zh` 的 `content`。
- `translatedContent` 不能作为入库正文。
- `catalogs/prompts.xlsx` 面向人工查看，只保留来源、分类、标题、详细提示词、来源链接、许可证、风险备注等精简字段。

刷新来源：

```bash
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py build
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py discover-youmind-sitemap --limit 20
```

刷新会访问 GitHub 公开来源和 YouMind 公开 detail 页，并更新 skill 内的 `prompt-library/gpt-image-2/catalogs/` 与 `raw-index/`。如果 YouMind 返回 429，降低 `--youmind-workers` 或稍后再试；脚本会优先使用已缓存的 sitemap URL。

需要追求 YouMind CMS 真正全量时，不要依赖 README 或 sitemap。若有授权的 CMS API 配置，则优先使用 CMS API。无论哪种方式，都只保留原始中文 prompt，不使用 `translatedContent` 作为入库正文。
