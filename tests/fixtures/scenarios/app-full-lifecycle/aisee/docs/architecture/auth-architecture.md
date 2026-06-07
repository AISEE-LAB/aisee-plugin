# Auth Architecture

## auth:ARCH-001 Session Boundary

The backend auth service owns session creation and token issuance.

## auth:DEC-001 Token Storage Decision

The browser client stores only issued session tokens. One-time codes are never persisted by the client.
