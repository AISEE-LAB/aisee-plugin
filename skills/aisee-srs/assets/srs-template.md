# aisee:srs — SRS Template Index

Read this file at the start of Phase 4 (SRS Generation). It is a routing index, not the full template.

## Template Selection

Choose the output mode from `SKILL.md` Phase 3:

| Output mode | Read these files |
|-------------|------------------|
| Standard | `references/writing-rules.md` + `assets/srs-template-standard.md` + relevant blocks from `references/scenario-extension-blocks.md` |
| Epic main document | `references/writing-rules.md` + `assets/srs-template-epic-main.md` |
| Epic module document | `references/writing-rules.md` + `assets/srs-template-epic-module.md` + relevant blocks from `references/scenario-extension-blocks.md` |

## Reading Rules

- Always read `references/writing-rules.md` before generating any SRS document.
- Read only the template file needed for the current output mode.
- Read only the scenario extension blocks that match the FRs being written.
- Do not copy scenario extension blocks mechanically when they do not apply.
- Keep SRS planning-level detailed: enough for UI Content, Architecture, and Change Plan handoff, but not implementation-level API, DB, code, or task design.

## Future Domain Extension

Current templates are optimized for software/full-stack requirements.

For hardware, embedded, firmware, or device requirements:
- Use the common SRS structure only when it fits.
- Do not force software scenario extension blocks onto hardware/device requirements.
- Future hardware-specific files may be added, for example:
  - `references/scenario-extension-blocks-device.md`
  - `assets/srs-template-device-standard.md`
  - `assets/srs-template-device-epic-main.md`
  - `assets/srs-template-device-epic-module.md`
