---
id: cli-json-output-stability
title: CLI JSON 输出必须保持字段稳定
status: active
applies_to:
  stacks: [python]
  frameworks: []
  phases: [implementation, review, verify]
  schemas: []
  surfaces: [cli, json-output]
trigger:
  - 修改 public CLI JSON command、issue code 或 machine-readable field
recommended_action:
  - 优先保持新增字段向后兼容
  - 为字段变化补充 CLI contract test
  - 破坏性语义调整时补充迁移说明
boundaries:
  - 不适用于 internal cache
  - 不适用于明确标记为 experimental 的 debug 输出
tags: [cli, json-output]
---

Public CLI JSON is consumed by agents and automation. Additive changes are preferred; breaking changes require a migration note and contract tests.
