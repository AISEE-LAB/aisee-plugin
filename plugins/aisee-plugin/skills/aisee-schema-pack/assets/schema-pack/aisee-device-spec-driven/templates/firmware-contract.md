# Firmware / Device Software Contract: {{change-name}}

状态：适用 / N/A

N/A 原因：

## 软件形态与构建目标

| 项 | 内容 | 来源 |
|---|---|---|
| 软件形态 | firmware / bootloader / RTOS app / Linux kernel driver / Linux user-space service / host tool / production tool / library / SDK wrapper | |
| 语言 / runtime | C / C++ / Rust / Python / Go / shell / other | |
| 构建目标 | debug / release / size optimized / production / test | |
| 生成代码 / vendor config | CubeMX / Kconfig / DTS / codegen / vendor IDE / N/A | |
| Public API / ABI | stable / internal / N/A | |

## 工程目录与文件归属

| FW ID | 模块 / 文件 | 推荐目录 | 职责 | 可依赖对象 | 禁止依赖 | 关联 FR / HW |
|---|---|---|---|---|---|---|
| FW-001 | | Core / Function / Drivers / vendor path / app path / kernel path / tools / scripts | | HAL / driver / module API / OS API | upper layer / hidden global / dynamic allocation unless approved | |

## 模块边界

| FW ID | 模块 | 职责 | 运行位置 | 输入 | 输出 | 关联 FR / HW |
|---|---|---|---|---|---|---|
| FW-001 | | | bare-metal loop / RTOS task / ISR / Linux kernel / Linux user-space / host tool / production tool | | | |

## 初始化与生命周期

| 阶段 | 顺序 | 模块 | 前置条件 | 失败处理 | 证据 |
|---|---:|---|---|---|---|
| boot / clock / gpio / dma / peripheral / service / app / daemon / tool | 1 | | | retry / degraded mode / stop / safe state / error report | |

## 接口、API 与协议入口

| 接口 | 类型 | 调用方 | 被调方 | 输入 | 输出 | 错误 |
|---|---|---|---|---|---|---|
| | HAL / Driver API / ioctl / sysfs / netlink / dbus / socket / message / callback / CLI / file / module API | | | | | |

## 错误码与状态语义

| 错误 / 状态 | 触发条件 | 对外表现 | 恢复方式 | 关联验证 |
|---|---|---|---|---|
| | | log / return code / status frame / event / errno | retry / reset / fallback / manual | VER-001 |

## 数据所有权与缓冲区

| 数据 / Buffer / File | Owner | Producer | Consumer | 生命周期 | 并发规则 | 内存 / 存储位置 |
|---|---|---|---|---|---|---|
| | | ISR / DMA / task / thread / process / tool | | static / stack / heap / DMA buffer / file / database | lock-free / flag / mutex / critical section / copy / IPC | .bss / heap / stack / special section / filesystem |

## 中断、DMA、回调与并发

| 触发源 | 上下文 | 处理规则 | 禁止事项 | 后续动作 | 关联 RT |
|---|---|---|---|---|---|
| | ISR / DMA callback / signal / thread / process / event loop | | blocking / printf / malloc / long loop / unsafe API | set flag / copy frame / schedule task / emit event | RT-001 |

## 状态机

| 状态 | 进入条件 | 事件 | 动作 | 下一状态 | 错误处理 |
|---|---|---|---|---|---|
| | | | | | |

## 配置、参数、日志与诊断

| 项 | 内容 | 约束 |
|---|---|---|
| 配置来源 | compile-time / factory / user / cloud / file / NVS / EEPROM / env | |
| 默认值 / 范围 / 单位 | | |
| 持久化位置 | Flash / EEPROM / file / database / cloud shadow / N/A | |
| 配置版本迁移 | | |
| 损坏恢复 | CRC / backup / factory reset / default fallback | |
| 日志等级 / 日志位置 | serial / RTT / SWO / dmesg / journald / file / cloud / none | |
| 诊断接口 | CLI / shell / API / cloud command / debug port / none | |
| 故障输出 | return code / event / alarm / log / UI-output / none | |

## 依赖、License 与资源成本

| 依赖 | 用途 | 资源成本 | License / 约束 | 替代方案 | 引入条件 | 验证 |
|---|---|---|---|---|---|---|
| vendor SDK / DSP / FFT / crypto / protocol stack / OS package / library | | Flash / RAM / CPU / disk / network | | | budget approved / map checked / license accepted | |

## 固件追踪矩阵

| FR | FW | HW | RT | CONN | SEC | PROD | OPS | VER | 是否完整 |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | FW-001 | HW-001 | RT-001 | CONN-001 | SEC-001 | PROD-001 | OPS-001 | VER-001 | 是 / 否 |