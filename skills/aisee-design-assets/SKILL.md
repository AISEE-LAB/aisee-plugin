---
name: aisee:design-assets
description: 通用视觉参考图、设计证据与素材生成工作流。用于用户要求基于描述生成 App、微信小程序、H5、PC Web、桌面端或多端参考图；从参考图/截图提取 StyleSpec 草稿或视觉线索；基于既有 design-spec / StyleSpec 生成新的参考图；规划参考图中的素材需求；生成或编辑背景、插画、装饰层、布局视觉层和生成型透明素材；整理项目本地图片索引、视觉来源索引和素材清单时触发。不要用于 SRS、UI 内容规格、长期 UI 设计规范事实源、前端实现、Figma 写入、对象分离、去背景、mask 生产或图层包生成；长期设计规范交给 aisee:design-spec。
---

# aisee:design-assets

把用户描述、参考图和已有视觉规范转成项目本地可复用的参考图、StyleSpec 草稿、素材和下游视觉 brief。它是轻量工作流 skill，不是完整工作台、需求工具、长期设计规范事实源、Figma 写入器或前端实现器。

## 适用输入

- 产品、页面、业务场景或视觉目标描述
- 参考图、截图、草图、品牌图或本地图片路径
- 已有 `aisee:design-spec`、StyleSpec 草稿或视觉规范，Markdown 或 JSON
- 需要生成、编辑或整理的视觉素材、生成型透明素材和素材索引
- 需要按意图查找内置 GPT Image 2 中文提示词素材

判断维度：平台（mobile / mini-program / h5 / pc / desktop / multi）、任务模式（reference / style-draft / assets / edit / figma-brief / dev-brief / auto）、输出格式（md / json / both）和输出目录。默认输出到目标项目的 `aisee/docs/design-assets/`。

## 边界

必须：

- 所有最终图片、生成参数摘要、索引和 brief 保存到目标项目目录，不写入 skill 目录。
- 参考图、StyleSpec、素材和编辑结果都记录来源路径、状态和用途。
- 如果 StyleSpec 草稿需要成为长期设计规范，提示交给 `aisee:design-spec` 沉淀，不在本技能内扩展为规范事实源。
- 面向 Figma MCP 时生成 `figma-brief`，并要求优先复用既有组件、变量和样式。
- 面向前端开发时生成 `dev-visual-brief`，只提供视觉输入。

不要：

- 不生成 SRS 或 UI 内容规格；分别交给 `aisee:srs` 和 `aisee:ui-content`。
- 不生成长期 UI 设计规范、组件库采用策略、Design Tokens 事实源、Screen Patterns 或 Interaction Patterns；这些交给 `aisee:design-spec`。
- 不把参考图当最终设计稿。
- 不做对象分离、去背景、mask 生产、透明对象提取、背景修补或图层包生成；这些交给专用对象处理 skill/工具。
- 不隐式选择多份参考图或 StyleSpec；依据不明确时先确认。
- 不覆盖已有图片、规范或索引，除非用户明确要求。
- 不保存、输出或提交 API Key、令牌、Cookie、证书等敏感信息。

## OpenSpec 接入

当视觉资产进入 OpenSpec change：

- `ui-contract.md` 只引用 StyleSpec、参考图、素材清单或 brief 的路径和本次适用约束。
- `source-map.md` 记录 STYLE/IMG/ASSET 与 PAGE、PAT、FR、tasks 和文件路径的关系。
- `tasks.md` 只记录资产接入、切图落地、截图比对或人工验收任务。
- 不把完整 StyleSpec、图片生成过程、prompt 库内容或资产索引正文复制进 change artifacts。

## 内置提示词库

内置 GPT Image 2 中文原始提示词库位于：

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

使用约束：

- 只保留原始语言为中文或 prompt 正文本身为中文的条目。
- 不把英文、日文、韩文等非中文 prompt 翻译后入库；正文含日文假名或韩文时必须排除。
- EvoLinkAI 作为默认种子来源，从 canonical cases 中按中文正文筛选。
- YouMind 作为补充来源，默认通过 sitemap 发现 detail 页，并只保留 detail 页原始 `language/originalLanguage == zh` 的 `content`。
- `translatedContent` 不能作为入库正文。
- `catalogs/prompts.xlsx` 面向人工查看，只保留来源、分类、标题、详细提示词、来源链接、许可证、风险备注等精简字段。
- 读取提示词时使用脚本，不手工批量打开整库。日常按意图优先用 `search` 读取 JSONL；需要核对 Excel 展示内容时用 `read-excel`：

```bash
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py search --intent ui --limit 5
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py search --query "电商 主图" --no-risk --limit 5
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py read-excel --query "UI 设计系统" --limit 5
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py categories
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py discover-youmind-sitemap --limit 20
```

支持的 `--intent`：`asset`、`character`、`ecommerce`、`infographic`、`poster`、`social`、`style`、`ui`。

需要刷新来源时运行：

```bash
python3 aisee-design-assets/scripts/gpt_image2_prompt_library.py build
```

刷新会访问 GitHub 公开来源和 YouMind 公开 detail 页，并更新 skill 内的 `prompt-library/gpt-image-2/catalogs/` 与 `raw-index/`。如果 YouMind 返回 429，降低 `--youmind-workers` 或稍后再试；脚本会优先使用已缓存的 sitemap URL。

需要追求 YouMind CMS 真正全量时，不要依赖 README 或 sitemap。若有授权的 CMS API 配置，则优先使用 CMS API。无论哪种方式，都只保留原始中文 prompt，不使用 `translatedContent` 作为入库正文。

## Phase 0 — 读取上下文

先定位目标项目目录：用户给了项目路径就用该路径，否则使用当前工作目录。

静默收集已有资产上下文：

```bash
find aisee/docs/design-assets -maxdepth 3 -type f 2>/dev/null | head -80
find aisee/docs/design-spec -maxdepth 3 -type f 2>/dev/null | head -80
find docs/designs -maxdepth 4 -type f 2>/dev/null | head -80
find . -maxdepth 3 \( -iname '*style*spec*.md' -o -iname '*style*spec*.json' -o -iname '*design*asset*index*.md' -o -iname '*asset*manifest*.md' \) 2>/dev/null | head -80
```

若存在既有索引，先读取它们，避免重复命名和覆盖。

## Phase 1 — 选择最小闭环

按用户意图选择最小流程，并只读取相关 reference：

- 生成参考图、保结构重绘、从规范生成新图：读 `references/workflow.md`
- 视觉质量优先、用户上传参考图/截图、图片转视觉 brief 或 image-first 工作流：读 `references/image-first.md`
- 图片生成、编辑、透明图、CLI fallback：读 `references/image-generation.md`
- 提取或生成 StyleSpec 草稿：读 `references/style-spec.md`
- 规划、提取、生成或复核素材：读 `references/asset-manifest.md`
- 生成前提示词优化：读 `references/prompt-optimization.md`
- 不同端尺寸、清晰度、安全区、图生图保留项：读 `references/output-specs.md`
- 图标库、组件库、通用图标替换策略：读 `references/icon-library.md`
- 生成 Figma / 开发视觉 brief：读 `references/downstream-briefs.md`
- 建立目录和索引：读 `references/output-layout.md`

当用户要生成参考图、视觉方向、海报、电商图、社媒图、信息图、角色、插画、图标或素材时，先用 `scripts/gpt_image2_prompt_library.py search` 按 `--intent` 或 `--query` 读取 3-5 条相关中文原始提示词作为参考；只借鉴结构、描述密度和视觉约束写法，不直接照抄，不引入无关品牌、人物、Logo、文案或业务字段。需要确认 Excel 里的人工表格内容时，再用 `read-excel`。

常见闭环：

1. 只有描述且要视觉方向：按 image-first 判断是否生成参考图。
2. 有参考图/截图且要沉淀风格线索：先分析参考图，再生成 StyleSpec 草稿；需要长期规范时交给 `aisee:design-spec`。
3. 有 `aisee:design-spec` 或 StyleSpec 且要新页面视觉：基于规范生成新参考图。
4. 有长页面、Landing、多状态或多端视觉任务：按页面 / section / 关键状态分图生成或分析，不压成单张超长图。
5. 有参考图/规范且要素材：生成素材清单，再生成或提取素材。
6. 有已有图片且要修改：进入编辑流程。
7. 需要进入 Figma MCP 或前端开发：生成对应 brief；前端只拿 `dev-visual-brief` 做视觉输入，不让本 skill 写代码。
8. 要从已有扁平图片中分离对象、生成 mask、交互式框选/点选、导出透明对象、移除对象并补背景或生成图层包：交给专用对象处理 skill/工具；本 skill 只负责把产物登记到设计资产索引。

## Phase 2 — 输入门禁

信息不足时最多追问 3 个会影响结果的问题：

- 平台、画布比例或输出目录不明确
- 页面/业务场景不明确
- 透明输出、参考依据或 StyleSpec 选择不明确

低风险默认：

- 输出目录：`aisee/docs/design-assets/`
- 规范格式：Markdown；需要机器复用时追加 JSON
- 透明范围：只对用户指定的独立素材生成透明版
- 候选数量：单页视觉方向参考图 2-4 张；长页面按 section 分图；素材每项 1 个主版本

## Phase 3 — 执行

执行前做轻量提示词优化：整理结构、补齐必要约束，不添加未确认的业务需求、Logo、文案、人物、字段或数据。

图像生成路径按 `references/image-generation.md` 决策。核心原则：

- 内置 `image_gen` 可用时，普通参考图、视觉变体、已有 UI 效果图保结构重绘和简单透明素材优先走内置工具。
- 内置工具不可用，或用户明确要求脚本、Images API、模型、本地路径、mask、批量或原生透明时，才走 CLI fallback。
- 项目绑定图片最终必须复制或移动到项目本地。
- 真实 API 调用必须使用用户显式配置的 `api_key` 和 `base_url`；运行时数据写入目标项目目录。
- 通用图标、导航图标、操作图标和状态图标优先使用成熟图标库；图片模型只生成占位或视觉氛围。
- 图生图和局部编辑默认是受控修改，必须保护品牌元素、布局结构、视觉风格和未遮罩区域。
- Prompt 只注入当前任务必要约束，不把全部规则一次性塞进图片模型请求。

内置脚本：

- `scripts/image_gen.py`
- `scripts/remove_chroma_key.py`
- `scripts/gpt_image2_prompt_library.py`

## Phase 4 — 更新索引

按需更新或创建：

- `aisee/docs/design-assets/index.md`
- `aisee/docs/design-assets/index.json`
- `aisee/docs/design-assets/manifests/asset-manifest.md`
- `aisee/docs/design-assets/briefs/figma-brief.md` / `.json`
- `aisee/docs/design-assets/briefs/dev-visual-brief.md` / `.json`

模板见 `assets/`。索引只记录事实、路径、来源和状态，不写冗长过程日志。若产物被 `aisee:design-spec` 引用，应在索引中记录被引用路径；不要把设计规范正文复制回资产索引。

## Phase 5 — 交付

最终回复使用中文，说明生成/编辑目标、使用方式、输出路径、规范/素材清单路径、复核结论和风险。未实际生成图片时，只输出可执行方案、提示词和建议目录，不声称已生成。
