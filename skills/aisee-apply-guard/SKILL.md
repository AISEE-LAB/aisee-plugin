---
name: aisee:apply-guard
description: OpenSpec apply 前的轻量门禁。用于判断当前 change 是否已经满足 apply 条件：validate 通过、tasks 完成、spec/source-map 同步、CE P0/P1 review 处理、verification 记录满足 domain/schema 要求。它不重新做 review、不重新跑完整测试、不替代 openspec apply。
---

# aisee:apply-guard

`aisee:apply-guard` 是 apply 前的放行判断，不是深度验证器。

## 职责

- 读取已有 validate、verify、review、test、verification 结果。
- 判断是否可以执行 `openspec apply`。
- 输出可以 apply / 暂不建议 apply / 有风险但可接受。

## 不负责

- 重新规划 change。
- 重新做代码 review。
- 重新跑完整测试。
- 修改 baseline spec。

## 输出

```md
# Apply Guard

## Decision

## Evidence

## Blocking Items

## Accepted Risks
```
