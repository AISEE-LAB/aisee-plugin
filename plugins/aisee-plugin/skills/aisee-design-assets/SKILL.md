---
name: aisee:design-assets
description: 通用视觉参考图、设计证据与生成型素材工作流。用于用户要求基于描述生成 App、微信小程序、H5、PC Web、桌面端或多端参考图；从参考图/截图提取 StyleSpec 草稿或视觉线索；基于既有 design-spec / StyleSpec 生成新的参考图；按参考图驱动 imagegen 生成风格一致的背景、插画、banner、装饰层、布局视觉层和生成型透明素材；规划素材需求并整理项目本地图片索引、视觉来源索引和素材清单时触发。不要用于 SRS、UI 内容规格、长期 UI 设计规范事实源、前端实现、Figma 写入、基于已有图片的对象分离、素材提取、去背景、mask 生产、背景修补或图层包生成；这些交给 aisee:image-object。通用 UI 图标优先映射成熟图标库，不默认用图片模型创造。长期设计规范应作为独立 design spec / delta planning doc 交给 aisee:design-spec。
---

# aisee:design-assets

把用户描述、参考图和已有视觉规范转成可执行的图片生成提示、项目本地参考图、StyleSpec 草稿、素材清单和下游视觉 brief。它是轻量工作流 skill，重点是为参考图和素材生成补齐 prompt 约束，不是完整工作台、需求工具、长期设计规范事实源、Figma 写入器或前端实现器。

生成 design-assets 索引、brief 或相关 planning doc 时，frontmatter 字段合同统一遵循 `plugins/aisee-plugin/references/planning-doc-frontmatter.md`；它只服务索引和追踪，不替代 OpenSpec 事实源。

## 适用输入

- 产品、页面、业务场景或视觉目标描述
- 参考图、截图、草图、品牌图或本地图片路径
- 已有 `aisee:design-spec`、StyleSpec 草稿或视觉规范，Markdown 或 JSON
- 需要按参考图生成、规划或整理的视觉素材、banner、插画、生成型透明素材和素材索引
- 需要按意图查找内置 GPT Image 2 中文提示词素材

判断维度：平台（mobile / mini-program / h5 / pc / desktop / multi）、任务模式（reference / style-draft / generated-assets / figma-brief / dev-brief / auto）、输出格式（md / json / both）和输出目录。默认输出到目标项目的 `aisee/docs/design-assets/`。

## 边界

必须：

- 所有最终图片、生成参数摘要、索引和 brief 保存到目标项目目录，不写入 skill 目录。
- 参考图、StyleSpec、生成型素材和外部对象产物索引都记录来源路径、状态和用途。
- 新生成或从对象流程登记的素材必须记录 `style_anchor`、`style_lock`、`allowed_variation` 和 `consistency_check`；无法确认与参考图一致时标记为 `warnings` 或 `failed`，不要写成已通过。
- 如果 StyleSpec 草稿需要成为长期设计规范，提示交给 `aisee:design-spec` 沉淀为 design spec / delta planning doc，不在本技能内扩展为规范事实源。
- 面向 Figma MCP 时生成 `figma-brief`，并要求优先复用既有组件、变量和样式。
- 面向前端开发时生成 `dev-visual-brief`，只提供视觉输入。
- 基于已有图片提取出的 cutout、mask、export、background 或图层包，只登记路径和用途；提取执行交给 `aisee:image-object`。
- 通用 UI 图标、导航图标、操作图标和状态图标优先使用图标库，只记录图标库名、图标名、尺寸和风格；只有品牌符号、业务专属图形、IP 形象或插画型图标才进入生成型素材流程。

不要：

- 不生成 SRS 或 UI 内容规格；分别交给 `aisee:srs` 和 `aisee:ui-content`。
- 不生成长期 UI 设计规范、组件库采用策略、Design Tokens 事实源、Screen Patterns 或 Interaction Patterns；这些交给 `aisee:design-spec`。
- 不把参考图当最终设计稿。
- 不做基于已有图片的对象分离、去背景、mask 生产、透明对象提取、背景修补、图层包生成或素材提取执行；这些交给 `aisee:image-object`。
- 不隐式选择多份参考图或 StyleSpec；依据不明确时先确认。
- 不覆盖已有图片、规范或索引，除非用户明确要求。
- 不保存、输出或提交 API Key、令牌、Cookie、证书等敏感信息。

## OpenSpec 接入

当视觉资产进入 OpenSpec change：

- `ui-contract.md` 只引用 StyleSpec、参考图、素材清单或 brief 的路径和本次适用约束。
- `source-map.md` 记录 STYLE/IMG/ASSET 与 PAGE、PAT、FR、tasks 和文件路径的关系。
- `tasks.md` 只记录资产接入、切图落地、截图比对或人工验收任务。
- 不把完整 StyleSpec、图片生成过程、prompt 库内容或资产索引正文复制进 change artifacts。

## Phase 0 — 读取上下文

先定位目标项目目录：用户给了项目路径就用该路径，否则使用当前工作目录。

静默收集已有资产上下文：

```bash
rg --files aisee/docs/design-assets 2>/dev/null | head -80
rg --files aisee/docs/design-spec 2>/dev/null | head -80
rg --files docs/designs 2>/dev/null | head -80
rg --files | rg '(style.*spec.*\.(md|json)|design.*asset.*index.*\.md|asset.*manifest.*\.md)' | head -80
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，并只查设计资产需要的文件类型。

若存在既有索引，先读取它们，避免重复命名和覆盖。

## Phase 1 — 选择最小闭环

按用户意图选择最小流程，并只读取相关 reference：

- 生成参考图、保结构重绘、从规范生成新图：读 `references/workflow.md`
- 视觉质量优先、用户上传参考图/截图、图片转视觉 brief 或 image-first 工作流：读 `references/image-first.md`
- Image2 图片生成、图生图视觉变体、透明生成型素材、CLI fallback：读 `references/image-generation.md`
- 提取或生成 StyleSpec 草稿：读 `references/style-spec.md`
- 规划、生成或复核素材清单，识别素材边界和 banner 文字策略：读 `references/asset-manifest.md`
- 生成前提示词优化：必须读 `references/prompt-optimization.md`
- 需要借鉴中文图片生成 prompt 写法：读 `references/prompt-library.md`
- 不同端尺寸、清晰度、安全区、图生图保留项：读 `references/output-specs.md`
- 图标库、组件库、通用图标替换策略：读 `references/icon-library.md`
- 生成 Figma / 开发视觉 brief：读 `references/downstream-briefs.md`
- 建立目录和索引：读 `references/output-layout.md`

当用户要生成参考图、视觉方向、海报、电商图、社媒图、信息图、角色、插画、图标或素材时，先做 prompt 完善；需要参考写法时，用 `scripts/gpt_image2_prompt_library.py search` 读取 3-5 条相关中文原始提示词，只借鉴结构和视觉约束写法。

常见闭环：

1. 只有描述且要视觉方向：按 image-first 判断是否生成参考图。
2. 有参考图/截图且要沉淀风格线索：先分析参考图，再生成 StyleSpec 草稿；需要长期规范时交给 `aisee:design-spec`。
3. 有 `aisee:design-spec` 或 StyleSpec 且要新页面视觉：基于规范生成新参考图。
4. 有长页面、Landing、多状态或多端视觉任务：按页面 / section / 关键状态分图生成或分析，不压成单张超长图。
5. 有参考图/规范且要素材：生成素材清单；生成型背景、插画、banner、装饰层和插画型小图形由本 skill 使用 Image2 生成，并以参考图一致性为硬约束；基于已有图片提取的对象素材转交 `aisee:image-object`。
6. 有已有图片且要修改：只有“保结构重绘 / 视觉变体 / 参考图再生成”留在本 skill；涉及对象、mask、局部修补、去背景、抠图、透明切图或图层包时转交 `aisee:image-object`。
7. 需要进入 Figma MCP 或前端开发：生成对应 brief；前端只拿 `dev-visual-brief` 做视觉输入，不让本 skill 写代码。
8. 要从已有扁平图片中分离对象、生成 mask、交互式框选/点选、导出透明对象、移除对象并补背景或生成图层包：交给 `aisee:image-object`；本 skill 只负责把产物登记到设计资产索引。
9. 要透明素材：从零生成的独立透明素材留在本 skill，先用 Image2 生成绿幕/纯色背景或按 CLI 原生透明流程处理；从已有图片提取透明对象、修边、抠图、去背景或 mask 的流程交给 `aisee:image-object`。
10. 要局部内容优化、补细节、增强氛围或完善某个区域：先理解用户意图，明确修改范围、保留项和禁止项；不需要精确 mask 的视觉增强可由本 skill 优化 prompt 后驱动 Image2 生成候选，需要精确区域、对象、抠图、修边或背景修补时先交给 `aisee:image-object` 准备 source/mask/bbox。

## Phase 2 — 输入门禁

信息不足时最多追问 3 个会影响结果的问题：

- 平台、画布比例或输出目录不明确
- 页面/业务场景不明确
- 生成型透明输出、参考依据或 StyleSpec 选择不明确
- 多个参考图、StyleSpec 或设计规范可能冲突，无法确定主 `style_anchor`

低风险默认：

- 输出目录：`aisee/docs/design-assets/`
- 规范格式：Markdown；需要机器复用时追加 JSON
- 透明范围：只对用户指定的生成型独立素材生成透明版；从已有图片提取透明对象交给 `aisee:image-object`
- 候选数量：单页视觉方向参考图 2-4 张；长页面按 section 分图；素材每项 1 个主版本

## Phase 3 — 执行

执行前必须先理解用户意图，再做轻量提示词优化：整理结构，补齐平台、用途、尺寸、参考依据、素材边界、文本策略、主体、构图、风格、不变项、允许变化和避免项；不添加未确认的业务需求、Logo、文案、人物、字段或数据。

CHECKPOINT: 执行图片生成、图生图视觉变体、外部 API 调用、刷新远程提示词来源、覆盖既有图片/索引或写入长期资产前，必须确认目标、输入来源、输出目录、是否覆盖、是否使用外部 API、成本/配额风险和敏感信息处理。未确认时只输出方案、提示词和待确认项，不声称已生成。

生成或登记素材前先建立一致性合同：

- `style_anchor`：主参考图、StyleSpec 或 design-spec 路径，只能有一个主锚点；多个辅助参考必须说明用途。
- `style_lock`：颜色、线条、圆角、材质、光照、构图密度、阴影、图标风格、品牌元素等必须保持的项目。
- `allowed_variation`：允许变化的主体、尺寸、裁切、状态、背景或透明导出范围。
- `consistency_check`：生成或登记后按 `passed` / `warnings` / `failed` 记录是否保持一致，以及需要人工复核的点。

图像生成路径按 `references/image-generation.md` 决策。主文件只保留四条执行原则：

- 普通参考图、视觉变体和生成型素材明确以 Image2 为目标模型：内置 `image_gen` 可用时优先使用内置工具；CLI/API fallback 默认使用 `gpt-image-2`，只有原生透明等模型能力不支持时才使用其它模型。
- 透明素材先分流：从零生成的独立主体由本 skill 做 Image2 prompt 完善、绿幕/纯色背景生成和去背景，或按 `references/image-generation.md` 的原生透明 fallback；从已有图片提取透明对象、mask、cutout、修边、去背景和导出变体必须交给 `aisee:image-object`，本 skill 只登记最终产物。
- 局部内容优化先分流：松散的视觉增强、氛围补充、背景丰富度、构图微调可由本 skill 生成受控编辑候选；需要像素级范围、mask、对象边缘、抠图、局部抹除或背景修补时必须交给 `aisee:image-object` 准备 handoff。
- 项目绑定图片、prompt 摘要、索引和 brief 必须写入目标项目目录。
- Prompt 只注入当前任务必要约束，不把全部规则一次性塞进图片模型请求；通用 UI 图标只做占位，最终由图标库替换。

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

最终回复使用中文，说明生成目标、使用方式、输出路径、规范/素材清单路径、复核结论和风险。未实际生成图片时，只输出可执行方案、提示词和建议目录，不声称已生成。
