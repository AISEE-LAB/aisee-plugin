---
id: openspec-source-map-is-routing
title: source-map 只承载路由与归属信息
status: active
applies_to:
  stacks: []
  frameworks: []
  phases: [planning, implementation, review]
  schemas: [aisee-app-spec-driven, aisee-device-spec-driven]
  surfaces: [openspec, source-map]
trigger:
  - 修改 source-map.md、implementation references、contracts 或 ownership metadata
recommended_action:
  - 在 source-map.md 中记录 routing 和 ownership
  - 规范性要求继续放在 specs、tasks 和 contracts
boundaries:
  - 不要把 source-map.md 当作 requirements、tasks 或 contract content 的替代品
tags: [openspec, source-map]
---

`source-map.md` helps agents route work and review ownership. It should not become a parallel specification source.
