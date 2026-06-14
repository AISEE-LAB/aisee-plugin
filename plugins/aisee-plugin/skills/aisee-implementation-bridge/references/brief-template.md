# Implementation Brief Template

当需要把 `aisee:implementation-bridge` 的读取策略保存成人读 handoff 时使用本模板。它只索引当前 change 下“先读什么、完成后回写什么”；缺细节时回读当前 change artifacts，不复制 artifact 正文。

规则：

- Brief 是 generated handoff / cache，不是规范事实源。
- 只写当前 change 已给出的读取顺序、apply tracks、verification / evidence 入口和 risks。
- 空字段删除或标 `N/A`；不要把模板占位当事实。
- 大 change 先用 `brief-index-template.md` 分批，再为每批使用本模板。

```md
---
title: "Implementation Brief"
doc_type: "implementation-brief"
status: "draft"
date: "{date}"
scope: "<change>"
source_refs:
  - "openspec/changes/<change>"
change_refs:
  - "openspec/changes/<change>"
---

# Implementation Brief

## Preflight

- Schema:
- Blocked: yes / no
- Optional memory / knowledge injection: yes / no

## Authoritative Sources

- Current change artifacts and supporting files:

## Scope And Traceability

- In scope:
- Out of scope:
- Source refs / mode, when present:
- Produced local IDs, when present:

## Execution Index

- Read first:
- Apply tracks to update:
- Before marking work complete:

## Rules

- Follow current schema apply tracks; do not create a parallel durable plan.
- Preserve traceability: source-map schema updates `source-map.md`; lighter schemas update the relevant artifact / apply tracks.
- Do not report the current batch as complete before apply tracks are updated. For `tasks.md` schemas, update checkbox state, verification tasks, and evidence entry first.
- If implementation facts conflict with specs or contracts, stop and update the current OpenSpec change first.
- UI icons: reuse the project's component library or icon package first. If no suitable icon exists, use globally installed `better-icons` / Iconify first for speed; install or invoke it via the project package manager, `npx -y better-icons`, or `bunx better-icons` when missing. Record the command and final `prefix:name` icon IDs as evidence.

## Verification And Evidence

- Required verification:
- Evidence destination:
- Icon evidence if UI icons changed: component library / icon package, `better-icons` command when used, selected `prefix:name`, size, color strategy.

## Risks And Follow-up

- Risks / blockers from current change gaps and evidence:
- Follow-up candidates:
- Review recommendation:
```
