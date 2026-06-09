---
title: "Auth UI Content"
doc_type: "ui-content"
status: "active"
date: "2026-06-09"
scope: "auth"
owner: "Aisee"
source_refs:
  - "aisee/docs/requirements/auth-srs.md#FR-001"
change_refs:
  - "openspec/changes/add-passwordless-login"
anchors:
  - "aisee/docs/ui-content/auth-ui.md#PAGE-001"
  - "aisee/docs/ui-content/auth-ui.md#FLOW-001"
  - "aisee/docs/ui-content/auth-ui.md#STATE-001"
---

# Auth UI Content

## Login Page PAGE-001

- Email input.
- Request code action.
- Code input after request success.
- Resend timer.
- Error feedback for invalid or expired code.

## Flow FLOW-001

Email entry -> code sent -> verification -> authenticated session.

## State STATE-001

The page shows a code input, resend timer, and return-to-email action after a code is sent.
