# 工作流

## 参考图生成

目标是探索视觉方向，不是交付最终设计稿。

步骤：

1. 确认平台、页面场景、目标用户、业务语气和禁用元素。
2. 按需读取 `references/output-specs.md` 选择尺寸、比例和安全区。
3. 涉及通用图标或组件风格时，读取 `references/icon-library.md`，只生成图标占位和图标清单。
4. 按 `references/image-generation.md` 选择内置 `image_gen` 或 CLI fallback。
5. 内置模式生成后按需裁切、缩放或移动到项目本地。
6. 生成参考图：
   - 单页面 / 单状态视觉方向：生成 2-4 张候选。
   - 长页面 / Landing / 多 section：按 section 生成清晰参考图，不合并成单张超长图。
   - App / 小程序 / H5 多状态：按页面或关键状态生成，不把列表、详情、表单、空状态压缩在一张图里。
7. 保存到 `aisee/docs/design-assets/references/`，更新 `index.md` / `index.json`。
8. 让用户选择主参考图，或基于反馈重做。

候选说明包含视觉方向、适用场景、差异点和风险。

当任务主要是视觉质量、重设计、图片转视觉 brief 或用户上传参考图时，必须同时读取 `references/image-first.md`，先完成参考图分析，再输出 StyleSpec 草稿、Figma brief 或 dev-visual-brief。

## Structure-locked redraw

当用户要求“基于已有 UI 效果图重新生成”“更符合手机端”“更高保真”“重新出一版但不要变结构”时，默认进入 `structure-locked redraw`。

规则：

- 保留页面信息架构、模块顺序、卡片数量、列表数量、底部导航数量和业务含义。
- 只优化视觉表现：比例、间距、圆角、阴影、色彩、图标风格、Hero 高度和整体精致度。
- 文字允许轻微生成误差；文字精度是硬要求时，改用 Figma、HTML/CSS 或前端代码叠字。
- 不替换业务模块、不改变导航语义、不增加未确认模块、不把行业主题改成另一套产品结构。
- Prompt 必须明确列出要保留的模块和业务含义，不能只说“参考原图”。

示例约束：

```text
这是 structure-locked redraw，不是重新设计。
保留原页面的信息架构和业务含义：
- 入口卡片：关于 CNEX、资质授权、标准化平台
- 权威实力：国家中心、CNAS 认可、IECEx / ATEX
- 新闻公告：公司新闻、通知公告、培训通知
- 底部导航：宣传展示、业务指南、证书查询，第一项高亮
允许文字有轻微生成误差，后续会在 Figma 中修正；但不得替换业务结构、不得改变模块语义。
```

## 从参考图提取设计规范

1. 明确来源参考图。
2. 识别颜色、构图、层级、图形语言、素材类型、组件形态、布局节奏、可实现性和禁用项。
3. 输出 Markdown StyleSpec；需要结构化复用时同时输出 JSON。
4. 保存到 `aisee/docs/design-assets/specs/`，更新索引。

## 基于规范生成新设计图

1. 读取 StyleSpec。
2. 确认新图的页面、场景和平台。
3. 保留核心视觉规则，只改变页面内容目标。
4. 保存新参考图到 `references/`，记录依赖的 StyleSpec。

## 素材生成

1. 先做 Asset Intent Scan：识别参考图/页面中哪些元素是生成型素材、UI 文案、图标库、CSS/SVG、既有品牌资产或 image-object 对象。
2. 明确 `generation_decision`、`asset_boundary` 和 `text_policy`，尤其是 banner、运营位、海报、电商图和透明素材。
3. 按背景、图标、插画、装饰层、布局视觉层、生成型透明素材和提取型对象素材分组。
4. 确认用途、尺寸、透明需求、来源依据和素材来源模式。
5. 通用图标优先映射图标库；不要用图片模型重画常见操作、导航和状态图标。
6. 生成型背景、插画、装饰层和生成型透明素材由本 skill 生成。
7. Banner 默认只生成背景/插画/装饰层，不生成标题、价格、按钮文案或角标；只有最终投放图且用户确认文字不可编辑风险时，才允许 raster text。
8. 从已有图片提取素材、去背景、mask、cutout、背景修补或图层包，转交 `aisee:image-object`。
9. 保存生成型素材到 `aisee/docs/design-assets/assets/`；提取型素材只登记 `aisee:image-object` 的最终 export/cutout/enhanced 路径。
10. 更新 `manifests/asset-manifest.md`。

## 图生图视觉变体

1. 只处理“保结构重绘 / 视觉变体 / 参考图再生成”。
2. 明确源图、保留项、允许变化项和输出目标。
3. 默认保持品牌元素、布局结构、视觉风格、色彩系统、字体层级、图标风格和不应变动区域。
4. 涉及 Logo、品牌标识、真实产品图或文字密集 UI 时，优先保留原像素、确定性贴图、Figma 或前端实现。
5. 需要 mask、bbox、cutout、局部抹除、背景修补或素材提取时，转交 `aisee:image-object` 建立 workspace。
6. 输出新版本，不覆盖原图。
7. 在索引中记录源图、保留项、修改项和风险。

## 局部内容优化

当用户要求“局部优化”“补充细节”“让某个区域更完整”“增强氛围”“让 banner 更像参考图”时，先理解意图再决定执行路径。

1. 摘要用户意图：要解决空、乱、不统一、不够精致、主体不突出、局部细节不足，还是需要扩展安全区。
2. 明确 scope：整图、section、banner 背景、插画主体、装饰层、自然语言区域、mask、bbox 或 object id。
3. 判断是否需要 `aisee:image-object`：只要涉及精确对象、边缘、抠图、透明、局部抹除、背景修补或 mask/bbox，就先交给 image-object。
4. 对松散视觉增强，由本 skill 按 `assets/prompt-template-edit.md` 生成受控编辑 prompt，并使用 Image2 生成候选。
5. Prompt 必须写清保留项、修改项、文本策略和避免项；Banner/App/Web 默认不生成文字，只保留可编辑文字区。
6. 输出到 `aisee/docs/design-assets/edits/`，不覆盖源图；在索引或 manifest 记录源图、scope、prompt 摘要、风险和 consistency_check。
