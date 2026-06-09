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

Any conclusion that must persist should be written back to the current OpenSpec change, baseline specs, schema apply tracks, source-map, or other formal sources such as `sources.json`.

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

## 6. Source-map Tracks; It Does Not Explain Everything

`source-map.md` should record:

- upstream anchor refs;
- local IDs produced inside the current change;
- artifact applicability;
- code paths;
- test paths;
- evidence paths;
- contract Required status.

Do not rewrite full requirements, page flows, API details, or data models in source-map. Detailed content belongs in specs, contracts, or the corresponding artifact.

## 7. Local IDs And Anchor Refs Are Stable; Content Evolves

Local IDs and anchor refs connect requirements, pages, APIs, data, tasks, code, and evidence.

Recommended:

- Use local IDs inside documents, such as `FR-001`, `PAGE-001`, or `API-001`.
- Use anchor refs across documents, such as `docs/requirements/auth-srs.md#FR-001`.
- Keep temporary `TYPE-NEW-001` IDs short-lived; they must not enter archive.
- When replacing or removing anchor/local IDs, keep migration notes.
- Do not treat headings, filenames, or natural-language descriptions as stable identifiers.

Use `sources.json`, `source-map.md`, and rebuildable index output for traceability; do not return to the full ID lifecycle model.

## 8. Context Pack Is A Read Entry, Not A New Document

`aisee context pack` gives AI a small and targeted context:

```bash
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for aisee-verify --json
aisee context pack --change <change> --for ce-code-review --json
```

Rules:

- Consume only the fields needed by the current target.
- Do not copy context pack output into durable documents.
- When gaps are found, write back to the current change artifact or apply tracks.
- Do not bypass the current change and search the whole repository to expand scope.

## 9. Reuse Existing Workflows Before Creating Or Executing Tasks

Before creating tasks, entering implementation, proposing reviewer roles, or recommending a next step, check existing workflows and skills first:

- When there is no explicit change, use `aisee:flow` or `aisee flow inspect --json` to identify the current stage.
- When there is an explicit change, read the target context pack first, such as `aisee context pack --change <change> --for ce-work --json`.
- `reusable_workflow_candidates` in the `ce-work` context pack is a routing hint only, not a source of truth.
- Use `ce-plan` only when `requires_ce_plan=true`; its conclusions must be written back to the current schema apply tracks, and only source-map schemas write back to `source-map.md`.
- When `requires_ce_plan=false` and paths/tasks are clear, prefer `aisee:implementation-bridge -> ce-work`.
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
aisee contract serve --host 127.0.0.1 --port 8765
```

Best practices:

- The provider owns the contract source.
- The consumer reads manifest first, then summary or sections as needed.
- Use `max_chars` to control context size.
- LAN access requires explicit `--host 0.0.0.0`.
- Do not use the contract service to expose source code, secrets, environment variables, or full-repository search results.

## 14. Team Knowledge Only Provides Guardrails

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

## 15. Do Not Make Aisee Another OpenSpec

Aisee should solve what OpenSpec does not:

- upfront clarification;
- schema-aware planning;
- ID and source-map traceability;
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

## 16. Dogfood Real Projects Instead Of Expanding Abstractions

Once the main path is usable, validate it with real or sample projects:

```text
init -> srs -> ui-content -> architecture -> change-plan
-> change-author -> implementation-bridge -> implementation
-> verify -> archive-guard -> archive
```

Fix problems exposed by dogfood runs. Avoid large abstractions designed only for possible future needs.
