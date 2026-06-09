# Implementation Brief Template

当 `aisee:implementation-bridge` 需要为单个 OpenSpec change 输出实现交接内容时，使用本模板。

规则：

- 只写摘要、路径、ID、允许路径、批次任务和验证入口，不复制 proposal、specs、contracts、source-map 或 tasks 正文。
- 大 change 使用 `brief-index-template.md` 生成 `brief-index.md`，再用本模板生成多个 `brief-part-NN.md`。每个 part 仍指向同一个 current change 和 apply tracks。
- 保存到文件时，优先使用 `aisee/cache/implementation-bridge/<change>/brief-part-NN.md`；这些文件是 generated handoff / cache，不是规范事实源。

```md
---
title: "Implementation Brief"
doc_type: "implementation-brief"
status: "draft"
date: "{date}"
scope: "<change>"
owner: "{作者或团队}"
source_refs:
  - "openspec/changes/<change>"
change_refs:
  - "openspec/changes/<change>"
anchors: []
---

# Implementation Brief

## Preflight

- Author check:
- Gaps:
- Context pack:
- Blocked:

## Authoritative Source

- Change: `openspec/changes/<change>`
- Schema:
- Source-map required:
- Apply tracks:
- Specs:
- Tasks / apply tracks:
- Source Map:
- Contracts:

## Change Scope

- In scope:
- Out of scope:
- Upstream IDs:
- Produced IDs:
- Batch: part N of M / single

## Read First

1. （待填）
2. （待填）
3. （待填）

## Artifact Map

| Artifact | Role in implementation | Required | Notes |
|---|---|---:|---|
| specs/**/*.md | Behavior contract | yes / no | 仅当 schema 生成 |
| source-map.md | ID and code routing | yes / no | 仅当 schema 生成 |
| tasks.md / apply tracks | Durable execution list | yes / no | 以 schema 为准 |
| change-context.md / design.md | Architecture / design constraints | yes / no | app change-context Required=no 时写 source-map N/A 原因；design.md 只在 schema 生成时出现 |
| ui-contract.md | UI implementation contract | yes / no | Required=no 时写 source-map N/A 原因 |
| service-contract.md | API / service contract | yes / no | Required=no 时写 source-map N/A 原因 |
| data-model.md | Data contract | yes / no | Required=no 时写 source-map N/A 原因 |

## Execution Rules

- Follow current schema apply tracks; do not create a parallel durable plan.
- Preserve traceability when touching code or tests; source-map schema 回写 `source-map.md`，轻量 schema 回写对应主 artifact / apply tracks。
- If implementation facts conflict with specs or contracts, pause and update the current OpenSpec change first.

## Scope Guardrails

- Do not implement:
- Follow-up candidates:
- Accepted assumptions:

## Task Execution

- Batch goal:
- Start from:
- Suggested order:
- Code paths:
- Test paths:
- Implementation path source:
- Apply tracks to update:

## Verification

- Required commands:
- Required manual checks:
- Evidence to record:
- Evidence destination:

## Review Recommendation

- Tier 2 code review required: yes / no
- Trigger reason:
- Existing review evidence:
- Suggested authorization: `使用审查代理做 Tier 2 code review` / N/A
- Evidence destination:

## Blockers and Assumptions

- Blockers:
- Assumptions:
- Temporary IDs / unresolved source-map entries:

## Recommended Compound Skill

- Recommended: `ce-work`
- Use `ce-plan` first only if:
- After implementation: recommended review gate if required, relevant `ce-test-*`, then `aisee:verify`
```
