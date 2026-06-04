# Hardware Architecture Template

```markdown
# <Project Name> Hardware-Aware Architecture

**Document ID**: HW-ARCH-<YYYY-MM-DD>-<slug>
**Version**: v1.0
**Status**: Draft / Confirmed
**Created**: <date>

## 1. Inputs And Scope

| Input | Path / Source | Status | Notes |
|---|---|---|---|
| Hardware SRS | aisee/docs/requirements/...-hw-srs.md | confirmed / draft | |
| Project Structure | docs/project-structure.md | confirmed / missing / N/A | |
| Clock Contract | docs/clock-contract.md | confirmed / missing / N/A | |
| Memory / Device Contract | docs/memory-device-contract.md | confirmed / missing / N/A | |
| Schematics / Datasheets / SDK |  | confirmed / missing / N/A | |

- Architecture scope:
- Non-goals:

## 2. Platform And Operating Model

| Topic | Decision | Rationale | Source |
|---|---|---|---|
| Platform | MCU / RTOS / Linux / FPGA / hybrid | | |
| Target device / board | | | |
| Toolchain | Keil / IAR / GCC / CMake / vendor SDK / Yocto / Buildroot | | |
| Runtime model | bare-metal loop / ISR-driven / RTOS / Linux user-space / kernel | | |

## 3. Global Hardware Resource Architecture

### 3.1 Resource Allocation

| Resource ID | Resource | Owner Module | Mode / Function | Constraint | Change Rule |
|---|---|---|---|---|---|
| HW-001 | pin / peripheral / bus / DMA / IRQ / timer / ADC / SPI / I2C / UART | | | | frozen / change requires review |

### 3.2 Electrical / Protocol / Timing Constraints

| Interface | Direction | Electrical / Protocol / Timing Constraint | Related HW ID | Verification |
|---|---|---|---|---|
|  | input / output / bidirectional |  | HW-001 |  |

### 3.3 Circuit-To-Software Impact

| Hardware / Circuit Decision | Software / Algorithm Impact | Required Handling | Related FR |
|---|---|---|---|
|  |  |  | FR-001 |

## 4. Clock, Timing, And Runtime Constraints

| Clock / Timing Item | Value / Source | Affected Modules | Risk | Verification |
|---|---|---|---|---|
| SYSCLK / HCLK / PCLK / ADC / TIM / UART / SPI / I2C / RTOS tick |  |  |  |  |

## 5. Memory, Device, And Build Constraints

| Constraint | Value / Source | Affected Modules | Change Rule |
|---|---|---|---|
| Flash / RAM / heap / stack / map margin / startup / linker / scatter / device macro / flash algorithm |  |  |  |

## 6. Module Architecture

Module document mode:
- Module count:
- Module docs enabled: yes / no
- Module docs directory: `docs/modules/`

| Module ID | Module | Responsibility | Inputs | Outputs | Init Order | Failure Handling | Test Entry |
|---|---|---|---|---|---|---|---|
| FW-001 |  |  |  |  |  |  |  |

## 7. Data Flow, Control Flow, And State Machines

- Startup path:
- Normal path:
- Failure path:
- Reset / recovery path:
- Timing-sensitive path:

## 8. Algorithms, Drivers, Protocols, And Dependencies

| Item | Why Needed | Input / Output | Complexity / Resource Cost | Alternative Considered | Decision | Related Module |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## 9. Resource Budget

| Resource | Budget | Estimate | Margin | Evidence | Risk |
|---|---|---|---|---|---|
| Flash / storage |  |  |  |  |  |
| RAM / heap / stack |  |  |  |  |  |
| CPU / latency |  |  |  |  |  |
| Interrupt / DMA / task priority |  |  |  |  |  |
| Peripheral / IO / bus bandwidth |  |  |  |  |  |
| Power |  |  |  |  |  |

## 10. Architecture Rules

Rules that later OpenSpec changes must not silently violate:

| Rule ID | Rule | Applies To | Violation Handling |
|---|---|---|---|
| AR-001 |  | HW / FW / RT / VER | update architecture or reject change |

## 11. Verification Strategy

| Target | Method | Evidence | Pass Criteria | Related FR/HW/FW/RT |
|---|---|---|---|---|
|  | unit / integration / measurement / HIL / field / manual |  |  |  |

## 12. Change-Plan Hints

| Candidate Change Area | Related FR | Related HW | Related FW | Related RT | Related VER | Dependency Hint |
|---|---|---|---|---|---|---|
|  | FR-001 | HW-001 | FW-001 | RT-001 | VER-001 |  |

## 13. Risks, Fallbacks, And Open Questions

- [BUDGET-FAIL]:
- [ARCH-BLOCKER]:
- [PROJECT-FACT-MISSING]:
- [RISK]:
- Rejected option:
```