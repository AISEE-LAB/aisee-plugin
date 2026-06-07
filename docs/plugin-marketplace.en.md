# Plugin Marketplace

This document explains how Aisee aligns with agent plugin marketplace conventions and how that relates to PyPI / pipx installation.

## Summary

Aisee currently uses two distribution channels:

```text
PyPI / pipx
  -> installs the Aisee CLI
  -> includes default skills / references / schema packs / plugin metadata

Plugin marketplace
  -> lets agent runtimes discover, install, or order the Aisee plugin entry
  -> describes display metadata, category, installation policy, and authentication policy
```

Before Public Beta, skills remain packaged in the Python wheel. The plugin marketplace is a runtime distribution and discovery channel, not a hard dependency for the CLI.

## Manifest vs Marketplace Listing

There are two different file types:

| File | Responsibility | Current Status |
| --- | --- | --- |
| `.codex-plugin/plugin.json` | Plugin manifest with name, version, skills path, and UI metadata | Provided in this repository |
| `marketplace.json` | Marketplace listing with source, installation policy, authentication policy, and category | Not embedded by default; this document provides an example |

`.codex-plugin/plugin.json` belongs to the plugin itself. The source repository and `aisee plugin export --target codex` both provide this file.

`marketplace.json` belongs to a marketplace root. Aisee should not force one into the source repository because different users, teams, and marketplaces may need different `source.path`, policies, and ordering.

## Current Codex Manifest

The source repository contains:

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
```

The Codex manifest declares:

```json
{
  "name": "aisee-plugin",
  "version": "0.1.0",
  "skills": "./skills/",
  "interface": {
    "displayName": "Aisee",
    "category": "Coding"
  }
}
```

Runtime export:

```bash
aisee plugin export --target codex --dest ./aisee-plugin-bundle --json
```

Exported directory:

```text
aisee-plugin-bundle/
  .codex-plugin/plugin.json
  skills/
  references/
```

## Marketplace Listing Example

A personal or team marketplace can point to the exported plugin directory or to a plugin directory arranged according to marketplace conventions.

Example:

```json
{
  "name": "team",
  "interface": {
    "displayName": "Team Plugins"
  },
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

If a non-default marketplace file is used, the runtime must first install or recognize that marketplace. Default personal marketplace and team marketplace management are runtime concerns.

## Relationship to PyPI / pipx

Recommended relationship:

- `pipx install aisee-plugin` installs the CLI and default resources.
- `aisee plugin export` exports an agent-runtime-loadable plugin directory from the installed package.
- marketplace listings point to the exported plugin directory or to a team-managed plugin directory.

Not recommended:

- making CLI execution depend on marketplace availability;
- removing default skills from the wheel;
- treating marketplace listings as schema pack or OpenSpec artifact sources of truth;
- forcing Codex marketplace fields onto Claude / Cursor metadata.

## Compatibility Commitments

The following are Aisee public contracts:

- plugin name `aisee-plugin`;
- Codex manifest `skills` points to a loadable skills directory;
- `aisee plugin export --target codex|claude|cursor` target names;
- exported directory contains target runtime metadata, `skills/`, and `references/`;
- marketplace examples use `policy.installation`, `policy.authentication`, and `category`.

The following are not yet stable:

- concrete marketplace file location;
- marketplace display ordering;
- team marketplace source path;
- remote marketplace distribution;
- automatic install, update, or authentication flows.

## Pre-Release Checks

When touching plugin marketplace compatibility, run at least:

```bash
python /Users/fengliang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python scripts/smoke_release.py
```

Also confirm manually:

- `.codex-plugin/plugin.json` has no unsupported fields;
- `aisee plugin export --target codex` exports a directory that the runtime can recognize;
- marketplace listing examples are not presented as the only installation path.
