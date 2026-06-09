# UI Contract

状态：适用

本文只描述页面内容结构、状态、操作、权限可见性和前端数据需求；视觉规范、组件库、配色、排版和像素级布局仍以 design spec / design assets 为事实源。

## 页面与入口

| ID | Surface | Change |
|---|---|---|
| PAGE-001 | Login page | Add passwordless code request and verification states |

## Flow And State

| ID | Description | Trigger | Next State |
|---|---|---|---|
| FLOW-001 | Request code then verify code | User submits email | `STATE-001` |
| STATE-001 | Code sent state | Code request succeeds | Show code input, resend timer, and error feedback |

## Operations

- Request login code.
- Submit login code.
- Resend login code after cooldown.
- Return to email entry.

## Frontend Data Needs

| Need | Source |
|---|---|
| Whether code request succeeded | `API-001` |
| Verification errors and retry state | `API-001` |
| Session token after successful verification | `API-001` |
