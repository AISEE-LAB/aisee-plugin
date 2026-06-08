---
id: cli-json-output-stability
title: CLI JSON 输出必须保持字段稳定
status: active
applies_to:
  stacks:
    - python
  frameworks: []
  phases:
    - implementation
    - verify
  schemas: []
  surfaces:
    - cli
    - json-output
trigger:
  - 新增或修改 public CLI command 的 JSON 输出
recommended_action:
  - 保持新增字段向后兼容，并补充 CLI contract test
boundaries:
  - 不适用于仅面向人类阅读的非 JSON 日志输出
risk_types:
  - public-contract
tags:
  - cli
  - json-output
---

## Guardrail

修改公开 CLI JSON 输出时，优先保持字段兼容，并用测试锁定 envelope、status、issues、summary 和 meta 字段。

