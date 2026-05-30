---
name: aisee:change-author
description: 将 aisee:change-plan 的结果转成 OpenSpec change artifacts 初稿。用于单个已确认 change 的 proposal、design、spec、tasks、source-map、ui/service/data contract 或 hardware/firmware/runtime/verification contract 编排。它不拆 change 边界、不写代码、不替代 aisee:change-design 的 design.md 专项规则。
---

# aisee:change-author

`aisee:change-author` 是 OpenSpec change 产物编排器。

## 职责

- 读取 change-plan、SRS、UI/device context、architecture 和项目事实。
- 识别当前 schema 需要哪些 artifacts。
- 为单个 OpenSpec change 创建或补齐 artifacts 初稿。
- 通过 ID 和 `source-map.md` 串联上游产物、spec、tasks、代码路径和验证。
- 对 `design.md` 调用或复用 `aisee:change-design` 规则。

## 不负责

- 拆 change 边界。
- 为多个 change 规划 schema。
- 写代码。
- 让 `ce-plan` 生成长期任务清单。

## Author 子阶段

```text
design.md -> aisee:change-design
ui-contract.md / service-contract.md / data-model.md -> app domain author
hardware-contract.md / firmware-contract.md / runtime-contract.md / verification-contract.md -> device domain author
source-map.md -> ID trace + sources + OpenSpec artifacts
```
