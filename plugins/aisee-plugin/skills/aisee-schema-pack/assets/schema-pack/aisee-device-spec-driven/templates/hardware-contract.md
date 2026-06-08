# Hardware Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

## 目标硬件与资料

| 项 | 内容 | 来源 |
|---|---|---|
| 板卡 / 模组 / 主机适配器 | | |
| MCU / SoC / FPGA / Linux 目标 / 网关 | | |
| 具体型号 / 子型号 | | |
| 硬件版本 / PCB 版本 / BOM 版本 | | |
| 封装 / Pin Count / 连接器 | | |
| 外设芯片 / 传感器 / 执行器 / 通信模块 | | |
| 原理图 / PCB / Pinout | | |
| 数据手册 / Reference Manual / Errata | | |
| Vendor SDK / HAL / BSP / sample project | | |

## 器件型号、版本与存储边界

| HW ID | 项 | 当前值 | 允许范围 / 替代项 | 变更影响 | 来源 |
|---|---|---|---|---|---|
| HW-DEV-001 | Device macro / part number / hardware revision | | | startup / linker / HAL config / DTS / driver binding | |
| HW-MEM-001 | Flash / ROM / eMMC / NAND / NOR / storage | | | map / image / partition / download / boot layout | |
| HW-MEM-002 | RAM / SRAM / DDR / memory bank | | | .bss / heap / stack / DMA / cache / Linux memory | |
| HW-PKG-001 | Package / pin / connector compatibility | | | pinout / PCB / alternate function / cable | |
| HW-BOM-001 | BOM-sensitive component | | | driver behavior / calibration / supply risk | |

## 启动、链接、镜像与下载/部署配置

| 项 | 当前配置 | 约束 | 验证方式 | 来源 |
|---|---|---|---|---|
| Startup / vector / boot chain | | 必须匹配目标系列/型号/boot flow | build / boot / reset test | |
| Linker / scatter / memory layout | | Flash/RAM/storage 地址和大小必须匹配目标 | map review / boundary build | |
| Flash algorithm / programmer / deployment method | | 必须匹配容量、bank、sector/page、image/package 格式 | erase/program/verify/deploy test | |
| Bootloader / partition / A-B slot | | 必须与 update/rollback 策略一致 | boot/update/recovery test | |
| Heap / stack / reserved memory | | 必须与 runtime-contract 一致 | map/runtime review | |
| Linux DTS / pinctrl / clock / regulator | | 如适用，必须与硬件版本一致 | boot log / driver probe | |

## 引脚、外设与硬件接口

| HW ID | 引脚 / 外设 / 接口 | 方向 | 复用功能 / 协议 | 电平 / 模式 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| HW-001 | | input / output / bidirectional | GPIO / bus / comms / timer / DMA / interrupt / analog / custom IP / OS device | | | |

## 外部接口、设备与信号/数据通路

| HW ID | 接口 / 设备 / 信号 / 数据通路 | 电气 / 协议 / 数据范围 | 调理 / 转换 / 编码 | 时序 / 吞吐 / 精度约束 | 软件影响 | 验证 |
|---|---|---|---|---|---|---|
| HW-IO-001 | | | | | 驱动配置 / 数据解析 / 校准 / 错误处理 | |

## 总线、地址与拓扑

| 总线 / 通道 | 设备 | 地址 / CS / endpoint | 速率 | 模式 | 上拉 / 终端 / 拓扑 | 备注 |
|---|---|---|---|---|---|---|
| I2C / SPI / UART / CAN / USB / Ethernet / PCIe / parallel / custom / OS device | | | | | | |

## 时钟、电源、复位与低功耗

| 资源 | 配置 | 约束 | 影响范围 | 来源 |
|---|---|---|---|---|
| 系统时钟 / boot clock | | | CPU / memory / boot / timing | |
| 外设 / 模块时钟 | | | bus / comms / timers / converters / UI-output / custom IP / OS driver | |
| 周期 / 计时源 | | | control loop / acquisition / capture / protocol timeout / scheduling accuracy | |
| 电源输入 / 电源域 | | | power budget / brown-out / stability | |
| 参考 / IO 电平 | | | sensor / actuator / converter / IO / module stability | |
| 复位线 / boot pin / strap | | | programming / startup / recovery | |
| 中断线 / wake source | | | ISR latency / priority / wakeup | |
| 低功耗模式 | | | wakeup / retention / timing / user experience | |

## 电源、热、环境、机械与合规

| 项 | 要求 / 目标 | 验证方式 | 风险 |
|---|---|---|---|
| 输入电压 / 峰值电流 / 平均电流 | | measurement / estimate | |
| 上电/断电时序 / brown-out | | scope / fault injection | |
| 热设计 / 温升 / 降额 | | thermal test / estimate | |
| ESD / surge / reverse polarity / protection | | pre-compliance / inspection | |
| EMC / EMI | | pre-compliance / lab | |
| 机械 / 连接器 / 线束 / 安装 | | inspection / fit test | |
| 环境范围 | temperature / humidity / vibration / ingress / altitude | environmental test | |
| 法规 / 认证 | CE / FCC / UL / CCC / RoHS / REACH / project-specific | compliance review | |

## 资源冲突与复用规则

| 资源 | 冲突对象 | 决策 | 禁止事项 | 变更规则 |
|---|---|---|---|---|
| | | | | update architecture / hardware-contract before implementation |

## 硬件版本与迁移规则

| 迁移场景 | 可直接复用 | 必须重新确认 | 禁止假设 |
|---|---|---|---|
| 同系列不同 Flash/RAM/storage | 源码模块 / 部分 HAL 配置 | linker/scatter、DTS、partition、startup、flash algorithm、map margin | 只改宏即可安全下载/部署 |
| 同系列不同封装 / PCB | 通用驱动逻辑 | pinout、alternate function、connector、BOM、PCB 连接 | 引脚兼容 |
| 相近系列 / SoC / module 替换 | 上层模块设计 | clock tree、peripheral capability、driver binding、errata、power | 外设行为完全一致 |
| 生产批次 / BOM 替代 | 软件接口 | calibration、timing、tolerance、driver workaround | BOM 替代无软件影响 |

## 硬件风险与待确认

| 编号 | 风险 / 问题 | 影响 | 建议处理 |
|---|---|---|---|
| HWQ-001 | | | |

## 硬件追踪矩阵

| FR | HW | FW | RT | CONN | SEC | PROD | OPS | VER | 是否完整 |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | HW-001 | FW-001 | RT-001 | CONN-001 | SEC-001 | PROD-001 | OPS-001 | VER-001 | 是 / 否 |