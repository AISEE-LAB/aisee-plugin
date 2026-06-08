# Hardware SRS + Platform Fit Template

```markdown
# <Project Name> Hardware SRS And Platform Fit

**Document ID**: HW-SRS-<YYYY-MM-DD>-<slug>
**Version**: v1.0
**Status**: Draft / Confirmed
**Created**: <date>

## 1. Background And Scope

- Problem:
- Goal:
- Users / operators:
- Operating environment:
- Project stage: prototype / validation board / product / retrofit / production:
- In scope:
- Out of scope:

## 2. Confirmed Requirements

### 2.1 Functional Requirements

| FR ID | Requirement | Priority | Acceptance Criteria | Source | Change Type |
|---|---|---:|---|---|---|
| FR-001 |  | P0 / P1 / P2 |  | user / baseline / inferred | new / modified / compatible / removed |

### 2.2 Non-Functional Requirements

| NFR ID | Category | Requirement | Acceptance Criteria | Source |
|---|---|---|---|---|
| NFR-001 | cost / size / power / latency / reliability / maintainability / compliance |  |  |  |

## 3. Requirement Flexibility

| Requirement / Constraint | Fixed / Adjustable | Adjustment Range | Impact If Changed | User Decision |
|---|---|---|---|---|
|  |  |  |  |  |

## 4. Operating Scenarios

| Scenario ID | Scenario | Preconditions | Main Flow | Failure / Edge Cases | Related FR |
|---|---|---|---|---|---|
| SC-001 |  |  |  |  | FR-001 |

## 5. Hardware / Platform Fit

### 5.1 Project Type Classification

Applicable domains:
- MCU bare-metal / RTOS:
- Embedded Linux:
- FPGA / high-speed digital:
- Analog / sensor front-end:
- Power / actuator:
- Communication / gateway:
- HMI / display:
- Low power / battery:
- Edge AI / audio / vision:
- Safety / compliance:

### 5.2 Key Requirement Metrics

| Metric | Value / Range | Fixed / Adjustable | Evidence | Related FR/NFR |
|---|---|---|---|---|
|  |  |  |  |  |

### 5.3 Candidate Matrix

| Candidate | Meets | Gaps | Cost / Supply | Toolchain / Debug | Risk | Decision |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  | selected / rejected / pending |

### 5.4 Requirement-Hardware Negotiation

| Gap | Relax Requirement | Change Hardware | Phase Delivery | User Decision |
|---|---|---|---|---|
|  |  |  |  |  |

### 5.5 Final Hardware Direction

- Selected / preferred platform:
- Confirmed by user: yes / no
- Accepted tradeoffs:
- Rejected alternatives:
- Follow-up checks for `hw:architecture`:
- Follow-up checks for `hw:init ingest-existing`:

## 6. Verification Expectations

| FR/NFR ID | Verification Method | Required Evidence |
|---|---|---|
| FR-001 | inspection / measurement / unit test / integration test / field test |  |

## 7. Architecture Input Hints

| Topic | Required Decision In `hw:architecture` | Related FR/NFR |
|---|---|---|
| hardware resources / module boundary / timing / memory / algorithm / safety |  |  |

## 8. Change Candidate List

> `hw:change-plan` uses this table as the primary input. Keep FR IDs stable.

| Priority | FR ID | Title | Candidate Change Area | Estimated Size | Dependencies | Notes |
|---|---|---|---|---|---|---|
| P0 | FR-001 |  |  | S / M / L | none |  |

## 9. Assumptions, Open Questions, And Missing Data

- [ASSUMPTION]:
- [OPEN]:
- [FIT-DATA-MISSING]:
- [SPEC-GAP]:

## 10. Change Log

| Date | Change | Reason |
|---|---|---|
|  |  |  |
```