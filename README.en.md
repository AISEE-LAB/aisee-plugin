<p align="center">
  <img src="https://raw.githubusercontent.com/AISEE-LAB/aisee-plugin/main/assets/aisee-logo-wordmark.svg" alt="Aisee" width="560">
</p>

<p align="center">
  <strong>Spec First. Better Handoffs. Compound Knowledge.</strong>
</p>

<p align="center">
  English · <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/README.md">简体中文</a>
</p>

<p align="center">
  <a href="https://aisee.wiki">Website</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin">GitHub</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/docs/workflow.en.md">Workflow</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/docs/best-practices.en.md">Best Practices</a> ·
  <a href="https://github.com/AISEE-LAB/aisee-plugin/blob/main/docs/plugin-marketplace.en.md">Plugin Marketplace</a> ·
  <a href="https://pypi.org/project/aisee-plugin/">PyPI</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/aisee-plugin/"><img src="https://img.shields.io/pypi/v/aisee-plugin" alt="PyPI"></a>
  <a href="https://pypi.org/project/aisee-plugin/"><img src="https://img.shields.io/pypi/pyversions/aisee-plugin" alt="Python"></a>
  <a href="https://github.com/AISEE-LAB/aisee-plugin/actions/workflows/ci.yml"><img src="https://github.com/AISEE-LAB/aisee-plugin/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://github.com/AISEE-LAB/aisee-plugin/stargazers"><img src="https://img.shields.io/github/stars/AISEE-LAB/aisee-plugin?style=social" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

# Aisee Plugin

> Aisee Plugin is a Codex-oriented OpenSpec workflow layer for spec-driven AI software engineering.

**Aisee** stands for **AI-Enhanced Software Engineering**.

Aisee Plugin is an AI software engineering plugin for OpenSpec workflows. It helps teams turn ambiguous ideas into reviewable requirements, UI content specifications, architecture context, OpenSpec changes, project memory, team knowledge guardrails, implementation-stage JSON decisions with optional handoff briefs, verification checks, and archive guardrails.

Aisee **does not replace OpenSpec**. OpenSpec remains the specification state machine and baseline source of truth. Aisee adds structured skills, project memory, team knowledge, JSON context tooling, and engineering handoff rules around OpenSpec.

It is especially relevant for maintainers who want Codex and other coding agents to work more reliably in open-source repositories:

- durable requirements and specifications instead of transient chat context;
- machine-readable context packs and schema packs for implementation, review, and verification;
- OpenSpec change planning that turns vague intent into reviewable deliverables;
- machine-readable implementation-stage decisions with optional handoff briefs that help maintainers and contributors hand off PR-ready work;
- verification evidence and archive gates that close the loop before AI-assisted changes are treated as complete.

## OpenSpec Boundary

Aisee does not replace OpenSpec and does not maintain a second schema state machine. Aisee reads the current schema declaration only when handling OpenSpec changes, context packs, or schema pack checks; project memory and team knowledge remain guidance / guardrails.

When Aisee handles OpenSpec artifacts, it acts only as a parser / checker / projector. `openspec validate` and `openspec archive` remain OpenSpec responsibilities.

## Why This Matters for Codex

Codex can write, review, and fix code, but the results are less reliable when a repository lacks explicit requirements, stable project context, review rules, and verification criteria.

Aisee supplies that workflow layer:

- it turns intent into durable OpenSpec changes, planning docs, and reusable project memory;
- it helps maintainers first reduce implementation entry into reusable JSON decisions, and only turn them into human-readable handoff briefs when needed;
- it lets Codex read against the same context boundaries across implementation, review, verification, and archive;
- it gives open-source projects clearer engineering constraints for AI-assisted contribution flows.

## Why Aisee?

AI coding assistants are useful, but projects drift when requirements, UI decisions, technical constraints, and implementation evidence live only in chat history.

Aisee makes that context explicit:

- clarify business requirements before implementation;
- separate requirements, UI content, architecture context, and change planning;
- create and complete OpenSpec changes while reading required artifacts from the current schema;
- keep OpenSpec as the only persistent specification source of truth;
- generate machine-readable context packs for implementation, verification, and review;
- constrain document-local numbering through skills/templates to reduce invented or duplicated labels;
- check whether artifacts, tasks, source maps, tests, and review evidence are closed before archive.

## Agile Delivery Model

Aisee now follows a version / iteration-oriented agile model:

- SRS, UI Content, Design Spec, and Architecture are **planning docs** for the current version or iteration;
- regular planning docs use a shared YAML frontmatter contract for identity, status, and source indexing without becoming OpenSpec baseline facts;
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
Aisee = planning, context, schemas, source routing, and workflow guardrails
Aisee CLI = JSON context bus, not a second source of truth
Compound Engineering = optional implementation / review / test consumer
```

## Skill Taxonomy

`plugins/aisee-plugin/.codex-plugin/plugin.json` still exposes all public skills through `skills: "./skills/"`, but the default happy path contains only **9 core iteration skills**, plus project orientation and setup / governance skills. The full contract lives in [Skill Taxonomy](plugins/aisee-plugin/references/skill-taxonomy.md).

Project setup / governance:

- `aisee:orient`
- `aisee:init`

Core iteration workflow:

- `aisee:srs`
- `aisee:ui-content`
- `aisee:architecture`
- `aisee:change-plan`
- `aisee:change-author`
- `aisee-schema-pack`
- `aisee:implementation-bridge`
- `aisee:verify`
- `aisee:archive-guard`

On-demand extensions:

- Optional extensions: `aisee:design-spec`, `aisee:design-assets`, `aisee:svg-assets`, `aisee:image-object`, `aisee:spec-migrate`
- Knowledge loop: `aisee:reflect`, `aisee:memory`, `aisee:knowledge`, `aisee:knowledge-curate`
- Hardware / experimental: `hw:srs`, `hw:architecture`, `hw:init`, `hw:change-plan`

## Features

- **Structured requirement clarification**: `aisee:srs` clarifies business needs through dialogue and produces planning-level SRS documents.
- **UI content specification**: `aisee:ui-content` turns confirmed requirements into pages, content, states, flows, permission visibility, and platform differences without writing visual design rules.
- **Architecture context**: `aisee:architecture` records technical facts, constraints, reusable capabilities, global engineering conventions, and artifact hints.
- **Schema-aware change planning**: `aisee:change-plan` maps confirmed inputs into independently deliverable OpenSpec changes.
- **OpenSpec schema pack**: includes app, device, docsite, infra, security, quick-fix, quick-research, and collaboration schemas.
- **Context packs**: `aisee context pack` provides optional project memory and team knowledge injection for the current change without replacing OpenSpec facts.
- **Project memory**: `aisee memory` retrieves and writes current-repository long-lived guidance without replacing OpenSpec facts.
- **Team knowledge guardrails**: `aisee knowledge` retrieves a small number of reviewed engineering lessons through pack/card protocols without turning the knowledge repository into a second specification source.
- **Controlled memory injection**: `aisee context pack` injects `project_memory` or `knowledge` only when explicitly requested and does not own implementation-stage routing.
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

Check CLI and plugin content status:

```bash
aisee plugin inspect --json
aisee doctor --json
```

When reading plugin content, the CLI checks only the Codex install location by default. For other agent runtimes, set `AISEE_AGENT_RUNTIME=claude|cursor|agents`; set it to `none` to disable installed plugin content discovery.

Plugin content, schema packs, and team knowledge templates come from the Codex marketplace plugin or external repositories; team knowledge onboarding uses `aisee knowledge init-repo` and `aisee knowledge configure`.

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

This command auto-selects OpenSpec tools from the current agent runtime (`codex` by default in Codex; falls back to `none` when no supported runtime is detected), enables the expanded workflow that Aisee expects by default, and ensures project-local OpenSpec instructions/skills are installed or refreshed:

```text
write ~/.config/openspec/config.json   # profile=custom, delivery=both, workflows=expanded set
openspec init . --tools <detected-runtime-or-none> --profile custom
openspec update .
```

If you want the lean OpenSpec `core` workflow instead, pass:

```bash
aisee openspec ensure --profile core --json
```

If you only want the OpenSpec directory layout without installing OpenSpec-provided agent skills/instructions, pass:

```bash
aisee openspec ensure --tools none --json
```

Schema packs come from the marketplace-installed plugin. `aisee schemas list/check` only reports project-installed schema state or source-checkout development schema state; it does not install schemas automatically.

Check the project state again:

```bash
aisee doctor --json
```

## Documentation

- [Documentation site](https://aisee.wiki): Aisee guides, workflows, and release notes.
- [Aisee Workflow](docs/workflow.en.md): end-to-end guidance from setup, requirement clarification, change authoring, implementation handoff, verification, and archive.
- [Aisee Best Practices](docs/best-practices.en.md): conventions for sources of truth, schemas, contracts, context packs, reuse-first routing, review, and archive when using Aisee with OpenSpec.
- [Compatibility Policy](docs/compatibility-policy.en.md): compatibility boundaries for CLI JSON, schema packs, context packs, plugin content, and experimental capabilities.
- [Plugin Marketplace](docs/plugin-marketplace.en.md): responsibilities of plugin manifests, marketplace listings, PyPI/pipx, and the Codex install path.
- [Team Knowledge Guardrails](docs/team-knowledge.en.md): experimental status, usage, and gaps before stability for shared team knowledge.
- [Aisee Team Knowledge Architecture](docs/architecture/aisee-team-knowledge.md): team knowledge guardrail retrieval, card/pack boundaries, CLI onboarding, and read model.
- [Schema Packs](docs/schema-packs.md): schema selection, app schema artifact DAG, source-map/numbering rules, and contract attachment boundaries.
- [Aisee / OpenSpec / Compound Engineering Integration](docs/architecture/aisee-openspec-compound-integration.md): high-level responsibility boundaries and historical decisions.
- [OpenSpec Multi-Schema Best Practices](docs/architecture/openspec-multi-schema-best-practices.md): multi-schema coexistence, conflict handling, and management rules.
- [CHANGELOG.md](CHANGELOG.md): release history, shipped notes, and user-visible changes for published versions.

## Typical Workflow

```text
1. aisee:srs / aisee:ui-content / aisee:architecture, as needed
2. aisee:change-plan
3. /opsx:new "<change>" --schema <schema>
4. aisee:change-author
5. openspec validate <change>
6. aisee:implementation-bridge
7. implementation / review / test (write back `tasks.md` / apply tracks before marking the batch complete)
8. openspec archive <change>

For small, bounded, low-risk work, an abbreviated path is also valid:

```text
quick-fix / quick-research / another lightweight schema
  -> change-author
  -> implementation-bridge
  -> implementation / review / test
  -> archive
```
```

Before and after implementation, use read-only Aisee reviewer lenses as needed: `aisee-change-architect`, `aisee-spec-reviewer`, and `aisee-implementation-reviewer`. See [Aisee Workflow](docs/workflow.en.md) for timing and boundaries, and [Aisee Best Practices](docs/best-practices.en.md) for reuse-first routing.

For existing projects, use `aisee:spec-migrate` to derive OpenSpec baseline specs from code, tests, docs, routes, and verified behavior.

## Main Skills

| Skill | Purpose |
| --- | --- |
| `aisee:orient` | Determine the current project stage and user intent, then route to the right Aisee skill or workflow. |
| `aisee:init` | Initialize or audit `AGENTS.md`, `openspec/project.md`, Aisee docs, memory, and Codex hooks. |
| `aisee:srs` | Clarify software requirements and produce planning-level SRS documents. |
| `aisee:ui-content` | Produce UI content specs for pages, elements, states, flows, permissions, and platform differences. |
| `aisee:architecture` | Capture software architecture context, technical constraints, reusable capabilities, and artifact hints. |
| `aisee:change-plan` | Plan independent OpenSpec changes and choose schemas. |
| `aisee-schema-pack` | Provide and maintain OpenSpec schema packs through the marketplace plugin. |
| `aisee:implementation-bridge` | Return implementation-stage JSON decisions for a single change by default, and generate handoff briefs only when explicitly needed. |
| `aisee:verify` | Diagnose artifact, task, source-map, numbering, and evidence gaps. |
| `aisee:archive-guard` | Provide the final recommendation before `openspec archive`. |
| `aisee:spec-migrate` | Build OpenSpec baseline specs for existing projects. |
| `aisee:design-spec` | Produce design specifications without duplicating UI content specs. |
| `aisee:design-assets` | Generate or extract visual references and design assets. |
| `aisee:svg-assets` | Generate, vectorize, optimize, and validate SVG assets. |
| `aisee:image-object` | Handle object-level image segmentation, masks, background removal, and exports. |
| `aisee:reflect` | Capture reusable project lessons and workflow improvements. |
| `aisee:memory` | Guide project memory CLI inspect/search/add/update-index usage. |
| `aisee:knowledge` | Guide team knowledge CLI initialization, configuration, sync, retrieval, and promote workflows. |
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
aisee context pack --change <change> --for ce-work --project-memory --json
aisee context pack --change <change> --for ce-work --knowledge --json
aisee context pack --change <change> --for aisee-verify --project-memory --json
aisee context pack --change <change> --for aisee-verify --knowledge --json
aisee memory inspect --json
aisee memory list --json
aisee memory search --query "<task>" --json
aisee memory add --type pref --title "<title>" --summary "<summary>" --body "<body>" --json
aisee memory update-index --json
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
```

Key CLI rules:

- JSON output is a context view, not a source of truth.
- `aisee memory` manages current-repository project memory; `aisee/cache/memory-index.json` is a deletable rebuildable cache.
- `aisee/cache/knowledge-index.json` is also a deletable and rebuildable cache; team knowledge persists in pinned pack/card files.
- `aisee knowledge promote-batch` only writes the local team knowledge worktree; it does not commit, push, or create PRs.
- OpenSpec artifacts and `source-map.md` are formal inputs for context packs.
- `bootstrap --plan` is a read-only plan and does not perform broad initialization writes.
- `aisee openspec ensure` installs or refreshes project-local OpenSpec instructions/skills and also aligns the global profile. It does not replace `aisee:init`.
- `aisee knowledge query` returns only a small number of guardrails. By default it reads pack manifests and card frontmatter; `--debug` is required for matched card body excerpts.

### Project Memory

Project memory stores current-repository guidance that is long-lived but does not belong in the OpenSpec baseline, such as stable preferences, architecture decision summaries, time-bound context snapshots, and stack constraints.

Common commands:

```bash
aisee memory inspect --json
aisee memory search --query "commit style" --json
aisee memory search --query "test command" --type stack --include-body --json
aisee memory add --type pref --title "Commit message language" --summary "Use Chinese commit messages by default." --body "Project commit messages should be Chinese and follow AGENTS.md." --source-ref AGENTS.md --priority high --json
aisee memory update-index --json
aisee context pack --change <change> --for ce-work --project-memory --json
```

Rules:

- `aisee:memory` guides day-to-day CLI usage; `aisee:reflect` still owns retrospective candidates.
- Default retrieval returns a small number of active metadata entries; use `--include-body` explicitly for bounded body excerpts.
- New writes go only to canonical `aisee/memory/`; legacy `.memory/` is read-only fallback.
- Hooks are read-only and can only hint `inspect/search` plus a few high-priority summaries.
- Project memory is guidance. If it conflicts with OpenSpec artifacts, `source-map.md`, or `tasks.md`, OpenSpec artifacts win.

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
aisee knowledge init-repo --dest ../aisee-team-knowledge --initial-pack web-app --json
aisee knowledge configure --path ../aisee-team-knowledge --enable-pack web-app --json
aisee knowledge inspect --json
aisee knowledge doctor --json
aisee knowledge check --json
aisee knowledge install --json
aisee knowledge update --json
aisee knowledge query --phase implementation --surface cli --query "public CLI JSON" --json
aisee knowledge query --from-change <change> --for ce-work --json
aisee context pack --change <change> --for ce-work --knowledge --json
aisee knowledge promote-batch --curation <path> --team-path ../aisee-team-knowledge --pack web-app --json
```

Rules:

- `aisee:knowledge` guides day-to-day CLI usage for onboarding, sync, retrieval, and promote.
- `install`, `update`, and `promote-batch` are experimental. Team knowledge examples come from the marketplace plugin or external repositories; PR automation and MCP service support are still unsettled.
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
docs/                User workflow, best practices, architecture, and release docs
docs/architecture/   Architecture docs
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
- When processing OpenSpec changes, read the current schema declaration instead of hardcoding app artifact assumptions.
- Keep `SKILL.md` concise and put long rules in references or architecture docs.
- Treat hardware and embedded workflows as dedicated extensions instead of forcing them into the app schema.

## Related Projects

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — a spec-driven development framework for AI coding assistants.
- [OpenSpec documentation](https://openspec.dev/) — OpenSpec installation and workflow documentation.
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin) — an agent workflow plugin for AI engineering execution, review, testing, commits, and team learning.

## Roadmap

### Ongoing Compatibility Governance

- Keep CLI JSON, project memory, team knowledge, context packs, marketplace plugin content, and skill contracts aligned with the Compatibility Policy; when a public contract changes, update tests, migration notes, and release notes together.
- Use real-project dogfood to verify memory retrieval, context pack handoffs, and knowledge guardrails instead of expanding abstract flows just to cover schema types.

### Later

- Add stronger Codex PR review and implementation-brief examples for maintainer workflows.
- Add a sample OpenSpec change so new repositories can see a concrete Aisee deliverable.
- Expand verify/archive gate examples to lower the trial cost for OSS maintainers.
- Improve project memory conflict hints, stale-entry policy, and low-context injection rules.
- Tighten team knowledge remote sync, promote workflows, lifecycle management, and optional MCP wrapping.

## License

MIT. See [LICENSE](LICENSE).
