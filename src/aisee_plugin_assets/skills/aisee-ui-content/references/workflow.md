# UI Content Workflow

本文是 `aisee:ui-content` 输入门禁、场景识别、输出模式和保存规则的维护源。

## Phase 1 — 输入门禁

可以继续的条件：

- 至少存在明确的用户角色或使用者。
- 至少存在一个主流程或 FR。
- 能判断功能是否需要用户可见页面、弹窗、通知、导入导出结果页等 UI 承载。

必须先追问的情况：

- 没有目标平台，且无法从上下文判断。
- 只有模糊想法，没有 SRS / FR / 主流程。
- 页面内容会因角色、平台或业务范围不同而产生明显分歧。
- 用户要求多端，但没有说明覆盖哪些端。
- 用户要求基于现有系统二开，但无法判断现有页面、入口或模块归属。

追问前读取 `question-bank.md`，每轮最多问 3 个问题，不追问视觉偏好。不超过 3 轮；仍不明确时，把未解决项写入 Open Questions。

## Phase 2 — 平台范围识别

目标端包括 `PC Web / Admin`、`Mobile Web / H5`、`Native App`、`微信小程序` 和 `多端共用`。如果 SRS 未说明目标端，必须询问用户；不要默认 PC 或移动端。

多端场景先生成跨端通用内容规格，再生成平台差异补充；只有平台差异足够复杂时，才拆出 `platform-diff.md`。平台差异只记录内容、入口、操作、授权、反馈和能力限制，不写视觉布局。

## Phase 3 — 场景模式识别

- `new-build`：新系统或新模块，没有可引用的既有 UI 基线，生成完整 UI 内容规格。
- `enhancement`：现有系统二次开发，生成 UI 内容增量规格，只展开本次变化。
- `inventory`：老项目迁移或现有 UI 盘点，生成 UI 内容索引 / 盘点，不设计新需求。

`enhancement` 模式必须先建立受影响 UI 范围：

| 状态 | 含义 | 写作要求 |
|------|------|----------|
| Existing | 原样复用的既有页面 / 入口 / 流程 | 只引用来源，不展开完整规格 |
| Changed | 在既有页面上修改 | 只写变更区块、字段、状态、操作、权限和流程影响 |
| New | 新增页面 / 弹窗 / 入口 / 非页面承载物 | 按页面模板写完整内容规格 |
| Deprecated | 删除、下线或废弃 | 写清替代去向、影响范围和用户反馈 |
| Unknown | 现有系统无法确认 | 写入 Open Questions，不假设 |

## Phase 4 — 页面与交互对象识别

识别所有用户可见承载物：页面、非完整页面、全局入口、非页面型交互结果。

页面划分原则：

- 优先按用户任务和业务模块划分。
- 不把每个弹窗机械拆成页面。
- 不为未确认需求创建页面。
- 同一业务流程不要拆散到多个无关文档。
- 二开场景只为 `Changed` / `New` / `Deprecated` 对象写变化细节，`Existing` 对象只保留引用。

## Phase 5 — 输出模式选择

标准模式使用单文件，适用于页面详情数量 ≤ 8、模块数 ≤ 2、跨页面流程 ≤ 5、覆盖平台 ≤ 2，且没有复杂权限矩阵或大量表单。

Epic 模式使用索引文档 + 多文档，适用于页面详情数量 > 8、模块数 ≥ 3、覆盖平台 ≥ 3、跨页面流程 > 5，或存在复杂权限矩阵、复杂审批流、大量表单、批量导入导出、多端显著差异。

Epic 拆分优先级：

1. 按业务模块拆。
2. 跨模块流程单独拆为 `shared-flows`。
3. 多端差异复杂时单独拆为 `platform-diff`。
4. 不按页数机械切割，除非单个模块超过 8 个页面详情。

## Phase 6 — 生成 UI 内容规格

先读取 `assets/ui-content-template.md` 入口索引，再按场景模式和输出模式读取必要模板；每次生成都必须同时读取 `references/writing-rules.md`。

标准模式按场景读取：

- `new-build`：`assets/ui-content-template-standard.md`
- `enhancement`：`assets/ui-content-template-enhancement.md`
- `inventory`：`assets/ui-content-template-inventory.md`

Epic 模式始终读取 `assets/ui-content-template-epic-index.md` 和 `assets/ui-content-template-epic-module.md`。

Epic 模式按需读取：

- `assets/ui-content-template-shared-flows.md`
- `assets/ui-content-template-platform-diff.md`

Epic 模式每份文档生成后暂停并告知用户进度，等待确认继续。

## Phase 7 — 保存与交付

标准模式保存到：

```text
aisee/docs/ui-content/<YYYY-MM-DD>-<slug>.md
```

Epic 模式保存到：

```text
aisee/docs/ui-content/<YYYY-MM-DD>-<slug>/
  ├── 00-index.md
  ├── 01-<module-a>.md
  ├── 02-<module-b>.md
  ├── shared-flows.md
  └── platform-diff.md
```

完成后说明保存路径、页面数量、流程数量、平台差异数量、Open Questions 数量，并建议将 UI 内容规格与 SRS、Architecture 和必要设计规范一起交给 `aisee:change-plan`。
