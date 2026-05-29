# Aisee Plugin

Aisee means **AI-Enhanced Software Engineering**.

This repository contains the Aisee plugin system for OpenSpec-driven development:

- Aisee skills for requirements, UI content, technical context, OpenSpec change authoring, verification, and reflection.
- OpenSpec schema packs for app, device, docsite, infra, security, quick-fix, research, and collaboration workflows.
- Planning documents for Aisee CLI, context packs, ID registry, source registry, and Compound Engineering handoffs.

## Repository Layout

```text
.codex-plugin/
.claude-plugin/
.cursor-plugin/
bin/
skills/
schemas/
references/
scripts/
docs/architecture/
```

## Current Status

This is the initial extracted project scaffold. Some orchestration skills are skeletons and should be implemented against the architecture documents under `docs/architecture/`.

## Core Idea

```text
Aisee skills
  structure requirements and author OpenSpec changes

OpenSpec
  remains the specification state machine and baseline source of truth

Aisee CLI
  parses templates and returns JSON context packs without becoming a second content source

Compound Engineering
  performs document review, implementation, test, code review, commit, and PR handoff
```
