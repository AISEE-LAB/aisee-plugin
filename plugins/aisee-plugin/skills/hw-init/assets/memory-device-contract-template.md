# Memory And Device Contract Template

```markdown
# Memory And Device Contract

## 1. Sources

| Source | Path / Value | Status |
|---|---|---|
| MCU model | .ioc / IDE target / user input |  |
| Package | .ioc / schematic / user input |  |
| Device macro | compiler defines |  |
| Startup file | startup_<device>.s |  |
| Linker/scatter file | .ld / .sct / .icf / IDE memory config |  |
| Map file | .map |  |
| Flash download algorithm | IDE/debug config |  |

## 2. Current Device

| Item | Value | Source |
|---|---|---|
| MCU family |  |  |
| Exact part number |  |  |
| Package |  |  |
| Flash size |  |  |
| RAM size |  |  |
| Flash address range |  |  |
| RAM address range |  |  |
| Core / FPU / DSP features |  |  |

## 3. Startup And Interrupts

| Item | Value | Source |
|---|---|---|
| Startup file |  |  |
| Vector table owner |  |  |
| Initial stack pointer symbol |  |  |
| Heap size |  |  |
| Stack size |  |  |
| Enabled IRQ handlers |  |  |

## 4. Linker / Scatter Memory Layout

| Region | Start | Size | Purpose | Source |
|---|---|---|---|---|
| Flash / ROM |  |  |  |  |
| RAM / IRAM |  |  |  |  |
| CCM / DTCM / SRAM2 / backup RAM |  |  |  |  |

## 5. Latest Map Summary

| Item | Used | Limit | Margin | Source |
|---|---|---|---|---|
| Code + RO data |  |  |  | map |
| RW data |  |  |  | map |
| ZI data |  |  |  | map |
| Total ROM |  |  |  | map |
| Total RAM |  |  |  | map |
| Heap |  |  |  | startup/linker |
| Stack |  |  |  | startup/linker |

## 6. Variant Migration Rules

### Same family / larger memory variant

Example: same package and peripheral set, different Flash/RAM size.

Required checks:
- [ ] Part number and package match the board.
- [ ] Device macro is updated if required.
- [ ] Startup file is compatible or replaced.
- [ ] Linker/scatter Flash/RAM sizes are updated.
- [ ] Flash download algorithm/debug target is updated.
- [ ] `.ioc` or vendor config target is updated.
- [ ] Map file confirms new memory limits.

### Same family / different peripheral or package variant

Required checks:
- [ ] Pinout and alternate functions.
- [ ] Clock tree and peripheral clock availability.
- [ ] ADC/DAC/OPAMP/comparator differences.
- [ ] DMA request mapping and interrupt vector names.
- [ ] Timer/channel availability.
- [ ] Communication peripheral instances.
- [ ] Analog front-end assumptions.

### Different but related family

Required checks:
- [ ] CMSIS/HAL device header.
- [ ] Startup file and vector table.
- [ ] Linker/scatter memory map.
- [ ] HAL/LL peripheral API compatibility.
- [ ] Errata and electrical limits.
- [ ] Rebuild and hardware smoke test.

## 7. Change Rules

- Do not change MCU model, startup file, linker/scatter memory, or device macro without updating this document.
- Do not claim variant compatibility from naming alone.
- Any memory-heavy feature must use the latest map file as evidence.

## 8. Missing Data

- [MEMORY-DEVICE-CONTRACT-MISSING]:
```
