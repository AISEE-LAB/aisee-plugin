# aisee:change-plan — Source-map Seed 规则

每个 planned change 必须包含 source-map seed。seed 不是最终 artifact 内容，只是后续 `source-map.md` 和 schema artifacts 的初始追踪线索。

## 通用规则

- FR 必须引用 SRS 或 proposal 中的需求 ID；没有 ID 时写 `TBD in proposal/specs`。
- PAGE / FLOW 必须来自 UI Content；没有 UI 时写 `N/A`，不要硬造页面。
- Design 相关来源只引用 design-spec 中的规则、pattern 或 token ID；没有 ID 时写 `TBD in ui-contract`。
- Architecture 相关来源只引用架构决策、共享前置或阻塞标签，不复制整段架构说明。
- artifact 适用性要写 yes/no 和原因，不能只写 yes/no。
- 不要在 seed 中写最终 API endpoint、数据库字段、引脚表、寄存器表或实现任务。

## App / Software Schema Seed

适用于 `aisee-app-spec-driven`：

| 字段 | 填写规则 |
|------|----------|
| FR | SRS / proposal 中的 FR ID |
| PAGE | UI Content 中的 PAGE ID，或 `N/A` |
| FLOW | UI Content 中的 FLOW ID，或 `N/A` |
| DS | design-spec 中的设计规则 / pattern / token ID，或 `TBD in ui-contract` |
| API | 预期服务能力 ID，或 `TBD in service-contract` |
| DATA | 预期数据能力 ID，或 `TBD in data-model` |

必须判断以下 artifact 是否适用：

- `ui-contract.md`
- `data-model.md`
- `service-contract.md`

## Device Schema Seed

适用于 `aisee-device-spec-driven`：

| 字段 | 填写规则 |
|------|----------|
| FR | SRS / proposal 中的 FR ID |
| HW | 预期硬件能力 ID，或 `TBD in hardware-contract` |
| FW | 预期固件能力 ID，或 `TBD in firmware-contract` |
| RT | 预期运行时能力 ID，或 `TBD in runtime-contract` |
| VER | 预期验证能力 ID，或 `TBD in verification-contract` |

必须判断以下 artifact 是否适用：

- `hardware-contract.md`
- `firmware-contract.md`
- `runtime-contract.md`
- `verification-contract.md`

## Hybrid Schema Seed

混合系统需要同时判断软件侧和设备侧 seed。不要为了简化而把云端、App、设备、固件全部塞进同一个 change；除非它们构成一个小而完整、可独立验证的纵向切片。
