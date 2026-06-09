# Proposal

## Background

Current users sign in with password credentials. Add passwordless login so existing users can request a one-time code and exchange it for a session token.

## Scope

- Cover `aisee/docs/requirements/auth-srs.md#FR-001`.
- Add `API-001`.
- Update UI state for `PAGE-001`, `FLOW-001`, and `STATE-001`.
- Add token persistence contract `DATA-001`.

## Out of Scope

- Social login.
- Registration.
- Admin user management.

## Success Criteria

- Specs, contracts, tasks, ID trace, implementation paths, and evidence are all connected through `source-map.md`.
