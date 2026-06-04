# aisee:architecture — Embedded Domain Blocks

用于 hardware / embedded / firmware / rtos / driver 技术域。只保留与当前需求相关的块，不要机械输出全部块。

```markdown
## 12. Domain Context Blocks（按需）

> 每块只写摘要级事实、约束、缺口和后续 artifact 提示；不写寄存器表、引脚表、时序表或固件实现步骤。

### 12.1 Hardware / Board Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 板卡 / MCU / SoC / FPGA / 电源 / 时钟 / 引脚 / 外设 / 总线 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.2 Firmware Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| 启动流程 / HAL / BSP / 内存布局 / 链接脚本 / 配置系统 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.3 RTOS / Runtime Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| RTOS / 任务模型 / 中断 / 优先级 / 同步机制 / 实时性约束 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.4 Driver / Peripheral Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| Driver / 外设 / 总线 / DMA / 中断 / 错误处理 / 设备抽象 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.5 Build / Flash / Debug Toolchain Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| CMake / Make / West / PlatformIO / 编译器 / 烧录 / JTAG / OpenOCD / J-Link | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |

### 12.6 Verification / Lab Context

| 项 | 当前事实 | 来源 | 对 change-plan 的影响 | 后续 artifact 提示 |
|----|----------|------|------------------------|--------------------|
| HIL / SIL / 仿真 / 实验室夹具 / 产测 / 校准 / 回归验证 | {fact or 未确认} | {source} | {impact} | {suggested artifact type} |
```
