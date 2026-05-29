# OpenSpec 自定义 Schema 指南
## 团队工作流定制与管理

> 本文档覆盖：Schema 原理、文件结构、创建方式、模板编写、团队管理规范。
> 适合已完成 OpenSpec 基础配置、需要针对不同任务类型定制工作流的团队。

---

## 目录

1. [Schema 是什么](#一schema-是什么)
2. [内置 Schema 解析](#二内置-schema-解析)
3. [Schema 解析优先级](#三schema-解析优先级)
4. [文件结构详解](#四文件结构详解)
5. [创建自定义 Schema](#五创建自定义-schema)
6. [编写 schema.yaml](#六编写-schemayaml)
7. [编写 Templates](#七编写-templates)
8. [接入 config.yaml](#八接入-configyaml)
9. [团队 Schema 管理规范](#九团队-schema-管理规范)
10. [我们项目的 Schema 清单](#十我们项目的-schema-清单)
11. [常用场景 Schema 设计参考](#十一常用场景-schema-设计参考)
12. [CLI 命令速查](#十二cli-命令速查)

---

## 一、Schema 是什么

Schema 是 **OpenSpec change 的工作流定义文件**，它声明：

- 一个 change folder 里要产出哪些 **artifacts**（文档）
- 这些 artifacts 的**依赖顺序**（哪个必须先完成才能开始下一个）
- 每个 artifact 的 **template**（AI 填写时的结构骨架）
- 每个 artifact 的 **instruction**（给 AI 的详细行为指导）
- **apply 阶段**何时可以开始实现

不同的任务类型可以用不同的 schema，从而得到完全不同的 artifacts 集合和工作流程。

```
同一套 OPSX 命令 (/opsx:new, :ff, :apply...)
         ↓
  读取不同 schema
         ↓
产出不同 artifacts，走不同工作流
```

---

## 二、内置 Schema 解析

OpenSpec 内置了一个 `spec-driven` schema，是所有功能开发的默认选择。

### spec-driven 依赖图

```
proposal.md
    │
    ├──────────────────┐
    ▼                  ▼
specs/**/*.md      design.md
    │                  │
    └────────┬─────────┘
             ▼
          tasks.md
             │
             ▼
          apply（实现阶段）
```

### Artifacts 说明

| Artifact | 文件 | 依赖 | 职责 |
|----------|------|------|------|
| `proposal` | `proposal.md` | 无（最先创建） | 为什么做、做什么、成功标准、不在范围内的事 |
| `specs` | `specs/**/*.md` | proposal | 需求场景、边界条件、验收标准（Given/When/Then） |
| `design` | `design.md` | proposal | 技术方案、架构决策、接口定义、数据流 |
| `tasks` | `tasks.md` | specs + design | 实现清单，checkbox 格式，tracked by apply |

apply 阶段在 `tasks.md` 存在后才解锁，由 tasks.md 的 checkbox 追踪进度。

---

## 三、Schema 解析优先级

当一个 change 需要确定用哪个 schema 时，按以下顺序查找：

### Schema 名称解析（用哪个名字）

```
1. CLI 显式参数          → /opsx:new my-feature --schema my-schema
2. Change 目录元数据     → openspec/changes/<feature>/.openspec.yaml
3. 项目配置              → openspec/config.yaml 的 schema: 字段
4. 默认值               → spec-driven
```

### Schema 文件位置解析（文件在哪里）

```
1. openspec/schemas/<name>/          ← 项目本地（最高优先级，可覆盖其他）
2. ~/.local/share/openspec/schemas/  ← 用户全局
3. npm 包内置 schemas/               ← 官方内置（最低优先级）
```

**关键点**：项目本地 schema（`openspec/schemas/`）总是覆盖同名的官方内置 schema。这意味着你可以 fork `spec-driven` 并在项目内修改，不影响其他项目。

---

## 四、文件结构详解

一个完整的 custom schema 目录结构：

```
openspec/schemas/<schema-name>/
├── schema.yaml              ← Schema 定义（必须）
└── templates/               ← AI 填写时的文档骨架（必须）
    ├── proposal.md          ← 对应 proposal artifact 的模板
    ├── spec.md              ← 对应 specs artifact 的模板
    ├── design.md            ← 对应 design artifact 的模板
    └── tasks.md             ← 对应 tasks artifact 的模板
```

对应你们项目里的 `opsx-collab-pr-loop`：

```
openspec/schemas/opsx-collab-pr-loop/
├── schema.yaml
└── templates/
    ├── intake.md            ← 接收问题/PR 的模板
    ├── research-plan.md     ← 调研计划的模板
    ├── implementation.md    ← 实现的模板
    └── checkpoints.md       ← 验收节点的模板
```

---

## 五、创建自定义 Schema

有三种方式，按推荐程度排序：

### 方式 A：Fork 现有 Schema（推荐）

基于 `spec-driven` 或其他已有 schema 进行修改，保留大部分结构：

```bash
# Fork 官方 spec-driven 到项目本地
openspec schema fork spec-driven my-schema-name

# 查看创建结果
ls openspec/schemas/my-schema-name/
# → schema.yaml  templates/

# 验证 schema 格式是否正确
openspec schema validate my-schema-name
```

Fork 后在 `openspec/schemas/my-schema-name/` 里直接编辑即可，不影响原始 schema。

### 方式 B：交互式创建（从零开始）

```bash
openspec schema init my-schema-name
# → 交互式 Q&A，指导你填写 artifacts、dependencies、description
```

### 方式 C：直接手写文件（最灵活）

手动创建目录和文件，适合对结构很清楚的情况：

```bash
mkdir -p openspec/schemas/my-schema-name/templates
touch openspec/schemas/my-schema-name/schema.yaml
# 然后手动编写 schema.yaml 和各 template 文件
```

---

## 六、编写 schema.yaml

### 完整字段说明

```yaml
name: my-schema-name          # 唯一标识符，kebab-case，与目录名一致
version: 1                    # 版本号（整数）
description: "schema 的用途描述"  # 可选，人类可读

artifacts:
  - id: artifact-id           # 在 requires 中引用的唯一 ID
    generates: output.md      # 输出文件路径，支持 glob（如 specs/**/*.md）
    description: "这个 artifact 是做什么的"
    template: templates/output.md  # 相对于 schema 目录的模板路径
    instruction: |            # 可选，给 AI 的详细行为指导（支持多行）
      创建这个文档时，你需要：
      - 做 XXX
      - 注意 YYY
    requires: []              # 依赖的其他 artifact ID 列表，空数组=无依赖

apply:                        # 可选，控制实现阶段何时解锁
  requires:                   # 哪些 artifacts 完成后才能 apply
    - tasks
  tracks: tasks.md            # 用哪个文件的 checkbox 追踪进度
  instruction: |              # 可选，apply 阶段的指导
    按照 tasks.md 逐项实现，完成一项打一个勾
```

### 最小可用 Schema 示例

```yaml
name: quick-fix
version: 1
description: "快速 bug fix，无需完整 spec"

artifacts:
  - id: problem
    generates: problem.md
    description: "描述问题"
    template: templates/problem.md
    requires: []

  - id: solution
    generates: solution.md
    description: "解决方案"
    template: templates/solution.md
    requires: [problem]

  - id: tasks
    generates: tasks.md
    description: "实现清单"
    template: templates/tasks.md
    requires: [solution]

apply:
  requires: [tasks]
  tracks: tasks.md
```

### 带 loop 子目录的 Schema（仿 opsx-collab-pr-loop）

当任务需要**多轮迭代**时，可以把 artifacts 放在子目录：

```yaml
name: opsx-collab-pr-loop
version: 1
description: "PR 协作与技术调研的迭代工作流"

artifacts:
  - id: intake
    generates: loop/intake.md       # ← 注意子目录
    description: "接收 PR/问题，理解背景"
    template: templates/intake.md
    requires: []

  - id: research-plan
    generates: loop/research-plan.md
    description: "调研计划与方向"
    template: templates/research-plan.md
    requires: [intake]

  - id: implementation
    generates: loop/implementation.md
    description: "实现内容或回应"
    template: templates/implementation.md
    requires: [research-plan]

  - id: checkpoints
    generates: loop/checkpoints.md
    description: "验收节点，确认是否需要下一轮"
    template: templates/checkpoints.md
    requires: [implementation]

apply:
  requires: [research-plan]
  tracks: loop/implementation.md
```

### Artifact 状态机

每个 artifact 在运行时有三种状态：

| 状态 | 条件 | 含义 |
|------|------|------|
| `BLOCKED` | 依赖项还未完成 | 还不能创建 |
| `READY` | 依赖项已完成，本文件不存在 | 可以创建了 |
| `DONE` | 文件已存在于磁盘 | 已完成 |

`/opsx:continue` 每次创建一个 READY 状态的 artifact，然后显示新解锁的 artifacts。

---

## 七、编写 Templates

Template 是 AI 填写 artifact 时的**结构骨架**，不是内容本身，AI 会按照骨架生成实际内容。

### 编写原则

- 用 `## ` 划分章节，AI 会按章节填写
- 用注释（`<!-- -->` 或 `> `）说明每个章节要填写什么
- 写清楚约束和格式要求（如 Given/When/Then）
- 不要填写具体内容，只提供骨架

### proposal.md 模板示例

```markdown
# Proposal: {{change-name}}

## Intent
<!-- 用 1-3 句话说明：为什么要做这个，解决什么问题 -->

## Scope

### In Scope
<!-- 明确列出本次 change 要覆盖的内容 -->
- 

### Out of Scope
<!-- 明确列出不做的事（防止 AI "善意"扩展） -->
- 

## Success Criteria
<!-- 什么情况下算成功完成？要可验证 -->
- [ ] 

## Spec Owner
<!-- @mention 负责人 -->

## Rollback Plan
<!-- 如果需要回滚，怎么做 -->
```

### spec.md 模板示例（Given/When/Then 格式）

```markdown
# Delta for {{capability}}

## ADDED Requirements

### Requirement: {{requirement-name}}
The system SHALL {{描述系统行为，使用 SHALL/MUST}}.

#### Scenario: {{主流程场景}}
- GIVEN {{前置条件}}
- WHEN {{触发动作}}
- THEN {{期望结果}}
- AND {{附加期望}}

#### Scenario: {{边界场景1}}
- GIVEN {{前置条件}}
- WHEN {{触发动作}}
- THEN {{期望结果}}

#### Scenario: {{边界场景2}}
<!-- 至少提供 2 个边界 case -->
```

### design.md 模板示例

```markdown
# Design: {{change-name}}

## Architecture Overview
<!-- 高层架构图或描述，复杂流程用序列图 -->

## Technical Decisions

### Decision: {{决策标题}}
**选择**：{{选择了什么}}
**理由**：{{为什么这样选}}
**放弃的选项**：{{考虑了哪些替代方案，为什么放弃}}

## Interface Changes
<!-- 新增或修改的 API / 函数签名 / 数据结构 -->

## Data Flow
<!-- 数据如何流动，用文字或图描述 -->

## Open Questions
<!-- 还未决定的问题，实现时需要关注 -->
```

### tasks.md 模板示例

```markdown
# Tasks: {{change-name}}

> 严格按顺序执行，完成一项打一个勾。
> 发现问题：暂停 → 更新本文件 → /opsx:sync → 继续。

## Phase 1: {{阶段名称}}

- [ ] 1.1 {{具体任务描述}}
- [ ] 1.2 {{具体任务描述}}
- [ ] 1.3 {{具体任务描述}}

## Phase 2: {{阶段名称}}

- [ ] 2.1 {{具体任务描述}}
- [ ] 2.2 {{具体任务描述}}

## Verification

- [ ] 单元测试覆盖主流程
- [ ] 边界 case 有对应测试
- [ ] /opsx:verify 通过
```

### intake.md 模板示例（collab-pr-loop 用）

```markdown
# Intake: {{change-name}}

## Source
<!-- PR 链接 / Issue 编号 / 需求来源 -->

## Background
<!-- 这个 PR/问题的背景，理解为什么有这个 -->

## What's Being Asked
<!-- 具体要求是什么，要做什么回应或实现 -->

## Initial Assessment
<!-- 初步判断：复杂度？风险？需要哪些调研？ -->

## Stakeholders
<!-- 谁提的，谁受影响，谁需要 review -->
```

---

## 八、接入 config.yaml

在 `openspec/config.yaml` 中配置 schema 相关设置，让团队成员无需手动指定 schema：

```yaml
# openspec/config.yaml

# 设置项目默认 schema
schema: spec-driven   # 所有新 change 默认使用这个 schema

# 注入所有 artifacts 的通用上下文（最大 50KB）
context: |
  Tech stack: TypeScript, React, Node.js
  API conventions: RESTful, JSON responses
  Testing: Vitest for unit tests, Playwright for e2e
  Style: ESLint with Prettier, strict TypeScript
  Team workflow: See TEAM_WORKFLOW.md

# 对特定 artifact 类型追加规则
rules:
  proposal:
    - Include rollback plan for all database changes
    - Identify affected teams and notify via Slack
    - Spec Owner must be assigned before proceeding
  specs:
    - Use Given/When/Then format for all scenarios
    - Minimum 2 boundary/edge case scenarios required
    - Use SHALL/MUST for requirements language
  design:
    - Include sequence diagrams for flows with 3+ actors
    - Document all rejected alternatives with reasons
    - Flag any breaking API changes with [BREAKING]
  tasks:
    - Each task should be completable in under 2 hours
    - Include a verification task for each phase
```

### Instruction 组装顺序

AI 收到的实际 instruction 由三层按顺序组装：

```
1. context（来自 config.yaml）
   → 包裹在 <context>...</context>

2. rules（来自 config.yaml，匹配 artifact 类型）
   → 包裹在 <rules>...</rules>

3. template（来自 schema 的 templates/ 目录）
   → 直接附在最后
```

这意味着你可以通过 `config.yaml` 的 `rules` 字段给所有 schemas 的特定 artifact 类型追加约束，而不必修改每个 schema 的 template。

---

## 九、团队 Schema 管理规范

### 9.1 Schema 存储位置规范

```
openspec/schemas/              ← 所有团队共享 schema 放这里
├── opsx-collab-pr-loop/       ← 已有的协作流程 schema
│   ├── schema.yaml
│   └── templates/
└── <your-next-schema>/        ← 新增的 schema
    ├── schema.yaml
    └── templates/
```

**强制要求**：所有 `openspec/schemas/` 下的文件都必须**提交到 Git**，随项目代码一起版本管理。Schema 变更通过 PR 走 code review，不得直接 push to main。

### 9.2 Schema 变更流程

```
需要新建或修改 schema
  ↓
创建 schema-change PR
  ├── 新增 schema：创建完整目录结构 + 写说明
  └── 修改 schema：说明为什么要改、影响哪些已有 changes

Tech Lead review + approve
  ↓
merge to main
  ↓
通知团队（Slack @ 所有人）：新 schema 可用
  ↓
需要的成员在本地 pull 最新代码即可使用
```

### 9.3 Schema 命名约定

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 官方内置 | `spec-driven` | `spec-driven` |
| 任务类型 | `<task-type>` | `quick-fix`、`research` |
| 协作流程 | `opsx-<pattern>-<flow>` | `opsx-collab-pr-loop` |
| 领域专用 | `<domain>-<type>` | `security-audit`、`infra-change` |
| Fork 修改版 | `<original>-<team>` | `spec-driven-extended` |

### 9.4 Schema 文档要求

每个自定义 schema 必须在 `schema.yaml` 的 `description` 字段写清楚：

```yaml
description: |
  适用场景：<什么任务类型用这个>
  与 spec-driven 的区别：<为什么不用默认的>
  创建时间：<YYYY-MM-DD>
  维护人：<@mention>
```

### 9.5 哪些任务用哪个 Schema

| 任务类型 | 推荐 Schema | 理由 |
|----------|------------|------|
| 新功能开发 | `spec-driven` | 标准流程，proposal → specs → design → tasks |
| Bug Fix（普通） | `spec-driven` | 同上，走完整流程保证质量 |
| Bug Fix（紧急/Hotfix） | `quick-fix`（如有） | 简化流程，快速出产 |
| PR Code Review | `opsx-collab-pr-loop` | 以外部输入为驱动，可多轮迭代 |
| 技术调研 | `opsx-collab-pr-loop` | 需要 intake + research plan |
| 依赖升级（复杂） | `spec-driven` | 需要完整的影响分析 |
| 架构变更 | `spec-driven` + 额外 config.yaml rules | 需要更严格的 design 要求 |

### 9.6 废弃 Schema

当一个 schema 不再使用时：

```bash
# 1. 确认没有 active changes 在用这个 schema
openspec list --json | grep "schema-name"

# 2. 在 schema.yaml 中添加废弃标注
# description: "[DEPRECATED 2026-05-01] 请使用 spec-driven 替代"

# 3. 3 个月后彻底删除目录
# rm -rf openspec/schemas/deprecated-schema-name/
```

---

## 十、我们项目的 Schema 清单

> 本节记录项目中所有自定义 schema，新增 schema 时必须在此更新。

### `spec-driven`（官方内置，项目默认）

- **来源**：OpenSpec 官方内置
- **适用**：所有标准功能开发、bug fix
- **Artifacts**：`proposal.md` → `specs/` + `design.md` → `tasks.md`
- **特别配置**：见 `openspec/config.yaml` 中的 rules

### `opsx-collab-pr-loop`（项目本地自定义）

- **来源**：项目自研，位于 `openspec/schemas/opsx-collab-pr-loop/`
- **适用**：PR 协作、技术调研、外部需求处理
- **Artifacts**：`loop/intake.md` → `loop/research-plan.md` → `loop/implementation.md` → `loop/checkpoints.md`
- **特点**：artifacts 在 `loop/` 子目录，支持多轮迭代
- **维护人**：@<owner>

---

## 十一、常用场景 Schema 设计参考

### 场景 A：安全审查 Schema

```yaml
name: security-audit
version: 1
description: |
  适用场景：涉及认证、授权、数据隐私的变更
  要求：在标准 spec-driven 基础上增加威胁模型文档

artifacts:
  - id: proposal
    generates: proposal.md
    description: "变更提案"
    template: templates/proposal.md
    requires: []

  - id: threat-model
    generates: threat-model.md
    description: "威胁模型分析"
    template: templates/threat-model.md
    requires: [proposal]
    instruction: |
      识别所有攻击面，评估每个威胁的影响和概率，
      提供缓解措施。使用 STRIDE 模型分类威胁。

  - id: specs
    generates: specs/**/*.md
    description: "需求场景（含安全场景）"
    template: templates/spec.md
    requires: [threat-model]

  - id: design
    generates: design.md
    description: "技术方案（含安全设计）"
    template: templates/design.md
    requires: [proposal]

  - id: tasks
    generates: tasks.md
    description: "实现清单"
    template: templates/tasks.md
    requires: [specs, design]

apply:
  requires: [tasks]
  tracks: tasks.md
```

### 场景 B：基础设施变更 Schema

```yaml
name: infra-change
version: 1
description: |
  适用场景：服务器配置、CI/CD、部署流程变更
  特点：增加影响评估和回滚测试两个 artifacts

artifacts:
  - id: proposal
    generates: proposal.md
    description: "变更提案"
    template: templates/proposal.md
    requires: []

  - id: impact
    generates: impact-assessment.md
    description: "影响评估：哪些服务受影响，停机时间评估"
    template: templates/impact.md
    requires: [proposal]

  - id: rollback
    generates: rollback-plan.md
    description: "回滚方案：如何快速恢复"
    template: templates/rollback.md
    requires: [proposal]

  - id: tasks
    generates: tasks.md
    description: "实现清单"
    template: templates/tasks.md
    requires: [impact, rollback]

apply:
  requires: [tasks]
  tracks: tasks.md
```

### 场景 C：快速调研 Schema（轻量版 collab-pr-loop）

```yaml
name: quick-research
version: 1
description: |
  适用场景：不需要完整实现的技术调研、可行性分析

artifacts:
  - id: question
    generates: question.md
    description: "调研问题是什么"
    template: templates/question.md
    requires: []

  - id: findings
    generates: findings.md
    description: "调研发现"
    template: templates/findings.md
    requires: [question]

  - id: recommendation
    generates: recommendation.md
    description: "建议和下一步"
    template: templates/recommendation.md
    requires: [findings]

# 注意：这个 schema 没有 apply block
# 因为调研不产生代码实现
```

---

## 十二、CLI 命令速查

### Schema 管理

```bash
# 查看所有可用 schema（及来源）
openspec schema which --all

# 查看某个 schema 的来源
openspec schema which my-schema

# Fork 已有 schema 到项目本地
openspec schema fork spec-driven my-new-schema
openspec schema fork opsx-collab-pr-loop my-variant

# 交互式创建新 schema
openspec schema init my-schema

# 验证 schema 格式
openspec schema validate my-schema
```

### 使用 Schema 创建 Change

```bash
# 使用默认 schema（来自 config.yaml 或 spec-driven）
/opsx:new "feature-name"
/opsx:propose "feature-name"

# 指定 schema
/opsx:new "pr-review-task" --schema opsx-collab-pr-loop
/opsx:new "security-feature" --schema security-audit

# 查看 change 状态（含 schema 信息）
openspec status --change <change-name>
openspec show <change-name>
```

### 调试 Schema

```bash
# 查看某个 change 当前的 artifact 状态
openspec status --change my-feature

# JSON 输出（用于脚本）
openspec status --change my-feature --json

# 查看 AI 会收到的完整 instructions（调试 schema 效果）
openspec instructions --change my-feature --artifact proposal

# 查看可用 templates
openspec templates
```

---

## 附录：Schema 字段完整参考

### schema.yaml 顶层字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 唯一标识符，kebab-case，与目录名一致 |
| `version` | integer | ✅ | 版本号（整数，从 1 开始） |
| `description` | string | ❌ | 人类可读的描述 |
| `artifacts` | array | ✅ | artifact 定义列表，顺序影响 dashboard 显示 |
| `apply` | object | ❌ | 实现阶段配置，不写则默认所有 artifacts 完成后解锁 |

### artifact 字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 在 `requires` 中引用的唯一 ID |
| `generates` | string | ✅ | 输出文件路径，支持 glob（`specs/**/*.md`） |
| `description` | string | ✅ | 这个 artifact 是做什么的 |
| `template` | string | ✅ | 相对于 schema 目录的模板路径 |
| `instruction` | string | ❌ | 给 AI 的详细行为指导，多行支持 |
| `requires` | string[] | ✅ | 依赖的 artifact ID 列表，无依赖写 `[]` |

### apply 字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `requires` | string[] | ✅ | 哪些 artifacts 完成后才能开始 apply |
| `tracks` | string | ❌ | 进度追踪文件路径（一般是 `tasks.md`） |
| `instruction` | string | ❌ | apply 阶段给 AI 的指导 |

---

*本文档随项目演进更新。如需新增 schema，请先阅读 §九 团队管理规范。*
*最后更新：2026-04-11*
