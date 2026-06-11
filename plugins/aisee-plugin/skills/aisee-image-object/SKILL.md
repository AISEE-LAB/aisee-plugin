---
name: aisee:image-object
description: 对象级图片处理与素材提取工作流。用于从单张图片中分离对象、基于图片提取素材、去背景、生成或修正 mask、点选/框选分割、透明切图、导出带背景/圆角/padding 的素材变体、背景修补、生成图层包和维护单图 source.json workspace 时触发。不要用于参考图生成、StyleSpec、全局视觉规范、Figma 写入或前端实现。
---

# aisee:image-object

把一张输入图处理成可复用对象素材、mask、背景修补图、导出变体和图层包。凡是“基于已有图片提取素材、切出素材、生成透明对象、修补背景或局部重绘”的执行流程，都归本 skill 管理。它是图片处理 workflow，不是图片生成或设计规范 skill；skill 目录只保存说明、模板和脚本，项目产物写入目标项目目录。

## 适用输入

- 本地 PNG/JPG/WebP、已有 mask/alpha、或 `aisee:design-assets` 生成的纯色/绿幕主体图。
- 抠图、去背景、对象分割、点选/框选、mask refine、透明切图、圆角/padding 导出、背景修补或图层拆分。
- 从截图、海报、参考图或产品图提取一个或多个可复用对象素材。
- 需要把过程文件整理成单图 workspace、`source.json`、导出变体或 Image Gen 局部优化 handoff。

## 边界

必须：

- 使用单图 workspace 管理产物，默认输出到 `aisee/docs/image-objects/<name>/`。
- `source.json` 是 GUI、CLI、模型 backend、导出和 handoff 的共同合同。
- 每次处理都明确 scope；原始 mask/cutout/background 与导出变体分开保存。
- 去背景优先成熟模型；背景修补优先 LaMa / IOPaint，OpenCV 只作显式低质量 fallback。
- SAM/SAM2、LaMa、BiRefNet 等作为可选 backend；运行环境优先复用全局配置，不重复配置重依赖。
- 局部重绘或 Image Gen handoff 只携带相关 source/mask/bbox/cutout/scope 和保护约束。
- 可复用素材进入项目级视觉资产库时，只把 export/cutout/enhanced 路径和用途交给 `aisee:design-assets` 登记。

不要：

- 不生成参考图、StyleSpec 或全局设计提示词；这些交给 `aisee:design-assets`。
- 不直接写入 Figma 或实现前端页面。
- 不把 GUI 对象备注、整个 `source.json`、全部缩略图或 `preview-cache/` 默认塞进大模型提示。
- 不默认覆盖 workspace 内已有产物，除非用户明确要求或传入 `--force`。
- 不保存、输出或提交 API Key、令牌、Cookie、证书等敏感信息。

## OpenSpec 接入

当对象素材进入 OpenSpec change：

- `ui-contract.md` 只引用 cutout、mask、export、enhanced 或图层包路径和使用范围。
- `source-map.md` 记录 IMG/OBJECT/MASK 与 PAGE、PAT、FR、tasks 和文件路径关系。
- `tasks.md` 只记录素材接入、边缘复核、背景验证、截图比对或人工验收。
- 不复制完整 `source.json`、过程图、mask 历史或 workspace 索引正文。

## Phase 0 — 读取上下文

先定位目标项目目录：用户给了项目路径就用该路径，否则使用当前工作目录。

静默收集已有对象处理产物：

```bash
rg --files aisee/docs/image-objects 2>/dev/null | head -80
rg --files | rg '(^|/)source\.json$|mask.*\.png$|cutout.*\.png$' | head -80
```

扫描必须遵守 `.gitignore`。优先使用 `rg --files`；如果 `rg` 不可用，fallback `find` 必须显式排除 `.git`、依赖目录、构建产物、缓存目录和生成产物，不要把无效文件当作 workspace 事实。

如果已有 workspace，先读取 `source.json`，避免重复命名、重复导出或覆盖用户手工修正的 mask。

## Phase 1 — 选择最小闭环

按用户意图选择最小流程，并只读取相关 reference：

- workspace、`source.json`、目录命名：读 `references/source-json.md`、`references/output-layout.md`
- 素材提取、端到端流程：读 `references/asset-extraction.md`、`references/workflows.md`
- 依赖、模型 backend、GUI：读 `references/dependencies.md`、`references/model-backends.md`、`references/gui-design.md`
- 导出选项、透明切图、图层包：读 `references/export-options.md`

常见闭环：

1. 有原图，要去背景：`init` → `remove-bg` → `export-variant`
2. 有图，要提取一个或多个素材：inventory → region/object selection → mask/cutout → export → index handoff。
3. 有原图，要点选/框选分割：`init` → `segment-point` / `segment-box` → `extract-object`
4. 已有 mask，要修边：`refine-mask` → `extract-object` → `export-variant`
5. 要背景修补：`inpaint-background`，默认优先 LaMa；必要时显式 `--fallback-opencv`
6. 要从 `aisee:design-assets` 的生成图得到透明素材：只做去背景、mask/cutout、修边和导出，不重新决定生成 prompt。
7. 要人工查看和微调：启动 `select --interactive`，具体 GUI 能力见 `references/gui-design.md`。

## Phase 2 — 输入门禁

信息不足时最多追问 3 个会影响结果的问题：

- 输入图片或 workspace 路径不明确
- 目标对象/素材不明确，且自动分割可能产生多个对象或多个候选素材
- 导出是否透明、背景颜色、圆角、padding 或尺寸要求不明确

低风险默认：

- 输出目录：`aisee/docs/image-objects/<源文件名>/`
- 模型 profile：`quality`；导出透明 PNG、按对象 BBox 裁切、无圆角、无 padding。
- 多素材提取先建立候选清单，逐个生成 object/export ID，不把多个素材混成一个对象。

## Phase 3 — 执行

执行思路：先建立单图 workspace，再确定 scope，然后生成或修正 mask，再提取 cutout，最后按用途导出 variant；背景修补和 Image Gen 增强都是带 mask/scope 的分支，不跳过 workspace 和 `source.json`。

内置脚本：

- `scripts/image_object_tool.py`：CLI 入口
- `scripts/gui/app.py`：PySide6 GUI 入口
- `scripts/check_dependencies.py`：依赖检查入口

Image Gen 深度优化不放入 GUI 第一版。需要深度优化时按 `references/workflows.md` 的 handoff 原则，与 `aisee:design-assets` 协作生成受控图片编辑提示词；GUI 只负责展示已经落到 `enhanced/` 的候选结果。

## Phase 4 — 更新状态

每次生成 mask、cutout、background、export 或 enhanced 候选，都更新 `source.json`：

- 记录输入、模型、参数、路径、尺寸、BBox、透明/背景设置、用户备注和操作历史。
- 大模型优化候选记录 `input_refs` / `prompt_ref` / `style_lock` / `scope`。
- 记录 fallback、依赖缺失原因；路径尽量写 workspace 相对路径。

## Phase 5 — 交付

最终回复使用中文，说明：

- 输入图和 workspace
- 已生成的 mask、cutout、background、export、enhanced 或图层包路径
- 素材 object/export ID、用途、状态、`aisee:design-assets` 登记情况、backend/fallback、验证结果和可选依赖影响
