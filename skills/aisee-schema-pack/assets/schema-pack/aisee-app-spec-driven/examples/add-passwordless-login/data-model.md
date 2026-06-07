# Data Model

状态：适用

## Entities

| ID | Entity | Change |
|---|---|---|
| auth:DATA-001 | login_verification_tokens | New table or collection for one-time login code verification |

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| id | string | yes | Request id returned to client |
| user_id | string | yes | Existing user |
| code_hash | string | yes | Never store raw code |
| expires_at | datetime | yes | Short-lived expiry |
| consumed_at | datetime | no | Set after successful verification |
| created_at | datetime | yes | Audit timestamp |

## Constraints

- Token must be single use.
- Expired tokens cannot create sessions.
- Raw codes must not be persisted.
