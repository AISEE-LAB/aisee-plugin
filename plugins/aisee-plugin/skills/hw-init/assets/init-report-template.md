# Init Report Template

```markdown
# <Project Name> Project Initialization Report

## 1. Inputs

- Mode:
- Design:
- Selected template:
- Toolchain:
- Build system / IDE:
- Existing project migration:

## 2. Created / Updated Structure

| Path | Purpose | Created / Existing / Skipped |
|---|---|---|
|  |  |  |

## 3. Project Structure Contract

- Project structure path:
- IDE/build file strategy: no edit / backup and edit / manual
- Files to add manually:

## 4. Build Entry

- Main build command:
- IDE entry:
- Flash / run command:
- Test command:

## 5. Clock Contract

- Clock contract path:
- Clock source files:
- Status: generated / existing / [CLOCK-CONTRACT-MISSING]

## 6. Memory And Device Contract

- Memory/device contract path:
- Map file:
- Startup file:
- Linker/scatter file:
- Device macro / target:
- Status: generated / existing / [MEMORY-DEVICE-CONTRACT-MISSING]

## 7. Directory Rules For Future AI Work

| Directory | Allowed Content | Forbidden Content |
|---|---|---|
|  |  |  |

## 8. Follow-Up Tasks

- [ ] Verify first build.
- [ ] Add board bring-up test.
- [ ] Verify clock-dependent peripherals.
- [ ] Verify map memory margin.
- [ ] Verify startup/linker/device target after any MCU variant change.
- [ ] Add project-specific module tasks from design.
```
