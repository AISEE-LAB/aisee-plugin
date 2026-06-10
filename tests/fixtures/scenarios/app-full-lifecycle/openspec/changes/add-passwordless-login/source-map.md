# Source Map

## Upstream Sources

| Source | Path / Description | Ref | Status | Notes |
|---|---|---|---|---|
| SRS | aisee/docs/requirements/auth-srs.md | aisee/docs/requirements/auth-srs.md#FR-001 | confirmed | Passwordless login |
| UI Content | aisee/docs/ui-content/auth-ui.md | aisee/docs/ui-content/auth-ui.md#PAGE-001, aisee/docs/ui-content/auth-ui.md#FLOW-001, aisee/docs/ui-content/auth-ui.md#STATE-001 | confirmed | Login page and states |
| Architecture | aisee/docs/architecture/auth-architecture.md | aisee/docs/architecture/auth-architecture.md#ARCH-001, aisee/docs/architecture/auth-architecture.md#DEC-001 | confirmed | Session boundary |

## Source Context

| Type | Ref | Title | Source | Handling | Artifact |
|---|---|---|---|---|---|
| FR | aisee/docs/requirements/auth-srs.md#FR-001 | Passwordless login | SRS | cover | specs/auth.md |
| PAGE | aisee/docs/ui-content/auth-ui.md#PAGE-001 | Login page | UI Content | change | ui-contract.md |
| FLOW | aisee/docs/ui-content/auth-ui.md#FLOW-001 | Request and verify code | UI Content | change | ui-contract.md |
| STATE | aisee/docs/ui-content/auth-ui.md#STATE-001 | Code sent state | UI Content | change | ui-contract.md |
| ARCH | aisee/docs/architecture/auth-architecture.md#ARCH-001 | Session boundary | Architecture | inherit | change-context.md |
| DEC | aisee/docs/architecture/auth-architecture.md#DEC-001 | Token storage decision | Architecture | inherit | change-context.md |
| SPEC | SPEC-001 | Passwordless login behavior | This change | produce | specs/auth.md |
| API | API-001 | Passwordless login API | This change | produce | service-contract.md |
| DATA | DATA-001 | Login verification token | This change | produce | data-model.md |
| TASK | TASK-001 | Implement passwordless login | This change | produce | tasks.md |
| TEST | TEST-001 | Passwordless login tests | This change | produce | tasks.md |

## Artifact Applicability

| Artifact | Required | Refs | Reason | Handoff |
|---|---|---|---|---|
| change-context.md | yes | aisee/docs/architecture/auth-architecture.md#ARCH-001, aisee/docs/architecture/auth-architecture.md#DEC-001 | Architecture decisions affect implementation | service-contract.md, data-model.md |
| ui-contract.md | yes | aisee/docs/ui-content/auth-ui.md#PAGE-001, aisee/docs/ui-content/auth-ui.md#FLOW-001, aisee/docs/ui-content/auth-ui.md#STATE-001 | Login page content changes | service-contract.md |
| service-contract.md | yes | API-001 | Frontend and backend are separate projects | tasks.md |
| data-model.md | yes | DATA-001 | One-time code verification needs persistence | service-contract.md, tasks.md |

## Contract Ownership / Sync

| Key | Value | Status | Notes |
|---|---|---|---|
| contract_owner | backend | confirmed | Backend owns API behavior |
| canonical_source | service-contract.md | confirmed | Human-readable contract for this change |
| provider_repo | backend-api | confirmed | Provider implementation |
| consumer_repo | frontend-app | confirmed | Consumer integration |
| sync_mode | local-http | confirmed | Use project-local OpenSpec artifacts and context pack when a summary is needed |
| machine_readable_contract | contracts/openapi.yaml | confirmed | Optional OpenAPI artifact |
| version_ref | change:add-passwordless-login | confirmed | Replace with tag or commit when released |

## Implementation Paths

| Kind | Path | Refs | Mode | Notes |
|---|---|---|---|---|
| code | src/auth/passwordless.py | API-001, DATA-001 | add | Provider implementation |
| code | app/login/page.tsx | PAGE-001, FLOW-001, STATE-001 | modify | Consumer integration |
| test | tests/auth/test_passwordless.py | TEST-001 | add | Provider and contract tests |
| test | tests/ui/test_login_flow.ts | TEST-001 | add | Consumer flow test |
| contract | contracts/openapi.yaml | API-001 | add | Optional machine-readable contract |

## Verification Evidence

| Path / Command | Refs | Status | Notes |
|---|---|---|---|
| docs/verification/add-passwordless-login-openspec-validate.md | TEST-001 | passed | `openspec validate` evidence |
| docs/verification/add-passwordless-login-tests.md | TEST-001 | passed | Automated test evidence |
| docs/reviews/add-passwordless-login-code-review.md | TEST-001 | passed | Code review evidence |

## Out of Scope

- Social login.
- Registration.
- Admin user management.
