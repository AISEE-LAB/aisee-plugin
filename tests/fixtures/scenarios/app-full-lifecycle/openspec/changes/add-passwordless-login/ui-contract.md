# UI Contract

状态：适用

## 页面与入口

| ID | Surface | Change |
|---|---|---|
| PAGE-001 | Login page | Add passwordless code request and verification states |

## Flow And State

| ID | Description | Trigger | Next State |
|---|---|---|---|
| FLOW-001 | Request code then verify code | User submits email | `STATE-001` |
| STATE-001 | Code sent state | Code request succeeds | Show code input, resend timer, and error feedback |

## Frontend Data Needs

| Need | Source |
|---|---|
| Code request result | `API-001` |
| Verification result | `API-001` |
| Session token | `API-001` |
