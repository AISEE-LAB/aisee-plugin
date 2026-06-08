---
id: cli-json-output-stability
title: Keep public CLI JSON stable
status: active
applies_to:
  phase: [implementation, review]
  surface: [cli]
trigger: "Changing a public JSON command, issue code, or machine-readable field."
recommended_action: "Preserve existing fields where possible, add tests for new fields, and document deprecation when a field changes meaning."
boundaries: "Does not apply to internal caches or explicitly experimental debug output."
---

Public CLI JSON is consumed by agents and automation. Additive changes are preferred; breaking changes require a migration note and contract tests.
