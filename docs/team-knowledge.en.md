# Team Knowledge Guardrails

> Experimental feature: suitable for local trials and workflow dogfooding, but not yet a stable public contract. The default onboarding path now uses `aisee knowledge init-repo` and `aisee knowledge configure`; remote sync and promote-batch are already available. PR automation and MCP support are still unsettled.

Team knowledge reuses a small number of reviewed engineering lessons across projects so AI agents can avoid repeating known mistakes during implementation, review, and verification.

It is not:

- a replacement for OpenSpec specs, active changes, or baselines;
- a cross-project copy of project memory;
- a full migration of `docs/solutions/` or reflect documents;
- a general knowledge QA system;
- a vector database source of truth.

## Current Capabilities

The current version supports:

- initializing a standalone team knowledge repository with `aisee knowledge init-repo --dest <path> --initial-pack <id> --json`;
- writing `aisee/knowledge.yaml` through `aisee knowledge configure --path <path> --enable-pack <id> --json`;
- using `skills/aisee-knowledge-curate/assets/team-knowledge/` in the marketplace-installed plugin as a contract-valid example template, or an external Git repository;
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

Business projects should pin only the packs they need. Prefer generating this file with `aisee knowledge configure` instead of editing it by hand:

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

V1 primarily uses the local `path`; `repo` and `ref` record provenance and support manual synchronization. `configure` preserves untouched fields unless you explicitly override them, and it never copies the full knowledge repository into the business project.

## Retrieval

Recommended initialization flow:

```bash
aisee knowledge init-repo --dest ../aisee-team-knowledge --initial-pack web-app --json
aisee knowledge check --team-path ../aisee-team-knowledge --json
aisee knowledge configure --path ../aisee-team-knowledge --enable-pack web-app --json
aisee knowledge doctor --json
```

If your team already maintains a static template repository, or wants to inspect the marketplace example, `skills/aisee-knowledge-curate/assets/team-knowledge/` remains a contract-valid reference. The default onboarding path no longer requires manually copying directories.

Inspect configuration first:

```bash
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
```

`aisee knowledge check --json` and `--team-path <path>` now expose `team_knowledge.write_ready` so callers can tell whether the repo already satisfies the `promote-batch` write preconditions. A `false` value usually means the marker or base directory structure is still missing.

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

Writing to the team knowledge repo, creating branches, committing, merging, or opening PRs requires explicit user authorization again. Before writing, `aisee knowledge promote-batch` validates the `.aisee-team-knowledge` marker plus the `knowledge/packs` and `knowledge/cards` directories so a business-project root is not mistaken for a team repo.

## Gaps Before Stability

Before the feature is stable, Aisee still needs:

- more real team knowledge card packs;
- stale card refresh workflow;
- optional semantic rerank or MCP wrapper without changing the Git + card/pack source of truth.

See [Aisee Team Knowledge Architecture](architecture/aisee-team-knowledge.md) for the underlying architecture.
