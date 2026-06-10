# Reflect 输出模板

本文维护 `aisee:reflect` 的报告和落盘模板。只有需要生成正式报告、写文件、提升 memory、生成技能草案、技能补丁或 workflow fix 时读取。

## Reflect 报告模板

```markdown
---
title: "Reflect 报告"
doc_type: "reflect"
status: "draft"
date: "YYYY-MM-DD"
scope: "session"
owner: "{作者或团队}"
source_refs: []
change_refs: []
---

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

## 可复用知识候选
1. `<candidate-id>`
   - 适用范围：
   - 触发：
   - 推荐动作：
   - 证据：
   - 不适用：

## Compound Solution Follow-up
- Suggested follow-up: run ce-compound for the concrete solution.
- 适用问题：
- 证据：

## 工作流修复
1. <fix title>
   - 新行为：
   - 适用范围：

## 优先建议
如果只做一件事：<highest-value action>

## 可执行选项
- 回复 `保存复盘` 写入 `aisee/docs/reflect/`
- 回复 `写入 memory 1` 将候选 1 交给 `aisee:memory`，并通过 `aisee memory add` 提升为项目记忆
- 回复 `保存技能 1` 写入技能草案
- 回复 `保存补丁 1` 写入技能优化建议
- 回复 `保存知识候选 1` 写入 reusable knowledge candidate
- 回复 `保存修复 1` 写入工作流修复
- 回复 `全部保存` 写入所有 reflect 建议产物；不自动提升到 `aisee/memory/`
```

如果用户已经要求写入文件，省略“可执行选项”中的等待语气，改为列出已写入路径。

## 会话复盘文档

路径：

```text
aisee/docs/reflect/YYYY-MM-DD_<slug>.md
```

模板：

```markdown
---
title: "Reflect: <Session Title>"
doc_type: "reflect"
status: "draft"
date: "YYYY-MM-DD"
scope: "session"
owner: "{作者或团队}"
source_refs: []
change_refs: []
---

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

## Reusable Knowledge Candidates

- <candidate summary or "无">

## Compound Solution Follow-ups

- <suggested ce-compound follow-up or "无">

## Open Questions

- <question or "无">
```

只保留有证据的内容。没有内容的章节可写“无”，不要强行填充。

## 提升为项目 Memory

只有用户明确要求时执行。先运行 `aisee memory inspect --json`，再通过 `aisee memory add ... --json` 写入 canonical `aisee/memory/`。

CLI 维护的推荐结构：

```text
aisee/memory/
  index.md
  arch/YYYY-MM-DD-{slug}.md
  pref/{topic}.md
  ctx/YYYY-MM-DD-{slug}.md
  stack/{technology}.md
```

`aisee memory add` 写入 YAML frontmatter + Markdown 正文；不要手工维护旧粗体 metadata 模板。最小字段为：

```markdown
---
id: <safe-slug>
title: <标题>
type: arch | pref | ctx | stack
status: active
priority: high | normal | low
summary: <一句话摘要>
source_refs: []
updated_at: <ISO datetime>
---

# <标题>

<正文>
```

CLI 会更新 `aisee/memory/index.md` 和 `aisee/cache/memory-index.json`；cache 不是事实源。

## 新技能草案

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

草案必须包含触发描述、工作流、输出格式和边界。不要把草案直接写入活动技能目录，除非用户明确要求。

## 技能优化建议

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

## 工作流修复建议

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

## Reflect Docs 索引文本

```markdown
## Reflect Docs

Session learning artifacts are stored in `aisee/docs/reflect/`.
Use them for project conventions, skill drafts, skill patch notes, and workflow fixes discovered during collaboration.
```
