# Team Knowledge Guardrails

> Experimental feature: suitable for local trials and workflow dogfooding, but not yet a stable public contract. Remote repository sync and promote-batch are available; default templates live under `skills/aisee-knowledge-curate/assets/team-knowledge/` in the marketplace-installed plugin, or in an external knowledge repository. They no longer come from PyPI CLI scaffolding. PR automation and MCP service support are still unsettled.

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
- obtaining team knowledge templates from `skills/aisee-knowledge-curate/assets/team-knowledge/` in the marketplace-installed plugin or an external Git repository;
- inspecting configuration with `aisee knowledge inspect --json`;
- checking that the configured path and actual team knowledge directory match with `aisee knowledge doctor --json`;
- validating cards and packs with `aisee knowledge check --json` or `--team-path <path>`;
- syncing a configured Git checkout with `aisee knowledge install/update --json`;
- retrieving a small number of guardrails with `aisee knowledge query ... --json`;
- building project or team lexical caches with `aisee knowledge index --json` and `--team-path`;
- injecting bounded matches into implementation context with `aisee context pack --knowledge`;
- creating project-local reusable knowledge candidates with `aisee:reflect`;
- batch-reviewing candidates and producing card drafts with `aisee:knowledge-curate`;
- writing reviewed drafts into a team knowledge worktree with `aisee knowledge promote-batch --curation <path> --team-path <path> --pack <id> --json`.

It does not currently:

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

For default templates, install the Aisee plugin through the Codex marketplace first, then copy `skills/aisee-knowledge-curate/assets/team-knowledge/` into a dedicated team knowledge repository. The CLI no longer copies scaffold templates from the wheel.

Inspect configuration first:

```bash
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
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

Refresh the local checkout:

```bash
aisee knowledge install --json
aisee knowledge update --json
```

Rebuild caches:

```bash
aisee knowledge index --json
aisee knowledge index --team-path .aisee/team-knowledge --json
```

## Curation

Knowledge curation is user-triggered by default:

```text
aisee:reflect
  -> aisee/docs/reflect/knowledge-candidates/
  -> aisee:knowledge-curate
  -> user confirmation before running aisee knowledge promote-batch
  -> human review of the diff before commit / PR
```

Writing to the team knowledge repo, creating branches, committing, merging, or opening PRs requires explicit user authorization again.

## Gaps Before Stability

Before the feature is stable, Aisee still needs:

- more real team knowledge card packs;
- stale card refresh workflow;
- optional semantic rerank or MCP wrapper without changing the Git + card/pack source of truth.

See [Aisee Team Knowledge Architecture](architecture/aisee-team-knowledge.md) for the underlying architecture.
