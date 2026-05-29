---
name: aisee:device-context
description: 为硬件/嵌入式 OpenSpec change 生成设备技术上下文。用于整理 MCU、RTOS、BSP、外设、通信协议、功耗、存储、启动链路、OTA、生产测试、调试接口、硬件版本和验证约束。它不生成 App/Web UI content，也不拆 change。
---

# aisee:device-context

## 职责

- 扫描或整理硬件/嵌入式项目事实。
- 输出 device domain 的上下文输入，供 `aisee:change-plan` 和 `aisee:change-author` 使用。
- 标记硬件、固件、运行时、验证、生产和安全约束。

## 应覆盖

- MCU / SoC / 模组。
- RTOS / bare-metal / BSP。
- 外设、总线、引脚、传感器、执行器。
- 通信协议和连接性。
- Flash/RAM/功耗/实时性。
- 启动、升级、回滚、看门狗。
- HIL、台架、烧录、量产测试和版本矩阵。

## 输出边界

不写 UI content，不做最终 change 拆分，不写固件实现代码。
