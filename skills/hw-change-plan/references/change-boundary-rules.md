# Hardware Change Boundary Rules

## Good Change Boundaries

A good hardware OpenSpec change should:
- deliver one independently verifiable capability or prerequisite contract
- keep the project buildable or at least not break existing build paths
- have clear FR/HW/FW/RT/VER traceability
- have explicit out-of-scope items
- be small enough to review and verify

## Prefer Vertical Hardware Slices

Prefer slices such as:
- ADC + DMA sampling path with verification
- display shell with known interface resources
- PGA/AGC control loop with safety behavior
- signal preprocessing with resource budget
- frequency detection with test vectors

Avoid pure horizontal slices unless they are prerequisite contracts:
- “all headers first”
- “all drivers first”
- “all algorithms later”

## Prerequisite Changes

Allowed prerequisite changes:
- create/import base project and build path
- freeze hardware resource contract
- establish clock/memory/device contracts
- create shared data model/interfaces needed by later independent changes

Do not create broad setup changes without a concrete handoff.

## Risk Strategy

Use a spike when:
- hardware feasibility is uncertain
- library resource cost is unknown
- algorithm accuracy or timing is unproven
- toolchain/build behavior is risky

Spike output must be a decision and evidence, not production implementation.

## Dependency Rules

A dependency exists only when one change must be completed before another can be implemented or verified safely.
Do not mark dependency just because two changes are conceptually related.