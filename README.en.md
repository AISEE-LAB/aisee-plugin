# Aisee Plugin

English | [简体中文](README.md)

**Aisee** stands for **AI-Enhanced Software Engineering**.

Aisee Plugin is an AI software engineering plugin for OpenSpec workflows. It helps teams turn ambiguous ideas into reviewable requirements, UI content specifications, architecture context, schema-aware OpenSpec changes, implementation briefs, verification checks, and archive guardrails.

Aisee **does not replace OpenSpec**. OpenSpec remains the specification state machine and baseline source of truth. Aisee adds structured skills, schema packs, JSON context tooling, stable ID tracking, and engineering handoff rules around OpenSpec.

> Status: early alpha. This repository is ready for local experiments and plugin development, but public distribution, installation automation, and versioned releases are still being refined.

## Why Aisee?

AI coding assistants are useful, but projects drift when requirements, UI decisions, technical constraints, and implementation evidence live only in chat history.

Aisee makes that context explicit:

- clarify business requirements before implementation;
- separate requirements, UI content, architecture context, and change planning;
- create and complete OpenSpec changes with schema-aware guidance;
- keep OpenSpec as the only persistent specification source of truth;
- generate machine-readable context packs for implementation, verification, and review;
- track requirement, page, contract, task, code, and evidence IDs;
- check whether artifacts, tasks, source maps, tests, and review evidence are closed before archive.

## Workflow Positioning

```text
User intent
  ↓
Aisee skills
  Clarify requirements, UI content, architecture, and change boundaries
  ↓
OpenSpec
  Manage active changes, baseline specs, validate, apply, and archive
  ↓
Aisee CLI
  Read OpenSpec/Aisee metadata and emit JSON context packs
  ↓
Compound Engineering or another coding agent
  Implement, review, test, and produce evidence
  ↓
Aisee verify / archive guard
  Check whether the current change is ready to archive
```

Core boundaries:

```text
OpenSpec = specification state machine and baseline source of truth
Aisee = planning, context, schemas, traceability, and workflow guardrails
Aisee CLI = JSON context bus, not a second source of truth
Compound Engineering = optional implementation / review / test consumer
```

## Features

- **Structured requirement clarification**: `aisee:srs` clarifies business needs through dialogue and produces planning-level SRS documents.
- **UI content specification**: `aisee:ui-content` turns confirmed requirements into pages, content, states, flows, permission visibility, and platform differences without writing visual design rules.
- **Architecture context**: `aisee:architecture` records technical facts, constraints, reusable capabilities, global engineering conventions, and artifact hints.
- **Schema-aware change planning**: `aisee:change-plan` maps confirmed inputs into independently deliverable OpenSpec changes.
- **OpenSpec schema pack**: includes app, device, docsite, infra, security, quick-fix, quick-research, and collaboration schemas.
- **Context packs**: `aisee context pack` generates JSON context for implementation, verification, and review.
- **ID registry and traceability**: `aisee id`, `aisee get`, and `aisee trace` connect upstream documents, OpenSpec artifacts, tasks, code paths, tests, and evidence.
- **Verification and archive guardrails**: `aisee:verify` and `aisee:archive-guard` diagnose gaps and risks before archive.
- **Harness design**: CLI contract tests and normalized skill eval cases keep the workflow stable.

## Requirements

- Python 3.10+
- Git
- Node.js and OpenSpec CLI

Install OpenSpec separately:

```bash
npm install -g @fission-ai/openspec@latest
```

Compound Engineering is optional. Aisee can use `aisee doctor --json` to check whether key Compound skills are available.

## Install

Install the CLI with `pipx`:

```bash
pipx install aisee-plugin
```

You can also use `pip`:

```bash
python -m pip install aisee-plugin
```

Before public release, install from source:

```bash
git clone <repository-url>
cd aisee-plugin
python -m pip install -e .
```

Check the CLI:

```bash
aisee --version
aisee doctor --json
```

You can also run the repository-local entrypoint without installing:

```bash
./bin/aisee doctor --json
```

## Plugin Usage

The Python package includes Aisee skills, schema packs, references, and agent plugin metadata. Inspect packaged plugin resources:

```bash
aisee plugin inspect --json
```

Export a plugin directory that can be loaded by an agent runtime:

```bash
aisee plugin export --target codex --dest ./aisee-plugin-bundle --json
```

Supported targets:

```text
codex
claude
cursor
```

The exported directory contains:

```text
aisee-plugin-bundle/
  .codex-plugin/plugin.json
  skills/
```

If your agent runtime supports loading local plugins, point it to the exported directory or the corresponding plugin metadata file.

The source repository also includes plugin metadata for multiple agent runtimes:

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
```

Codex plugin metadata declares the skills directory directly:

```json
{
  "skills": "./skills/"
}
```

## Quick Start

Inside a project that should use OpenSpec:

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee plugin inspect --json
```

If the project has not initialized OpenSpec yet:

```bash
aisee openspec ensure --json
```

This command bridges OpenSpec initialization with conservative defaults:

```text
openspec init . --tools none --profile core
openspec config profile core
```

Then install the schema packs provided by this plugin:

```bash
aisee schemas install --all --json
```

Check the project state again:

```bash
aisee doctor --json
aisee flow inspect --json
```

## Typical Workflow

```text
1. aisee:srs
2. aisee:ui-content
3. aisee:architecture
4. aisee:change-plan
5. /opsx:new "<change>" --schema <schema>
6. aisee:change-author
7. openspec validate <change>
8. aisee:implementation-bridge
9. implementation / review / test
10. aisee:verify
11. aisee:archive-guard
12. openspec archive <change>
```

For existing projects, use `aisee:spec-migrate` to derive OpenSpec baseline specs from code, tests, docs, routes, and verified behavior.

## Main Skills

| Skill | Purpose |
| --- | --- |
| `aisee:flow` | Inspect the current workflow stage and recommend the next step. |
| `aisee:init` | Initialize or audit `AGENTS.md`, `openspec/project.md`, Aisee docs, memory, and Codex hooks. |
| `aisee:srs` | Clarify software requirements and produce planning-level SRS documents. |
| `aisee:ui-content` | Produce UI content specs for pages, elements, states, flows, permissions, and platform differences. |
| `aisee:architecture` | Capture software architecture context, technical constraints, reusable capabilities, and artifact hints. |
| `aisee:change-plan` | Plan independent OpenSpec changes and choose schemas. |
| `aisee-schema-pack` | Install and maintain OpenSpec schema packs. |
| `aisee:implementation-bridge` | Produce implementation briefs and context pack summaries for a single change. |
| `aisee:verify` | Diagnose artifact, task, source-map, ID, and evidence gaps. |
| `aisee:archive-guard` | Provide the final recommendation before `openspec archive`. |
| `aisee:spec-migrate` | Build OpenSpec baseline specs for existing projects. |
| `aisee:design-spec` | Produce design specifications without duplicating UI content specs. |
| `aisee:design-assets` | Generate or extract visual references and design assets. |
| `aisee:svg-assets` | Generate, vectorize, optimize, and validate SVG assets. |
| `aisee:image-object` | Handle object-level image segmentation, masks, background removal, and exports. |
| `aisee:reflect` | Capture reusable project lessons and workflow improvements. |

Hardware-related skills are retained but still being integrated into the main Aisee workflow:

```text
hw-init
hw-srs
hw-architecture
hw-change-plan
```

## Schema Packs

Schema pack source:

```text
skills/aisee-schema-pack/assets/schema-pack/
```

Current schemas:

| Schema | Use Case |
| --- | --- |
| `aisee-app-spec-driven` | App and software changes with source-map, contracts, specs, and tasks. |
| `aisee-device-spec-driven` | Device, firmware, runtime, production, and verification changes. |
| `aisee-docsite-driven` | Documentation site changes. |
| `infra-change` | Infrastructure changes. |
| `security-audit` | Security audit workflow. |
| `quick-fix` | Small, clear fixes. |
| `quick-research` | Technical research and recommendations. |
| `opsx-collab-pr-loop` | Collaboration and PR loop workflow. |

Install one schema:

```bash
aisee schemas install --schema aisee-app-spec-driven --json
```

Install all schemas:

```bash
aisee schemas install --all --json
```

Check schema packs:

```bash
aisee schemas check --json --fail-on-blocker
```

## CLI Reference

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
aisee plugin inspect --json
aisee plugin path --target codex --json
aisee plugin export --target codex --dest ./aisee-plugin-bundle --json
aisee schemas list --json
aisee schemas check --json
aisee schemas install --all --json
aisee sources list --json
aisee sources check --json
aisee index --json
aisee flow inspect --json
aisee flow inspect --change <change> --json
aisee change inspect <change> --json
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for aisee-verify --json
aisee change verify-check <change> --json
aisee change archive-check <change> --json
aisee id check --json
aisee id reserve --scope <scope> --type <type> --count 3 --json
aisee get <id> --json
aisee trace <id> --json
```

Key CLI rules:

- JSON output is a context view, not a source of truth.
- `aisee/cache/context-index.json` is a deletable and rebuildable cache.
- `aisee/registry/id-registry.json`, `aisee/registry/sources.json`, OpenSpec artifacts, and `source-map.md` are persistent traceability inputs.
- `bootstrap --plan` is a read-only plan and does not perform broad initialization writes.
- `aisee openspec ensure` only bridges OpenSpec initialization and profile setup. It does not replace `aisee:init`.

## Repository Layout

```text
.codex-plugin/       Codex plugin metadata
.claude-plugin/      Claude plugin metadata
.cursor-plugin/      Cursor plugin metadata
bin/                 Local CLI entrypoint
src/aisee_cli/       Aisee Python CLI
src/aisee_plugin_assets/
                     Skills, schemas, references, and plugin metadata packaged into wheels
skills/              Aisee skills and skill assets
references/          Cross-skill contracts and references
docs/architecture/   Architecture and workflow design docs
docs/plans/          Development plans
docs/reviews/        Audit and review records
scripts/             Development and release helper scripts
tests/               CLI and harness tests
```

## Development

Run tests:

```bash
python -m pytest
```

Validate skill eval JSON:

```bash
python -m pytest tests/test_skill_eval_schema.py
```

Show CLI help:

```bash
python -m aisee_cli.__main__ --help
```

Sync packaged plugin assets:

```bash
python scripts/sync_package_assets.py
```

Build a wheel:

```bash
python -m build
```

## Design Principles

- OpenSpec is the canonical specification source.
- Do not create parallel sources of truth in Aisee docs, CLI cache, or chat summaries.
- Keep skills single-purpose: requirements, UI content, architecture, change planning, implementation bridge, verify, and archive guard.
- Prefer schema-aware checks over hardcoded artifact assumptions.
- Keep `SKILL.md` concise and put long rules in references or architecture docs.
- Treat hardware and embedded workflows as dedicated extensions instead of forcing them into the app schema.

## Related Projects

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — a spec-driven development framework for AI coding assistants.
- [OpenSpec documentation](https://openspec.dev/) — OpenSpec installation and workflow documentation.

## Roadmap

- Stabilize public plugin installation instructions.
- Continue normalizing skill eval cases to `aisee.skill-eval.v1`.
- Add full lifecycle workflow scenario fixtures.
- Add schema pack documentation and examples.
- Integrate hardware and embedded workflows into the Aisee system.
- Add release, contributing, and license files before public 1.0.

## License

MIT. The current license declaration lives in plugin metadata.
