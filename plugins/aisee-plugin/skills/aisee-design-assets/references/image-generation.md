# 图像生成与脚本约定

## 决策

先检查当前会话工具列表是否存在内置 `image_gen` / `image_gen.imagegen`。这是会话工具检测，不是 shell 检测；不能用 `which image_gen` 或查找本地脚本判断。

参考图、视觉变体和生成型素材默认使用 Image2。内置 `image_gen` 可用时优先走内置工具；CLI/API fallback 默认显式指定 `gpt-image-2`。只有原生透明 PNG 等 Image2 不支持的能力，才使用其它模型并在交付中说明原因。

优先使用内置 `image_gen`：

- 普通参考图、视觉草图、背景、插画和素材探索
- 基于已有图片生成视觉变体
- 已有 UI 效果图的保结构重绘
- 简单透明素材：生成纯色绿幕图，再本地去背景

使用 CLI fallback：

- 内置 `image_gen` 不可用
- 用户明确要求脚本、API、模型、base_url 或本地 CLI
- 需要固定模型、精确尺寸、输出格式、图生图视觉变体或批量
- 需要原生透明 PNG

不要仅因为要保存到固定路径或常规尺寸就放弃内置工具；内置工具生成后把选中结果复制或移动到项目本地即可。不要把 CLI 结果描述成内置 `image_gen` 结果。

## 脚本边界

`scripts/image_gen.py` 是生成和编辑 API 入口，保留用于：

- 文生图参考图
- 图生图和保结构重绘
- 与 `aisee:image-object` 协作时的受控编辑候选
- 固定模型、尺寸、格式或批量生成

它不负责：

- 去背景
- 生成或管理 mask
- SAM / SAM 2 分割
- mask 后处理
- 对象透明 PNG 提取
- 本地背景修补
- 图层包或单图对象状态文件

遇到对象分离、抠图、对象图层、背景修补、素材提取或交互式框选/点选时，转给 `aisee:image-object`；本 skill 只接收结果并登记到设计资产目录。

## UI 效果图编辑

已有 App、小程序、H5、PC 页面效果图要求“再生成一版”“更高保真”“更符合手机端”“不要变结构”时，按 `references/workflow.md` 的 `structure-locked redraw` 执行。

如果 CLI text-to-image 或 CLI edit 出现明显业务结构漂移，不继续堆 prompt，改用内置 `image_gen`、Figma MCP、确定性图像处理或页面重绘。

## 图生图视觉变体

图生图视觉变体默认是受控修改，不是重新设计。除非用户明确要求重设风格，否则：

- 保护 Logo、品牌色、品牌字体、品牌图形、吉祥物、IP 形象等品牌元素。
- 保持导航、卡片、按钮、模块位置、留白节奏和信息层级。
- 保持线条粗细、圆角、阴影、材质、插画风格、摄影风格、色彩系统和图标风格。
- 不应变动区域默认保持不变，尤其是文字、Logo、产品名和关键数据。

只在视觉变体或保结构重绘任务中加入最小保留约束：

```text
Preserve the original brand identity, layout structure, visual style, color system, typography hierarchy, and icon style. Only modify the requested area or elements. Keep unmasked areas unchanged.
```

涉及 Logo、品牌标识、真实产品图或文字密集 UI 时，不要求模型重画这些细节；优先保留原像素、确定性贴图、Figma 或前端实现。

如果任务需要 mask、bbox、对象 cutout、背景修补或从已有图片提取素材，先进入 `aisee:image-object` 建立 workspace；本 skill 只能根据 image-object 的 handoff brief 生成受控编辑提示词或登记最终候选。

## 局部内容优化

局部内容优化是图生图编辑的一种受控候选生成，先由 `references/prompt-optimization.md` 理解用户意图并整理 prompt。

留在本 skill 的场景：

- 丰富 banner 背景、Hero 氛围、插画细节、装饰层、光影或留白安全区。
- 基于参考图生成更完整的视觉候选，但不要求像素级只改某个对象。
- 对生成型素材做风格一致的局部完善。

转交 `aisee:image-object` 的场景：

- 用户要求只改具体对象、边缘、背景残留、抠图、透明、mask 范围或背景修补。
- 需要 bbox、mask、cutout、source/object 对齐或交互式框选。
- 结果需要回写 image-object workspace 的 `enhanced/`。

CLI 示例：

```bash
python <skill-dir>/scripts/image_gen.py edit \
  --model gpt-image-2 \
  --image aisee/docs/design-assets/references/hero-reference.png \
  --prompt "<局部内容优化 prompt：写清用户意图、局部范围、保留项、修改项、文本策略和避免项>" \
  --out aisee/docs/design-assets/edits/hero-reference-local-001.png
```

没有 mask/bbox 的局部优化只能作为视觉候选；交付时必须标注“松散范围，需人工复核未授权区域是否变化”。

## API 配置

真实 API 调用必须显式配置 `api_key` 和 `base_url`，不依赖 SDK 默认地址。配置来源：

```text
OPENAI_API_KEY
OPENAI_BASE_URL
AISEE_IMAGEGEN_CONFIG
aisee/config/design-assets/openai.local.json
```

默认配置文件格式见 `assets/openai-config-template.json`。

优先级：

```text
--base-url > OPENAI_BASE_URL > config.base_url
OPENAI_API_KEY > config.api_key
--config > AISEE_IMAGEGEN_CONFIG > aisee/config/design-assets/openai.local.json
```

约束：

- 不提供 `--api-key` 参数，避免进入 shell history。
- 配置文件必须加入项目 `.gitignore`，不要提交。
- 不把 API Key 写入文件、日志、截图或交付说明。
- 运行时图片、索引和临时文件都写入目标项目目录，不写入 skill 目录。

## 模型与尺寸

模型：

- 常规生成和编辑：`gpt-image-2`
- 原生透明 PNG：`gpt-image-1.5 --background transparent --output-format png`
- `gpt-image-2` 不支持 `background=transparent`

常用 CLI 示例尺寸：

| 用途 | 建议尺寸 |
|------|----------|
| 移动端 / 小程序参考图 | `1024x1536` |
| 移动端 Hero / Banner | `1248x624` |
| PC Web 页面参考图 | `1536x1024` |
| PC / Web Hero 背景 | `2048x1152` |
| 大屏 / 展示页 | `3840x2160` |
| 方形插画或复杂素材 | `1024x1024` |

`gpt-image-2` 尺寸约束：宽高都是 16 的倍数，最大边不超过 3840px，长短边比例不超过 3:1，总像素在 655,360 到 8,294,400 之间。

不同端的推荐尺寸、安全区和素材尺寸按 `references/output-specs.md` 选择。不要把图标和小 UI 素材统一生成到 `1024x1024` 以上；尺寸应按最终展示面积反推。真实设备尺寸不满足模型或脚本约束时，先生成接近比例的合规尺寸，再裁切或缩放。

## CLI 最小用法

生成：

```bash
python <skill-dir>/scripts/image_gen.py generate \
  --model gpt-image-2 \
  --prompt "<prompt>" \
  --size 1536x1024 \
  --quality high \
  --output-format png \
  --out aisee/docs/design-assets/references/reference-001.png
```

图生图视觉变体：

```bash
python <skill-dir>/scripts/image_gen.py edit \
  --model gpt-image-2 \
  --image aisee/docs/design-assets/references/reference-001.png \
  --prompt "<只描述要改的内容，同时写清保留项>" \
  --out aisee/docs/design-assets/edits/reference-001-edit-001.png
```

来自 `aisee:image-object` 的局部编辑 handoff：

```bash
python <skill-dir>/scripts/image_gen.py edit \
  --model gpt-image-2 \
  --image input.png \
  --mask mask.png \
  --prompt "只修改 mask 区域，其他区域保持不变。" \
  --out output.png
```

这种调用必须由 `aisee:image-object` 提供 source、mask、bbox、保护约束和目标路径。脚本只保留 Images API 的 `generate`、`edit` 和 `generate-batch` 子命令；多轮意图、版本关系和追溯信息由本 skill 的索引、manifest、brief 或 image-object 的 `source.json` 记录。

## 透明素材

先分流：

- 从零生成透明素材：属于 `aisee:design-assets`。先完成 prompt 优化和一致性合同，再按下面的绿幕/纯色背景或原生透明 fallback 生成。
- 从已有图片提取透明素材：属于 `aisee:image-object`。包括抠图、去背景、mask、cutout、修边、alpha、导出透明 PNG/WebP、圆角、padding、图层包和背景修补。本 skill 只登记 image-object 的 export/cutout/enhanced 结果。
- 基于 image-object 过程文件做局部增强：由 `aisee:image-object` 提供 source、mask、bbox、object/cutout 和保护约束，本 skill 只帮助整理 Image2 受控编辑 prompt，候选图仍回写 image-object workspace。

简单、边缘清晰的素材优先走内置 `image_gen` 绿幕方案，再用本地脚本去背景：

```bash
python <skill-dir>/scripts/remove_chroma_key.py \
  --input tmp/imagegen/input-green.png \
  --out aisee/docs/design-assets/assets/transparent/output-transparent.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

绿幕提示词追加：

```text
Create the requested subject on a perfectly flat solid #00ff00 chroma-key background for background removal.
The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation.
Keep the subject fully separated from the background with crisp edges and generous padding.
Do not use #00ff00 anywhere in the subject.
No cast shadow, no contact shadow, no reflection, no watermark, and no text unless explicitly requested.
```

复杂边缘、半透明、发光、玻璃、烟雾、液体或用户明确要求原生透明时，使用 CLI：

```bash
python <skill-dir>/scripts/image_gen.py generate \
  --model gpt-image-1.5 \
  --prompt "<独立主体，无文字、水印或背景>" \
  --background transparent \
  --output-format png \
  --quality high \
  --out aisee/docs/design-assets/assets/transparent/asset-001.png
```

通用 UI 图标不走透明素材生图流程，优先使用 SVG 图标库。小型透明 UI 素材通常使用 `256x256` 或 `512x512`；只有复杂插画、角色、营销视觉或大面积背景装饰才使用 `1024+`。

## Prompt 基本结构

脚本默认启用 `--augment`，会把用户 prompt 和提示字段组织成结构化 prompt。需要完全原样传递时使用 `--no-augment`。

```text
目标平台：
页面/素材用途：
视觉定位：
构图：
主体：
背景：
色彩：
参考依据：
必须保留：
必须避免：
输出要求：
```

生成参考图时避免在图中放置真实业务文字，除非用户明确要求。生成素材时避免文字、Logo、水印和无关 UI 控件。

涉及通用图标时，不把完整图标库列表写入 prompt。只说明使用标准图标占位，并在 manifest 或 brief 中记录最终推荐库和图标语义。
