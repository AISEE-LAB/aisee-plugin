# GPT Image 2 中文原始提示词库

- 更新时间：2026-05-24 11:18:45 UTC
- 主库条目：177
- 中文筛选：只保留原始语言为中文或 prompt 正文本身为中文的条目；不翻译非中文 prompt。
- YouMind 抓取模式：sitemap
- 完整性：当前 catalog 是离线库；使用 sitemap detail 模式时覆盖公开 sitemap 可发现的 YouMind detail 页，不等同于授权 CMS 全量。
- 已排除非中文/低中文比例条目：1104
- 已排除重复条目：0

## 来源

- YouMind-OpenLab/awesome-gpt-image-2：https://github.com/YouMind-OpenLab/awesome-gpt-image-2，许可证 CC BY 4.0；README 模式仅保留元数据 `多语言: zh` 的条目，README 不是全量来源。
- EvoLinkAI/awesome-gpt-image-2-API-and-Prompts：https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts，许可证 CC0 1.0，从 canonical cases 中保留中文 prompt 正文。
- YouMind prompts sitemap：https://youmind.com/sitemaps/prompts/sitemap.xml，用于发现网页图库候选 detail URL；detail 页可解析原始语言，但全量抓取需节流并遵守站点 robots。

## 输出文件

- `catalogs/prompts.jsonl`：skill 脚本按意图检索的主数据。
- `catalogs/prompts.csv`：精简字段表格，便于外部表格工具使用。
- `catalogs/prompts.xlsx`：精简字段 Excel，列为来源、分类、标题、详细提示词、来源链接、许可证、风险备注。
- `catalogs/excluded.jsonl`：因非中文、低中文比例或重复被排除的条目。
- `raw-index/`：导入时读取的原始 Markdown 快照。

## 来源统计

| 来源 | 条目数 |
|------|--------|
| EvoLinkAI/awesome-gpt-image-2-API-and-Prompts | 85 |
| YouMind web detail | 92 |

## 分类统计

| 分类 | 条目数 |
|------|--------|
| poster | 35 |
| comparison | 26 |
| 信息图 / 教育视觉图 | 21 |
| 社交媒体帖子 | 21 |
| 产品营销 | 17 |
| ui | 13 |
| 海报 / 传单 | 11 |
| portrait | 6 |
| 游戏素材 | 6 |
| App / 网页设计 | 5 |
| YouMind detail | 4 |
| character | 4 |
| 个人资料 / 头像 | 4 |
| 漫画 / 故事板 | 2 |
| ecommerce | 1 |
| 团体 / 情侣 | 1 |

## 使用约束

- 不把非中文 prompt 翻译后入库。
- 使用当前离线库时注意来源模式；如果需要 YouMind CMS 真正全量，需接入授权 CMS API。
- CC BY 4.0 来源在复用、改写或对外分发时必须保留署名、来源链接和许可证链接。
- `risk_notes` 标记品牌、IP、公众人物或 Logo 风险；这些条目不应默认用于商用生成。
- 预览图片只保存 URL，不复制图片文件；如需图片资产，应单独确认授权和用途。
