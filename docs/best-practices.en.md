# Aisee Best Practices

This document records recommended conventions for using Aisee. The goal is to let OpenSpec manage specification facts while Aisee manages context and handoff, without making the workflow heavy or creating a second specification system.

## 1. Keep OpenSpec As The Single Specification Source

OpenSpec baseline and active changes are the durable specification source:

```text
openspec/specs/
openspec/changes/
```

Aisee documents, CLI JSON, Implementation Briefs, review reports, and chat summaries are not baseline facts. They can be:

- planning inputs;
- context views;
- implementation handoffs;
- verification evidence;
- improvement suggestions.

Any conclusion that must persist should be written back to the current OpenSpec change, baseline specs, schema apply tracks, or source-map.

## 1.1 Use The Core Workflow By Default

The default new-feature happy path should start with the core workflow only. `design-*`, `svg-assets`, `image-object`, `spec-migrate`, `reflect`, `knowledge-curate`, and `hw:*` are on-demand extensions; do not flatten them into mandatory steps for every iteration.

## 2. Do Not Let Upfront Documents Replace Change Artifacts

SRS, UI Content, Design Spec, and Architecture help plan the current version or iteration's changes.

Recommended:

```text
SRS / UI Content / Architecture
  -> aisee:change-plan
  -> OpenSpec change artifacts
```

Avoid:

```text
Implementing directly after SRS
Using UI Content as ui-contract
Using Architecture as change-context
Using chat history as tasks
```

Change artifacts should contain only what the current change needs. Do not copy entire upstream documents into the change.

## 3. One Change Owns One Verifiable Outcome

A good change should be:

- independently validatable;
- independently implementable and testable;
- independently archivable;
- isolated enough that failures do not confuse unrelated changes.

Avoid using these as change boundaries:

- document sections;
- technical layers;
- page types;
- schema artifacts;
- task phases;
- frontend/backend slices that cannot be accepted independently.

For multi-repository work, prefer a contract change or prerequisite shared change to govern the interface.

## 3.1 Use The Lightweight Path For Small Low-Risk Work

When work is small, bounded, and low-risk:

- it can skip heavier upfront docs such as SRS, UI Content, or Architecture;
- it can enter `quick-fix`, `quick-research`, or another suitable lightweight schema directly;
- it still must close the current change artifacts, verify flow, and archive gate.

## 4. Choose Schema By Risk

Recommended schema choices:

| Scenario | Schema |
| --- | --- |
| New feature or cross-module software change | `aisee-app-spec-driven` |
| Small low-risk fix | `quick-fix` |
| Technical research or recommendation | `quick-research` |
| Documentation site change | `aisee-docsite-driven` |
| Infrastructure change | `infra-change` |
| Security-related change | `security-audit` |

`aisee-app-spec-driven` is useful when specs, source-map, contracts, and tasks need to close together. Do not force every small fix to generate UI, service, and data contracts.

## 5. Expand As-Needed Contracts Only When Required=yes

As-needed app artifacts include:

```text
change-context.md
ui-contract.md
service-contract.md
data-model.md
```

Recommended:

- Mark Required=yes/no in `source-map.md`.
- Expand the artifact when Required=yes.
- Write a concrete N/A reason when Required=no.
- Avoid keeping empty Required=no templates in the change.

This reduces duplication and keeps AI context smaller.

## 6. Source-map Routes; It Does Not Explain Everything

`source-map.md` should record:

- upstream sources or user-input summaries;
- document-local numbers produced inside the current change;
- artifact applicability;
- code paths;
- test paths;
- evidence paths;
- contract Required status.

Do not rewrite full requirements, page flows, API details, or data models in source-map. Detailed content belongs in specs, contracts, or the corresponding artifact.

## 7. Numbers Are Stable; Content Evolves

Document-local numbers reduce duplicate naming and let source-map and context packs perform lightweight parsing.

Recommended:

- Use document-local numbers such as `FR-001`, `PAGE-001`, or `API-001`.
- Put cross-document sources in `source-map.md`; keep only routing information useful for implementation and verification.
- Keep temporary `TYPE-NEW-001` IDs short-lived; they must not enter archive.
- When replacing or removing numbers, keep migration notes.
- Do not treat headings, filenames, or natural-language descriptions as stable identifiers.

Use `source-map.md` and context pack's rebuildable scan view as context entries; durable specification facts still belong in OpenSpec artifacts and baseline specs.

## 8. Context Pack Is A Read Entry, Not A New Document

`aisee context pack` is useful when you explicitly want to inject a small amount of project memory or team knowledge:

```bash
aisee context pack --change <change> --for ce-work --project-memory --json
aisee context pack --change <change> --for ce-work --knowledge --json
```

Rules:

- Consume only the fields needed by the current target.
- Do not copy context pack output into durable documents.
- When gaps are found, write back to the current change artifact or apply tracks.
- Do not bypass the current change and search the whole repository to expand scope.

## 9. Reuse Existing Workflows Before Creating Or Executing Tasks

Before creating tasks, entering implementation, proposing reviewer lenses, or recommending a next step, check existing workflows and skills first:

- When there is no explicit change, return to requirements clarification, change-plan, or the current change itself rather than relying on a dedicated flow command.
- When there is an explicit change, read the current change artifacts, schema, `tasks.md`, `source-map.md` when applicable, and evidence entrypoints directly.
- Only read `aisee context pack --change <change> --for ce-work --project-memory --json` or `--knowledge --json` when you explicitly need that optional guidance.
- `aisee:implementation-bridge` should tell `ce-work` what to read first and how to write back `tasks.md` / apply tracks and evidence after implementation.
- Do not create execution, code-review, or test agents that overlap with CE responsibilities.

Interface, UI, hardware, firmware, security, and verification differences should remain schema-aware check lenses. When Aisee reviewers are needed, use only the read-only consistency roles `aisee-change-architect`, `aisee-spec-reviewer`, and `aisee-implementation-reviewer`.

## 10. Implementation Brief Is Only A Handoff Index

A brief should include:

- read-first paths;
- allowed edit paths;
- current batch goal;
- verification commands;
- evidence writeback location;
- review gate recommendation.

A brief should not include:

- full proposal text;
- full specs;
- full contracts;
- durable task lists;
- new requirements;
- business facts not recognized by OpenSpec artifacts.

Large changes can use multiple brief parts, but they still belong to the same OpenSpec change.

## 11. Review And Test Evidence Must Be Traceable

After implementation, the team should be able to answer:

- Which tests ran?
- Which manual checks passed?
- Which review findings were resolved?
- Which risks were formally accepted?
- Where is the evidence recorded?

For public CLI behavior, HTTP endpoints, API/service contracts, schemas, parsers, path reads, security, or privacy changes, Tier 2 code review is recommended. If no review agent is available, local focused self-review is acceptable only when the limitation is recorded.

## 12. Archive Guard Is Not A Formality

Do not treat `openspec archive` as a command to run casually after development.

Before archive:

- `openspec validate <change>` passes.
- `aisee:verify` has no blockers.
- apply tracks are closed.
- Required=yes contracts are closed.
- review/test/manual evidence is sufficient.
- accepted risks have an owner, reason, impact, and follow-up path.

When `aisee:archive-guard` says archive is not recommended, fix blockers first.

## 13. Share Cross-Repository Contracts Read-Only

For frontend/backend split work, the contract provider can expose read-only context:

```bash
Read the current project's OpenSpec artifacts directly or use `aisee context pack`
```

Best practices:

- The provider owns the contract source.
- The consumer only reads explicitly shared OpenSpec artifacts, contract attachments, or context pack summaries.
- Use human-confirmed paths and excerpts to keep context bounded.
- Do not expose source code, secrets, environment variables, or full-repository search results.

## 14. Project Memory Only Provides Current-Project Guidance

Project memory is for long-lived current-repository guidance that does not belong in the OpenSpec baseline.

Recommended:

- Use `aisee memory inspect --json` to discover status and command entry points.
- Use `aisee memory search --query "<task>" --json` to retrieve a few active metadata entries.
- Use `--include-body` explicitly when a bounded body excerpt is needed.
- Write only when the user explicitly asks to remember long-term guidance, using `aisee memory add ... --json`.
- Use `aisee memory update-index --json` to rebuild `index.md` and cache.

Avoid:

- Recursively reading the whole `aisee/memory/` or `.memory/` tree as AI context.
- Writing project memory into OpenSpec artifacts or treating it as baseline truth.
- Letting hooks write memory automatically.
- Treating `aisee/cache/memory-index.json` as a source of truth.
- Copying current-project memory into team knowledge; cross-project reuse should go through `aisee:knowledge-curate`.

## 15. Team Knowledge Only Provides Guardrails

Team knowledge helps reuse engineering lessons across projects, but it must not become a second specification source.

Recommended:

- Use an independent `aisee-team-knowledge` repository for reviewed cards and packs.
- Let each business project pin repo/path/ref/packs in `aisee/knowledge.yaml`.
- Use `aisee knowledge query` to retrieve a small number of matches.
- Let the CLI read pack manifests and card frontmatter first, then read matched summaries on demand.
- Run `aisee:reflect` or `aisee:knowledge-curate` only when the user explicitly asks.
- Require explicit user authorization before writing to the team knowledge repo, creating branches, commits, or PRs.

Avoid:

- Scanning `knowledge/cards/**/*.md` directly as AI context.
- Copying entire `docs/solutions/`, memory, or reflect documents into business projects.
- Making evidence a hard required card field.
- Treating vector indexes, caches, or AI summaries as fact sources.
- Automatically writing team knowledge after archive or verify.

## 16. Do Not Make Aisee Another OpenSpec

Aisee should solve what OpenSpec does not:

- upfront clarification;
- schema-aware planning;
- document-local numbering constraints and source-map routing;
- AI context packs;
- implementation handoff;
- verify / archive guard.

It should not add:

- parallel specs;
- parallel tasks;
- parallel contract store;
- parallel archive;
- an OpenSpec-independent state machine.

When OpenSpec already owns a capability, Aisee should only bridge, validate, or optimize context around it.

## 17. Dogfood Real Projects Instead Of Expanding Abstractions

Once the main path is usable, validate it with real or sample projects:

```text
init -> srs -> ui-content -> architecture -> change-plan
-> change-author -> implementation-bridge -> implementation
-> verify -> archive-guard -> archive
```

Fix problems exposed by dogfood runs. Avoid large abstractions designed only for possible future needs.
