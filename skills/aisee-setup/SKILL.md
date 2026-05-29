---
name: aisee:setup
description: 初始化、审计和修复 Aisee/OpenSpec/Compound 项目基础设施。用于检查 OpenSpec CLI、openspec init、Aisee schema pack、AGENTS.md、openspec/project.md、.memory、.aisee/sources.json、.aisee/id-registry.json、Codex hooks 和 Compound Engineering plugin/skills 是否可用。它不处理业务需求、不拆 change、不写实现计划。
---

# aisee:setup

`aisee:setup` 负责让项目具备 Aisee + OpenSpec + Compound 协作基础设施。

## 职责

- 检查 OpenSpec CLI 是否可用。
- 检查当前项目是否已 `openspec init`。
- 安装或审计 Aisee schema pack。
- 初始化或修复 `AGENTS.md`、`openspec/project.md`、`.memory/`。
- 初始化 `.aisee/sources.json` 和 `.aisee/id-registry.json`。
- 配置 Codex hooks。
- 检查 Compound Engineering plugin 和关键 CE skills 是否可用。

## 安全规则

- 默认先输出 plan，不直接覆盖已有文件。
- 修改 `AGENTS.md`、`CLAUDE.md`、`openspec/project.md`、hooks 前必须确认影响。
- 不静默安装全局依赖。
- 不替代 `openspec init` 的内部逻辑；需要初始化 OpenSpec 时调用 OpenSpec CLI。

## 推荐输出

```md
# Aisee Setup Report

## Status

## Missing

## Planned Changes

## Risks

## Commands
```
