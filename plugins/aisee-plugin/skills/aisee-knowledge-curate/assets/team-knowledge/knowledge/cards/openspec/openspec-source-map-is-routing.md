---
id: openspec-source-map-is-routing
title: Keep source-map as routing metadata
status: active
applies_to:
  phase: [planning, implementation, review]
  surface: [openspec]
trigger: "Adding implementation references, contracts, or ownership metadata to an OpenSpec change."
recommended_action: "Record routing and ownership in source-map.md, while keeping normative requirements in specs and contracts."
boundaries: "Do not use source-map.md as a replacement for requirements, tasks, or contract content."
---

`source-map.md` helps agents route work and review ownership. It should not become a parallel specification source.
