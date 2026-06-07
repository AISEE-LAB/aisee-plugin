# Proposal

## Background

Current users sign in with password credentials. Add passwordless login so existing users can request a one-time code and exchange it for a session token.

## Scope

- Cover `auth:FR-001`.
- Add `auth:API-001`.
- Update UI state for `auth:PAGE-001`, `auth:FLOW-001`, and `auth:STATE-001`.
- Add token persistence contract `auth:DATA-001`.

## Out of Scope

- Social login.
- Registration.
- Admin user management.

## Success Criteria

- Specs, contracts, tasks, ID trace, implementation paths, and evidence are all connected through `source-map.md`.
