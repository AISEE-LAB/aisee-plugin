# Service Contract

状态：适用

## 契约归属与同步

| Field | Value |
|---|---|
| Owner | backend |
| Provider | backend-api |
| Consumer | frontend-app |
| Sync Mode | local-http |
| Machine-readable Contract | contracts/openapi.yaml |

## 能力契约

### auth:API-001 Request login code

- Method: `POST`
- Path: `/auth/passwordless/request`
- Request: email
- Response: request id, resend cooldown seconds
- Errors: unknown user, rate limited, invalid email

### auth:API-001 Verify login code

- Method: `POST`
- Path: `/auth/passwordless/verify`
- Request: request id, code
- Response: session token and user summary
- Errors: expired code, invalid code, already used code

## Compatibility

- Existing password login remains available.
- Consumers must handle old password login and new passwordless login during rollout.
