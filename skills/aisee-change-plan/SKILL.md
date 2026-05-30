---
name: aisee:change-plan
description: 将已确认的 SRS、UI 内容规格、设计规范、技术上下文和项目事实映射为可独立交付的 OpenSpec changes。用于规划 change 边界、依赖顺序、并行关系、source-map 初稿和 /opsx:new 命令；不重新做业务模块划分，不重新生成需求。
---

# aisee:change-plan — Change Boundary Planner for OpenSpec

Map confirmed requirements into properly scoped OpenSpec changes. Each output change should be small enough to create with `/opsx:new`, then complete through the selected schema's artifact sequence before implementation. For app/device schemas this commonly includes `source-map.md`, `specs/`, `design.md`, contract artifacts, and `tasks.md`; lighter schemas may use different artifacts.

`aisee:change-plan` 不负责业务模块划分。SRS 的模块回答“业务上有哪些模块”，本技能回答“哪些 FR / PAGE / API / DATA 应放进同一个可独立交付的 OpenSpec change”。

## Inputs

The user provides one of:
- A raw requirement description (free text)
- A ticket/issue reference (will be read if MCP is available)
- A file path to an existing requirements doc (including SRS output from `aisee:srs`)
- Optional companion inputs: UI content spec from `aisee:ui-content`, design spec from `aisee:design-spec`, and technical context from `aisee:tech-context`

Optional flags the user may include:
- `--strategy vertical|risk|parallel` (default: vertical)
- `--granularity fine|medium|coarse` (default: medium) — sets explicit target size constraints:
  - `fine`: prefer S changes; each change should be 1–3 days; split M/L candidates unless doing so would break independent deployability
  - `medium`: allow S/M changes; each change should be 1–7 days; default for most product work
  - `coarse`: prefer fewer changes; allow M/L changes up to 14 days; never allow XL
- `--schema <name>` — schema for generated `/opsx:new` commands (default: `aisee-app-spec-driven`)
- `--max-changes <N>` — maximum changes to output (default: `8`)
- `--single-if-small` — if the input is already a single ≤3 day change, output one change and do not force a multi-change plan

## Phase 1 — Read Project Context

Before analyzing the requirement, gather all inputs. Run these commands silently:

```bash
# If input is a file path, read it first
cat <input-file-path> 2>/dev/null || echo "File not found"

# Read project OpenSpec config
cat openspec/config.yaml 2>/dev/null || echo "No config found"

# Check existing active changes (to avoid name collisions and understand current state)
openspec list --json 2>/dev/null \
  || ls openspec/changes/ 2>/dev/null \
  || echo "No existing changes found"

# Read archived changes list for naming conventions
ls openspec/changes/archive/ 2>/dev/null | head -20

# Read CLAUDE.md or AGENTS.md for team conventions
cat CLAUDE.md 2>/dev/null | head -100
```

Use this context to:
- Understand the project's tech stack and conventions
- Identify any in-progress changes that the new work may depend on or conflict with
- Match the naming style of existing changes (kebab-case, length, vocabulary)

### Tech-context Input Mode

If the user provides a technical context document produced by `aisee:tech-context`:

- Treat its technical facts, stack state, reusable capabilities, shared prerequisites, coupling points, and platform constraints as change planning inputs.
- Preserve blocking tags such as `[STACK-CONTEXT-MISSING]`, `[STACK-GAP]`, `[STACK-DECISION-REQUIRED]`, `[SPEC-GAP]`, and `[STACK-CONFLICT]` in change rationale when they affect boundaries.
- Do not reinterpret tech-context hints as a pre-made change list; `aisee:change-plan` still owns final change boundaries, dependencies, names, and `/opsx:new` commands.
- Do not use `aisee:change-plan` to choose a missing project tech stack. If tech-context marks a stack decision as missing, surface it as a blocker or assumption instead of silently selecting tools.

### Design-spec Input Mode

If the user provides a design spec document produced by `aisee:design-spec`:

- Treat its design strategy, component policy, design tokens, screen patterns, interaction patterns, responsive rules, accessibility rules, and Do/Don't as planning inputs.
- Preserve blocking tags such as `[DESIGN-DECISION-REQUIRED]` and `[TECH-CONTEXT-MISSING]` in change rationale when they affect boundaries.
- Do not reinterpret design-spec as a page list; UI Content still owns PAGE / FLOW content scope.
- Do not use `aisee:change-plan` to create a design system from scratch. If design-spec marks a design decision as missing, surface it as a blocker or assumption instead of silently inventing visual rules.
- If a shared component policy, token foundation, or cross-page screen pattern must exist before multiple UI changes can proceed, record that as a design prerequisite in the relevant change rationale.

### SRS Input Mode

If the input file is a SRS document produced by `aisee:srs` (detected by the presence of `FR-xxx` requirement IDs and a "变更候选清单" section), activate **SRS input mode**:

- Use the FR-xxx IDs as the canonical unit of analysis — do not re-derive requirements from scratch
- Read Section 7 (变更候选清单) as the primary change planning input: priority, complexity estimates, and dependency hints are already populated
- Read Section 5.2 (假设) and Section 6 (Open Questions) — unresolved items here should influence change rationale and may warrant a clarification question in Phase 2
- Preserve FR-xxx references in each change's In Scope list so the SRS remains traceable

## Phase 2 — Clarify (only when needed)

`aisee:change-plan` short-circuits clarification when the requirement is already specific enough. Ask **at most two questions**, and only if:
- The requirement spans multiple unrelated domains with no clear boundary
- It's genuinely unclear which components are in scope

Skip clarification entirely for:
- Requirements under ~100 words that describe a single user-facing feature
- SRS input mode where FR scope is already explicit

When asking, frame as a single focused question:

> "Before I plan these change boundaries, one thing to clarify: [specific ambiguity]. This affects whether I treat X and Y as one change or two."

If the user does not respond or says "you decide", record the assumption in the Overall rationale section with an `[ASSUMPTION]` tag and proceed.

## Phase 3 — Apply Change Boundary Algorithm

Analyze the requirement using these principles, in priority order:

### Rule 1 — Independent deployability (non-negotiable)

Every change must leave the system in a working state when merged alone. A change that only adds a DB table with no API or UI is not independently deployable. A change that adds a half-built UI is not independently deployable.

**Test**: "If this change merged today and nothing else did, would the system still work correctly?"

**Feature flags**: A change that ships behind a feature flag counts as independently deployable, provided the flag-off path leaves existing behavior intact. Note the flag explicitly in the change's In Scope list.

### Rule 2 — Single ownership

Each change should have one Spec Owner who can independently make all technical decisions. If a change touches payments AND notifications AND auth, it likely needs a different owner for each — plan separate changes unless there is a strong vertical-slice reason.

### Rule 3 — Planning strategy

Apply the strategy specified by `--strategy`. Default is `vertical`.

#### Strategy: vertical (default)

Each change delivers a complete user-facing scenario end-to-end (UI + API + DB). Avoid horizontal slicing (all DB first, then all API, then all UI) unless there is a strong technical reason — for example, a shared data model that blocks all parallel work.

#### Strategy: risk

Prioritize the most uncertain parts of the requirement first. The highest-risk change (novel algorithm, external integration, unproven architecture) goes into Phase 1. Subsequent changes depend on its validated output.

Signals that a change is high-risk:
- First time integrating a third-party service
- Technical feasibility is uncertain
- Requires performance benchmarking before committing to an approach

When using this strategy, the first change is often a time-boxed spike or PoC. Its output is a design decision, not a shippable feature. Mark it explicitly:

```
Title: [SPIKE] Validate <approach>
In Scope:
  - Prototype implementation to validate feasibility
  - Decision document: go / no-go + recommended approach
Out of Scope:
  - Production-quality code
  - Error handling beyond happy path
```

#### Strategy: parallel

Identify module boundaries that allow maximum concurrent work. Changes in the same phase must have zero shared mutable state and no cross-team coordination required during implementation.

When using this strategy:
- Prefer a single small prerequisite change (S-sized) to establish any shared contracts (API schema, event types, DB tables) before parallel work begins
- Strictly re-verify Rule 1 for each parallel change — parallel strategy creates the most risk of invisible coupling
- Label each parallel group clearly in the dependency graph

### Rule 4 — Schema selection

- `aisee-app-spec-driven`: default for feature development that needs SRS / UI Content / Tech Context / Change Plan traceability
- `aisee-device-spec-driven`: for embedded, firmware, Linux device, driver, RTOS, bare-metal, MCU, SoC, or board bring-up work
- `spec-driven`: use only for lightweight changes that do not need the aisee planning chain
- `opsx-collab-pr-loop`: for technical research, external PR review, investigative work with uncertain scope
- If the user passes `--schema <name>`, use that schema consistently in every change block and every `/opsx:new` command.

### Rule 5 — Granularity and complexity bounds

| Label | Estimated effort | When to use |
|-------|-----------------|-------------|
| S     | 1–3 days        | Single component change, clear implementation path |
| M     | 3–7 days        | Multi-component, requires design decisions |
| L     | 7–14 days       | Significant architectural scope, high uncertainty |

Apply `--granularity` as a planning constraint, not a loose preference:

| Granularity | Output constraint | Required behavior |
|-------------|-------------------|-------------------|
| fine | Prefer S; avoid M; no L unless explicitly justified | Break down any M/L candidate when the resulting changes remain independently deployable |
| medium | Allow S/M; avoid L unless the boundary is naturally indivisible | Default balance between reviewability and change count |
| coarse | Allow S/M/L; no XL | Merge tightly related sub-features when they are independently deployable together and share one owner |

If a change would exceed 14 days (XL), it must be broken down further. Mark it in the Summary with ⚠️ and add a note in its Change rationale:

```
⚠️ This change is estimated at >14 days. Recommend completing /ce:brainstorm
first to validate scope boundaries before deciding how to break it down.
```

Do not attempt to break down an XL change mechanically without domain context — flag it and let the team decide after brainstorm.

### Rule 6 — Change count bounds

- Default maximum output is **8 changes**.
- If the user passes `--max-changes <N>`, use that limit instead, but never output more than 8 without explicitly warning that the requirement should be handled as an epic planning session.
- If `--single-if-small` is present and the scope is clearly ≤3 days with one owner and no risky coupling, output exactly one change.

### Rule 7 — Explicit Out-of-Scope

Every change must have a non-empty Out-of-Scope list. This is what prevents scope creep during `/opsx:apply`. Things that are "obviously not included" still need to be written down.

### Rule 8 — Dependency discipline

- Mark a dependency only when one change **must be merged** before another can start implementation (not just before it can be designed)
- Prefer enabling parallel work. If two changes touch different modules and their only shared concern is a config value, make the config change a prerequisite change (S-sized), then run the others in parallel.
- Never create circular dependencies.

### Rule 9 — Source-map seed

Every planned change must include a source-map seed.

For `aisee-app-spec-driven`:
- FR IDs from SRS or proposal
- PAGE / FLOW IDs from UI Content, or `N/A`
- Expected API capability IDs, or `TBD in service-contract`
- Expected DATA IDs, or `TBD in data-model`
- Artifact applicability for `ui-contract.md`, `data-model.md`, and `service-contract.md`

For `aisee-device-spec-driven`:
- FR IDs from SRS or proposal
- Expected HW IDs, or `TBD in hardware-contract`
- Expected FW IDs, or `TBD in firmware-contract`
- Expected RT IDs, or `TBD in runtime-contract`
- Expected VER IDs, or `TBD in verification-contract`
- Artifact applicability for `hardware-contract.md`, `firmware-contract.md`, `runtime-contract.md`, and `verification-contract.md`

## Phase 4 — Output

Produce the following output in order:

---

### Summary

`N changes across M phases · estimated total: X weeks · Y can run in parallel`

Include a ⚠️ marker for any change estimated at XL (>14 days).

---

### Dependency graph

For straightforward dependency chains, render as ASCII:

```
Phase 1 (sequential):
  [change-name-1] ─── [change-name-2]

Phase 2 (parallel after phase 1):
  [change-name-3]
  [change-name-4]  ← both depend on change-name-2
  [change-name-5]

Phase 3:
  [change-name-6] ─── depends on change-name-3 and change-name-4
```

If the dependency graph has more than 3 phases or contains diamond dependencies (one change depending on multiple parallel branches), append a table for clarity:

| Change | Depends on | Can run in parallel with |
|--------|-----------|--------------------------|
| change-name-3 | change-name-2 | change-name-4, change-name-5 |
| change-name-4 | change-name-2 | change-name-3, change-name-5 |

---

### Change details

For each change, output a block:

```
─────────────────────────────────────────────────
change N/total

Name:         change-name-kebab-case
Title:        Human readable title
Schema:       aisee-app-spec-driven | spec-driven | opsx-collab-pr-loop
Complexity:   S | M | L

Description:
  One sentence describing what this change delivers.

In Scope:
  - Concrete thing 1 (FR-001)      ← reference FR-xxx when in SRS input mode
  - Concrete thing 2 (FR-002)
  - Concrete thing 3

Out of Scope:
  - Explicitly excluded thing 1
  - Explicitly excluded thing 2

Source-map seed:
  FR:   FR-001, FR-002
  APP schema fields:
    PAGE: PAGE-001, PAGE-002 (or "N/A")
    FLOW: FLOW-001 (or "N/A")
    DS:   expected design rule / pattern IDs or "TBD in ui-contract"
    API:  expected API capability IDs or "TBD in service-contract"
    DATA: expected DATA IDs or "TBD in data-model"
  DEVICE schema fields:
    HW:  expected HW IDs or "TBD in hardware-contract"
    FW:  expected FW IDs or "TBD in firmware-contract"
    RT:  expected RT IDs or "TBD in runtime-contract"
    VER: expected VER IDs or "TBD in verification-contract"
  Artifact applicability:
    - ui-contract.md: yes/no — reason
    - data-model.md: yes/no — reason
    - service-contract.md: yes/no — reason
    - hardware-contract.md: yes/no — reason
    - firmware-contract.md: yes/no — reason
    - runtime-contract.md: yes/no — reason
    - verification-contract.md: yes/no — reason

Depends on:    change-name (or "none")
Parallel with: change-name, change-name (or "none")

Change rationale:
  Why this is a natural boundary. What makes this independently deployable.

Command:
  /opsx:new "change-name-kebab-case" --schema aisee-app-spec-driven
─────────────────────────────────────────────────
```

---

### All commands (copy-ready, ordered by execution)

```bash
# Phase 1
/opsx:new "change-name-1" --schema aisee-app-spec-driven
/opsx:new "change-name-2" --schema aisee-app-spec-driven

# Phase 2 — run in parallel
/opsx:new "change-name-3" --schema aisee-app-spec-driven
/opsx:new "change-name-4" --schema aisee-app-spec-driven
/opsx:new "change-name-5" --schema aisee-app-spec-driven

# Phase 3
/opsx:new "change-name-6" --schema aisee-app-spec-driven
```

---

### Overall rationale

2–4 sentences explaining the overall change planning strategy: why these boundaries were chosen, what the main sequencing constraint is, and which part of the requirement has the most uncertainty.

Include any `[ASSUMPTION]` entries made during Phase 2 here, formatted as:

```
[ASSUMPTION] {what was assumed} — {which changes this affects} — confirm before starting implementation.
```

---

## Phase 5 — Save Output

Save the change plan output to `docs/change-plan/` (create if it does not exist).

Naming convention: `docs/change-plan/<YYYY-MM-DD>-<requirement-slug>.md`

Where `requirement-slug` is the kebab-case of the first 5 significant words of the requirement title. When input is a SRS file, derive the slug from the SRS filename.

```bash
mkdir -p docs/change-plan
# write document to above path
```

After saving, output:

> ✅ **Change plan saved**: `docs/change-plan/{filename}.md`
>
> **{N} changes** across **{M} phases** · {Y} can run in parallel
>
> Run the Phase 1 `/opsx:new` commands above to create change folders, then use `/opsx:continue` or the relevant change artifact authoring workflow to fill artifacts step by step.

---

## Guardrails

- **Never** output more than 8 changes for a single requirement. If the requirement needs more than 8, it's an epic that needs a separate planning session.
- **Never** create a change whose only purpose is "infrastructure" or "setup" with no user-visible outcome — bundle it into the first change that uses it, or make it an S-sized prerequisite with a clear handoff.
- **Never** plan changes based on file type or technology layer alone (no "frontend change" + "backend change" for the same feature unless they are genuinely independent).
- If the requirement is already small enough to be a single change (≤3 days of work), say so clearly and output a single `/opsx:new` command. Don't create multiple changes for the sake of planning.
- Do not invent scope that wasn't in the original requirement. If something is implied but not stated, list it under the first relevant change's Out-of-Scope with a note: `(not stated in requirement — confirm before including)`.

## Integration with the OpenSpec Workflow

```
aisee:srs                        ← 需求发现，输出 SRS 文档（docs/requirements/）
  ├─ aisee:ui-content            ← 页面内容规格（可选但推荐）
  ├─ aisee:design-spec           ← UI 设计规范事实源（UI 型需求可选但推荐）
  ├─ aisee:tech-context          ← 技术事实与约束（可选但推荐）
  └─ aisee:change-plan <inputs>        ← 本 skill：规划独立 OpenSpec Change 边界
       └─ /opsx:new <change>     ← 创建 Change Folder
            └─ /opsx:continue    ← 创建 / 补 proposal.md
            └─ change artifact authoring ← 按 schema 创建 / 补 specs、contracts、tasks
            └─ /opsx:apply       ← 实现
            └─ /ce:review        ← 代码审查
            └─ /opsx:archive     ← 归档
```

When multiple changes are in-flight simultaneously, always specify the change name explicitly:

```bash
/opsx:apply change-name-3     ← prevents ambiguity
```
