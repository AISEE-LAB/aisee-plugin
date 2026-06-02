---
name: aisee:image-object
description: 对象级图片处理工作流。用于从单张图片中分离对象、去背景、生成或修正 mask、点选/框选分割、透明切图、导出带背景/圆角/padding 的素材变体、背景修补、生成图层包和维护单图 source.json workspace 时触发。不要用于参考图生成、StyleSpec、全局视觉规范、Figma 写入或前端实现。
---

# aisee:image-object

把一张输入图处理成可复用对象素材、mask、背景修补图、导出变体和图层包。skill 目录只保存说明、模板和脚本；所有项目产物写入目标项目目录。

## 适用输入

- 本地 PNG/JPG/WebP 图片路径
- 用户要求抠图、去背景、对象分割、透明素材、局部 mask、点选/框选、切图、图层拆分或背景修补
- 已有 mask / alpha 图，需要 refine、羽化、扩缩边、导出圆角或加背景
- 需要把对象素材整理成可复用 workspace 和 `source.json`
- 需要在同一张图上框选多个区域，并分别生成素材、修补背景或导出变体
- 需要把过程文件交给大模型做局部优化、局部重绘、边缘修复、背景语义修补或候选重生成

## 边界

必须：

- 使用单图 workspace 管理产物，默认输出到 `aisee/docs/image-objects/<name>/`。
- `source.json` 是 GUI、CLI、模型后端和导出流程的共同合同。
- 成熟模型优先：去背景主路径使用 rembg 已集成模型，优先 BiRefNet 类模型；U²-Net 作为兼容 fallback。
- SAM/SAM2、LaMa、BiRefNet 等依赖按可选 backend 处理，缺失时给出中文安装/配置提示，不伪造结果。
- 背景修补优先使用 LaMa / IOPaint；OpenCV 只作为用户显式 fallback，不作为质量主路径。
- 原始 cutout/mask 与导出变体分开保存；透明、背景、圆角、padding、裁切模式属于导出设置。
- 区域、素材、修补和导出都必须记录明确 scope，不隐式作用于整图。
- 图生图或局部修改时保护原图风格、品牌元素、未遮罩区域和对象比例。
- 过程文件也是可复用输入：`regions`、`masks`、`cutouts`、`backgrounds`、`exports` 和 `enhanced` 都可以被整理成大模型局部编辑 handoff，但必须只携带相关 scope、参考图、mask 和用户要求。

不要：

- 不生成参考图、StyleSpec 或全局设计提示词；这些交给 `aisee:design-assets`。
- 不直接写入 Figma 或实现前端页面。
- 不把 GUI 中的对象备注当作全局图片生成 prompt。
- 不把整个 `source.json`、全部缩略图或 `preview-cache/` 默认塞进大模型提示；只摘取本次任务相关的对象、mask、bbox、路径和保护约束。
- 不默认覆盖 workspace 内已有产物，除非用户明确要求或传入 `--force`。
- 不保存、输出或提交 API Key、令牌、Cookie、证书等敏感信息。

## OpenSpec 接入

当对象素材进入 OpenSpec change：

- `ui-contract.md` 只引用 cutout、mask、export 或图层包路径，以及本次页面/组件使用范围。
- `source-map.md` 记录 IMG/OBJECT/MASK 与 PAGE、PAT、FR、tasks 和文件路径的关系。
- `tasks.md` 只记录素材接入、边缘复核、背景验证、截图比对或人工验收任务。
- 不把完整 `source.json`、全部过程图、mask 历史或 workspace 索引正文复制进 change artifacts；长期对象事实保留在 `aisee/docs/image-objects/`。

## Phase 0 — 读取上下文

先定位目标项目目录：用户给了项目路径就用该路径，否则使用当前工作目录。

静默收集已有对象处理产物：

```bash
find aisee/docs/image-objects -maxdepth 4 -type f 2>/dev/null | head -80
find . -maxdepth 4 \( -iname 'source.json' -o -iname '*mask*.png' -o -iname '*cutout*.png' \) 2>/dev/null | head -80
```

如果已有 workspace，先读取 `source.json`，避免重复命名、重复导出或覆盖用户手工修正的 mask。

## Phase 1 — 选择最小闭环

按用户意图选择最小流程，并只读取相关 reference：

- 单图 workspace、source.json 合同：读 `references/source-json.md`
- 单图产物目录和命名规范：读 `references/output-layout.md`
- 依赖检查、安装和可选 backend：读 `references/dependencies.md`
- 抠图、去背景、点选/框选模型：读 `references/model-backends.md`
- GUI 双画布和中文界面：读 `references/gui-design.md`
- 透明切图、背景、圆角、padding、图层包：读 `references/export-options.md`
- 端到端流程：读 `references/workflows.md`

常见闭环：

1. 有原图，要去背景：`init` → `remove-bg` → `export-variant`
2. 有原图，要点选/框选分割：`init` → `segment-point` / `segment-box` → `extract-object`
3. 已有 mask，要修边：`refine-mask` → `extract-object` → `export-variant`
4. 要背景修补：`inpaint-background`，默认优先 LaMa；必要时显式 `--fallback-opencv`
5. 要人工查看和微调：启动 `select --interactive`，使用 PySide6 双画布 GUI；GUI 支持框选 region、先预览后确认区域属性、从 region 生成 Mask、从 Mask 提取 Cutout、缩略图素材栏、画布定位预览和区域/Cutout 单素材导出。

## Phase 2 — 输入门禁

信息不足时最多追问 3 个会影响结果的问题：

- 输入图片或 workspace 路径不明确
- 目标对象不明确，且自动分割可能产生多个对象
- 导出是否透明、背景颜色、圆角、padding 或尺寸要求不明确

低风险默认：

- 输出目录：`aisee/docs/image-objects/<源文件名>/`
- 模型 profile：`quality`
- 导出：透明 PNG、按对象 BBox 裁切、无圆角、无 padding
- GUI 文案：中文；Mask、Cutout、Alpha、SAM、BBox 等专业术语可保留

## Phase 3 — 执行

内置脚本：

- `scripts/image_object_tool.py`：CLI 入口
- `scripts/gui/app.py`：PySide6 GUI 入口
- `scripts/check_dependencies.py`：依赖检查入口

示例：

```bash
python aisee-image-object/scripts/check_dependencies.py
python aisee-image-object/scripts/image_object_tool.py config-preview
python aisee-image-object/scripts/image_object_tool.py init --input input.png --output aisee/docs/image-objects/input
python aisee-image-object/scripts/image_object_tool.py remove-bg --workspace aisee/docs/image-objects/input --profile quality
python aisee-image-object/scripts/image_object_tool.py export-variant --workspace aisee/docs/image-objects/input --object-id obj_001 --transparent true --corner-radius 0 --padding 0
python aisee-image-object/scripts/image_object_tool.py select --workspace aisee/docs/image-objects/input --interactive
```

Image Gen 深度优化不放入 GUI 第一版。需要深度优化时，在对话中基于 `source.json` 的相关条目、mask、cutout、background/export 过程文件和用户要求，与 `aisee:design-assets` 协作生成受控图片编辑提示词、参考约束和产物索引；GUI 只负责展示已经落到 `enhanced/` 的候选结果。

生成 handoff 时保持轻量：

- 输入只列本次要编辑的 `source`、`region`/`mask`/`object`/`background`/`export` 路径和 bbox。
- 约束只写必要的风格一致性、品牌保留、未遮罩区域保护、输出尺寸/格式。
- 如果任务是局部抹除或局部重绘，必须明确 mask 或用户标记区域；不要让大模型自由改整张图。
- 输出候选统一写入 `enhanced/`，提示词或编辑 brief 用同一个 `enh_###` 前缀保存。

## Phase 4 — 更新状态

每次生成 mask、cutout、background、export 或 enhanced 候选，都更新 `source.json`：

- 记录输入、模型、参数、产物路径、尺寸、BBox、透明/背景设置、用户备注和操作历史。
- 对大模型优化候选记录 `input_refs` / `prompt_ref` / `style_lock` / `scope`，让候选图可以追溯到具体过程文件。
- 记录 fallback 或依赖缺失原因。
- 路径尽量写 workspace 相对路径，便于迁移。

## Phase 5 — 交付

最终回复使用中文，说明：

- 输入图和 workspace
- 已生成的 mask、cutout、background、export 或图层包路径
- 使用的模型/backend 和 fallback
- 已运行的验证
- 未安装可选依赖时的影响和下一步命令
