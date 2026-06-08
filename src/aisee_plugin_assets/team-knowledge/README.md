# Aisee Team Knowledge

This repository stores reviewed engineering guardrails for Aisee projects.

Facts source:

- `knowledge/cards/**`
- `knowledge/packs/**`

Rebuildable cache:

- `indexes/lexical-index.json`
- `indexes/vector-index/`

Do not copy OpenSpec changes, tasks, contracts, source-map files, project memory, secrets, customer names, private URLs, or solution document bodies into team knowledge cards.

## Basic Workflow

1. Author candidate cards from project-local curation reports.
2. Review privacy, applicability, trigger, action, and boundaries.
3. Activate only reviewed cards.
4. Let business projects pin specific packs through `aisee/knowledge.yaml`.

