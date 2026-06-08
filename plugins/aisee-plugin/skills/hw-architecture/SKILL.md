---
name: hw:architecture
description: 基于 hw:srs 和可选的 hw:init 工程事实，生成硬件感知的整体架构设计文档，统一确认全局接口、资源分配、时钟/时序、存储/型号、模块划分、算法路线、运行约束、验证策略和禁止偏离规则。用于在拆分 OpenSpec changes 前冻结硬件/固件/系统级约束，避免局部 change 合理但整体冲突。触发词包括“硬件架构”“整体设计”“系统设计”“全局约束”“资源分配”“接口和设计合并”“hw:architecture”。
---

# hw:architecture

生成硬件/嵌入式项目的整体架构文档。该文档是 OpenSpec 前置输入层，用于约束后续 `hw:change-plan` 和每个 `aisee-device-spec-driven` change。

本技能合并原 `hw:interfaces` 与 `hw:design` 的主职责：接口、资源、模块、算法、运行时和全局规则必须在同一份整体架构里统一判断。

## Inputs

必需：
- `aisee/docs/requirements/*-hw-srs.md`

可选但强烈建议：
- `docs/project-structure.md`
- `docs/clock-contract.md`
- `docs/memory-device-contract.md`
- 原理图、PCB、器件手册、旧项目接口表、Linux dts、协议文档
- 已有工程源码、map、启动文件、linker/scatter、工程宏

可选参数：
- `--mode standard|deep|review`，默认 `standard`
- `--focus interfaces|modules|algorithm|resources|all`，默认 `all`

## References

需要接口和资源检查时读取：

`references/architecture-checklist.md`

生成文档时读取：

`assets/architecture-template.md`

模块数量 `>=5` 时读取：

`assets/module-architecture-template.md`

## Output

保存到：

`aisee/docs/architecture/<YYYY-MM-DD>-<slug>-hw-architecture.md`

模块数量 `>=5` 时还必须生成：

`docs/modules/<module-name>.md`

必须包含：
- SRS 和工程事实来源
- 项目类型与运行形态
- 最终硬件/平台方向
- 全局接口与资源分配：引脚、外设、总线、地址、电源、复位、中断、DMA
- 时钟/时序策略：采样率、通信速率、控制周期、tick、延时基准
- 存储与型号策略：Flash/RAM/heap/stack/map/linker/startup/同系列换型规则
- 模拟前端、传感器、执行器、电源和机械约束
- 软件/固件模块划分
- 数据流、控制流、状态机、启动/复位/异常恢复
- 算法链路、库选择、替代方案和放弃方案
- 资源预算与依据
- 全局验证策略
- 可变更项、禁止偏离项、变更影响评估规则
- 给 `initialize-hardware-project` change 的工程骨架输入
- 给 `hw:change-plan` 的拆分提示和 OpenSpec source-map seed 线索

## Phase 0 - Read Inputs

PowerShell:

```powershell
Get-Content -ErrorAction Stop aisee/docs/requirements/*-hw-srs.md
Get-Content -ErrorAction SilentlyContinue docs/project-structure.md
Get-Content -ErrorAction SilentlyContinue docs/clock-contract.md
Get-Content -ErrorAction SilentlyContinue docs/memory-device-contract.md
rg --files | rg '(\.ioc$|\.uvprojx$|\.ewp$|\.eww$|CMakeLists\.txt$|\.map$|\.sct$|\.ld$|\.icf$|startup_.*\.s$)'
```

POSIX shell:

```bash
cat aisee/docs/requirements/*-hw-srs.md
cat docs/project-structure.md 2>/dev/null
cat docs/clock-contract.md 2>/dev/null
cat docs/memory-device-contract.md 2>/dev/null
rg --files | rg '(\.ioc$|\.uvprojx$|\.ewp$|\.eww$|CMakeLists\.txt$|\.map$|\.sct$|\.ld$|\.icf$|startup_.*\.s$)'
```

如果缺少 SRS，停止并输出 `[SRS-REQUIRED]`。

## Phase 1 - Global Decision Gate

先确认会影响全局设计的决策是否足够明确：
- 目标平台/硬件方向
- 工具链和工程形态
- 关键接口/电路/传感器/执行器
- 性能指标和资源边界
- 验证方式

每轮最多问 3 个问题。仍不明确但可推进的写 `[ASSUMPTION]`；会影响全局资源或不可逆硬件决策的写 `[ARCH-BLOCKER]` 并暂停。

## Phase 2 - Resource And Interface Architecture

统一设计接口和资源，不拆成孤立接口文档。

必须按项目类型选择相关域：
- MCU 引脚、外设、DMA、中断、Timer、ADC/DAC/OPAMP、通信总线
- RTOS task/ISR/queue/timer 资源
- Linux device tree、驱动、文件节点、服务、权限
- FPGA 寄存器、数据通道、时钟域、约束
- 模拟前端、传感器、执行器、电源、连接器、测试点

必须输出资源冲突和冻结规则。

## Phase 3 - System And Module Architecture

定义模块边界：
- 职责
- 输入输出
- 初始化顺序
- 状态机/流程
- 错误处理
- 共享资源
- 验证入口

模块数量 `>=5` 时：
- 主架构文档只保留全局结构、模块索引、跨模块数据流、预算总表和风险。
- 每个模块生成 `docs/modules/<module-name>.md`。
- 模块文档必须包含职责、输入输出、依赖、状态机/流程、资源预算、接口约束、错误处理、验证方式。

## Phase 4 - Algorithm / Library / Dependency Architecture

对关键算法、库和依赖写清：
- 为什么需要
- 输入输出语义
- 复杂度和资源成本
- 替代方案
- 放弃方案及原因
- 对 Flash/RAM/CPU/实时性的影响

不得只写最终方案。

## Phase 5 - Budget And Constraint Gate

预算按项目类型选择：
- MCU：Flash/RAM/CPU/中断/外设/栈/堆/map 余量
- MCU 时序：SYSCLK/HCLK/PCLK/ADC/TIM/PWM/UART/SPI/I2C/RTOS tick
- MCU 工程约束：启动文件、向量表、linker/scatter、heap/stack、工程宏、目标芯片型号、下载算法
- Linux：CPU/RAM/存储/启动时间/进程/文件句柄/服务依赖
- FPGA：逻辑资源/BRAM/DSP/时钟/吞吐
- 通信：带宽/延迟/重试成本
- 控制：采样周期/控制周期/保护响应时间

预算不过时标记 `[BUDGET-FAIL]`，不得进入 `hw:change-plan`，除非用户明确接受风险并写入文档。

## Phase 6 - Generate Document

读取 `assets/architecture-template.md` 生成整体架构文档。若模块数量 `>=5`，再读取 `assets/module-architecture-template.md` 生成模块文档。

## Guardrails

- 不要把某个项目的模块名当成通用模板。
- 不要跳过接口/资源/时钟/存储预算。
- 不要在没有来源的情况下断言采样率、baudrate、SPI/I2C 速率、heap/stack 安全或芯片可直接替换。
- 整体架构可以提出后续 OpenSpec change 拆分建议，但不得替代 `hw:change-plan`。
- 整体架构不得直接生成实现任务；任务由 OpenSpec `tasks.md` 生成。
- 所有全局禁止偏离项必须明确写入 “Architecture Rules”。

## Next

- 运行 `hw:change-plan`。
- 如果需要创建或整理工程骨架，`hw:change-plan` 必须把 `initialize-hardware-project` 规划为第一个 OpenSpec change。
- 如果发现已有工程事实缺失，可先运行 `hw:init scan-existing` 只读扫描，或标记 `[PROJECT-FACT-MISSING]`。
