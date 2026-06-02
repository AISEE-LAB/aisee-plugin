---
name: aisee:reflect
description: 复盘当前会话并把可复用经验沉淀为项目内可审查资产。用于会话结束复盘、总结“这次学到了什么”、提炼团队约定、发现可转成新 skill 的重复流程、审查现有 skill 的缺口、记录 workflow fix，或用户明确说 reflect、aisee:reflect、aisee-reflect、复盘、沉淀、保存经验、转成技能、优化技能、总结本次协作时触发。长会话中如果出现多轮纠错、重复工具链、稳定偏好或可复用流程，也应主动建议使用本技能。
---

# aisee:reflect

复盘当前会话，识别可复用经验，并把结论写成项目内可版本化、可审查的 Markdown 资产。

本技能默认只负责“反思、归纳、候选沉淀”。`aisee/docs/reflect/` 是复盘与候选区；`aisee/memory/` 才是 `aisee:init` 定义的长期项目记忆区。不要直接修改全局记忆、隐藏配置或其他技能目录，除非用户明确要求继续执行对应改动。

## 输出位置

| 产物 | 路径 |
|---|---|
| 会话复盘与 memory 候选 | `aisee/docs/reflect/YYYY-MM-DD_<slug>.md` |
| 新技能草案 | `aisee/docs/reflect/skills/YYYY-MM-DD_<skill-name>.md` |
| 现有技能优化建议 | `aisee/docs/reflect/skill-patches/YYYY-MM-DD_<skill-name>.md` |
| 工作流修复建议 | `aisee/docs/reflect/workflow-fixes/YYYY-MM-DD_<slug>.md` |
| 已确认长期记忆 | `aisee/memory/arch/`、`aisee/memory/pref/`、`aisee/memory/ctx/`、`aisee/memory/stack/` |

文件名使用当天日期和短 kebab-case slug。默认使用用户语言；没有明确语言时使用中文。

## 工作模式

根据用户意图选择模式：

| 用户意图 | 行为 |
|---|---|
| 只说“reflect / 复盘 / 总结这次” | 先输出复盘报告，不写文件，等待用户确认 |
| 明确说“保存 / 写入 / 生成文档 / 全部落盘” | 输出报告后直接写入对应文件 |
| 明确说“写入 memory / 提升到记忆 / 更新 aisee/memory” | 按 `aisee/memory/rules.md` 分类写入项目记忆，并更新 `aisee/memory/index.md` |
| 明确要求“转成 skill / 优化某技能” | 生成技能草案或技能补丁，不把草案直接提升为活动技能 |
| 会话很短或缺少可沉淀信息 | 说明发现有限，只列出有信号的事项 |

如果用户要求修改真实技能目录，应改用或结合 skill-creator 工作流；本技能生成的草案默认只是审查材料。

## Memory 边界

Codex 或其他代理即使支持某种自动记忆能力，也不要假设它会按本项目结构保存。项目内长期记忆必须以 `aisee:init` 生成的 `aisee/memory/rules.md` 和 `aisee/memory/index.md` 为准。

规则：

- `aisee/docs/reflect/`：复盘记录、候选规则、技能草案、补丁建议。默认写这里。
- `aisee/memory/`：用户确认后的长期记忆。只有用户明确要求“写入 memory / 提升到记忆 / 更新 aisee/memory”时才写。
- 不写全局 memory、用户主目录 memory 或代理私有 memory，除非用户明确要求并确认影响。
- 如果 `aisee/memory/rules.md` 或 `aisee/memory/index.md` 不存在，先建议运行 `aisee:init` 初始化；不要临时发明另一套结构。

提升到 `aisee/memory/` 时按以下规则分类：

| 类型 | 写入位置 | 用途 |
|---|---|---|
| 架构决策 | `aisee/memory/arch/YYYY-MM-DD-{slug}.md` | 长期保留的技术、架构、流程决策 |
| 用户偏好 | `aisee/memory/pref/{topic}.md` | 语言、格式、工具、协作风格等稳定偏好 |
| 上下文快照 | `aisee/memory/ctx/YYYY-MM-DD-{slug}.md` | 约 30 天内有用的任务背景、阶段性结论 |
| 技术栈笔记 | `aisee/memory/stack/{technology}.md` | 版本、配置、兼容性、已知问题 |

写入顺序：

1. 读取 `aisee/memory/rules.md` 和 `aisee/memory/index.md`。
2. 把 reflect 发现筛选为“长期仍有价值”的最小集合。
3. 先写对应 `aisee/memory/<type>/...md` 文件。
4. 再更新 `aisee/memory/index.md` 的一行摘要链接。
5. 最终回复列出写入路径和未提升的候选项。

## Phase 1 — 收集上下文

先通读当前会话，并优先检查项目内已有规则，避免重复沉淀：

```bash
rg --files \
  -g 'AGENTS.md' \
  -g 'CLAUDE.md' \
  -g 'README.md' \
  -g 'aisee/memory/*.md' \
  -g 'aisee/memory/**/*.md' \
  | sort

find aisee/docs/reflect -maxdepth 3 -type f 2>/dev/null | sort | tail -20
```

如果 `rg` 不可用，使用当前目录范围的 `find .`，并排除依赖和版本控制目录：

```bash
find . \
  -path './node_modules' -prune -o \
  -path './.git' -prune -o \
  \( -name AGENTS.md -o -name CLAUDE.md -o -name README.md \) \
  -print
```

关注以下信号：

- 用户目标：本次会话实际想完成什么。
- 重复流程：是否出现可固化为技能、脚本或检查清单的步骤。
- 纠错记录：模型哪里误判、遗漏、过度设计或输出格式不合适。
- 稳定偏好：用户明确或反复体现的语言、格式、验证、工具偏好。
- 项目事实：路径、命名、配置、约束、团队流程等可复用信息。
- 验证缺口：哪些测试、浏览器检查、命令或审查步骤应该补上。

不要把一次性偶然事件写成长期规则。优先沉淀“未来再次发生时会节省时间或降低风险”的内容。

## Phase 2 — 分类判断

把发现归入四类；没有发现的类别不要输出。

### 新技能候选

适合沉淀为 skill 的信号：

- 形成了 4 步以上稳定流程。
- 用户未来很可能重复执行。
- 涉及特定领域、工具链、文档格式或团队规范。
- 现有技能无法覆盖，或覆盖后仍需要大量临场补充。

每条包含：

- 建议技能名。
- 触发场景。
- 核心流程。
- 本次会话证据。
- 不应覆盖的边界。

### 现有技能优化

适合写 skill patch 的信号：

- 技能触发描述不够明确，导致该用未用。
- 技能步骤遗漏关键检查、确认门或验证。
- 输出格式让用户反复纠正。
- 技能边界过宽或过窄。

每条包含：

- 技能名。
- 问题。
- 建议修改的位置。
- 替换或新增文本。
- 预期收益与风险。

### Memory 候选

适合作为 memory 候选写入 reflect doc 的信号：

- 用户明确表达偏好或团队约定。
- 项目路径、命名、配置、流程被确认。
- 某个检查步骤被证明必要。
- 某个默认行为在本项目中应避免。

每条写成可执行规则，而不是观察记录：

```markdown
- 默认用中文回复和生成项目文档，除非用户明确要求其他语言。
- 修改技能时先检查同仓库已有 `aisee-*` 技能的命名和说明风格。
```

### 工作流修复

适合写 workflow fix 的信号：

- 某个协作步骤反复产生摩擦。
- 可通过执行顺序、确认门、验证命令或输出模板降低风险。
- 该修复不属于单个技能，也不是项目事实本身。

每条包含：

- 问题。
- 新行为。
- 适用范围：全局或本项目。
- 建议加入的规则文本。

## Phase 3 — 输出复盘报告

报告要简洁、可执行，使用以下结构：

```markdown
# Reflect 报告

## 会话概览
- 目标：
- 已完成：
- 主要摩擦：

## 新技能候选
1. `<skill-name>`
   - 触发：
   - 流程：
   - 证据：
   - 边界：

## 现有技能优化
1. `<skill-name>`
   - 问题：
   - 修改：
   - 收益：

## Memory 候选
1. <ready-to-write rule>
   - 理由：
   - 建议类型：arch | pref | ctx | stack

## 工作流修复
1. <fix title>
   - 新行为：
   - 适用范围：

## 优先建议
如果只做一件事：<highest-value action>

## 可执行选项
- 回复 `保存复盘` 写入 `aisee/docs/reflect/`
- 回复 `写入 memory 1` 将候选 1 按 `aisee/memory/rules.md` 提升为项目记忆
- 回复 `保存技能 1` 写入技能草案
- 回复 `保存补丁 1` 写入技能优化建议
- 回复 `保存修复 1` 写入工作流修复
- 回复 `全部保存` 写入所有 reflect 建议产物；不自动提升到 `aisee/memory/`
```

如果用户已经要求写入文件，省略“可执行选项”中的等待语气，改为列出已写入路径。

## Phase 4 — 写入文件

写文件前先创建目录：

```bash
mkdir -p aisee/docs/reflect aisee/docs/reflect/skills aisee/docs/reflect/skill-patches aisee/docs/reflect/workflow-fixes
```

### 会话复盘文档

路径：

```text
aisee/docs/reflect/YYYY-MM-DD_<slug>.md
```

模板：

```markdown
# Reflect: <Session Title>

_Date: YYYY-MM-DD_

## Context

<1-2 sentences>

## Memory Candidates

- <rule>  
  Type: arch | pref | ctx | stack

## Project Facts

- <fact>

## Workflow Preferences

- <rule>

## Open Questions

- <question or "无">
```

只保留有证据的内容。没有内容的章节可写“无”，不要强行填充。

### 提升为项目 Memory

只有用户明确要求时执行。必须遵循项目根目录下 `aisee/memory/rules.md`：

```text
aisee/memory/
  index.md
  arch/YYYY-MM-DD-{slug}.md
  pref/{topic}.md
  ctx/YYYY-MM-DD-{slug}.md
  stack/{technology}.md
```

记忆文件模板：

```markdown
# {标题}

**日期：** YYYY-MM-DD
**类型：** arch | pref | ctx | stack

## 摘要

一到两句话说明这条记忆记录了什么。

## 详情

正文内容。

## 引用

- 相关 reflect 文档、项目文件或会话依据
```

更新 `aisee/memory/index.md` 时只追加一行摘要链接，不把正文写进 index。

### 新技能草案

路径：

```text
aisee/docs/reflect/skills/YYYY-MM-DD_<skill-name>.md
```

模板：

```markdown
# Skill Draft: <skill-name>

> Status: Draft. Review before promoting to an active skill directory.

---
name: <skill-name>
description: <trigger-focused description>
---

# <skill-name>

## Purpose

## When To Use

## Workflow

## Inputs

## Outputs

## Verification

## Boundaries
```

草案必须包含触发描述、工作流、输出格式和边界。不要把草案直接写入 `.claude/skills/` 或活动技能目录，除非用户明确要求。

### 技能优化建议

路径：

```text
aisee/docs/reflect/skill-patches/YYYY-MM-DD_<skill-name>.md
```

模板：

```markdown
# Skill Patch: <skill-name>

_Date: YYYY-MM-DD_

## Issue

## Proposed Change

## Before

## After

## Edge Cases Addressed

## Verification
```

`After` 应给出可直接复制到技能中的文本，而不只是泛泛建议。

### 工作流修复建议

路径：

```text
aisee/docs/reflect/workflow-fixes/YYYY-MM-DD_<slug>.md
```

模板：

````markdown
# Workflow Fix: <short title>

_Date: YYYY-MM-DD_

## Problem

## Fix

## Applies To

- [ ] Global
- [ ] This project only

## Suggested Instruction

```markdown
<ready-to-paste instruction>
```

## Verification
````

## Phase 5 — 更新索引

写入任何 `aisee/docs/reflect/` 产物后，检查项目根目录是否有 `AGENTS.md`、旧项目兼容用 `CLAUDE.md` 或其他项目规则索引。

- 如果已有 `aisee/docs/reflect` 入口，不重复添加。
- 如果存在项目规则文件但没有入口，建议用户确认是否添加索引；不要擅自改全局规则。
- 如果没有项目规则文件，只在最终回复中说明未更新索引。

可建议的索引文本：

```markdown
## Reflect Docs

Session learning artifacts are stored in `aisee/docs/reflect/`.
Use them for project conventions, skill drafts, skill patch notes, and workflow fixes discovered during collaboration.
```

## 质量标准

- 具体：每条发现都能对应到本次会话中的行为、纠错或明确偏好。
- 可执行：结论应能转成规则、补丁、草案或检查步骤。
- 有边界：说明什么不属于该发现，避免规则泛化。
- 少而精：优先输出高信号内容，避免把普通过程记录成长期约定。
- 可验证：涉及命令、路径或文件时，检查其存在性或明确标注未验证。
- 不扩散敏感信息：不要写入 secrets、token、cookie、私密身份信息或生产凭据。

## 最终回复

最终回复包含：

- 写入或修改的文件路径。
- 每类产物数量。
- 是否更新索引。
- 未执行的验证或剩余风险。
