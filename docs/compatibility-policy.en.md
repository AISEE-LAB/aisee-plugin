# Compatibility Policy

This document defines Aisee Plugin's public contract layers and change rules. The goal is not to freeze every implementation detail, but to make clear which surfaces affect user projects, agent runtimes, OpenSpec changes, and downstream automation.

During `0.x`, Aisee can still evolve quickly, but public contract changes must be documented, tested, and called out in release notes.

## Contract Layers

| Layer | Meaning | Examples | Change Requirement |
| --- | --- | --- | --- |
| Public Contract | Interfaces users or automation can depend on | CLI commands, JSON output semantics, schema artifact DAGs, context pack fields, plugin export layout | Must be tested; breaking changes require versioning and changelog notes |
| Experimental Contract | Usable but not yet stable capabilities | team knowledge remote install, promote-batch, optional MCP, hardware workflow integration | Must be marked experimental; can change, but must not appear stable |
| Internal Detail | Implementation details that can change freely | parser helpers, cache contents, temporary indexes, scoring weights, fixture layout | No compatibility promise; must not become a user source of truth |

## Public Contracts

### CLI JSON

The following are public contracts:

- whether a command exists;
- whether `--json` emits valid JSON;
- cross-command semantics of `status`, `issues`, `summary`, `meta.command`, and `meta.writes`;
- documented field meanings;
- read-only commands must not write project files;
- write commands must be identifiable through `meta.writes` or command documentation.

Backward-compatible changes:

- adding fields;
- adding enum values that old consumers can ignore;
- adding warning / risk issues;
- adding commands.

Breaking changes:

- deleting or renaming documented fields;
- changing field meaning;
- turning a read-only command into a write command;
- changing exit codes or JSON error structure so existing automation cannot detect failure;
- reading oversized context by default or exposing source code, secrets, or environment variables.

### Schema Packs

The following are public contracts:

- `schema.yaml` names and versions;
- artifact `id`, `generates`, `template`, and `requires`;
- apply/archive tracks;
- template filenames and artifact applicability rules;
- the as-needed contract strategy of `aisee-app-spec-driven`;
- the positioning of `aisee-device-spec-driven` as a hardware/embedded extension.

Backward-compatible changes:

- adding optional artifacts;
- relaxing template requirements;
- adding explanatory fields;
- adding N/A rules;
- adding schemas.

Breaking changes:

- deleting artifacts;
- renaming artifacts or template files;
- changing the artifact DAG so existing changes no longer validate;
- making as-needed artifacts mandatory by default;
- creating a parallel source of truth beside OpenSpec baseline specs.

### Context Pack

Field-level contracts are defined in:

- [references/context-pack-contract.md](../references/context-pack-contract.md)
- [references/context-pack-targets.md](../references/context-pack-targets.md)
- [references/context-pack-gaps.md](../references/context-pack-gaps.md)

Rules:

- `facts.parsed` represents facts parsed from files;
- `facts.derived` represents CLI-derived views;
- `knowledge.matches` is optional guardrail output and must not pollute `facts.parsed` or `facts.derived`;
- context packs may grow, but default output must stay bounded;
- new targets must document consumer, read order, and missing-field behavior.

### Plugin Export

The following are public contracts:

- `aisee plugin inspect --json` can locate the packaged asset root;
- `aisee plugin export --target codex|claude|cursor` emits runtime metadata;
- exported directories include runtime metadata, `skills/`, and `references/`;
- package assets stay synced with source `skills/`, `references/`, and plugin metadata.

Breaking changes include export layout changes, target name changes, metadata path changes, or missing skills.

### Plugin Marketplace

The following are public contracts:

- plugin name `aisee-plugin`;
- `.codex-plugin/plugin.json` remains present and accepted by the Codex plugin validator;
- Codex manifest `skills` points to a loadable skills directory;
- marketplace listing examples use `policy.installation`, `policy.authentication`, and `category`;
- PyPI / pipx installation and plugin marketplace installation remain separate channels, and the CLI must not require marketplace availability to run.

Breaking changes include renaming the plugin, removing the Codex manifest, changing marketplace listing policy semantics, or making marketplace listings sources of truth for OpenSpec, schema, or source-map.

See [Plugin Marketplace](plugin-marketplace.en.md) for details.

## Experimental Contracts

The following remain experimental:

- team knowledge remote install, automatic sync, promote-batch, PR automation, and MCP wrapping;
- hardware and embedded workflow integration;
- runnable full lifecycle dogfood fixtures;
- final schema sample change directory and format;
- semantic rerank / vector index.

Experimental capabilities can change, but documentation must clearly state:

- what currently works;
- what is explicitly unsupported;
- whether the capability writes project or remote repository files;
- whether explicit user authorization is required again.

## Internal Details

The following are not stable contracts or sources of truth:

- `aisee/cache/context-index.json`;
- `aisee/cache/knowledge-index.json`;
- parser internals;
- scoring weights;
- build caches;
- internal test fixture layout;
- chat summaries.

Caches must be deletable and rebuildable. Sources of truth can only come from OpenSpec artifacts, Aisee registry, source-map, tasks, and explicitly pinned team knowledge card/pack files.

## Version Rules

During `0.x`:

- breaking a Public Contract: at least `MINOR`, with migration impact in the changelog;
- adding a Public Contract: `MINOR`;
- backward-compatible fixes or docs: `PATCH`;
- Experimental Contract changes: usually `PATCH` or `MINOR`, but documentation must stay accurate.

After a stable public release:

- breaking a Public Contract: `MAJOR`;
- backward-compatible capabilities: `MINOR`;
- fixes, docs, and tests: `PATCH`.

## Change Checks

Changes touching Public Contracts must consider:

- whether README / workflow / best practices / release docs need updates;
- whether schema pack docs need updates;
- whether context pack references need updates;
- whether CLI contract tests need updates;
- whether `python scripts/check_versions.py` was run;
- whether related tests and `python scripts/smoke_release.py` were run.

Recommended minimum checks:

```bash
python scripts/check_versions.py
python -m pytest tests/test_plugin_packaging.py tests/test_doctor_flow_schema.py tests/test_version_consistency.py -q
python -m pytest -q
git diff --check
```

Before release, also run:

```bash
python scripts/smoke_release.py
```
