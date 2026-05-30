# aisee:change-plan — Source-map Seed 规则

每个 planned change 必须包含 source-map seed。seed 不是最终 artifact 内容，只是后续 `source-map.md` 和 schema artifacts 的初始追踪线索。

## 通用规则

- FR / NFR / RULE / FLOW / STATE 必须引用 SRS 中的完整 ID；没有 ID 时标注 `[SOURCE-ID-MISSING]` 或 `[ID-RESERVATION-REQUIRED]`。
- PAGE / FLOW / STATE 必须来自 UI Content；没有 UI 时写 `N/A`，不要硬造页面。
- Architecture 相关来源只引用 `ARCH / DEC / CONSTRAINT / RISK` 完整 ID，不复制整段架构说明。
- `aisee:change-plan` 不分配上游 ID，不临时发明正式 ID。
- SPEC / API / DATA / TASK / TEST 是 change-author 阶段产出，seed 中写 `TBD in <artifact>`。
- artifact 适用性要写 yes/no 和原因，不能只写 yes/no。
- 不要在 seed 中写最终 API endpoint、数据库字段、引脚表、寄存器表或实现任务。

## App / Software Schema Seed

适用于 `aisee-app-spec-driven`：

| 字段 | 填写规则 |
|------|----------|
| FR / NFR / RULE | SRS 中的完整 ID |
| PAGE / FLOW / STATE | UI Content 中的完整 ID，或 `N/A` |
| ARCH / DEC / CONSTRAINT / RISK | Architecture 中的完整 ID，或 `N/A` |
| SPEC | `TBD in change-author` |
| API | `TBD in service-contract` |
| DATA | `TBD in data-model` |
| TASK / TEST | `TBD in tasks` |

必须判断以下 artifact 是否适用：

- `change-context.md`
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
