# Change Context

## Architecture Inputs

| ID | Source | Constraint |
|---|---|---|
| ARCH-001 | aisee/docs/architecture/auth-architecture.md#ARCH-001 | Backend auth service owns session creation |
| DEC-001 | aisee/docs/architecture/auth-architecture.md#DEC-001 | Browser client does not persist one-time codes |

## Handoff

- API shape and errors go to `service-contract.md`.
- Verification token storage goes to `data-model.md`.
- Login page states go to `ui-contract.md`.
- Implementation and verification sequencing goes to `tasks.md`.
