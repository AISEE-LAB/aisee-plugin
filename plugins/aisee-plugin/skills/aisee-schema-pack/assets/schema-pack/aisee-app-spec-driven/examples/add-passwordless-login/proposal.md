# Proposal

## Background

Current users sign in with password credentials. The product needs a passwordless login path so mobile and web clients can request a one-time code and exchange it for a session token.

## Scope

- Add passwordless login request and verification behavior for `auth:FR-001`.
- Add the service capability `auth:API-001`.
- Add the login UI state contract for `auth:PAGE-001`, `auth:FLOW-001`, and `auth:STATE-001`.
- Add the verification token data contract `auth:DATA-001`.

## Out of Scope

- Social login providers.
- Account registration.
- Administrative user management.

## Success Criteria

- The request-code and verify-code flows are covered by specs.
- UI, service, and data contracts are traceable through `source-map.md`.
- Provider, consumer, mock/client, contract test, and backward compatibility tasks are explicit in `tasks.md`.
