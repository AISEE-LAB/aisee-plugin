# Design: {{change-name}}

## 上下文

- 来源：proposal.md、source-map.md、specs
- 上游 hw:srs：
- 上游 hw:architecture：
- 上游 hw:change-plan：
- 当前硬件 / 软件 / 外部系统事实：
- 工具链 / SDK / BSP / OS / cloud / production 约束：
- 相关既有模块：

## 系统边界

| 边界 | 内容 | 本 change 是否涉及 | 说明 |
|---|---|---|---|
| 硬件 / 板级 | MCU / SoC / FPGA / module / sensor / actuator / gateway / host adapter | yes / no | |
| 固件 / 设备软件 | bare-metal / RTOS / bootloader / kernel driver / user-space service / host tool / production tool | yes / no | |
| 运行环境 | scheduler / OS / rootfs / process / filesystem / memory / power / timing | yes / no | |
| 连接 / 外部系统 | cloud / APP / gateway / protocol / bus / IPC / file exchange | yes / no | |
| 安全 | identity / key / cert / secure boot / debug lock / access control / privacy | yes / no | |
| 生产 | factory programming / fixture / calibration / serial / traceability | yes / no | |
| 运维 | update / rollback / logs / diagnostics / field support / compatibility | yes / no | |

## 总体方案

- 平台边界：MCU / RTOS / bare-metal / embedded Linux / Linux kernel / Linux user-space / bootloader / host tool / production tool
- 分层设计：hardware / BSP / HAL / driver / service / application / connectivity / security / production / operations
- 硬件抽象策略：
- 数据流：
- 控制流：
- 状态机 / 生命周期：
- 通信与协议：
- 错误处理与恢复：
- 安全 / 保护策略：
- 升级 / 回滚 / 兼容策略：

## 全局架构约束引用

| 约束来源 | 约束内容 | 对本 change 的影响 | 是否满足 |
|---|---|---|---|
| aisee/docs/architecture/... | | | 是 / 否 |
| docs/project-structure.md | | | 是 / 否 / N/A |
| docs/clock-contract.md | | | 是 / 否 / N/A |
| docs/memory-device-contract.md | | | 是 / 否 / N/A |
| external contract / protocol / security / production spec | | | 是 / 否 / N/A |

## 资源与工程影响

| 项 | 预计影响 | 预算 / 边界 | 证据 | 处理规则 |
|---|---|---|---|---|
| Flash / ROM / image / package | | | map / size / estimate | |
| RAM / .bss / heap / stack / process memory | | | map / runtime monitor / estimate | |
| CPU / latency / event rate / data rate | | | timing / estimate / profiler | |
| Storage / filesystem / partition | | | layout / df / image | |
| Network / bus / IPC throughput | | | measurement / estimate | |
| Power / thermal | | | measurement / estimate | |
| Project structure / files | | | path list | |
| Startup / linker / deployment config | | | config review | |

## 关键决策

| 决策 | 选择 | 原因 | 影响 | 来源 |
|---|---|---|---|---|
| | | | | proposal / source-map / specs / architecture / datasheet / protocol / code |

## Contract 适用性确认

| Contract | 适用性 | 依据 |
|---|---|---|
| hardware-contract.md | 适用 / N/A | |
| firmware-contract.md | 适用 / N/A | |
| runtime-contract.md | 适用 / N/A | |
| connectivity-contract.md | 适用 / N/A | |
| security-contract.md | 适用 / N/A | |
| production-contract.md | 适用 / N/A | |
| operations-contract.md | 适用 / N/A | |
| verification-contract.md | 适用 | verification-contract.md 默认适用 |

## 风险与取舍

| 风险 | 影响 | 缓解 | 是否阻塞 |
|---|---|---|---|
| | | | 是 / 否 |

## Open Questions

| 编号 | 问题 | 影响 artifact | 是否阻塞 |
|---|---|---|---|
| Q-001 | | | 是 / 否 |