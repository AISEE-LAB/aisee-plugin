# Hardware SRS Question Bank

Use this question bank selectively. Do not ask every question. Each round is a topic, not a single exchange.

Rules:
- Ask at most 3 questions per message.
- A topic may have multiple follow-ups.
- Stop a topic when it is clear enough, explicitly assumed, or marked open.
- Ask at most 3 follow-up messages for the same topic.
- Hardware/platform choices may force earlier requirements to be adjusted; record those adjustments.

## Round 1 - Project Boundary

- Is this a new product, prototype, validation board, retrofit, or production project?
- Who will operate or use it?
- What physical object is being measured, controlled, displayed, powered, or communicated with?
- Is this a standalone device, a module in a larger system, or a replacement for an existing design?

Exit when the system boundary and project stage are clear enough.

## Round 2 - Use Scenarios

- What is the normal operating scenario?
- What startup, shutdown, calibration, or maintenance actions are expected?
- What failure or edge cases must be handled?
- What will the user see or observe as success/failure?

## Round 3 - Key Functional Requirements

- What must the device/system do?
- Which functions are mandatory for the first version?
- Which functions can be deferred?
- Are there existing behaviors or compatibility constraints?

## Round 4 - Performance And Measurement Targets

- What accuracy, bandwidth, sample rate, latency, throughput, control period, or response time is required?
- What range must be covered?
- What is the minimum acceptable result if the ideal target is too expensive or too hard?
- What evidence will prove that the target is met?

## Round 5 - Constraints

- What is the target cost or BOM limit?
- What limits exist for board size, power, heat, enclosure, connectors, or environment?
- What delivery schedule or development difficulty is acceptable?
- Are there procurement, inventory, certification, or manufacturing constraints?

## Round 6 - Candidate Hardware / Platform

- Does the user already prefer a chip, board, platform, sensor, actuator, or toolchain?
- Is there existing stock or a previous project to reuse?
- Is Keil/IAR/CubeMX/vendor SDK/GCC/CMake/Linux/FPGA tooling required or optional?
- Is a lower-cost platform preferred even if requirements need to be reduced?

## Round 7 - Hardware Fit Collision

Use when requirements and hardware capability do not obviously match.

- Which requirement is exceeding the candidate hardware/platform capability?
- Can the requirement be relaxed? If yes, what is the lowest acceptable target?
- Should the hardware be upgraded instead? What cost or complexity increase is acceptable?
- Can delivery be phased: minimal version first, improved version later?
- What risk is acceptable to keep for prototyping?

## Round 8 - Verification And Acceptance

- What tests or measurements are required before the requirement is considered done?
- Does acceptance require lab equipment, field tests, long-run tests, compliance tests, or user observation?
- What logs, screenshots, waveforms, map files, or measurements should be saved as evidence?

## Topic Exit Labels

Use these labels in the final document:
- `[ASSUMPTION]`: reasonable inference accepted for now.
- `[OPEN]`: user has not decided and it affects later work.
- `[FIT-DATA-MISSING]`: hardware/platform judgment lacks data.
- `[RISK]`: known implementation, hardware, schedule, or validation risk.
