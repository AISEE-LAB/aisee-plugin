---
title: "Auth Architecture"
doc_type: "architecture"
status: "active"
date: "2026-06-09"
scope: "auth"
owner: "Aisee"
source_refs:
  - "aisee/docs/requirements/auth-srs.md#FR-001"
  - "aisee/docs/ui-content/auth-ui.md#FLOW-001"
change_refs:
  - "openspec/changes/add-passwordless-login"
---

# Auth Architecture

## ARCH-001 Session Boundary

The backend auth service owns session creation and token issuance.

## DEC-001 Token Storage Decision

The browser client stores only issued session tokens. One-time codes are never persisted by the client.
