---
name: aisee:change-plan
description: 将已确认的 SRS、UI 内容规格、设计规范、技术架构和项目事实映射为可独立交付的 OpenSpec changes。用于规划 change 边界、依赖顺序、并行关系、source-map 初稿和 /opsx:new 命令；不重新做业务模块划分，不重新生成需求。
---

# aisee:change-plan — OpenSpec Change 边界规划

将已确认需求映射为边界清晰、可独立交付的 OpenSpec changes。每个输出 change 都应足够小，可以用 `/opsx:new` 创建，并在实现前按所选 schema 的 artifact 顺序补齐内容。对于 app schema v2，通常会包含 `source-map.md`、`specs/`、`change-context.md`、contract artifacts 和 `tasks.md`；device schema 可能包含 `design.md` 或设备侧 contracts；轻量 schema 可能使用不同 artifacts。

`aisee:change-plan` 不负责业务模块划分。SRS 的模块回答“业务上有哪些模块”，本技能回答“哪些 FR / PAGE / FLOW / ARCH / DEC / CONSTRAINT / RISK 应放进同一个可独立交付的 OpenSpec change”。

## 输入

用户提供以下任意一种输入：
- 原始需求描述（自由文本）
- ticket / issue 引用（如果可用则读取）
- 既有需求文档路径，包括 `aisee:srs` 输出的 SRS
- 可选配套输入：`aisee:ui-content` 的 UI 内容规格、`aisee:design-spec` 的设计规范、`aisee:architecture` 的技术架构文档

可选参数：
- `--strategy vertical|risk|parallel`：规划策略，默认 `vertical`
- `--granularity fine|medium|coarse`：粒度约束，默认 `medium`
  - `fine`：优先 S change；每个 change 约 1–3 天；除非会破坏独立交付，否则拆分 M/L 候选
  - `medium`：允许 S/M change；每个 change 约 1–7 天；适合大多数产品需求
  - `coarse`：偏少 change；允许 M/L change，最长不超过 14 天；不得输出 XL
- `--schema <name>`：生成 `/opsx:new` 命令使用的 schema，默认 `aisee-app-spec-driven`
- `--max-changes <N>`：最大输出 change 数，默认 `8`
- `--single-if-small`：如果输入已经是单个 ≤3 天的小 change，只输出一个 change，不强行拆分

## 阶段 1 — 读取项目上下文

分析需求前，收集全部输入。静默运行：

```bash
# 如果输入是文件路径，先读取输入文件
cat <input-file-path> 2>/dev/null || echo "File not found"

# 读取项目 OpenSpec 配置
cat openspec/config.yaml 2>/dev/null || echo "No config found"

# 检查当前 active changes，避免命名冲突并理解现状
openspec list --json 2>/dev/null \
  || ls openspec/changes/ 2>/dev/null \
  || echo "No existing changes found"

# 读取归档 change，了解命名习惯
ls openspec/changes/archive/ 2>/dev/null | head -20

# 读取团队约定；AGENTS.md 是主入口，CLAUDE.md 只作为旧项目兼容
cat AGENTS.md 2>/dev/null | head -120
cat CLAUDE.md 2>/dev/null | head -80
cat .aisee/id-registry.json 2>/dev/null || true
```

用这些上下文：
- 理解项目技术栈和团队约定
- 识别可能依赖或冲突的进行中 changes
- 匹配既有 change 命名风格（kebab-case、长度、词汇）

### Architecture 输入模式

如果用户提供 `aisee:architecture` 生成的技术架构文档：

- 将技术事实、架构决策、技术栈状态、可复用能力、共享前置、耦合点和平台约束作为规划输入。
- 引用 Architecture 中已有的完整 `ARCH / DEC / CONSTRAINT / RISK` ID；不要在 change-plan 阶段分配这些 ID。
- 当阻塞标签影响边界时，在 change rationale 中保留 `[STACK-CONTEXT-MISSING]`、`[STACK-GAP]`、`[STACK-DECISION-REQUIRED]`、`[ARCHITECTURE-DECISION-REQUIRED]`、`[SPEC-GAP]`、`[STACK-CONFLICT]`。
- 不要把 architecture hints 解释成预先写好的 change 列表；最终 change 边界、依赖、命名和 `/opsx:new` 命令仍由 `aisee:change-plan` 决定。
- 不要在 `aisee:change-plan` 中替用户选择缺失的技术栈。如果 architecture 标记技术栈决策缺失，把它作为 blocker 或 assumption 暴露出来。

### Design-spec 输入模式

如果用户提供 `aisee:design-spec` 生成的设计规范文档：

- 将设计策略、组件策略、Design Tokens、screen patterns、交互模式、响应式规则、可访问性规则和 Do/Don't 作为规划输入。
- 当阻塞标签影响边界时，在 change rationale 中保留 `[DESIGN-DECISION-REQUIRED]` 和 `[ARCHITECTURE-CONTEXT-MISSING]`。
- 不要把 design-spec 解释成页面清单；PAGE / FLOW 范围仍由 UI Content 负责。
- 不要用 `aisee:change-plan` 从零创建设计系统。如果 design-spec 标记设计决策缺失，把它作为 blocker 或 assumption 暴露出来。
- 如果共享组件策略、token foundation 或跨页面 screen pattern 必须先存在，才能推进多个 UI changes，则在相关 change rationale 中记录为设计前置。

### SRS 输入模式

如果输入文件是 `aisee:srs` 生成的 SRS（可通过 `FR-xxx` 需求 ID 和“变更候选清单”识别），启用 **SRS 输入模式**：

- 将完整 `FR / NFR / RULE / FLOW / STATE` ID 作为分析的规范单元，不重新发明需求。
- 读取 Section 7（变更候选清单）作为主要规划输入，其中的优先级、规模估计和依赖提示可作为参考。
- 读取 Section 5.2（假设）和 Section 6（Open Questions）；未解决事项应影响 change rationale，并可能触发 Phase 2 的澄清问题。
- 每个 change 的 In Scope 必须保留完整 FR ID，确保能追踪回 SRS。
- SRS 模块名只是能力边界提示，不是 change 名称或 change 边界结论；最终边界必须通过 `references/input-boundary-rules.md` 审查。

### ID 输入规则

`aisee:change-plan` 只引用前置文档已经存在的正式 ID，不负责为上游对象分配 ID：

- SRS：引用 `FR / NFR / RULE / FLOW / STATE`。
- UI Content：引用 `PAGE / FLOW / STATE`。
- Architecture：引用 `ARCH / DEC / CONSTRAINT / RISK`。

如果前置文档缺少 ID：

- 不得临时发明正式 ID。
- 在相关 change 的 source-map seed 中写 `[SOURCE-ID-MISSING]` 或 `[ID-RESERVATION-REQUIRED]`。
- 如边界无法判断，输出 blocker；如边界可判断，继续规划但保留风险。

`SPEC / API / DATA / TASK / TEST` 属于 change-author 阶段产出，change-plan 只能写 `TBD in <artifact>`。

### 输入边界审查

在进入 Phase 3 前，读取 `references/input-boundary-rules.md`。

必须完成：
- 区分真实需求、上下文材料、技术层、页面类型、schema artifact 和实施任务。
- 对候选 change 做“保留 / 合并 / 拆分 / 拒绝”审查。
- 如果输入材料包含“背景 / UI / API / 数据库 / 测试 / 上线计划”等章节，不得直接生成同名 change。
- 如果关键架构决策缺失导致无法判断独立交付边界，输出 blocker，不要硬拆。

## 阶段 2 — 必要时澄清

当需求已经足够具体时，`aisee:change-plan` 应跳过澄清。最多问 **两个问题**，且只在以下情况提问：
- 需求横跨多个无关领域，边界不清
- 范围内组件或能力确实不明确
- 输入边界审查发现关键架构 / 设计 / 需求决策缺失，且会影响是否能独立交付

以下情况直接跳过澄清：
- 少于约 100 字、且只描述一个用户可见功能的小需求
- SRS 输入模式下 FR 范围已经明确

提问时只问一个聚焦问题：

> "在规划 change 边界前，需要先确认一点：{具体不确定项}。这会影响我把 X 和 Y 规划成一个 change 还是两个 change。"

如果用户没有回答或表示“你决定”，在整体理由中用 `[ASSUMPTION]` 记录假设并继续。

## 阶段 3 — 应用 Change 边界算法

先读取：
- `references/input-boundary-rules.md`
- `references/source-map-rules.md`

然后按以下优先级分析需求：

### 规则 1 — 可独立交付（不可协商）

每个 change 单独合并后，系统必须仍处于可工作状态。只添加数据库表但没有 API 或 UI 的 change，不算可独立交付；只添加半成品 UI 的 change，也不算可独立交付。

**测试问题**：如果今天只合并这个 change，其他 change 都不合并，系统是否仍能正确工作？

**Feature flags**：如果 change 在 feature flag 后发布，且 flag 关闭时既有行为保持不变，则可算作可独立交付。需要在 In Scope 中明确写出该 flag。

### 规则 2 — 单一 owner

每个 change 应该有一个可以独立做出技术决策的 Spec Owner。如果一个 change 同时触及支付、通知和鉴权，通常意味着 owner 不同；除非存在强纵向切片理由，否则应拆成多个 change。

### 规则 3 — 规划策略

按 `--strategy` 指定的策略规划，默认 `vertical`。

#### 策略：vertical（默认）

每个 change 交付一个端到端的用户 / 操作者 / 系统 / 设备可观察场景。避免横向切分（先全部 DB、再全部 API、再全部 UI），除非存在强技术理由，例如共享数据模型阻塞所有并行工作。

#### 策略：risk

优先处理最不确定的部分。最高风险 change（新算法、外部集成、未验证架构）进入 Phase 1，后续 changes 依赖其验证结果。

高风险信号：
- 首次集成第三方服务
- 技术可行性不确定
- 需要性能基准验证后才能确定方案
- 硬件 / 固件 / 设备约束尚未验证

使用该策略时，第一个 change 常常是限时 spike 或 PoC。它的输出是决策，不是可发布功能。必须明确标记：

```
Title: [SPIKE] 验证 <approach>
In Scope:
  - Prototype implementation to validate feasibility
  - Decision document: go / no-go + recommended approach
Out of Scope:
  - Production-quality code
  - Error handling beyond happy path
```

#### 策略：parallel

识别能最大化并行的边界。同一 phase 内的 changes 不应共享可变状态，也不应要求多个团队在实现过程中持续协调。

使用该策略时：
- 如需共享 contract（API schema、事件类型、数据模型、设备协议或配置约定），优先规划一个 S 级前置 change。
- 对每个并行 change 严格复查规则 1；并行策略最容易产生隐形耦合。
- 在依赖图中清楚标记每个并行组。

### 规则 4 — Schema 选择

- `aisee-app-spec-driven`：默认用于需要 SRS / UI Content / Architecture / Change Plan 追踪的新功能或功能迭代。
- `aisee-device-spec-driven`：用于嵌入式、固件、Linux 设备程序、驱动、RTOS、bare-metal、MCU、SoC 或板级 bring-up。
- `spec-driven`：仅用于不需要 Aisee 规划链追踪的轻量 change。
- `opsx-collab-pr-loop`：用于技术调研、外部 PR review 或范围不确定的调查工作。
- 如果用户传入 `--schema <name>`，每个 change block 和每条 `/opsx:new` 命令都必须一致使用该 schema。
- 混合系统可以同时需要 app 与 device schema，但每个具体 change 仍只能选择一个 schema；不要为了省事把云端、App、设备和固件塞进一个超大 change。

### 规则 5 — 粒度与复杂度上限

| 标记 | 估计工作量 | 使用场景 |
|------|------------|----------|
| S | 1–3 天 | 单一组件或单一场景，实施路径清晰 |
| M | 3–7 天 | 多组件协作，需要设计决策 |
| L | 7–14 天 | 架构范围较大，或不确定性较高 |

把 `--granularity` 当作规划约束，而不是宽松偏好：

| 粒度 | 输出约束 | 必须行为 |
|------|----------|----------|
| fine | 优先 S；避免 M；除非明确说明，否则不输出 L | 只要拆分后仍能独立交付，就拆分 M/L 候选 |
| medium | 允许 S/M；除非边界天然不可拆，否则避免 L | 默认策略，平衡可审查性和 change 数量 |
| coarse | 允许 S/M/L；不得输出 XL | 紧密相关、同 owner、可一起独立交付的子能力可合并 |

如果某个 change 超过 14 天（XL），必须继续拆分。在摘要中标记 ⚠️，并在 change rationale 中加入说明：

```
⚠️ 该 change 预计超过 14 天。建议先完成 /ce:brainstorm，
确认范围边界后再决定如何拆分。
```

没有足够领域上下文时，不要机械拆分 XL change；标记风险，并建议团队先补充 brainstorm 或需求澄清。

### 规则 6 — Change 数量上限

- 默认最多输出 **8 个 changes**。
- 如果用户传入 `--max-changes <N>`，使用该上限；但没有明确提醒“该需求应作为 epic planning session 处理”时，不得输出超过 8 个 changes。
- If `--single-if-small` is present and the scope is clearly ≤3 days with one owner and no risky coupling, output exactly one change.

### 规则 7 — 明确 Out-of-Scope

每个 change 必须有非空 Out-of-Scope。它用于防止实现阶段范围膨胀。“显然不包含”的事项也要写明。

### 规则 8 — 依赖纪律

- 只有当一个 change **必须先合并**，另一个 change 才能开始实现时，才标记依赖；“设计时需要知道”不等于实现依赖。
- 优先支持并行。如果两个 changes 只共享一个配置值，把配置作为 S 级前置 change，然后让其他 changes 并行。
- 不得创建循环依赖。

### 规则 9 — Source-map seed

每个 planned change 必须包含 source-map seed。生成 seed 前读取 `references/source-map-rules.md`。

对于 `aisee-app-spec-driven`：
- FR / NFR / RULE / FLOW / STATE ID 来自 SRS
- PAGE / FLOW / STATE ID 来自 UI Content，或写 `N/A`
- ARCH / DEC / CONSTRAINT / RISK ID 来自 Architecture，或写 `N/A`
- API 能力 ID 写 `TBD in service-contract`
- DATA ID 写 `TBD in data-model`
- SPEC / TASK / TEST ID 写 `TBD in change-author`
- 判断 `change-context.md`、`ui-contract.md`、`data-model.md`、`service-contract.md` 是否适用

对于 `aisee-device-spec-driven`：
- FR ID 来自 SRS 或 proposal
- 预期 HW ID，或写 `TBD in hardware-contract`
- 预期 FW ID，或写 `TBD in firmware-contract`
- 预期 RT ID，或写 `TBD in runtime-contract`
- 预期 VER ID，或写 `TBD in verification-contract`
- 判断 `hardware-contract.md`、`firmware-contract.md`、`runtime-contract.md`、`verification-contract.md` 是否适用

## 阶段 4 — 输出

按以下顺序输出：

---

### 摘要

`N 个 changes · M 个 phases · 预计总计 X 周 · Y 个可并行`

任何估计为 XL（>14 天）的 change 都要标记 ⚠️。

---

### 依赖图

简单依赖链使用 ASCII 展示：

```
Phase 1（顺序执行）:
  [change-name-1] ─── [change-name-2]

Phase 2（Phase 1 后可并行）:
  [change-name-3]
  [change-name-4]  ← 都依赖 change-name-2
  [change-name-5]

Phase 3:
  [change-name-6] ─── 依赖 change-name-3 和 change-name-4
```

如果依赖图超过 3 个 phase，或存在菱形依赖（一个 change 依赖多个并行分支），追加表格说明：

| Change | 依赖 | 可并行 |
|--------|------|--------|
| change-name-3 | change-name-2 | change-name-4, change-name-5 |
| change-name-4 | change-name-2 | change-name-3, change-name-5 |

---

### Change 详情

每个 change 输出一个区块：

```
─────────────────────────────────────────────────
change N/total

Name:         change-name-kebab-case
Title:        可读标题
Schema:       aisee-app-spec-driven | spec-driven | opsx-collab-pr-loop
Complexity:   S | M | L

Description:
  用一句话说明该 change 交付什么。

In Scope:
  - 具体范围 1 (FR-001)      ← SRS 输入模式下必须引用 FR-xxx
  - 具体范围 2 (FR-002)
  - 具体范围 3

Out of Scope:
  - 明确排除事项 1
  - 明确排除事项 2

Source-map seed:
  Upstream:
    FR:          <scope>:FR-001, <scope>:FR-002
    NFR/RULE:    <scope>:NFR-001, <scope>:RULE-001 (or "N/A")
    PAGE/FLOW:   <scope>:PAGE-001, <scope>:FLOW-001 (or "N/A")
    ARCH/DEC:    <scope>:ARCH-001, <scope>:DEC-001 (or "N/A")
    CONSTRAINT:  <scope>:CONSTRAINT-001 (or "N/A")
    RISK:        <scope>:RISK-001 (or "N/A")
  APP schema fields:
    SPEC: TBD in change-author
    API:  TBD in service-contract
    DATA: TBD in data-model
    TASK: TBD in tasks
    TEST: TBD in tasks / verification evidence
  DEVICE schema fields:
    HW:  expected HW IDs or "TBD in hardware-contract"
    FW:  expected FW IDs or "TBD in firmware-contract"
    RT:  expected RT IDs or "TBD in runtime-contract"
    VER: expected VER IDs or "TBD in verification-contract"
  Artifact applicability:
    - change-context.md: yes/no — 原因
    - ui-contract.md: yes/no — 原因
    - data-model.md: yes/no — 原因
    - service-contract.md: yes/no — 原因
    - hardware-contract.md: yes/no — 原因
    - firmware-contract.md: yes/no — 原因
    - runtime-contract.md: yes/no — 原因
    - verification-contract.md: yes/no — 原因

Depends on:    change-name（或 none）
Parallel with: change-name, change-name（或 none）

Change rationale:
  说明为什么这是自然边界，以及它为什么可以独立交付。

Command:
  /opsx:new "change-name-kebab-case" --schema aisee-app-spec-driven
─────────────────────────────────────────────────
```

---

### 全部命令（可复制，按执行顺序）

```bash
# Phase 1
/opsx:new "change-name-1" --schema aisee-app-spec-driven
/opsx:new "change-name-2" --schema aisee-app-spec-driven

# Phase 2 — 可并行运行
/opsx:new "change-name-3" --schema aisee-app-spec-driven
/opsx:new "change-name-4" --schema aisee-app-spec-driven
/opsx:new "change-name-5" --schema aisee-app-spec-driven

# Phase 3
/opsx:new "change-name-6" --schema aisee-app-spec-driven
```

---

### 整体理由

用 2–4 句话说明整体 change 规划策略：为什么选择这些边界、主要顺序约束是什么、需求中最不确定的部分是什么。

这里必须包含阶段 2 记录的所有 `[ASSUMPTION]`，格式如下：

```
[ASSUMPTION] {假设内容} — 影响 {change 列表} — 开始实现前请确认。
```

---

## 阶段 5 — 保存输出

将 change plan 输出保存到 `docs/change-plan/`，目录不存在则创建。

命名规则：`docs/change-plan/<YYYY-MM-DD>-<requirement-slug>.md`

其中 `requirement-slug` 使用需求标题前 5 个有意义词的 kebab-case。如果输入是 SRS 文件，则从 SRS 文件名推导 slug。

```bash
mkdir -p docs/change-plan
# 将文档写入上述路径
```

保存后输出：

> ✅ **Change plan 已保存**：`docs/change-plan/{filename}.md`
>
> **{N} 个 changes** · **{M} 个 phases** · {Y} 个可并行
>
> 先运行 Phase 1 的 `/opsx:new` 命令创建 change folders，然后使用 `aisee:change-author`（必要时配合 `/opsx:continue`）按 schema 逐步补齐 artifacts。

---

## 保护规则

- **单个需求不得输出超过 8 个 changes**。如果需要超过 8 个，说明它是 epic，需要单独规划。
- **不得创建只做 infrastructure 或 setup、没有用户可见结果的 change**。这类工作应并入第一个使用它的 change，或作为有清晰交接的 S 级前置 change。
- **不得只按文件类型或技术层规划 change**。同一功能不要机械拆成 “frontend change” + “backend change”，除非它们确实可以独立交付。
- 如果需求已经小到一个 change 即可完成（≤3 天），明确说明并只输出一条 `/opsx:new` 命令；不要为了规划而拆分。
- 不得发明原需求中不存在的范围。隐含但未说明的事项，放到第一个相关 change 的 Out-of-Scope，并标注：`（需求中未说明，纳入前请确认）`。

## 与 OpenSpec 工作流集成

```
aisee:srs                        ← 需求发现，输出 SRS 文档（docs/requirements/）
  ├─ aisee:ui-content            ← 页面内容规格（可选但推荐）
  ├─ aisee:design-spec           ← UI 设计规范事实源（UI 型需求可选但推荐）
  ├─ aisee:architecture          ← 技术架构事实、决策与约束（可选但推荐）
  └─ aisee:change-plan <inputs>        ← 本 skill：规划独立 OpenSpec Change 边界
       └─ /opsx:new <change>     ← 创建 Change Folder
            └─ aisee:change-author ← 按 schema 创建 / 补 proposal、specs、contracts、tasks、source-map
            └─ openspec validate
            └─ aisee:implementation-bridge ← 生成给 Compound 的实现上下文
            └─ compound plan / work / review / test ← 工程实现与验证
            └─ aisee:verify       ← 验证 specs / source-map / tasks / 实现一致性
            └─ aisee:archive-guard  ← archive 前门禁
            └─ openspec archive     ← 已验证 change 合入 baseline
```

当多个 changes 同时进行时，必须显式指定 change 名：

```bash
openspec archive change-name-3     # 避免歧义
```
