# Change Context

## Architecture Inputs

| ID | Source | Constraint |
|---|---|---|
| ARCH-001 | aisee/docs/architecture/auth-architecture.md#ARCH-001 | Session creation remains owned by backend auth service |
| DEC-001 | aisee/docs/architecture/auth-architecture.md#DEC-001 | Browser client stores only the issued session token, not verification codes |

## Local Decisions

- Verification codes are short lived and single use.
- The frontend never persists one-time codes after submission.
- Provider and consumer must stay aligned through `service-contract.md` and optional `contracts/openapi.yaml`.

## Handoff

- API shape and errors go to `service-contract.md`.
- Verification token storage goes to `data-model.md`.
- Login page states go to `ui-contract.md`.
- Implementation and verification sequencing goes to `tasks.md`.
