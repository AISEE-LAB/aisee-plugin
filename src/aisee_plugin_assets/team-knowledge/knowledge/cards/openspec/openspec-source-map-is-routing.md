---
id: openspec-source-map-is-routing
title: Source map 只能作为路由表
status: active
applies_to:
  stacks: []
  frameworks: []
  phases:
    - implementation
    - review
    - verify
  schemas:
    - aisee-app-spec-driven
    - aisee-device-spec-driven
  surfaces:
    - openspec
    - source-map
trigger:
  - 需要从 OpenSpec change 推导实现路径或测试路径
recommended_action:
  - 只把 source-map 用作 ID、artifact、路径和 evidence 路由，不把它当成需求正文
boundaries:
  - 不适用于当前 schema 不生成 source-map 的 quick-fix、quick-research 或 docsite change
risk_types:
  - traceability
tags:
  - openspec
  - source-map
---

## Guardrail

Source map 的职责是保持路由和追踪闭合。需求、契约、任务和归档判断仍以对应 OpenSpec artifacts 为准。

