# Auth Spec Delta

## ADDED Requirements

### Requirement: auth:SPEC-001 Passwordless login

The system MUST allow an existing user to request a one-time login code and exchange a valid code for an authenticated session.

#### Scenario: Request login code

- Given a known user enters a valid email address
- When the user requests a login code
- Then the system sends a one-time code
- And the login page enters `auth:STATE-001`

#### Scenario: Verify login code

- Given a user has a valid unexpired one-time code
- When the user submits the code
- Then the system returns an authenticated session
- And the user can continue from the originally requested page
