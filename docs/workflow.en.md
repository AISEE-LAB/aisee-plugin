# Aisee Workflow

This document describes the recommended software development workflow for Aisee with OpenSpec. It follows the OpenSpec rhythm: propose a change, complete artifacts, validate, implement and verify, then archive into the baseline.

## Core Principles

- OpenSpec is the specification state machine and baseline source of truth.
- Aisee handles requirement clarification, context shaping, memory/knowledge enhancement, schema-aware handoff, and guardrails.
- Aisee CLI emits JSON context views. It does not create a second specification source.
- Implementation, review, and test work can be handled by Compound Engineering or another coding agent.
- `openspec archive <change>` is the final operation that merges a verified change into the baseline.
- planning docs serve the current version or iteration only; they do not replace baseline facts.
- regular planning docs use a shared YAML frontmatter contract for identity, status, and source indexing; OpenSpec changes and baseline specs remain the authoritative facts.
- formal authoring uses stable numbers inside documents; cross-document sources are recorded in `source-map.md`.

## 0. Project Setup

Use this for new projects or existing projects that are adopting OpenSpec.

If you have just entered a project and do not know which Aisee workflow should start, use `aisee:orient` first to identify project state, user intent, and the next route.

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

For existing projects, avoid writing new changes immediately. Prefer `aisee:spec-migrate` to derive baseline specs from verified current behavior first.

## Default Path vs On-Demand Extensions

`aisee:orient` and `aisee:init` belong to project orientation, setup, and governance, not to the default new-feature iteration happy path. The default new-feature happy path depends only on the core iteration workflow: `aisee:srs`, `aisee:ui-content`, `aisee:architecture`, `aisee:change-plan`, `aisee:change-author`, `aisee-schema-pack`, and `aisee:implementation-bridge`.

The following capabilities are conditional, not mandatory on every iteration:

- `aisee:design-spec` / `aisee:design-assets`: only when visual rules, references, or asset planning are needed.
- `aisee:svg-assets` / `aisee:image-object`: only for asset production or image-object workflows.
- `aisee:spec-migrate`: only when onboarding an existing project into a baseline spec flow.
- `aisee:memory`: only for controlled project memory retrieval, writes, and index maintenance.
- `aisee:reflect` / `aisee:knowledge-curate`: only for retrospectives, project memory candidates, and team knowledge curation.
- `hw:*`: only for hardware, embedded, or experimental domains; they do not affect the default app workflow.

## 1. Upfront Clarification

The goal is to turn chat-based ideas into reviewable inputs before implementation.

Recommended order:

```text
aisee:srs
  -> aisee:ui-content, when UI exists
  -> aisee:architecture
```

If visual rules, reference imagery, or asset planning are needed, enter `aisee:design-spec` / `aisee:design-assets` as an on-demand branch. They are not mandatory in the default happy path.

Artifact roles:

| Artifact | Purpose | Notes |
| --- | --- | --- |
| SRS | Clarifies business goals, scope, functional requirements, non-functional requirements, and acceptance criteria | Does not write implementation tasks |
| UI Content | Describes pages, content, states, actions, permission visibility, and frontend data needs | Does not write component library, color, typography, or layout rules |
| Design Spec / Assets | Describes or generates visual rules, references, assets, and style inputs | Does not duplicate page content |
| Architecture | Records technical facts, architecture boundaries, platform constraints, shared conventions, and risks | Does not replace change artifacts |

These documents are planning docs for the current version or iteration. They are planning inputs, not OpenSpec baseline facts.

## 2. Change Planning

Use `aisee:change-plan` to map confirmed inputs into independently deliverable OpenSpec changes. One version or iteration can be split into one or more changes.

```text
aisee:change-plan
  -> change list
  -> dependency order
  -> schema recommendation
  -> source-map seed
```

Splitting rules:

- One change should represent one verifiable user or engineering outcome.
- Do not treat source document sections, technical layers, page types, schema artifacts, or task phases as changes.
- Large work may have dependency ordering, but a single change should not carry the whole product.
- Low-risk fixes can use `quick-fix` instead of the app schema.
- Small, bounded, low-risk work can skip heavy upfront docs such as SRS, UI Content, or Architecture and enter an appropriate lightweight schema directly.
- When frontend and backend share APIs, events, data models, or SDKs, prefer a prerequisite contract change.

## 3. Change Creation And Authoring

After creating a change, use `aisee:change-author` to complete artifacts according to the schema artifact DAG.

Typical commands:

```bash
/opsx:new "<change>" --schema aisee-app-spec-driven
openspec validate <change>
```

Common app schema artifacts:

```text
proposal.md
source-map.md
specs/**/*.md
tasks.md
change-context.md        # as needed
ui-contract.md           # as needed
service-contract.md      # as needed
data-model.md            # as needed
```

`source-map.md` decides whether as-needed artifacts are required:

- Required=yes: expand the artifact.
- Required=no: provide a concrete N/A reason.
- Do not generate unrelated contracts for completeness.
- Use `Ref` / `Refs` for source references in upstream tables; use document-local numbers for new objects created inside the current change.

## 4. Implementation Handoff

Before implementation, confirm the change is authored.

```bash
aisee context pack --change <change> --for ce-work --json
```

If the project has long-lived local guidance such as commit preferences, test commands, architecture decision summaries, or stack constraints, retrieve project memory explicitly:

```bash
aisee memory search --query "<current implementation task>" --json
aisee context pack --change <change> --for ce-work --project-memory --json
```

Project memory matches are guidance only. They do not change the current change's specification source and should not be copied into OpenSpec artifacts.

If the project has configured team knowledge, read a small number of guardrails before high-risk implementation such as public interfaces, schemas, path reads, security, or cross-repository contracts:

```bash
aisee knowledge query --from-change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
```

Knowledge matches are reminders only. They do not change the current change's specification source and should not be copied into durable artifacts.

Then use `aisee:implementation-bridge` to produce an Implementation Brief. The brief is an execution index:

- current change and schema;
- read-first artifacts;
- allowed code and test paths;
- apply tracks writeback location;
- verification commands and evidence location;
- whether Tier 2 code review is recommended.

If a change is large, do not go back to change-plan just to split it again. Create `brief-index.md` and multiple `brief-part-NN.md` files inside the same current change handoff flow.

## 5. Implementation, Review, And Test

Implementation can be handled by a coding agent or human developer. Regardless of tooling:

- Implement only the current change scope.
- If specs, contracts, and code disagree, update the current OpenSpec change before continuing.
- Update `tasks.md` or the current schema apply tracks after implementation.
- Record test, manual verification, preview, monitoring, or review results as evidence.

When a change touches public CLI behavior, HTTP endpoints, API/service contracts, schemas, parsers, path reads, security, or privacy, Tier 2 code review is recommended.

Read-only Aisee reviewer lens timing:

| Reviewer | When to trigger | Purpose |
| --- | --- | --- |
| `aisee-change-architect` | After `aisee:change-plan` and before `aisee:change-author` when the change has complex boundaries, cross-module or cross-schema impact, unclear dependencies, or uncertain granularity | Review change boundaries, dependencies, granularity, and independent deliverability |
| `aisee-spec-reviewer` | After `aisee:change-author` and before `aisee:implementation-bridge` / `ce-work` | Review whether artifacts, contracts, source-map, and tasks are complete, consistent, and verifiable |
| `aisee-implementation-reviewer` | After `ce-work` | Compare implementation, tasks, specs/source-map, and evidence for drift |

These reviewers only return structured review conclusions. They do not edit code, run tests, submit PRs, or replace `ce-doc-review`, `ce-code-review`, `ce-test-*`, or `ce-work`. Interface, UI, hardware, firmware, security, and verification differences should remain schema-aware check lenses rather than new all-purpose agents.

## 6. Verify

After implementation, run:

```bash
openspec validate <change>
aisee context pack --change <change> --for aisee-verify --json
```

Then use `aisee:verify` or a manual review pass to check:

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
| New feature | SRS -> UI/Architecture -> change-plan -> change-author -> implementation-bridge -> verify -> archive-guard |
| Small fix | `quick-fix` schema -> change-author -> implementation-bridge -> implementation / review / test -> archive |
| Technical research | `quick-research` schema -> findings/recommendation -> validate -> archive-guard |
| Documentation site change | `aisee-docsite-driven` schema -> doc-change/tasks -> build/link evidence -> archive-guard |
| Unsure where to start | `aisee:orient` -> recommended next skill / workflow |
| Existing project adoption | `aisee:init` -> `aisee:spec-migrate` -> baseline specs -> new change |

## When To Stop

Do not continue into implementation when:

- the requirement scope is still unclear;
- the current change cannot map to a verifiable outcome;
- schema artifacts are missing or contradictory;
- a Required=yes contract is missing;
- implementation paths are not referenced by the current change or context pack;
- OpenSpec validate fails without a clear fix path.

Return to the relevant artifact instead of guessing during implementation.
