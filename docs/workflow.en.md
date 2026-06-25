# Aisee Workflow

This document describes the recommended software development workflow for Aisee with OpenSpec. It follows the OpenSpec rhythm: propose a change, complete artifacts, validate, implement and verify, then archive into the baseline.

## Core Principles

- OpenSpec is the specification state machine and baseline source of truth.
- Aisee currently emphasizes OpenSpec setup, baseline migration, intent clarification, change authoring, and memory/knowledge enhancement.
- Aisee CLI emits JSON context views. It does not create a second specification source.
- Implementation, review, and test work can be handled by Compound Engineering or another coding agent.
- `openspec archive <change>` is the final operation that merges a verified change into the baseline.
- planning docs serve the current version or iteration only; they do not replace baseline facts.
- regular planning docs use a shared YAML frontmatter contract for identity, status, and source indexing; OpenSpec changes and baseline specs remain the authoritative facts.
- formal authoring uses stable numbers inside documents; cross-document sources are recorded in `source-map.md`.

## 0. Project Setup

Use this for new projects or existing projects that are adopting OpenSpec.

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
aisee doctor --json
```

Boundary note: `aisee openspec ensure` is the step that writes OpenSpec instructions/skills into the current project directory and also aligns global `openspec config profile`; do not treat `config profile` itself as the project-local installation step.

Use `aisee:init` to audit or create:

- `AGENTS.md`
- `openspec/project.md`
- `aisee/memory/`
- required hooks

For existing projects, or when doing brownfield enhancement work, avoid writing new changes immediately. Prefer `aisee:spec-migrate` to derive baseline specs from verified current behavior first.

## Default Path vs On-Demand Extensions

`aisee:init` belongs to project setup and governance, not to the default new-feature happy path. The current recommended path for new work centers on `aisee:srs`, `aisee:change-plan`, and `aisee:change-author`; use `aisee:spec-migrate` only when an existing project needs a baseline first.

The following capabilities are conditional, not mandatory on every iteration:

- `aisee:design-spec` / `aisee:design-assets`: only when visual rules, references, or asset planning are needed.
- `aisee:spec-migrate`: only when onboarding an existing project or establishing a brownfield baseline, not for every iteration.
- `aisee:memory`: only for controlled project memory retrieval, writes, and index maintenance.
- `aisee:reflect` / `aisee:knowledge-curate`: only for retrospectives, project memory candidates, and team knowledge curation.
- Other legacy / transitional skills remain publicly exposed today, but they are not part of the currently recommended product path.

## 1. Upfront Clarification

The goal is to turn chat-based ideas into reviewable inputs before implementation.

Recommended order:

```text
aisee:srs
  -> aisee:change-plan
  -> /opsx:new
  -> aisee:change-author
```

Artifact roles:

| Artifact | Purpose | Notes |
| --- | --- | --- |
| SRS | Clarifies business goals, scope, functional requirements, non-functional requirements, and acceptance criteria | Does not write implementation tasks |
| Change Plan | Maps confirmed inputs into one or more OpenSpec changes | Does not write change artifact bodies directly |
| Change Author | Fills out the current change's schema-defined documents in detail and strengthens them with clearer boundaries, risks, verification, and implementation sequencing | Does not write implementation code |

These documents are planning docs for the current version or iteration. They are planning inputs, not OpenSpec baseline facts.

## 2. Change Planning

Use `aisee:change-plan` to map confirmed inputs into independently deliverable OpenSpec changes. One version or iteration can be split into one or more changes.

```text
aisee:change-plan
  -> change list
  -> dependency order
  -> schema recommendation
  -> /opsx:new input
```

Splitting rules:

- One change should represent one verifiable user or engineering outcome.
- Do not treat source document sections, technical layers, page types, schema artifacts, or task phases as changes.
- Large work may have dependency ordering, but a single change should not carry the whole product.
- Low-risk fixes can use `quick-fix` instead of the app schema.
- Small, bounded, low-risk work can skip heavy upfront docs and enter an appropriate lightweight schema directly.
- When frontend and backend share APIs, events, data models, or SDKs, prefer a prerequisite contract change.

## 3. Change Creation And Authoring

After creating a change, use `aisee:change-author` to fill out the current schema's documents in detail. Preserve the template structure first, then strengthen the parts most likely to cause implementation, review, or verification mistakes.

Typical commands:

```bash
/opsx:new "<change>" --schema <project-schema-or-spec-driven>
openspec validate <change>
```

Common as-needed document examples:

- `service-contract.md`
- `data-model.md`

Current rules:

- Only write documents declared by the current schema; do not invent undeclared files.
- Templates are the starting skeleton, not the completion condition; each document should strengthen the needed boundaries, exceptions, risks, verification details, or implementation handoff.
- Required=yes documents must be expanded; Required=no documents must provide a concrete N/A reason.
- Do not generate unrelated contracts or helper docs for completeness.
- If a schema still declares `source-map.md`, treat it as an ordinary schema document and fill it according to its template; do not make it the center of the whole authoring phase.

## 4. Implementation Handoff

Before implementation, confirm the change is authored.

```bash
openspec/changes/<change>/
```

If the project has long-lived local guidance such as commit preferences, test commands, architecture decision summaries, or stack constraints, retrieve project memory explicitly:

```bash
aisee memory search --query "<current implementation task>" --json
```

Project memory matches are guidance only. They do not change the current change's specification source and should not be copied into OpenSpec artifacts.

If the project has configured team knowledge, read a small number of guardrails before high-risk implementation such as public interfaces, schemas, path reads, security, or cross-repository contracts:

```bash
aisee knowledge query --from-change <change> --for ce-work --json
```

Knowledge matches are reminders only. They do not change the current change's specification source and should not be copied into durable artifacts.

Before implementation, read the current change, schema, related artifacts, `tasks.md`, the necessary evidence entrypoints, and any project memory / team knowledge guidance directly; no separate Aisee implementation handoff skill is required.

## 5. Implementation, Review, And Test

Implementation can be handled by a coding agent or human developer. Regardless of tooling:

- Implement only the current change scope.
- If specs, contracts, and code disagree, update the current OpenSpec change before continuing.
- Do not defer this until verify or archive; before `ce-work` reports the current batch complete, update `tasks.md` or the current schema apply tracks first.
- Record test, manual verification, preview, monitoring, or review results as evidence.

When a change touches public CLI behavior, HTTP endpoints, API/service contracts, schemas, parsers, path reads, security, or privacy, Tier 2 code review is recommended.

Read-only Aisee reviewer lens timing:

| Reviewer | When to trigger | Purpose |
| --- | --- | --- |
| `aisee-change-architect` | After `aisee:change-plan` and before `aisee:change-author` when the change has complex boundaries, cross-module or cross-schema impact, unclear dependencies, or uncertain granularity | Review change boundaries, dependencies, granularity, and independent deliverability |
| `aisee-spec-reviewer` | After `aisee:change-author` and before implementation | Review whether the current schema documents, N/A reasons, tasks, and verification posture are complete, consistent, and verifiable |
| `aisee-implementation-reviewer` | After `ce-work` | Compare implementation, the current schema documents, tasks, and evidence for drift |

These reviewers only return structured review conclusions. They do not edit code, run tests, submit PRs, or replace `ce-doc-review`, `ce-code-review`, `ce-test-*`, or `ce-work`. Interface, UI, hardware, firmware, security, and verification differences should remain schema-aware check lenses rather than new all-purpose agents.

## 6. Verify

After implementation, run:

```bash
openspec validate <change>
```

Then read the current change artifacts, schema, `tasks.md`, `source-map.md` when applicable, and evidence directly, and produce a manual or tool-assisted consistency review that checks:

- whether schema artifacts exist;
- whether Required=yes contracts are closed;
- whether source-map, document-local numbers, code paths, test paths, and evidence are consistent;
- whether `tasks.md` or apply tracks are truly complete;
- whether OpenSpec validate passed;
- whether review/test/manual evidence is sufficient;
- whether Tier 2 review is still needed.

Before archive, confirm that:

- `openspec validate <change>` passed;
- apply tracks are closed;
- review/test/manual evidence is sufficient;
- accepted risks have an owner, reason, impact, and follow-up path.

Then run:

```bash
openspec archive <change>
```

## 7. Project Memory Usage

Project memory serves current-repository guidance. It is not cross-project reuse and does not replace OpenSpec.

Recommended path:

```bash
aisee memory inspect --json
aisee memory search --query "<task>" --json
aisee memory add --type pref --title "<title>" --summary "<summary>" --body "<body>" --json
aisee memory update-index --json
```

Boundaries:

- Default retrieval returns a small number of active metadata entries, not full bodies.
- Write only when the user explicitly says "remember", "from now on", or asks to write project memory.
- New writes go only to canonical `aisee/memory/`; legacy `.memory/` is read-only fallback.
- Hooks are read-only and never write memory automatically.
- If memory conflicts with OpenSpec artifacts, `source-map.md`, or `tasks.md`, OpenSpec artifacts win.

## 8. Team Knowledge Reuse

When a project produces reusable engineering lessons, first let the user explicitly trigger `aisee:reflect` to create project-local candidates, then run `aisee:knowledge-curate` when batch review, desensitization, generalization, and deduplication are needed.

Recommended path:

```text
aisee:reflect
  -> aisee/docs/reflect/knowledge-candidates/
  -> aisee:knowledge-curate
  -> batch review report / card drafts
  -> user confirmation before writing to the team knowledge repo
```

Boundaries:

- Do not write team knowledge automatically after archive or verify.
- Do not copy whole `docs/solutions/`, memory, or reflect documents into other projects.
- Do not let AI scan team knowledge repository bodies directly; use `aisee knowledge query`.
- Writing to the team repo, creating branches, committing, merging, or opening PRs requires explicit user authorization again.

## Fast Paths

| Scenario | Recommended Path |
| --- | --- |
| New feature | SRS -> change-plan -> change-author -> implementation / review / test -> archive |
| Small fix | `quick-fix` schema -> change-author -> implementation / review / test -> archive |
| Technical research | `quick-research` schema -> findings/recommendation -> validate -> archive-guard |
| Documentation site change | `aisee-docsite-driven` schema -> doc-change/tasks -> build/link evidence -> archive-guard |
| Existing project adoption / brownfield baseline | `aisee:init` -> `aisee:spec-migrate` -> baseline specs -> new change |

## When To Stop

Do not continue into implementation when:

- the requirement scope is still unclear;
- the current change cannot map to a verifiable outcome;
- schema artifacts are missing or contradictory;
- a Required=yes contract is missing;
- implementation paths are not referenced by the current change, `tasks.md`, or `source-map.md` when applicable;
- OpenSpec validate fails without a clear fix path.

Return to the relevant artifact instead of guessing during implementation.
