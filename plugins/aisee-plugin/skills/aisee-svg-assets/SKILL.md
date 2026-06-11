---
name: aisee:svg-assets
description: 通用 SVG 资产生成、位图矢量化、按参考图准确重绘 SVG、SVG logo 设计、SVG 优化与校验工作流。用于用户要求根据描述生成 SVG 图标、线性图标、多色图标、装饰图形、简单插画、logo-like mark、品牌标识、wordmark、lettermark、组合标；将 PNG/JPG/WebP 转为 SVG；基于位图先识别理解原图内容再分步骤绘制可维护 SVG；使用 VTracer 矢量化简单位图；清理、压缩、校验已有 SVG；生成适合前端 inline SVG、Figma 导入、图标库、文档插图或设计资产库使用的 SVG 时必须触发。通用 UI 图标优先使用成熟图标库并记录库名和图标名，不默认重新创造。不要用于复杂照片级精确还原、完整 UI 页面转 SVG、Figma 文件写入、商标法律审查、生成位图参考图、图片编辑、对象分离、去背景、mask 或背景修补工作流。
---

# aisee:svg-assets — SVG 生成与位图矢量化

生成、转换、优化和校验项目本地 SVG 资产。skill 目录只保存脚本、模板和说明；所有 SVG、报告、索引和转换结果都写入目标项目目录。优先完成一个可验证的小闭环：产物文件、校验报告、索引记录和交付说明。

## 输入

用户提供以下任意一种输入：

- SVG 图标、装饰图形、简单插画的文字描述
- Logo、brand mark、wordmark、lettermark 或组合标需求
- 需要转为 SVG 或作为 SVG 重绘参考的 PNG/JPG/WebP 路径
- 需要清理、优化或校验的 SVG 路径
- 目标用途：frontend inline、icon library、Figma import、docs illustration、design asset

可选参数：

- `--mode generate|logo|trace|optimize|validate|auto`，默认 `auto`
- `--style line|filled|duotone|multi-color|logo-mark|decorative|illustration`
- `--out <dir>`，默认 `aisee/docs/svg-assets/`
- `--name <asset-slug>`，用于稳定命名文件和索引 ID
- `--preset icon-color|icon-bw|logo|illustration`，仅用于位图矢量化

## 输出边界

必须做：

- 输出统一保存到项目本地 `aisee/docs/svg-assets/`，除非用户明确指定其他项目内目录
- PNG/JPG/WebP 转 SVG 前先识别原图内容、结构、图层、颜色和文字；只有简单扁平图形才优先使用 Python `vtracer` 包，失败后 fallback 到 `vtracer` CLI
- 需要可维护、语义准确或按参考图还原的 SVG 时，按 brief 分步骤重绘，不把 VTracer 输出直接当最终设计。
- 校验 SVG 是否包含 `viewBox`，是否存在脚本、事件属性、外链、`foreignObject` 等风险
- 更新 `aisee/docs/svg-assets/index.md` / `index.json`；如果用户只要求审查且不希望改文件，说明建议更新项
- 任何写入前先确认不会覆盖同名文件；需要覆盖时使用明确的 `--force` 或用户确认
- 直接生成的 SVG 必须包含 `viewBox`；面向可访问展示的图形应包含 `<title>` 和 `<desc>`，纯装饰图可使用 `aria-hidden="true"`
- 通用 UI 图标、导航图标、操作图标和状态图标优先使用图标库；可用 `better-icons` 或 Iconify 生态检索候选，交付时说明使用的图标库和 `prefix:name`，只有库中没有合适表达或存在品牌/业务专属图形时才绘制自定义 SVG。

不要做：

- 不承诺照片级精确矢量还原
- 不把复杂 UI 页面转换成可维护 SVG 设计稿
- 不把图片中文字精确 OCR 成可编辑文本
- 不直接写入 Figma 文件
- 不做商标可注册性、侵权或法律风险判断
- 不生成位图参考图；这属于 `aisee:design-assets`
- 不做对象分离、去背景、mask 生产或背景修补；这些属于对象处理工作流

## 职责分流

- 用户要“生成位图参考图、App 截图风格图、视觉方向图、插画背景、图片编辑提示词”：转 `aisee:design-assets`。
- 用户要“从图片中抠出对象、去背景、修 mask、补背景、导出透明 PNG/WebP”：转 `aisee:image-object`。
- 用户要“把简单图标、logo-like mark、线稿、扁平图形转成 SVG”：留在本 skill，先判断 `trace` 还是 `redraw`。
- 用户要“把 PNG/JPG 里的图形准确画成可维护 SVG”：留在本 skill，用 `redraw` 流程先做识别 brief，再按图层分步骤绘制。
- 用户要“常见搜索、关闭、返回、设置、删除、状态等 UI 图标”：优先映射图标库并记录来源，不重新发明图形。
- 用户给的是完整 UI 截图或复杂照片，只能提取可重建的 SVG 子资产建议；不要承诺整图 SVG 复刻。

## OpenSpec 接入

当 SVG 资产进入 OpenSpec change：

- `ui-contract.md` 只引用 SVG 文件、用途、状态、可访问性要求和本次页面/组件适用范围。
- `source-map.md` 记录 ICON/SVG/LOGO 与 PAGE、PAT、FR、tasks 和文件路径的关系。
- `tasks.md` 只记录接入、替换、校验、截图比对或设计确认任务。
- 不把完整 SVG 源码、矢量化报告或资产索引正文复制进 change artifacts；长期资产事实保留在 `aisee/docs/svg-assets/`。

## Phase 0 — 读取上下文

先定位目标项目目录。若用户给了项目路径，在该路径下工作；否则使用当前工作目录。

静默收集已有 SVG 资产：

```bash
rg --files aisee/docs/svg-assets 2>/dev/null | head -80
rg --files | rg '\.svg$|svg.*index.*\.md$|svg.*manifest.*\.md$' | head -80
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，并只查 SVG 资产需要的文件类型。

Fallback 示例：

```bash
find . \
  -path './.git' -prune -o \
  -path './node_modules' -prune -o \
  -path './dist' -prune -o \
  -path './build' -prune -o \
  -path './.next' -prune -o \
  -path './aisee/cache' -prune -o \
  -type f \( -name '*.svg' -o -name '*svg*index*.md' -o -name '*svg*manifest*.md' \) -print | head -80
```

若存在 `aisee/docs/svg-assets/index.md` 或 `index.json`，先读取，避免重复命名、覆盖旧资产或让索引漂移。

## Phase 1 — 判断任务模式

- 根据描述生成 SVG：读 `references/svg-generation.md`
- Logo / brand mark 设计：读 `references/logo-design.md`，并先执行其中的强制需求澄清
- PNG/JPG/WebP 转 SVG 或按位图重绘 SVG：读 `references/png-to-svg.md`
- 优化或校验 SVG：读 `references/svg-validation.md`
- 输出目录和索引：读 `references/output-layout.md`

`auto` 模式：

1. 用户提供位图路径并要求 SVG：先读图并形成重建 brief；简单扁平图形使用 `trace`，需要准确语义、可维护结构或复杂局部还原时使用 `redraw`
2. 用户提供 SVG 路径并要求压缩、清理、检查：使用 `optimize` 或 `validate`；若会生成新文件，优先 `optimize` 后 `validate`
3. 用户要求 logo、品牌标识、wordmark、lettermark、组合标：使用 `logo`
4. 用户只给描述并要求通用 UI 图标：先映射项目已有图标库；需要跨库查找且工具可用时使用 `better-icons` / Iconify；只有确需自定义时使用 `generate`
5. 用户只给描述并要求专属图形、装饰图形或简单插画：使用 `generate`，直接生成 SVG 代码

Logo 模式的执行门槛：

- 用户请求 logo、品牌标识、brand mark、wordmark、lettermark、组合标时，不要直接进入 SVG 生成。
- 先向用户提出 1-3 个关键问题，至少确认品牌/产品名称、风格方向、主要使用场景。
- 只有当用户在同一条消息中已经给出足够约束，或明确表示“不用问、直接生成、快速出稿”时，才可以基于合理假设继续。
- 如果基于假设继续，必须在输出中标注这些假设。

CHECKPOINT: 生成 logo / brand mark / wordmark / lettermark 前，或任何操作会覆盖既有 SVG、索引或报告前，必须确认品牌名称、用途、风格方向、输出路径和覆盖策略。未确认时停在提问或输出草案方案，不创建或覆盖文件。

CHECKPOINT: 安装 `vtracer`、`cargo install vtracer`、使用 `--allow-unsafe`、处理疑似敏感图片或商标素材前，必须说明影响并等待用户确认；不能把这些动作作为静默前置步骤。若用户要求调用图片生成/编辑模型，先按“职责分流”判断是否应转 `aisee:design-assets` 或 `aisee:image-object`。

## Phase 2 — 依赖检测

只在 `trace` 模式下检查 VTracer。其他模式不要求安装额外依赖。

```bash
python -c "import vtracer; print('python-vtracer=present')" 2>/dev/null || true
command -v vtracer >/dev/null && echo "vtracer-cli=present" || true
```

安装建议：

```bash
pip install vtracer
```

备用：

```bash
cargo install vtracer
```

## Phase 3 — 执行

项目内脚本：

- `scripts/trace_bitmap.py`：位图转 SVG，优先 Python API，fallback CLI
- `scripts/optimize_svg.py`：基础 SVG 清理，默认拒绝已知不安全输入
- `scripts/validate_svg.py`：安全、结构、可访问性和复用性校验

SVG 绘制以准确还原为目标。对位图来源或参考图来源，先完成四步：

1. 识别：说明原图主体、语义、几何结构、颜色、线条、阴影、文字和不可还原项。
2. 分解：把图拆成背景、主体轮廓、内部细节、装饰、文字或状态层，并确定 `viewBox`。
3. 绘制：按图层逐步创建 SVG，优先使用可读的基础形状；必要 path 应对应明确图层。
4. 复核：对照原图检查比例、位置、颜色、语义、可读性和小尺寸表现。

简单图标优先映射图标库；确需自定义时直接写 SVG。简单位图可使用 VTracer，但 VTracer 输出必须经过人工判断、优化和校验。生成或转换后的 SVG 必须运行校验脚本；校验失败时不要把结果描述为可直接使用。

Logo 模式在执行前必须满足 Phase 1 的澄清门槛；如果信息不足，停在提问，不要创建或覆盖 logo 文件。

## Phase 4 — 索引和报告

每个最终 SVG 建议至少有一条索引记录：

- `id`：稳定 slug
- `file`：相对 `aisee/docs/svg-assets/` 的路径
- `source`：`local-generation` / `bitmap-trace` / `user-provided-svg` / `optimized-svg`
- `usage`：目标用途
- `method`：`icon-library` / `handwritten-svg` / `redraw-from-bitmap` / `python-vtracer` / `vtracer-cli` / `optimize-svg`
- `icon_library`：通用图标使用的库名和图标名；不适用时写 `N/A`
- `reconstruction_brief`：位图重绘或矢量化时的识别和分解 brief 路径或摘要
- `accuracy_check`：比例、颜色、语义和小尺寸可读性的复核结论
- `validation`：`passed` / `warnings` / `failed`
- `notes`：只记录必要事实，不写敏感信息或冗长过程

校验报告保存到 `aisee/docs/svg-assets/reports/<asset>.validate.json`。位图转换报告可保存到 `aisee/docs/svg-assets/reports/<asset>.trace.json`。

## Phase 5 — 交付

最终回复使用中文，包含：

- 任务类型和输出路径
- 使用方式：直接 SVG / Python vtracer / vtracer CLI / optimize / validate
- 校验结果和风险
- 是否适合 inline SVG、Figma 导入或图标库复用
- 未完成的限制：例如缺依赖、信息不足、校验失败或只生成了草案
