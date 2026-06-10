# Compatibility Policy

This document defines Aisee Plugin's public contract layers and change rules. The goal is not to freeze every implementation detail, but to make clear which surfaces affect user projects, agent runtimes, OpenSpec changes, and downstream automation.

During `0.x`, Aisee can still evolve quickly, but public contract changes must be documented, tested, and called out in release notes.

## Contract Layers

| Layer | Meaning | Examples | Change Requirement |
| --- | --- | --- | --- |
| Public Contract | Interfaces users or automation can depend on | CLI commands, JSON output semantics, schema artifact DAGs, context pack fields, plugin manifest / marketplace listing | Must be tested; breaking changes require versioning and changelog notes |
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

- [references/context-pack-contract.md](../plugins/aisee-plugin/references/context-pack-contract.md)
- [references/context-pack-targets.md](../plugins/aisee-plugin/references/context-pack-targets.md)
- [references/context-pack-gaps.md](../plugins/aisee-plugin/references/context-pack-gaps.md)

Rules:

- `facts.parsed` represents facts parsed from files;
- `facts.derived` represents CLI-derived views;
- `knowledge.matches` is optional guardrail output and must not pollute `facts.parsed` or `facts.derived`;
- `project_memory.matches` appears only with explicit `--project-memory` and must not pollute `facts.parsed` or `facts.derived`;
- context packs may grow, but default output must stay bounded;
- new targets must document consumer, read order, and missing-field behavior.

### Plugin Content

The following are public contracts:

- `plugins/aisee-plugin/.codex-plugin/plugin.json`, `plugins/aisee-plugin/skills/`, `plugins/aisee-plugin/references/`, and schema pack directories in the GitHub repository remain loadable by the Codex marketplace plugin;
- the core / optional / knowledge / hardware layering defined in `plugins/aisee-plugin/references/skill-taxonomy.md`, including the core set of 10 workflow skills;
- `aisee plugin inspect --json` returns stable status and setup hints in CLI-only installs;
- the PyPI wheel only promises CLI capabilities; skills, references, schema packs, team knowledge templates, and plugin metadata are distributed through the marketplace plugin or external repositories.

Breaking changes include renaming the plugin, removing the Codex manifest, breaking the marketplace plugin root layout, or changing the core workflow skill set.

### Plugin Marketplace

The following are public contracts:

- plugin name `aisee-plugin`;
- `plugins/aisee-plugin/.codex-plugin/plugin.json` remains present and accepted by the Codex plugin validator;
- Codex manifest `skills` points to a loadable skills directory;
- marketplace listing examples use `policy.installation`, `policy.authentication`, and `category`;
- PyPI / pipx installation and plugin marketplace installation remain separate channels, and the CLI must not require marketplace availability to run.

Breaking changes include renaming the plugin, removing the Codex manifest, changing marketplace listing policy semantics, or making marketplace listings sources of truth for OpenSpec, schema, or source-map.

See [Plugin Marketplace](plugin-marketplace.en.md) for details.

### Planning Docs And Root Resolution

The following are public contracts:

- the planning-doc frontmatter contract and the read-only diagnostics exposed through `aisee doctor --json` and `aisee context pack --json`;
- the basic semantics of planning-doc fields such as `status`, `doc_type`, `source_refs`, and `change_refs`;
- `resolve_project_root` preferring the nearest Aisee/OpenSpec project marker before falling back to the Git top-level;
- release smoke checks for CLI-only wheels, marketplace setup hints, the public command surface, and root-resolver fixtures.

Breaking changes include turning planning-doc diagnostics into write commands or changing root resolution so monorepo subprojects are silently interpreted as repository roots.

### Project Memory

The following are public contracts:

- `aisee memory inspect/list/search/add/update-index --json` commands exist and emit valid JSON;
- the canonical project memory path is `aisee/memory/`, while legacy `.memory/` is read-only fallback;
- `inspect/search/list` are read-only by default, while `add/update-index` must mark writes through `meta.writes`;
- default retrieval returns bounded metadata only, not full bodies;
- `aisee/cache/memory-index.json` is a deletable rebuildable cache, not a source of truth;
- `aisee context pack --project-memory` emits matches only in a separate `project_memory` field.

Breaking changes include removing commands, injecting full memory bodies by default, mixing memory into OpenSpec facts, or allowing hooks to write memory automatically.

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

- `aisee/cache/knowledge-index.json`;
- `aisee/cache/memory-index.json`;
- parser internals;
- scoring weights;
- build caches;
- internal test fixture layout;
- chat summaries.

Caches must be deletable and rebuildable. Sources of truth can only come from OpenSpec artifacts, source-map, tasks, and explicitly pinned team knowledge card/pack files. Project memory is project guidance, not an OpenSpec source of truth.

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
- whether the skill taxonomy reference needs updates;
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
