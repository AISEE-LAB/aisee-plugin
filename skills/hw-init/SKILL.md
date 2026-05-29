---
name: hw:init
description: 硬件工程初始化辅助技能。用于在 initialize-hardware-project OpenSpec change 的实现阶段，按 hw:architecture 确认的模板创建或校验工程目录、厂商库位置、Core + Function 结构、项目结构契约、时钟契约和存储/型号契约；也可在前期以 scan-existing 只读模式扫描已有 CubeMX/Keil/IAR/CMake/vendor SDK 工程事实。不得作为主流程节点绕过 OpenSpec 创建/修改工程。触发词包括“hw:init”“工程骨架”“项目目录模板”“Core+Function”“scan-existing”“generate-skeleton”。
---

# hw:init

`hw:init` 是辅助技能，不是主流程节点。

主流程是：

```text
hw:srs -> hw:architecture -> hw:change-plan -> /opsx:new ... -> /opsx:apply
```

`hw:init generate-skeleton` 只能在 `initialize-hardware-project` 这类 OpenSpec change 的实现阶段使用。任何会创建或修改项目文件的初始化都必须被 OpenSpec change 追踪。

## Modes

### scan-existing

只读扫描已有工程事实，可在 `hw:architecture` 前使用。

允许：
- 读取目录结构
- 读取 `.ioc`、`.uvprojx`、`.ewp`、`CMakeLists.txt`、Makefile
- 读取 map、startup、linker/scatter、工程宏、芯片型号配置
- 读取 `SystemClock_Config()` 和 vendor configuration
- 输出事实摘要和缺口

禁止：
- 创建目录
- 修改工程文件
- 添加源码
- 改 linker/scatter/startup
- 改 `.uvprojx` / `.ioc`

### generate-skeleton

创建或校验工程骨架。必须满足：
- 当前处于 OpenSpec change，例如 `initialize-hardware-project`
- 已有 `docs/architecture/*-hw-architecture.md`
- `tasks.md` 或当前用户请求明确要求使用 `hw:init generate-skeleton`

生成或修改的文件必须由该 OpenSpec change 追踪。

## Inputs

`scan-existing` 输入：
- 已存在的基础工程目录
- `.ioc`、`.uvprojx`、`.ewp`、`.eww`、`CMakeLists.txt`、Makefile、vendor SDK
- `SystemClock_Config()`、map 文件、启动文件、linker/scatter、工程宏、芯片型号配置

`generate-skeleton` 输入：
- `openspec/changes/<change>/proposal.md`
- `openspec/changes/<change>/source-map.md`
- `openspec/changes/<change>/design.md`
- `openspec/changes/<change>/hardware-contract.md`
- `openspec/changes/<change>/firmware-contract.md`
- `openspec/changes/<change>/runtime-contract.md`
- `openspec/changes/<change>/tasks.md`
- `docs/architecture/*-hw-architecture.md`
- 可选 `docs/modules/*.md`

可选参数：
- `--mode scan-existing|generate-skeleton`
- `--template mcu-keil|mcu-iar|mcu-gcc-cmake|rtos-cmake|embedded-linux-app|embedded-linux-bsp|fpga-host|generic-library|custom`

## References

模板选择时读取：

`assets/project-templates.md`

项目结构说明生成时读取：

`assets/project-structure-template.md`

MCU 工程时钟契约生成时读取：

`assets/clock-contract-template.md`

MCU 存储与型号契约生成时读取：

`assets/memory-device-contract-template.md`

报告生成时读取：

`assets/init-report-template.md`

## Output

`scan-existing` 输出：
- 聊天中的只读扫描摘要，或用户明确要求时写入 `docs/requirements/<YYYY-MM-DD>-<slug>-scan.md`
- 不创建长期工程契约，除非用户明确要求且不修改项目文件

`generate-skeleton` 输出：
- 架构确认后的目录结构
- 必要源码目录和 README/说明
- 模块目录，若存在 `docs/modules/*.md` 必须按模块文档创建或校验
- `docs/project-structure.md`
- MCU/RTOS 项目的 `docs/clock-contract.md`
- MCU/RTOS 项目的 `docs/memory-device-contract.md`
- `docs/requirements/<YYYY-MM-DD>-<slug>-init.md`

## Phase 0 - Confirm OpenSpec Tracking

如果模式是 `generate-skeleton`，先确认当前是否在 OpenSpec change 中。

PowerShell:

```powershell
Get-ChildItem -Path openspec/changes -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne 'archive' }
```

POSIX shell:

```bash
find openspec/changes -maxdepth 1 -mindepth 1 -type d ! -name archive 2>/dev/null
```

如果没有 active change，停止并输出 `[OPENSPEC-CHANGE-REQUIRED]`，建议先由 `hw:change-plan` 创建 `initialize-hardware-project`。

如果 active change 不是工程初始化类 change，但用户要求创建/修改工程骨架，停止并输出 `[INITIALIZATION-CHANGE-REQUIRED]`。

## Phase 1 - Select Template

从 `assets/project-templates.md` 选择最接近模板：
- `mcu-keil`
- `mcu-iar`
- `mcu-gcc-cmake`
- `rtos-cmake`
- `embedded-linux-app`
- `embedded-linux-bsp`
- `fpga-host`
- `generic-library`

如果没有合适模板，生成 `custom` 模板并说明差异。

## Phase 2 - Project Structure Contract

`generate-skeleton` 必须生成或更新：

`docs/project-structure.md`

必须包含：
- 工程类型和工具链
- 工程文件位置
- 厂商库位置，保留厂家真实目录名，不改成通用 `Vendor_HAL`
- `Drivers/Core/Function` 或项目确认目录的语义
- AI 允许修改和禁止修改的目录/文件
- 新增 `.c/.h` 文件需要加入 IDE group 或 build system 的规则
- 工程文件修改策略：不修改 / 备份后修改 / 用户手动添加

## Phase 3 - MCU Clock Contract

MCU/RTOS 项目必须生成：

`docs/clock-contract.md`

读取来源：
- `.ioc`、`.mxproject` 或 vendor configuration
- `SystemClock_Config()`
- `HAL_RCC_OscConfig`
- `HAL_RCC_ClockConfig`
- `HAL_RCCEx_PeriphCLKConfig`

不得从猜测生成时钟值。无法解析时标记 `[CLOCK-CONTRACT-MISSING]`。

## Phase 4 - MCU Memory And Device Contract

MCU/RTOS 项目必须生成：

`docs/memory-device-contract.md`

读取来源：
- map 文件
- 启动文件
- linker/scatter/IDE target memory 配置
- 工程宏
- `.ioc` 或 vendor configuration 中的芯片型号
- flash download algorithm/debug target 配置，仅用于记录烧录配置风险

不得猜测 Flash/RAM 或兼容型号。无法解析时标记 `[MEMORY-DEVICE-CONTRACT-MISSING]`。

## Phase 5 - Generate Skeleton

仅 `generate-skeleton` 执行。

必须先读取：
- `docs/architecture/*-hw-architecture.md`
- OpenSpec change artifacts
- 可选 `docs/modules/*.md`

创建或校验目录时遵守：
- 不覆盖已有文件，除非用户明确同意。
- 默认使用项目确认的目录名；厂商库和工程目录使用真实名称。
- MCU 简化模板优先使用 `Drivers + Core + Function` 语义。
- 不默认创建 `App`、`Config`、`BSP`、`Test`，除非 architecture 或当前 change 明确要求。
- IDE 工程文件默认不自动修改，只输出手动添加清单。

## Phase 6 - Save Init Report

生成：

`docs/requirements/<YYYY-MM-DD>-<slug>-init.md`

报告必须包含：
- 当前 OpenSpec change 名称
- 执行模式
- 选择的模板
- 项目结构契约位置
- 创建/校验的文件和目录
- 未创建的文件及原因
- 时钟契约位置或 `[CLOCK-CONTRACT-MISSING]`
- 存储与型号契约位置或 `[MEMORY-DEVICE-CONTRACT-MISSING]`
- 手动前置条件
- 后续 changes 需要继承的工程规则

## Guardrails

- `generate-skeleton` 不得在 OpenSpec change 外执行。
- `generate-skeleton` 不得在 `hw:architecture` 之前执行。
- `scan-existing` 不得修改任何项目文件。
- 未确认工具链不得创建 IDE 专用工程。
- MCU/RTOS 工程没有时钟契约时，不得生成依赖采样率、PWM、通信速率或精确定时的实现计划。
- MCU/RTOS 工程没有存储与型号契约时，不得承诺 Flash/RAM 余量、heap/stack 安全性或同系列芯片可直接替换。
- 不要把项目初始化和业务实现混在一起。

## Next

- `scan-existing` 完成后，把事实输入给 `hw:architecture`。
- `generate-skeleton` 完成后，回到当前 OpenSpec change 的 `tasks.md`，继续勾选任务并执行验证。