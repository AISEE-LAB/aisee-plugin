# Implementation Brief Template

当需要把 `aisee context pack --change <change> --for ce-work --json` 保存成人读 handoff 时使用本模板。优先消费 `facts.derived.execution.brief`；缺细节时回读当前 change artifacts，不复制 artifact 正文。

规则：

- Brief 是 generated handoff / cache，不是规范事实源。
- 只写 context pack 已给出的 source refs、scope、paths、tasks、verification 和 risks。
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

## Context Pack

- Command: `aisee context pack --change <change> --for ce-work --json`
- Schema:
- Blocked: yes / no
- Requires ce-plan: yes / no
- ce-plan reason: N/A

## Authoritative Sources

- From `facts.derived.execution.brief.authoritative_sources`:

## Scope And Traceability

- In scope:
- Out of scope:
- Source refs / mode:
- Produced local IDs:

## Execution Index

- Read first:
- Allowed code paths:
- Allowed test paths:
- Start from:
- Apply tracks to update:

## Rules

- Follow current schema apply tracks; do not create a parallel durable plan.
- Preserve traceability: source-map schema updates `source-map.md`; lighter schemas update the relevant artifact / apply tracks.
- If implementation facts conflict with specs or contracts, stop and update the current OpenSpec change first.
- UI icons: reuse the project's component library or icon package first. If no suitable icon exists, use globally installed `better-icons` / Iconify first for speed; install or invoke it via the project package manager, `npx -y better-icons`, or `bunx better-icons` when missing. Record the command and final `prefix:name` icon IDs as evidence.

## Verification And Evidence

- Required verification:
- Evidence destination:
- Icon evidence if UI icons changed: component library / icon package, `better-icons` command when used, selected `prefix:name`, size, color strategy.

## Risks And Follow-up

- Risks / blockers from `gaps` and `facts.derived.execution.brief.risks`:
- Follow-up candidates:
- Review recommendation:
```
