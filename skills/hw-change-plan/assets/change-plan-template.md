# Hardware Change Plan Template

Use this structure directly. Do not wrap the whole output in a Markdown code fence.

# Hardware Change Plan: <Project Name>

**Source SRS**: aisee/docs/requirements/...-hw-srs.md
**Source Architecture**: aisee/docs/architecture/...-hw-architecture.md
**Schema**: aisee-device-spec-driven
**Created**: <date>

## Summary

<N> changes across <M> phases · estimated total: <X> weeks · <Y> can run in parallel

## Dependency Graph

```text
Phase 1:
  [change-a]

Phase 2:
  [change-b]  depends on change-a
  [change-c]  depends on change-a
```

## Change Details

### Change 1/<N>

Name: `<change-name-kebab-case>`

Title: <human readable title>

Schema: `aisee-device-spec-driven`

Complexity: S / M / L

Description:
- <one sentence describing what this change delivers>

In Scope:
- <concrete scope> (FR-xxx)

Out of Scope:
- <explicit exclusion>

Source-map seed:
- FR: FR-xxx
- HW: HW-xxx / TBD in hardware-contract
- FW: FW-xxx / TBD in firmware-contract
- RT: RT-xxx / TBD in runtime-contract
- VER: VER-xxx / TBD in verification-contract

Artifact applicability:
- hardware-contract.md: yes / no — <reason>
- firmware-contract.md: yes / no — <reason>
- runtime-contract.md: yes / no — <reason>
- verification-contract.md: yes — <reason>

Implementation helper:
- Use `hw:init generate-skeleton` during `/opsx:apply` if this change is `initialize-hardware-project`; otherwise N/A.

Depends on: <change-name or none>

Parallel with: <change-name or none>

Change rationale:
- <why this is a natural independently verifiable boundary>

Command:
```bash
/opsx:new "<change-name-kebab-case>" --schema aisee-device-spec-driven
```

## All Commands

```bash
/opsx:new "<change-a>" --schema aisee-device-spec-driven
/opsx:new "<change-b>" --schema aisee-device-spec-driven
```

## Initialization Rule Check

- Project skeleton required: yes / no
- First change is `initialize-hardware-project`: yes / no / N/A
- Reason:

## Overall Rationale

- [ASSUMPTION]:
- [RISK]:
- [ARCH-BLOCKER]: