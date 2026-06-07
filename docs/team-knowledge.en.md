# Team Knowledge Guardrails

> Experimental feature: suitable for local trials and workflow dogfooding, but not yet a stable public contract. Remote repository install, automatic sync, promote-batch, PR automation, and MCP service support are still unsettled.

Team knowledge reuses a small number of reviewed engineering lessons across projects so AI agents can avoid repeating known mistakes during implementation, review, and verification.

It is not:

- a replacement for OpenSpec specs, active changes, or baselines;
- a cross-project copy of project memory;
- a full migration of `docs/solutions/` or reflect documents;
- a general knowledge QA system;
- a vector database source of truth.

## Current Capabilities

The current version supports:

- pinning a local team knowledge path, ref, and packs through `aisee/knowledge.yaml`;
- inspecting configuration with `aisee knowledge inspect --json`;
- retrieving a small number of guardrails with `aisee knowledge query ... --json`;
- injecting bounded matches into implementation context with `aisee context pack --knowledge`;
- creating project-local reusable knowledge candidates with `aisee:reflect`;
- batch-reviewing candidates and producing card drafts with `aisee:knowledge-curate`.

It does not currently:

- automatically clone or update a remote team knowledge repository;
- automatically write project lessons into team knowledge;
- automatically create branches, commits, merges, or PRs;
- read full card bodies by default;
- let AI scan `knowledge/cards/**/*.md` directly as context.

## Recommended Configuration

Business projects should pin only the packs they need:

```yaml
repo: git@example.com:org/aisee-team-knowledge.git
path: .aisee/team-knowledge
ref: v0.1.0
packs:
  - web-app
retrieval:
  max_cards: 3
  include_project_candidates: true
```

V1 primarily uses the local `path`; `repo` and `ref` record provenance and support manual synchronization.

## Retrieval

Inspect configuration first:

```bash
aisee knowledge inspect --json
```

Query by phase and surface:

```bash
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
```

Query from the active change:

```bash
aisee knowledge query --from-change <change> --for ce-work --json
```

Explicitly enable matches in context packs:

```bash
aisee context pack --change <change> --for ce-work --knowledge --json
```

## Curation

Knowledge curation is user-triggered by default:

```text
aisee:reflect
  -> aisee/docs/reflect/knowledge-candidates/
  -> aisee:knowledge-curate
  -> user confirmation before writing to the independent team knowledge repo
```

Writing to the team knowledge repo, creating branches, committing, merging, or opening PRs requires explicit user authorization again.

## Gaps Before Stability

Before the feature is stable, Aisee still needs:

- an independent `aisee-team-knowledge` repository scaffold;
- card / pack schema examples and test fixtures;
- `aisee knowledge install/update` or equivalent sync workflow;
- `aisee knowledge promote-batch` or equivalent human-reviewed submission helper;
- stale / deprecated card lifecycle;
- optional semantic rerank or MCP wrapper without changing the Git + card/pack source of truth.

See [Aisee Team Knowledge Architecture](architecture/aisee-team-knowledge.md) for the underlying architecture.
