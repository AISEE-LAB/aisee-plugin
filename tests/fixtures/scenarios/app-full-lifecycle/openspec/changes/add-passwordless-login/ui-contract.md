# UI Contract

状态：适用

## 页面与入口

| ID | Surface | Change |
|---|---|---|
| auth:PAGE-001 | Login page | Add passwordless code request and verification states |

## Flow And State

| ID | Description | Trigger | Next State |
|---|---|---|---|
| auth:FLOW-001 | Request code then verify code | User submits email | `auth:STATE-001` |
| auth:STATE-001 | Code sent state | Code request succeeds | Show code input, resend timer, and error feedback |

## Frontend Data Needs

| Need | Source |
|---|---|
| Code request result | `auth:API-001` |
| Verification result | `auth:API-001` |
| Session token | `auth:API-001` |
