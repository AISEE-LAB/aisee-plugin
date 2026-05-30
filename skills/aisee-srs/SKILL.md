---
name: aisee:srs
description: 通过结构化对话充分澄清业务需求，并生成规划级详细的软件需求规格说明书（SRS）。当用户想写需求文档、澄清产品范围、整理业务目标/用户角色/业务能力/业务流程/业务规则/权限/非目标、为 UI Content、Tech Context 或 aisee:change-plan 准备稳定输入，或把模糊想法整理成可测试需求时使用。触发词包括“帮我写需求文档”“编写需求规格说明书”“整理产品需求”“生成 SRS”“业务需求澄清”“我有个需求想整理一下”“aisee:srs”。SRS 应写到足够支持后续拆 change 和生成 UI/技术上下文，但不要写成接口设计、数据库设计、技术方案、视觉设计或开发任务。
---

# aisee:srs — OpenSpec 需求规格说明书

通过结构化对话挖掘需求，然后生成可交给 `aisee:ui-content`、`aisee:tech-context` 和 `aisee:change-plan` 使用的软件需求规格说明书（SRS）。

## Inputs

The user provides one of:
- A raw requirement or feature idea (free text)
- A vague product goal or problem statement
- A partially written requirements draft

Optional flags the user may include:
- `--lang zh|en` — output language (default: `zh`, Chinese)
- `--depth shallow|standard|deep` — dialogue depth (default: `standard`)
  - `shallow`: skip Phase 3 deepening, suitable for small features
  - `deep`: add a third dialogue round focused on edge cases and error flows
- `--baseline-aware` — 基于现有 OpenSpec baseline specs、active changes 和既有需求文档识别新增 / 修改 / 移除 / 兼容行为。若项目中存在 `openspec/specs/`、`openspec/changes/`、`docs/spec-migration/` 或历史 SRS，默认自动启用。
- `--ui-handoff` — SRS 生成后追加简短移交说明，列出适合继续扩展为 UI 内容规格的候选模块。不要在 SRS 内展开页面布局、视觉风格或组件设计。

---

## 输出边界

`aisee:srs` 产出的是 **规划级需求契约**：它要足够详细，能支撑后续 UI 内容规格、技术上下文和 change 边界规划；但它不是实现级接口设计、数据库设计、技术方案、UI 内容规格或设计系统。

如果是既有项目二次开发，SRS 必须是 **baseline-aware**：识别现有业务行为、现有 OpenSpec specs、历史需求和 active changes 对本需求的影响。SRS 只记录业务行为层面的新增 / 修改 / 移除 / 兼容，不写接口、数据库、代码模块、迁移脚本或实现方案。

只有当页面相关信息属于功能行为时才写入 SRS：
- 必须采集或展示的数据字段
- 业务流程要求的列表列、筛选条件、空状态、行操作
- 用户任务流中的入口和完成后的去向
- 用户可感知的权限、校验、反馈行为

可以写入规划级业务信息：
- 业务对象、业务状态、状态流转、业务规则和权限规则
- 交付形态信号，例如 Web 管理后台、小程序、桌面 GUI、后端服务、CLI、导入导出、通知、异步处理
- 外部系统交互的业务目的、触发条件、成功/失败处理和数据含义
- 后续是否需要 UI Content、Tech Context 或特殊 change artifact 的提示

不要写入：
- 视觉布局、间距、颜色、字体、图标或组件库选择
- 逐页线框图或屏幕构图
- 未由已确认需求推导出的页面
- API endpoint、数据库表字段、ORM、代码文件结构或迁移实现
- 具体技术栈选择、服务拆分、队列方案、任务拆解或代码实现计划

如果用户需要“开发哪些页面、页面上有什么内容、页面元素和交互流程”，先完成 SRS，再建议进入独立的 UI 内容规格步骤。这样既能保持 `aisee:change-plan` 的输入稳定，又能给后续界面设计更完整的材料。

---

## Phase 0 — Read Project Context

Before any dialogue, silently gather available project context:

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -120
find openspec/specs -maxdepth 3 -type f 2>/dev/null | head -40
find openspec/changes -maxdepth 2 \( -name proposal.md -o -name source-map.md -o -path '*/specs/*' \) 2>/dev/null | head -60
find docs/spec-migration docs/requirements -maxdepth 3 -type f 2>/dev/null | head -60
ls docs/requirements/ 2>/dev/null | head -20
```

Use this context to understand project boundaries, existing business behavior, current specs, and avoid asking questions the project already answers. If no project context is found (pre-`openspec-init`), proceed normally — `aisee:srs` is designed to run before `openspec-init`.

### Baseline-aware Mode

Enable baseline-aware mode when:
- 用户传入 `--baseline-aware`
- 存在 `openspec/specs/`
- 存在 active changes under `openspec/changes/`
- 存在 `docs/spec-migration/` 或历史 `docs/requirements/`
- 用户说“基于现有系统”“二次开发”“改造”“替换”“兼容”“保留旧逻辑”

Baseline-aware mode must:
- Identify existing business behavior and terminology from baseline specs or existing docs.
- Classify each affected requirement as `新增 / 修改 / 移除 / 兼容`.
- Record impacted baseline references when available, such as `openspec/specs/<domain>/spec.md`.
- Preserve user-observable compatibility constraints.
- Put unresolved baseline conflicts in Open Questions with `[SPEC-GAP]` or `[SPEC-CHANGE-REQUIRED]`.

Baseline-aware mode must not:
- Design APIs, DB tables, migrations, services, tasks, or code modules.
- Treat technical implementation files as business truth unless they are the only available source; when inferred from code, mark it as low-confidence and ask for confirmation.

---

## Phase 1 — Scope Anchoring

Open with a short acknowledgement and **one** anchoring question to establish the system boundary. Do not ask multiple questions in the first turn.

> "明白了。在我们深入细节之前，先确认一下范围边界：[一个聚焦的问题]。"

Choose the anchoring question based on the most uncertain dimension:

| If this is unclear... | Ask about... |
|-----------------------|--------------|
| Who uses it | 目标用户是谁？他们的核心诉求是什么？ |
| What it replaces | 这个功能是全新的，还是替换/改进现有流程？ |
| Where it lives | 它是独立系统、新模块，还是现有系统的扩展？ |
| Why now | 触发这个需求的业务事件或痛点是什么？ |

---

## Phase 2 — Discovery Dialogue

**Before starting this phase, read `references/question-bank.md`** for the full question bank and round progression logic.

Rules:
- Ask **at most 3 questions per round**, grouped by theme
- Display round number at the start of each round: `[需求探讨 · 第 N 轮]`
- Wait for the user's response before proceeding
- After **Round 8**, display the over-limit warning (see question-bank.md)
- Record unresolved ambiguities as `[ASSUMPTION]` tags and move forward
- 对页面占比较高的需求，只追问理解任务路径所必需的功能性 UI 问题。详细页面清单和页面内容留给独立 UI 内容规格。
- 在进入确认门禁前，确保至少覆盖：目标用户、业务目标、范围/非目标、核心流程、业务对象与状态、关键业务规则、权限/数据范围、异常和验收方向。缺失但不阻塞的信息写入假设或 Open Questions。

---

## Phase 3 — Confirmation Gate

**体量评估（在展示摘要前静默执行）**

计算以下指标，判断是否进入 Epic 模式：
- 预计 FR 总数 > 10，**或**
- 识别出的功能模块 ≥ 3 个，**或**
- 存在 ≥ 2 个复杂场景扩展块（工作流、外部集成、权限矩阵）

满足任意一条 → **Epic 模式**，在摘要中增加以下提示：

> ⚠️ **需求体量较大**，将生成 **1 份主文档 + {N} 份模块文档**，避免单文档过长导致内容截断。
> 主文档：系统概述、跨模块约束、术语表、变更候选清单
> 模块文档：{模块 1}（FR-001 ~ FR-00X）/ {模块 2}（FR-00X ~ FR-00Y）/ …

Present a structured summary before generating the document. **Do not proceed until the user explicitly confirms.**

```
📋 需求摘要（生成前确认）

- 系统 / 功能名称：{name}
- 核心用户：{users}
- 主流程数量：{N} 条（已列出）
- 功能需求条数：约 {N} 条
- 非功能需求：{list or "暂无"}
- 业务对象 / 状态：{list or "暂无"}
- 关键业务规则：{list or "暂无"}
- 明确非目标：{list or "暂无"}
- 待确认假设：{list or "无"}
- 已识别风险：{list or "无"}
- 后续建议：UI Content 需要 / 不需要；Tech Context 需要 / 不需要；change-plan 输入是否已充足
- 基线感知：启用 / 未启用（如启用，列出主要影响基线）
- 📄 输出模式：**标准模式**（单文档）/ **Epic 模式**（主文档 + {N} 份模块文档）← 自动选择

主流程预览：
1. {flow 1}
2. {flow 2}
...
```

> 如果以上内容准确，请回复 **"确认，生成 SRS"**。
> 如果需要修改，请直接告诉我哪里有偏差。

If the user corrects something, update the internal model and re-present the summary. Re-presentation counts as a new round for the round counter.

---

## Phase 4 — SRS Generation

**根据 Phase 3 体量评估结果，选择生成模式：**

### 标准模式（FR ≤ 10，模块 < 3，无复杂扩展块）

Upon confirmation:
1. **Read `assets/srs-template.md`** 中的"标准文档模板"部分
2. Populate the template with all information gathered during dialogue
3. Apply the Requirement Quality Checklist (in the template) to each FR before writing it
4. 如果启用 baseline-aware mode，填写 Section 2.5，并为每条 FR 填写“变更类型”和“影响基线”。
5. 填写 Section 8（后续交接提示），说明是否建议继续生成 UI Content、Tech Context，以及传给 `aisee:change-plan` 时需要注意的业务边界。只写规划提示，不展开实现级设计。

### Epic 模式（超出阈值）

**Read `assets/srs-template.md`** 中的"主文档模板"和"模块文档模板"部分，按以下顺序逐份生成。**每份生成后暂停并告知用户进度**，再继续下一份：

**Step 1 — 生成主文档**

读取 `assets/srs-template.md` 中的"主文档模板"部分，填充：
- Section 1（引言）、Section 2（整体描述）
- Section 4（非功能需求，完整版）
- Section 5（约束与假设，完整版，包含所有 `[ASSUMPTION]`）
- Section 6（Open Questions，完整版）
- Section 7（变更候选清单，列出所有 FR ID，链接到对应模块文档）
- Section 8（后续交接提示，列出 UI Content / Tech Context / Change Plan 的输入建议）
- 如果启用 baseline-aware mode，Section 2.5 必须列出全局基线影响，并在 Section 7 标注每个 FR 的变更类型和影响基线
- **Section 3 留空**，注明"各模块 FR 详情见模块文档索引"

生成后输出：
> 📄 **主文档已完成**（1/{N+1}）。接下来逐份生成模块文档，每份完成后会通知你。继续生成？

**Step 2 — 逐模块生成详情文档**

每份模块文档读取 `assets/srs-template.md` 中的"模块文档模板"部分，只包含：
- 模块引言（1–2 句，说明该模块职责及与主文档的关系）
- Section 3（该模块的全部 FR，含完整场景扩展块）
- Section 4（本模块特有的非功能补充；没有则写"无"）
- 模块级假设（仅与本模块相关的 `[ASSUMPTION]`，已在主文档 Section 5 中出现，此处仅列编号和标题作为引用）
- 模块级待确认事项（仅与本模块相关的问题）
- 模块变更候选清单（列出该模块全部 FR，确保模块文档可独立传给 `aisee:change-plan`）
- 模块级后续交接提示（该模块是否需要 UI Content、Tech Context 重点补充项、change-plan 注意事项）
- 如果启用 baseline-aware mode，每条 FR 必须填写“变更类型”和“影响基线”

每份生成后输出：
> 📄 **{模块名}模块文档已完成**（{i}/{N+1}）。继续生成下一份？

---

## Phase 5 — Save Document

**标准模式**（单文件）：

命名：`docs/requirements/<YYYY-MM-DD>-<requirement-slug>.md`

其中 `requirement-slug` 为功能名称前 5 个有意义词的 kebab-case。

```bash
mkdir -p docs/requirements
```

**Epic 模式**（多文件）：

```
docs/requirements/<YYYY-MM-DD>-<slug>/
  ├── 00-main.md          ← 主文档（系统概述 + 全局索引）
  ├── 01-<module-a>.md    ← 模块 A 详情
  ├── 02-<module-b>.md    ← 模块 B 详情
  └── ...
```

主文档 Section 7 中，每个 FR ID 附上相对路径链接，例如：`[FR-003](./02-module-b.md#fr-003)`

```bash
mkdir -p docs/requirements/<YYYY-MM-DD>-<slug>
```

---

**标准模式**完成后输出：

> ✅ **SRS 已生成**：`docs/requirements/{filename}.md`
>
> 包含 **{N} 条功能需求**、**{M} 条非功能需求**、**{K} 个待确认事项**。
>
> **下一步**：运行 `aisee:change-plan`，建议传入本文档路径：
> ```
> aisee:change-plan docs/requirements/{filename}.md
> ```
>
> 如果 Section 8 标注需要 UI Content 或 Tech Context，请先补齐对应文档，再进入 `aisee:change-plan`；不要把接口、数据库或技术实现设计补进 SRS。

**Epic 模式**完成后输出：

> ✅ **SRS 已生成**（Epic 模式，共 {N+1} 份文档）：
>
> - 主文档：`docs/requirements/{slug}/00-main.md`
> - 模块文档：
>   - `01-{module-a}.md`（FR-001 ~ FR-00X，{N} 条需求）
>   - `02-{module-b}.md`（FR-00X ~ FR-00Y，{N} 条需求）
>   - …
>
> **下一步**：运行 `aisee:change-plan`，建议逐模块传入：
> ```
> aisee:change-plan docs/requirements/{slug}/01-{module-a}.md
> aisee:change-plan docs/requirements/{slug}/02-{module-b}.md
> ```
>
> 如果其中某些模块的 Section 8 标注需要 UI Content 或 Tech Context，请先按模块补齐对应文档，再进入 `aisee:change-plan`。

---

## Guardrails

- **Never generate the SRS before the user confirms** in Phase 3.
- **Never ask more than 3 questions per round.**
- **Never include implementation decisions** in functional requirements (no framework choices, no specific API endpoints, no DB schema).
- **Never invent requirements** not raised by the user. Implied-but-unstated items go to Section 6 (Open Questions).
- **不要把 SRS 写成 UI 设计文档**。页面字段、列表列、操作和空状态只作为功能合约；视觉布局和详细页面构成应留给独立的 UI 内容/设计步骤。
- **不要把 baseline-aware 写成技术设计**。已有基线只用于描述业务行为变化、兼容约束和影响范围；接口、数据库、迁移、代码结构留给 tech-context 和 change artifacts。
- **不要把后续交接提示写成实现方案**。Section 8 只能说明后续需要哪些上下文、哪些 FR/PAGE/业务对象值得关注，不输出 API path、DB 字段、服务拆分或任务清单。
- **Do not exceed 20 FRs** in a single SRS document (主文档或单份模块文档均适用). If total scope exceeds 20 FRs, flag it as an epic and enter Epic 模式.
- Every `[ASSUMPTION]` recorded during dialogue must appear in the main document's Section 5.2.
- **Epic 模式下，每份文档独立完整** — 模块文档不依赖主文档即可被 `aisee:change-plan` 单独处理。
- **Epic 模式下，每份文档生成后必须暂停** — 不允许连续生成所有文档后才通知用户，每次暂停时等待用户确认继续。
- **模块划分依据功能边界** — 不按 FR 数量机械切割，避免把同一业务流程的 FR 拆到不同文档。
- **主文档的 Section 7 必须包含所有 FR 的链接** — 确保主文档可独立作为全局索引使用。

---

## Integration with the OpenSpec Workflow

```
aisee:srs                         ← 本 skill：需求发现 → SRS 文档
  ├─ [conditional] aisee:ui-content       ← UI 型软件的页面清单、页面内容、页面元素、交互路径（不含视觉设计规范）
  ├─ [recommended] aisee:tech-context     ← 技术栈状态、架构边界、共享前置和技术约束
  └─ aisee:change-plan <srs-file>       ← 将 SRS 映射为独立 Change
       └─ /opsx:new <change>   ← 创建 Change Folder
            └─ aisee:change-author       ← 按当前 schema 生成 / 补齐 change artifacts
            └─ /opsx:apply     ← 实现
            └─ /ce:review      ← 代码审查
            └─ /opsx:archive   ← 归档
```
