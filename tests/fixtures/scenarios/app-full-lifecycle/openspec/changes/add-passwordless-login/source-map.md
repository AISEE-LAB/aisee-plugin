# Source Map

## Upstream Sources

| Source | Path / Description | Source ID | Status | Notes |
|---|---|---|---|---|
| SRS | aisee/docs/requirements/auth-srs.md | auth:FR-001 | confirmed | Passwordless login |
| UI Content | aisee/docs/ui-content/auth-ui.md | auth:PAGE-001, auth:FLOW-001, auth:STATE-001 | confirmed | Login page and states |
| Architecture | aisee/docs/architecture/auth-architecture.md | auth:ARCH-001, auth:DEC-001 | confirmed | Session boundary |

## ID Trace

| Type | ID | Title | Source | Handling | Artifact |
|---|---|---|---|---|---|
| FR | auth:FR-001 | Passwordless login | SRS | cover | specs/auth.md |
| PAGE | auth:PAGE-001 | Login page | UI Content | change | ui-contract.md |
| FLOW | auth:FLOW-001 | Request and verify code | UI Content | change | ui-contract.md |
| STATE | auth:STATE-001 | Code sent state | UI Content | change | ui-contract.md |
| ARCH | auth:ARCH-001 | Session boundary | Architecture | inherit | change-context.md |
| DEC | auth:DEC-001 | Token storage decision | Architecture | inherit | change-context.md |
| SPEC | auth:SPEC-001 | Passwordless login behavior | This change | produce | specs/auth.md |
| API | auth:API-001 | Passwordless login API | This change | produce | service-contract.md |
| DATA | auth:DATA-001 | Login verification token | This change | produce | data-model.md |
| TASK | auth:TASK-001 | Implement passwordless login | This change | produce | tasks.md |
| TEST | auth:TEST-001 | Passwordless login tests | This change | produce | tasks.md |

## Artifact Applicability

| Artifact | Required | IDs | Reason | Handoff |
|---|---|---|---|---|
| change-context.md | yes | auth:ARCH-001, auth:DEC-001 | Architecture decisions affect implementation | service-contract.md, data-model.md |
| ui-contract.md | yes | auth:PAGE-001, auth:FLOW-001, auth:STATE-001 | Login page content changes | service-contract.md |
| service-contract.md | yes | auth:API-001 | Frontend and backend are separate projects | tasks.md |
| data-model.md | yes | auth:DATA-001 | One-time code verification needs persistence | service-contract.md, tasks.md |

## Contract Ownership / Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | Backend owns API behavior |
| canonical_source | service-contract.md | confirmed | Human-readable contract for this change |
| provider_repo | backend-api | confirmed | Provider implementation |
| consumer_repo | frontend-app | confirmed | Consumer integration |
| sync_mode | local-http | confirmed | `aisee contract serve` can expose this change |
| machine_readable_contract | contracts/openapi.yaml | confirmed | Optional OpenAPI artifact |
| version_ref | change:add-passwordless-login | confirmed | Replace with tag or commit when released |

## Implementation Paths

| Kind | Path | IDs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/passwordless.py | auth:API-001, auth:DATA-001 | add | Provider implementation |
| code | app/login/page.tsx | auth:PAGE-001, auth:FLOW-001, auth:STATE-001 | modify | Consumer integration |
| test | tests/auth/test_passwordless.py | auth:TEST-001 | add | Provider and contract tests |
| test | tests/ui/test_login_flow.ts | auth:TEST-001 | add | Consumer flow test |
| contract | contracts/openapi.yaml | auth:API-001 | add | Optional machine-readable contract |

## Verification Evidence

| Path / Command | IDs | Status | Notes |
|---|---|---|---|
| docs/verification/add-passwordless-login-openspec-validate.md | auth:TEST-001 | passed | `openspec validate` evidence |
| docs/verification/add-passwordless-login-tests.md | auth:TEST-001 | passed | Automated test evidence |
| docs/reviews/add-passwordless-login-code-review.md | auth:TEST-001 | passed | Code review evidence |

## Out of Scope

- Social login.
- Registration.
- Admin user management.
