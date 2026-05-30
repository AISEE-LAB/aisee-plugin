---
name: aisee:srs
description: 通过结构化对话充分澄清业务需求，并生成规划级详细的需求规格说明书（SRS）。当用户想写需求文档、澄清产品范围、整理业务目标/用户角色/业务能力/业务流程/业务规则/权限/非目标，或为 UI Content、Architecture、aisee:change-plan 准备稳定输入时使用。适用于软件、App、小程序、桌面、后端/API、CLI、Job、硬件、嵌入式、固件和混合系统的需求澄清；触发词包括“帮我写需求文档”“编写需求规格说明书”“整理产品需求”“生成 SRS”“硬件需求”“嵌入式需求”“业务需求澄清”“我有个需求想整理一下”“aisee:srs”。SRS 应写到足够支持后续拆 change 和生成 UI/技术架构，但不要写成接口设计、数据库设计、技术方案、视觉设计、硬件架构、固件设计或开发任务。
---

# aisee:srs — OpenSpec 需求规格说明书

通过结构化对话挖掘需求，然后生成可交给 `aisee:ui-content`、`aisee:architecture` 和 `aisee:change-plan` 使用的需求规格说明书（SRS）。

## 输入

用户提供以下任意一种输入：
- 原始需求或功能想法（自由文本）
- 模糊的产品目标或问题描述
- 已有但尚未成型的需求草稿

可选参数：
- `--lang zh|en` — 输出语言，默认 `zh`
- `--depth shallow|standard|deep` — 对话深度，默认 `standard`
  - `shallow`：只完成第 1–2 轮；如果范围、用户、主流程、MVP、非目标和验收方向已经清楚，则进入确认门禁
  - `standard`：按 `references/question-bank.md` 的第 1–4 轮推进
  - `deep`：第 4 轮后，针对复杂业务规则、基线冲突、外部协作、权限和边界场景追加定向追问
- `--baseline-aware` — 基于现有 OpenSpec baseline specs、active changes 和既有需求文档识别新增 / 修改 / 移除 / 兼容行为。若项目中存在 `openspec/specs/`、`openspec/changes/`、`docs/spec-migration/` 或历史 SRS，默认自动启用。

---

## 输出边界

`aisee:srs` 产出的是 **规划级需求契约**：它要足够详细，能支撑后续 UI 内容规格、技术架构和 change 边界规划；但它不是实现级接口设计、数据库设计、技术方案、UI 内容规格或设计系统。

如果是既有项目二次开发，SRS 必须是 **baseline-aware**：识别现有业务行为、现有 OpenSpec specs、历史需求和 active changes 对本需求的影响。SRS 只记录业务行为层面的新增 / 修改 / 移除 / 兼容，不写接口、数据库、代码模块、迁移脚本或实现方案。

只有当页面相关信息属于功能行为时才写入 SRS：
- 必须采集或展示的数据字段
- 业务流程要求的列表列、筛选条件、空状态、行操作
- 用户任务流中的入口和完成后的去向
- 用户可感知的权限、校验、反馈行为

可以写入规划级业务信息：
- 业务对象、业务状态、状态流转、业务规则和权限规则
- 交付形态信号，例如 Web 管理后台、小程序、桌面 GUI、后端服务、CLI、导入导出、通知、异步处理
- 对硬件 / 嵌入式 / 混合系统，可写设备能力、操作环境、输入输出信号的业务含义、可观察状态、故障表现、验收方向和安全 / 可靠性要求
- 外部系统交互的业务目的、触发条件、成功/失败处理和数据含义
- 后续是否需要 UI Content、Architecture 或特殊 change artifact 的提示

不要写入：
- 视觉布局、间距、颜色、字体、图标或组件库选择
- 逐页线框图或屏幕构图
- 未由已确认需求推导出的页面
- API endpoint、数据库表字段、ORM、代码文件结构或迁移实现
- 具体技术栈选择、服务拆分、队列方案、任务拆解或代码实现计划
- 引脚表、寄存器表、RTOS 任务设计、驱动结构、BOM、PCB 布局、固件实现步骤或制造工艺

如果用户需要“开发哪些页面、页面上有什么内容、页面元素和交互流程”，先完成 SRS，再建议进入独立的 UI 内容规格步骤。这样既能保持 `aisee:change-plan` 的输入稳定，又能给后续界面设计更完整的材料。

---

## ID 规则

`aisee:srs` 负责需求侧上游 ID：

- `FR`：功能需求。
- `NFR`：非功能需求。
- `RULE`：业务规则。
- `FLOW`：业务流程或用户任务流，只有在 SRS 阶段已经明确时分配。
- `STATE`：业务状态或用户可感知状态，只有在 SRS 阶段已经明确时分配。

正式 ID 必须来自 `.aisee/id-registry.json`。生成 SRS 前应确定 `scope`，并在需要新增 ID 时使用：

```bash
aisee id reserve --scope <scope> --type FR --count <N> --json
aisee id reserve --scope <scope> --type NFR --count <N> --json
aisee id reserve --scope <scope> --type RULE --count <N> --json
aisee id reserve --scope <scope> --type FLOW --count <N> --json
aisee id reserve --scope <scope> --type STATE --count <N> --json
```

写入文档后，使用 `aisee id activate <full-id> --owner <path> --title "<title>"` 激活；交付前运行或建议运行 `aisee id check --json`。

如果 Aisee CLI 或 ID registry 不可用，只能使用临时占位符，例如 `{{scope}}:FR-NEW-001`，并在文档 ID 状态中标注 `[ID-RESERVATION-REQUIRED]`。不要声称占位符是正式 ID。

SRS 不负责 `PAGE / API / DATA / TASK / TEST`。`PAGE / FLOW / STATE` 的 UI 细化由 `aisee:ui-content` 承接；`API / DATA / TASK / TEST` 由 change artifacts 承接。

---

## 阶段 0 — 读取项目上下文

开始对话前，静默收集可用项目上下文：

```bash
cat openspec/config.yaml 2>/dev/null || echo "No openspec config found"
cat openspec/project.md 2>/dev/null || echo "No project.md found"
cat AGENTS.md 2>/dev/null | head -120
cat .aisee/id-registry.json 2>/dev/null || true
find openspec/specs -maxdepth 3 -type f 2>/dev/null | head -40
find openspec/changes -maxdepth 2 \( -name proposal.md -o -name source-map.md -o -path '*/specs/*' \) 2>/dev/null | head -60
find docs/spec-migration docs/requirements -maxdepth 3 -type f 2>/dev/null | head -60
find . -maxdepth 4 \( -iname 'CMakeLists.txt' -o -iname '*.ioc' -o -iname '*.dts' -o -iname '*.dtsi' -o -iname 'platformio.ini' -o -iname 'Kconfig' -o -iname '*.ld' \) 2>/dev/null | head -40
ls docs/requirements/ 2>/dev/null | head -20
```

用这些上下文理解项目边界、现有业务行为和当前 specs，避免重复询问项目已经回答的问题。如果没有项目上下文（尚未 `openspec-init`），正常继续；`aisee:srs` 允许在 `openspec-init` 前运行。

### Baseline-aware 模式

出现以下情况时启用 baseline-aware 模式：
- 用户传入 `--baseline-aware`
- 存在 `openspec/specs/`
- 存在 active changes under `openspec/changes/`
- 存在 `docs/spec-migration/` 或历史 `docs/requirements/`
- 用户说“基于现有系统”“二次开发”“改造”“替换”“兼容”“保留旧逻辑”

Baseline-aware 模式必须：
- 从 baseline specs 或现有文档识别既有业务行为和术语。
- 将每条受影响需求标记为 `新增 / 修改 / 移除 / 兼容`。
- 在可用时记录受影响基线引用，例如 `openspec/specs/<domain>/spec.md`。
- 保留用户可观察的兼容性约束。
- 将未解决的基线冲突写入 Open Questions，并标注 `[SPEC-GAP]` 或 `[SPEC-CHANGE-REQUIRED]`。

Baseline-aware 模式不得：
- 设计 API、数据库表、迁移、服务、任务或代码模块。
- 把技术实现文件直接当作业务事实，除非它们是唯一可用来源；如果从代码推断，必须标注低可信度并要求确认。

---

## 阶段 1 — 范围锚定

以简短回应开头，并只问 **一个** 锚定问题来建立系统边界。第一轮不要连续问多个问题。

> "明白了。在我们深入细节之前，先确认一下范围边界：[一个聚焦的问题]。"

根据最不确定的维度选择锚定问题：

| 不清楚的维度 | 询问方向 |
|----------------|----------|
| 谁使用 | 目标用户是谁？他们的核心诉求是什么？ |
| 替代什么 | 这个功能是全新的，还是替换 / 改进现有流程？ |
| 放在哪里 | 它是独立系统、新模块，还是现有系统的扩展？ |
| 为什么现在做 | 触发这个需求的业务事件或痛点是什么？ |

---

## 阶段 2 — 需求探讨

**开始本阶段前，读取 `references/question-bank.md` 和 `references/domain-rules.md`**，获取问题库、需求域识别和轮次推进规则。

规则：
- 每轮最多问 **3 个问题**，按主题分组
- 每轮开头显示轮次：`[需求探讨 · 第 N 轮]`
- 等待用户回答后再继续
- **第 8 轮**后展示过轮提醒（见 question-bank.md）
- 将未解决但不阻塞的信息记录为 `[ASSUMPTION]`，然后继续推进
- 对页面占比较高的需求，只追问理解任务路径所必需的功能性 UI 问题。详细页面清单和页面内容留给独立 UI 内容规格。
- 在进入确认门禁前，确保至少覆盖：目标用户、业务目标、范围/非目标、核心流程、业务对象与状态、关键业务规则、权限/数据范围、异常和验收方向。缺失但不阻塞的信息写入假设或 Open Questions。
- 在进入确认门禁前，识别需求域：software / backend / cli / job / hardware / embedded / hybrid。域不明确且会改变范围时，先追问；不改变范围时写入 `[ASSUMPTION]`。

---

## 阶段 3 — 确认门禁

**体量评估（在展示摘要前静默执行）**

先读取 `references/module-boundary-rules.md`，审查模块候选。不要直接沿用输入材料章节、技术层、页面类型、架构主题或任务阶段作为模块。

计算以下指标，判断是否进入 Epic 模式：
- 预计 FR 总数 > 10，**或**
- 通过模块候选审查后的有效能力模块 ≥ 3 个，**或**
- 存在 ≥ 2 个复杂场景扩展块（工作流、外部集成、权限矩阵）

满足任意一条 → **Epic 模式**，在摘要中增加以下提示：

> ⚠️ **需求体量较大**，将生成 **1 份主文档 + {N} 份模块文档**，避免单文档过长导致内容截断。
> 主文档：系统概述、跨模块约束、术语表、变更候选清单
> 模块文档：{模块 1}（FR-001 ~ FR-00X）/ {模块 2}（FR-00X ~ FR-00Y）/ …

生成文档前展示结构化摘要。**用户明确确认前不得继续生成。**

```
📋 需求摘要（生成前确认）

- 系统 / 功能名称：{name}
- 核心用户：{users}
- 主流程数量：{N} 条（已列出）
- 功能需求条数：约 {N} 条
- 非功能需求：{list or "暂无"}
- 业务对象 / 状态：{list or "暂无"}
- 需求域 / 交付形态：{software/backend/cli/job/hardware/embedded/hybrid + delivery shape}
- 关键业务规则：{list or "暂无"}
- 明确非目标：{list or "暂无"}
- 待确认假设：{list or "无"}
- 已识别风险：{list or "无"}
- 后续建议：UI Content 需要 / 不需要；Architecture 需要 / 不需要；change-plan 输入是否已充足
- 基线感知：启用 / 未启用（如启用，列出主要影响基线）
- 📄 输出模式：**标准模式**（单文档）/ **Epic 模式**（主文档 + {N} 份模块文档）← 基于有效能力模块和复杂度自动选择

主流程预览：
1. {flow 1}
2. {flow 2}
...
```

> 如果以上内容准确，请回复 **"确认，生成 SRS"**。
> 如果需要修改，请直接告诉我哪里有偏差。

如果用户修正内容，更新内部需求模型并重新展示摘要。每次重新展示都计入轮次。

---

## 阶段 4 — 生成 SRS

**根据阶段 3 的体量评估结果，选择生成模式：**

### 标准模式（FR ≤ 10，模块 < 3，无复杂扩展块）

用户确认后：
1. **Read `assets/srs-template.md`** to confirm template routing.
2. Read `references/writing-rules.md`, `references/domain-rules.md`, and `references/module-boundary-rules.md`.
3. Read `assets/srs-template-standard.md`.
4. Read only the relevant blocks from `references/scenario-extension-blocks.md`.
5. Populate the template with all information gathered during dialogue.
6. 写入每条 FR / NFR / RULE / FLOW / STATE 前，检查 ID registry；工具不可用时使用临时 ID 并标注 `[ID-RESERVATION-REQUIRED]`。
7. 写入每条 FR 前，应用需求质量检查清单。
8. 如果启用 baseline-aware mode，填写 Section 2.5，并为每条 FR 填写“变更类型”和“影响基线”。
9. 填写 Section 8（后续交接提示），说明是否建议继续生成 UI Content、Architecture，以及传给 `aisee:change-plan` 时需要注意的业务边界。只写规划提示，不展开实现级设计。

### Epic 模式（超出阈值）

读取 `assets/srs-template.md` 确认模板路由，然后读取 `references/domain-rules.md` 和 `references/module-boundary-rules.md`。按以下顺序生成文档。**每份生成后暂停并告知用户进度**，再继续下一份：

**Step 1 — 生成主文档**

读取 `references/writing-rules.md` 和 `assets/srs-template-epic-main.md`，填充：
- Section 1（引言）、Section 2（整体描述）
- Section 4（非功能需求，完整版）
- Section 5（约束与假设，完整版，包含所有 `[ASSUMPTION]`）
- Section 6（Open Questions，完整版）
- Section 7（变更候选清单，列出所有 FR ID，链接到对应模块文档）
- Section 8（后续交接提示，列出 UI Content / Architecture / Change Plan 的输入建议）
- 模块索引必须使用通过审查的能力模块，并说明被拒绝或合并的输入章节不会作为模块输出
- 如果启用 baseline-aware mode，Section 2.5 必须列出全局基线影响，并在 Section 7 标注每个 FR 的变更类型和影响基线
- **Section 3 留空**，注明"各模块 FR 详情见模块文档索引"

生成后输出：
> 📄 **主文档已完成**（1/{N+1}）。接下来逐份生成模块文档，每份完成后会通知你。继续生成？

**Step 2 — 逐模块生成详情文档**

每份模块文档读取 `references/writing-rules.md`、`assets/srs-template-epic-module.md`，并按需读取 `references/scenario-extension-blocks.md` 中匹配的扩展块。模块文档只包含：
- 模块引言（1–2 句，说明该模块职责及与主文档的关系）
- Section 3（该模块的全部 FR，含完整场景扩展块）
- Section 4（本模块特有的非功能补充；没有则写"无"）
- 模块级假设（仅与本模块相关的 `[ASSUMPTION]`，已在主文档 Section 5 中出现，此处仅列编号和标题作为引用）
- 模块级待确认事项（仅与本模块相关的问题）
- 模块变更候选清单（列出该模块全部 FR，确保模块文档可独立传给 `aisee:change-plan`）
- 模块级后续交接提示（该模块是否需要 UI Content、Architecture 重点补充项、change-plan 注意事项）
- 如果启用 baseline-aware mode，每条 FR 必须填写“变更类型”和“影响基线”

每份生成后输出：
> 📄 **{模块名}模块文档已完成**（{i}/{N+1}）。继续生成下一份？

---

## 阶段 5 — 保存文档

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
> 如果 Section 8 标注需要 UI Content 或 Architecture，请先补齐对应文档，再进入 `aisee:change-plan`；不要把接口、数据库或技术实现设计补进 SRS。

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
> 如果其中某些模块的 Section 8 标注需要 UI Content 或 Architecture，请先按模块补齐对应文档，再进入 `aisee:change-plan`。

---

## 保护规则

- **用户在阶段 3 确认前，不得生成 SRS**。
- **每轮不得问超过 3 个问题**。
- **功能需求不得包含实现决策**，例如框架选择、具体 API endpoint 或数据库 schema。
- **功能需求不得包含硬件 / 固件实现决策**，例如引脚表、寄存器表、RTOS 任务设计、驱动结构、PCB / BOM / 制造细节。
- **不得发明用户没有提出的需求**。隐含但未明确的事项放入 Section 6（Open Questions）。
- **不要把 SRS 写成 UI 设计文档**。页面字段、列表列、操作和空状态只作为功能合约；视觉布局和详细页面构成应留给独立的 UI 内容/设计步骤。
- **不要把 baseline-aware 写成技术设计**。已有基线只用于描述业务行为变化、兼容约束和影响范围；接口、数据库、迁移、代码结构留给 architecture 和 change artifacts。
- **不要把后续交接提示写成实现方案**。Section 8 只能说明后续需要哪些上下文、哪些 FR/PAGE/业务对象值得关注，不输出 API path、DB 字段、服务拆分或任务清单。
- **单份 SRS 文档不得超过 20 条 FR**（主文档或单份模块文档均适用）。如果总范围超过 20 条 FR，标记为 Epic 并进入 Epic 模式。
- Every `[ASSUMPTION]` recorded during dialogue must appear in the main document's Section 5.2.
- **Epic 模式下，每份模块文档必须包含模块上下文摘要** — 即使模块文档链接到主文档，也要包含足够的模块范围、用户/角色、业务对象/状态、关键规则和非目标，确保可被 `aisee:change-plan` 单独处理。
- **Epic 模式下，每份文档生成后必须暂停** — 不允许连续生成所有文档后才通知用户，每次暂停时等待用户确认继续。
- **模块划分依据功能边界** — 不按 FR 数量机械切割，避免把同一业务流程的 FR 拆到不同文档。
- **模块候选必须经过审查** — 不把输入材料章节、技术层、页面类型、设计规范、架构主题、测试计划或任务阶段直接当作 SRS 模块。
- **主文档的 Section 7 必须包含所有 FR 的链接** — 确保主文档可独立作为全局索引使用。
- **正式 ID 必须来自 ID registry** — 不得由 AI 临时编正式 FR / NFR / RULE / FLOW / STATE 编号；工具不可用时使用 `{{scope}}:<TYPE>-NEW-001` 并标注 `[ID-RESERVATION-REQUIRED]`。

---

## 与 OpenSpec 工作流集成

```
aisee:srs                         ← 本 skill：需求发现 → SRS 文档
  ├─ [conditional] aisee:ui-content       ← UI 型软件的页面清单、页面内容、页面元素、交互路径（不含视觉设计规范）
  ├─ [recommended] aisee:architecture     ← 技术栈状态、架构边界、共享前置和技术约束
  └─ aisee:change-plan <srs-file>       ← 将 SRS 映射为独立 Change
       └─ /opsx:new <change>   ← 创建 Change Folder
            └─ aisee:change-author       ← 按当前 schema 生成 / 补齐 change artifacts
            └─ openspec validate
            └─ aisee:implementation-bridge
            └─ compound plan / work / review / test
            └─ aisee:verify
            └─ aisee:archive-guard
            └─ openspec archive
```
