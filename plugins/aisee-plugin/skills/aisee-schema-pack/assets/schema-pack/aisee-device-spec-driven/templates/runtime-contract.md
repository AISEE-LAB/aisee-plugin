# Runtime Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

## 运行环境

| 项 | 内容 | 来源 |
|---|---|---|
| 运行形态 | bare-metal / RTOS / Linux user-space / Linux kernel / bootloader / host tool / production environment | |
| Kernel / RTOS / Host OS | | |
| 调度模型 | preemptive / cooperative / event loop / ISR-driven / process-based / service-based | |
| 工具链 / 构建系统 | | |
| 构建配置 | Debug / Release / size optimized / speed optimized / production / test | |

## Linux / OS 集成约束

| 项 | 内容 | 验证 |
|---|---|---|
| Device tree / overlay / pinctrl / clocks / regulators | | boot log / driver probe |
| Kernel config / module / built-in | | config review / modprobe |
| Rootfs / package / dependencies | | image build / package install |
| systemd / init / service order | | boot test / systemctl status |
| udev / permissions / user / group / capabilities | | runtime permission test |
| IPC / socket / dbus / shared memory / file path | | integration test |
| Log path / rotation / crash dump | | log review / fault injection |

## 时钟、调度与实时性

| RT ID | 时钟 / 调度项 | 配置 | 影响范围 | 验证方式 |
|---|---|---|---|---|
| RT-CLK-001 | SYSCLK / HCLK / PCLK / RTOS tick / timer tick / process timer / scheduler | | latency / event timing / data path / communication / timeout | scope / logic analyzer / log / profiler / register readback |

| 场景 | 预算 | 触发条件 | 超时处理 | 验证方式 |
|---|---|---|---|---|
| | latency / period / jitter / throughput / event rate / data rate | | | |

## 任务、线程、进程与中断

| RT ID | 名称 | 类型 | 优先级 | 周期 / 触发 | 栈 / 内存 / 资源 | 关联 FW |
|---|---|---|---|---|---|---|
| RT-001 | | task / thread / process / ISR / timer / main loop / service | | | | FW-001 |

## 资源预算

| 资源 | 上限 | 当前估算 / 基线 | Margin | 测量方式 | 超限处理 |
|---|---|---|---|---|---|
| Flash / ROM / image / package | | | | map / size / image tool | reject change / split module / replace library |
| RAM / SRAM / DDR / process memory | | | | map / runtime watermark / top / ps | reduce buffers / move storage / reject change |
| .data / .bss / static objects | | | | map file | review static objects |
| heap / dynamic allocation | | | | linker / runtime monitor / malloc stats | avoid dynamic allocation / fixed pool |
| stack / MSP / PSP / task stack / thread stack | | | | watermark / fault log | increase stack / reduce call depth |
| CPU / scheduler | | | | profiler / GPIO timing / perf / cycle counter | optimize / lower rate / split work |
| disk / filesystem / partition | | | | df / image size / filesystem check | reduce logs / adjust partition |
| network / bus throughput | | | | benchmark / capture | rate limit / protocol change |
| power | | | | power meter / estimate | duty-cycle / low-power mode |

## Map / Image / Package 审查

| 项 | 当前值 | 风险阈值 | 证据 | 处理规则 |
|---|---|---|---|---|
| Total RO / ROM / image size | | | map / image build | |
| Total RW + ZI / RAM / process memory | | | map / runtime monitor | |
| Largest .bss / static owners | | | map file | |
| Heap / Stack | | | startup / linker / map / watermark | |
| Large library / package members | | | map / package report | |
| Download / deployment image size | | | build log / programming log / deployment log | |

## 库、算法与资源门控

| 变更类型 | 必须检查 | 通过标准 | 失败处理 |
|---|---|---|---|
| 引入 DSP / FFT / crypto / protocol stack / OS package / heavy library | Flash/RAM/CPU/disk/network delta | margin 满足 architecture 预算 | 替换库 / 降级算法 / 拆 change |
| 增加数据缓冲 / 图像缓冲 / 通信缓冲 / 队列 | memory/cache/alignment/owner | buffer owner 明确且不越界 | 减小缓冲 / 分块处理 / 流式处理 |
| 提高事件频率 / 数据率 / 控制周期 / 输出周期 / 通信速率 | CPU/ISR/DMA/bus/scheduler 占用 | 时序验证通过 | 降低指标 / 调整架构 / 调整硬件 |

## 启动、复位、电源与恢复

- 启动流程：
- 复位行为：
- 看门狗策略：
- 低功耗进入 / 退出：
- 崩溃 / 异常恢复：
- 升级 / 回滚运行时影响：
- fault / crash 诊断输出：

## 运行时追踪矩阵

| FR | RT | FW | CONN | SEC | PROD | OPS | VER | 是否完整 |
|---|---|---|---|---|---|---|---|---|
| FR-001 | RT-001 | FW-001 | CONN-001 | SEC-001 | PROD-001 | OPS-001 | VER-001 | 是 / 否 |