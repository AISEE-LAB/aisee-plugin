# Plugin Marketplace

This document explains the boundary between Aisee plugin content, the Codex marketplace, and the PyPI / pipx CLI.

## Summary

```text
GitHub / Codex marketplace
  -> distributes Aisee skills / references / schema packs / team knowledge templates / plugin metadata

PyPI / pipx
  -> installs the Aisee CLI
  -> provides project-local JSON context tooling, OpenSpec companion checks, project memory, team knowledge, and version/distribution governance commands
```

Marketplace installation does not install the `aisee` CLI. PyPI / pipx installation provides only the CLI; skills, schema packs, references, and team knowledge templates come from the marketplace plugin.

## Codex Install

Add the GitHub marketplace and install the plugin in Codex:

```bash
codex plugin marketplace add AISEE-LAB/aisee-plugin --ref main
codex plugin add aisee-plugin@aisee-plugin
```

The CLI only prints these commands as setup hints. It does not write Codex config, cache, or plugin state.

When reading plugin content, the CLI checks only the Codex install location by default and does not scan across agent runtimes. To choose another runtime, set `AISEE_AGENT_RUNTIME=claude|cursor|agents`; set it to `none` to disable installed plugin content discovery.

## Manifest vs Marketplace Listing

| File | Responsibility | Current Status |
| --- | --- | --- |
| `plugins/aisee-plugin/.codex-plugin/plugin.json` | Plugin manifest with name, version, skills path, and UI metadata | Provided in this repository |
| `.agents/plugins/marketplace.json` | Codex marketplace listing pointing at the `plugins/aisee-plugin` plugin root | Provided in this repository |

`plugins/aisee-plugin/.codex-plugin/plugin.json` belongs to the plugin itself:

```json
{
  "name": "aisee-plugin",
  "skills": "./skills/"
}
```

`.agents/plugins/marketplace.json` is the marketplace entry. Its source points at the plugin directory inside the repository:

```json
{
  "plugins": [
    {
      "name": "aisee-plugin",
      "source": {
        "source": "local",
        "path": "./plugins/aisee-plugin"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

The manifest continues to expose the whole `./skills/` directory. Marketplace installations therefore see all 22 public skills, while the difference between the default happy path and on-demand extensions is governed by [Skill Taxonomy](../plugins/aisee-plugin/references/skill-taxonomy.md), README, workflow docs, and tests rather than by splitting the plugin into multiple installs.

## Relationship to PyPI / pipx

Recommended relationship:

- `pipx install aisee-plugin` installs the CLI.
- Codex marketplace installs plugin content.
- `aisee doctor --json` and legacy content distribution commands may print marketplace setup hints, but they do not perform installation.
- The single `aisee-plugin` continues to carry core workflow, optional extensions, knowledge loop, and hardware / experimental skills in one install topology.

Not recommended:

- letting the CLI write Codex marketplace or plugin cache state;
- copying skills, references, schema packs, or team knowledge templates into the PyPI / pipx distribution channel;
- treating marketplace listings as project sources of truth for OpenSpec, schemas, source-map, or team knowledge;
- forcing Codex marketplace fields onto Claude / Cursor metadata.

## Compatibility Commitments

The following are Aisee public contracts:

- plugin name `aisee-plugin`;
- Codex manifest `skills` points to a loadable skills directory;
- Codex marketplace setup commands;
- base JSON semantics for CLI `status`, `issues`, `summary`, `meta`, and setup hints;
- public legacy commands return stable deprecation/blocker JSON during migration instead of silently writing old content assets.

The following are not stable:

- Codex internal cache paths;
- marketplace display ordering;
- Codex config file internal schema;
- Claude / Cursor marketplace-native distribution.

## Pre-Release Checks

When touching plugin marketplace compatibility, run at least:

```bash
python /Users/fengliang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/aisee-plugin
python scripts/smoke_release.py
```

Also confirm manually:

- `plugins/aisee-plugin/.codex-plugin/plugin.json` has no unsupported fields;
- `.agents/plugins/marketplace.json` points at the `./plugins/aisee-plugin` plugin root;
- `pipx install aisee-plugin` validates the CLI only and does not assume PyPI / pipx installation also provides plugin content.
