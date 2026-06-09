# Aisee Plugin

English | [简体中文](https://github.com/AISEE-LAB/aisee-plugin/blob/main/README.md)

**Aisee** stands for **AI-Enhanced Software Engineering**.

Aisee Plugin is an AI software engineering plugin for OpenSpec workflows. It helps teams turn ambiguous ideas into reviewable requirements, UI content specifications, architecture context, schema-aware OpenSpec changes, implementation briefs, verification checks, and archive guardrails.

Aisee **does not replace OpenSpec**. OpenSpec remains the specification state machine and baseline source of truth. Aisee adds structured skills, schema packs, JSON context tooling, anchor-aware traceability, and engineering handoff rules around OpenSpec.

## Why Aisee?

AI coding assistants are useful, but projects drift when requirements, UI decisions, technical constraints, and implementation evidence live only in chat history.

Aisee makes that context explicit:

- clarify business requirements before implementation;
- separate requirements, UI content, architecture context, and change planning;
- create and complete OpenSpec changes with schema-aware guidance;
- keep OpenSpec as the only persistent specification source of truth;
- generate machine-readable context packs for implementation, verification, and review;
- track requirements, pages, contracts, tasks, code, and evidence through local IDs and anchor refs;
- check whether artifacts, tasks, source maps, tests, and review evidence are closed before archive.

## Agile Delivery Model

Aisee now follows a version / iteration-oriented agile model:

- SRS, UI Content, Design Spec, and Architecture are **planning docs** for the current version or iteration;
- `aisee:change-plan` splits one iteration into **one or more** independently deliverable OpenSpec changes;
- the current change's proposal, source-map, specs, contracts, and tasks are the formal implementation-time commitments;
- after `openspec archive`, baseline specs take over as the current source of truth;
- small, bounded, low-risk work can skip heavy upfront docs and enter an appropriate lightweight schema directly.

## Workflow Positioning

```text
User intent
  ↓
Aisee skills
  Produce planning docs and clarify requirements, UI content, architecture, and change boundaries
  ↓
aisee:change-plan
  One iteration -> one or more OpenSpec changes
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
- **Contract context service**: `aisee contract` exposes service contracts through manifest-first and section-level reads for cross-repository frontend/backend collaboration.
- **Team knowledge guardrails**: `aisee knowledge` retrieves a small number of reviewed engineering lessons through pack/card protocols without turning the knowledge repository into a second specification source.
- **Anchor-aware traceability**: `aisee get`, `aisee trace`, and `aisee index` connect upstream documents, OpenSpec artifacts, tasks, code paths, tests, and evidence through `doc-ref#LOCAL-ID` or alias anchors.
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

For development or local changes, install from source:

```bash
git clone https://github.com/AISEE-LAB/aisee-plugin
cd aisee-plugin
python -m pip install -e .
```

You can also build and install a local wheel:

```bash
python -m pip install build
python -m build
python -m pip install dist/aisee_plugin-*.whl
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

PyPI / pipx installs only the `aisee` CLI. Aisee skills, references, schema packs, team knowledge templates, and plugin metadata are distributed through the GitHub-backed Codex marketplace.

Add the marketplace and install the plugin in Codex:

```bash
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

Check CLI-only state and marketplace setup hints:

```bash
aisee plugin inspect --json
aisee doctor --json
```

When reading plugin content, the CLI checks only the Codex install location by default. For other agent runtimes, set `AISEE_AGENT_RUNTIME=claude|cursor|agents`; set it to `none` to disable installed plugin content discovery.

`aisee plugin export`, `aisee schemas install`, and `aisee knowledge scaffold` no longer distribute plugin content from the PyPI wheel. These public legacy commands return stable JSON blockers with the Codex marketplace setup path.

The source repository also includes plugin metadata for multiple agent runtimes:

```text
plugins/aisee-plugin/.codex-plugin/plugin.json
plugins/aisee-plugin/.claude-plugin/plugin.json
plugins/aisee-plugin/.cursor-plugin/plugin.json
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

Schema packs come from the marketplace-installed plugin. `aisee schemas list/check` only reports project-installed schema state or source-checkout development schema state; it does not install schemas from the PyPI wheel.

Check the project state again:

```bash
aisee doctor --json
aisee flow inspect --json
```

## Documentation

- [Documentation site](https://aisee.wiki): Aisee guides, workflows, and release notes.
- [Aisee Workflow](docs/workflow.en.md): end-to-end guidance from setup, requirement clarification, change authoring, implementation handoff, verification, and archive.
- [Aisee Best Practices](docs/best-practices.en.md): conventions for sources of truth, schemas, contracts, context packs, reuse-first routing, review, and archive when using Aisee with OpenSpec.
- [Compatibility Policy](docs/compatibility-policy.en.md): compatibility boundaries for CLI JSON, schema packs, context packs, plugin content, and experimental capabilities.
- [Plugin Marketplace](docs/plugin-marketplace.en.md): responsibilities of plugin manifests, marketplace listings, PyPI/pipx, and the Codex install path.
- [Team Knowledge Guardrails](docs/team-knowledge.en.md): experimental status, usage, and gaps before stability for shared team knowledge.
- [Aisee Team Knowledge Architecture](docs/architecture/aisee-team-knowledge.md): team knowledge guardrail retrieval, card/pack boundaries, and read model.
- [Schema Packs](docs/schema-packs.md): schema selection, app schema artifact DAG, anchor/source-map rules, and contract attachment boundaries.
- [Aisee / OpenSpec / Compound Engineering Integration](docs/architecture/aisee-openspec-compound-integration.md): high-level responsibility boundaries and historical decisions.
- [OpenSpec Multi-Schema Best Practices](docs/architecture/openspec-multi-schema-best-practices.md): multi-schema coexistence, conflict handling, and management rules.
- [Release And Version Governance](docs/release.md): single version source, release checks, and tag rules.

## Typical Workflow

```text
1. aisee:srs / aisee:ui-content / aisee:architecture, as needed
2. aisee:change-plan
3. /opsx:new "<change>" --schema <schema>
4. aisee:change-author
5. openspec validate <change>
6. aisee:implementation-bridge
7. implementation / review / test
8. aisee:verify
9. aisee:archive-guard
10. openspec archive <change>

For small, bounded, low-risk work, an abbreviated path is also valid:

```text
quick-fix / quick-research / another lightweight schema
  -> change-author
  -> implementation-bridge
  -> verify
  -> archive-guard
```
```

Before and after implementation, use read-only Aisee reviewer roles as needed: `aisee-change-architect`, `aisee-spec-reviewer`, and `aisee-implementation-reviewer`. See [Aisee Workflow](docs/workflow.en.md) for timing and boundaries, and [Aisee Best Practices](docs/best-practices.en.md) for reuse-first routing.

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
| `aisee-schema-pack` | Provide and maintain OpenSpec schema packs through the marketplace plugin. |
| `aisee:implementation-bridge` | Produce implementation briefs and context pack summaries for a single change. |
| `aisee:verify` | Diagnose artifact, task, source-map, ID, and evidence gaps. |
| `aisee:archive-guard` | Provide the final recommendation before `openspec archive`. |
| `aisee:spec-migrate` | Build OpenSpec baseline specs for existing projects. |
| `aisee:design-spec` | Produce design specifications without duplicating UI content specs. |
| `aisee:design-assets` | Generate or extract visual references and design assets. |
| `aisee:svg-assets` | Generate, vectorize, optimize, and validate SVG assets. |
| `aisee:image-object` | Handle object-level image segmentation, masks, background removal, and exports. |
| `aisee:reflect` | Capture reusable project lessons and workflow improvements. |
| `aisee:knowledge-curate` | Batch-review project-local reusable knowledge candidates and produce card drafts for human submission to team knowledge. |

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
plugins/aisee-plugin/skills/aisee-schema-pack/assets/schema-pack/
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

Check project schema state:

```bash
aisee schemas list --json
aisee schemas check --json --fail-on-blocker
```

## CLI Reference

```bash
aisee doctor --json
aisee bootstrap --plan --json
aisee openspec ensure --json
aisee plugin inspect --json
aisee schemas list --json
aisee schemas check --json
aisee sources list --json
aisee sources check --json
aisee index --json
aisee flow inspect --json
aisee flow inspect --change <change> --json
aisee change inspect <change> --json
aisee change author-check <change> --json
aisee gaps --change <change> --json
aisee context pack --change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
aisee context pack --change <change> --for aisee-verify --json
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
aisee knowledge check --team-path .aisee/team-knowledge --json
aisee knowledge install --json
aisee knowledge update --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee knowledge index --json
aisee knowledge index --team-path .aisee/team-knowledge --json
aisee knowledge promote-batch --curation <path> --team-path .aisee/team-knowledge --pack web-app --json
aisee contract manifest --json
aisee contract summary --change <change> --json
aisee contract get --change <change> --artifact service-contract --section capabilities --json
aisee contract serve --host 127.0.0.1 --port 8765
aisee change verify-check <change> --json
aisee change archive-check <change> --json
aisee index --json
aisee get docs/requirements/auth-srs.md#FR-001 --json
aisee trace srs:auth-login#FR-001 --json
```

Key CLI rules:

- JSON output is a context view, not a source of truth.
- `aisee/cache/context-index.json` is a deletable and rebuildable cache.
- `aisee/cache/knowledge-index.json` is also a deletable and rebuildable cache; team knowledge persists in pinned pack/card files.
- `aisee knowledge promote-batch` only writes the local team knowledge worktree; it does not commit, push, or create PRs.
- `aisee/registry/sources.json`, OpenSpec artifacts, and `source-map.md` are the current formal traceability inputs.
- If `aisee/registry/id-registry.json` still exists, treat it as legacy compatibility data rather than a formal authoring entry point.
- `bootstrap --plan` is a read-only plan and does not perform broad initialization writes.
- `aisee openspec ensure` only bridges OpenSpec initialization and profile setup. It does not replace `aisee:init`.
- `aisee contract serve` is a read-only contract context service, not a mock backend, API gateway, or second API source of truth. It binds to `127.0.0.1` by default; LAN access requires explicit `--host 0.0.0.0` and exposes local contract documents to that network.
- `aisee knowledge query` returns only a small number of guardrails. By default it reads pack manifests and card frontmatter; `--debug` is required for matched card body excerpts.

### Cross-Repository Contract Reads

When frontend and backend are developed in separate repositories, the backend repository, BFF repository, or independent contract repository should own `service-contract.md` and optional machine-readable attachments such as `contracts/openapi.yaml`, `contracts/events.yaml`, `contracts/webhooks.yaml`, or `contracts/proto/*.proto`.

Recommended flow:

```bash
# In the contract provider repository
aisee contract manifest --json
aisee contract summary --change <change> --json
aisee contract serve --host 127.0.0.1 --port 8765

# In the consumer repository AI context, read the manifest first and fetch small sections as needed
curl http://127.0.0.1:8765/manifest
curl http://127.0.0.1:8765/changes/<change>/summary
curl "http://127.0.0.1:8765/changes/<change>/contracts/service-contract/sections/<section>?max_chars=4000"
```

OpenSpec/Aisee artifacts remain the authoritative contract source. The HTTP service reads current files on request and returns a JSON view; it does not persist contract copies and does not expose source code, environment variables, secrets, or full-repository search results.

### Team Knowledge Guardrails

Team knowledge is experimental. It reuses engineering lessons across projects, but it does not replace OpenSpec, `source-map.md`, contracts, tasks, or baseline specs.

Business projects can pin an independent knowledge repository, local path, ref, and packs in `aisee/knowledge.yaml`:

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

Common commands:

```bash
aisee knowledge inspect --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
```

Rules:

- `install`, `update`, and `promote-batch` are experimental. The PyPI CLI no longer provides local default scaffolding. PR automation and MCP service support are still unsettled.
- Query through the CLI instead of letting AI scan `knowledge/cards/**/*.md` directly.
- Return a small number of bounded matches as implementation, review, or verification reminders.
- Project-local `aisee/docs/reflect/knowledge-candidates/` remains a candidate area and is not promoted automatically.
- `aisee:knowledge-curate` only produces review reports and card drafts. Writing to the team repo, creating branches, committing, merging, or opening PRs requires explicit user authorization again.

## Repository Layout

```text
.agents/plugins/marketplace.json
                     Codex marketplace listing
plugins/aisee-plugin/
  .codex-plugin/     Codex plugin metadata
  .claude-plugin/    Claude plugin metadata
  .cursor-plugin/    Cursor plugin metadata
  skills/            Aisee skills and skill assets
  references/        Cross-skill contracts and references
bin/                 Local CLI entrypoint
src/aisee_cli/       Aisee Python CLI
src/aisee_plugin_assets/
                     Minimal compatibility package; no bundled skills, schemas, references, or plugin metadata
docs/                User workflow, best practices, architecture, plans, and review docs
docs/architecture/   Architecture and historical decision docs
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

Check and sync versions:

```bash
python scripts/check_versions.py
python scripts/sync_versions.py
```

Build a wheel:

```bash
python -m build
```

Run the release smoke test:

```bash
python scripts/smoke_release.py
```

For release candidates, also run the isolated `pipx` install smoke test when `pipx` is available:

```bash
python scripts/smoke_release.py --with-pipx
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
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) — an agent workflow plugin for AI engineering execution, review, testing, commits, and team learning.

## Roadmap

### Ongoing Compatibility Governance

- Maintain compatibility boundaries for CLI JSON, schema packs, context packs, marketplace plugin content, and skill contracts.
- Maintain deprecation and migration rules for breaking changes.
- Decide which hardware and embedded workflows remain experimental and which enter the main Aisee workflow.
- Add more real-world lifecycle fixtures beyond the app scenario.

### Later

- Expand cross-repository contract collaboration examples.
- Stabilize team knowledge remote sync, promote workflows, lifecycle management, and optional MCP wrapping.

## License

MIT. See [LICENSE](LICENSE).
