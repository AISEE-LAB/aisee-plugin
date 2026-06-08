# Project Templates

用于 `hw:init` 选择工程骨架。实际创建时按项目裁剪，不要求全部目录都生成。

默认原则：
- MCU 项目优先使用 `Drivers + Core + Function` 三层结构。
- `Drivers/` 放厂商库、CMSIS、HAL/LL、SDK、第三方底层依赖。目录名必须按厂家实际包名生成，例如 `STM32G4xx_HAL_Driver/`、`GD32F30x_standard_peripheral/`，不要固定写死为 `Vendor_HAL/`。
- `Core/` 放芯片自带外设初始化、主程序、主流程调度、中断、系统时钟、DMA、GPIO、USART、ADC、SPI 等基础代码。
- `Function/` 放扩展外设、业务模块、算法库、显示、通信协议、测量/控制逻辑。
- 如果旧项目已经使用 `FunctionB/FunctionE`，不要强制改名；将 `FunctionB` 视为 `Core`，将 `FunctionE` 视为 `Function`。
- 工程目录名必须跟随工具链实际生成结果，例如 `MDK-ARM/`、`EWARM/`、`.vscode/`、`build/`，不要把某个 IDE 目录当成通用必选项。
- 不默认创建 `App/`、`BSP/`、`Config/`、`Tests/`。只有设计文档明确需要时才创建。
- `docs/` 建议保留，用于需求、接口、设计、调试记录和验证记录。
- `tools/` 可选，仅在需要脚本、烧录辅助、日志解析、数据生成时创建。

## mcu-keil

```text
project/
  <keil_project_dir>/
    <project>.uvprojx
  Core/
    Inc/
    Src/
  Drivers/
    CMSIS/
    <vendor_driver_dir>/
  Function/
    <module>/
      Inc/
      Src/
  docs/
  tools/                 # optional
```

适用：Keil MDK，ARMCC/ARMCLANG，STM32/NXP/GD32 等 MCU。

说明：
- `<keil_project_dir>` 常见为 `MDK-ARM/`，但必须按实际工程生成目录命名。
- `<vendor_driver_dir>` 必须按厂家库真实目录命名。
- 简单模块可直接放在 `Function/<module>/`，复杂模块再拆 `Inc/`、`Src/`。

## mcu-iar

```text
project/
  <iar_project_dir>/
  Core/
    Inc/
    Src/
  Drivers/
    CMSIS/
    <vendor_driver_dir>/
  Function/
    <module>/
      Inc/
      Src/
  docs/
  tools/                 # optional
```

适用：IAR Embedded Workbench。

说明：
- `<iar_project_dir>` 常见为 `EWARM/`，但必须按实际工程生成目录命名。
- 不默认创建板级抽象目录；板级逻辑复杂时再按设计文档增加。

## mcu-gcc-cmake

```text
project/
  CMakeLists.txt
  Core/
    Inc/
    Src/
  Drivers/
    CMSIS/
    <vendor_driver_dir>/
  Function/
    <module>/
      Inc/
      Src/
  Linker/                # optional
  Startup/               # optional
  cmake/                 # optional
  docs/
  tools/                 # optional
```

适用：arm-none-eabi-gcc、clang、跨平台 CI。

说明：
- 若启动文件和链接脚本由 SDK 或 IDE 管理，可以不创建 `Startup/`、`Linker/`。
- 若工程很小，可以让 `Function/<module>/` 直接包含 `.c/.h`。

## rtos-cmake

```text
project/
  CMakeLists.txt
  Core/
    Inc/
    Src/
  Drivers/
    CMSIS/
    <vendor_driver_dir>/
  RTOS/
    <rtos_kernel_or_port>/
  Function/
    <module>/
      Inc/
      Src/
  docs/
  tools/                 # optional
```

适用：FreeRTOS、RT-Thread、Zephyr 风格项目。

说明：
- RTOS 项目仍保持 `Core + Function`，任务编排和主流程调度放 `Core/` 或明确的调度模块中。
- 不默认创建 `app/`、`middleware/`；只有设计文档明确需要分层时再增加。

## embedded-linux-app

```text
project/
  Makefile
  CMakeLists.txt
  src/
  include/
  config/
  scripts/
  systemd/
  tests/
  docs/
```

适用：用户态应用、守护进程、网关服务。

## embedded-linux-bsp

```text
project/
  board/
  dts/
  drivers/
  rootfs/
  packages/
  scripts/
  docs/
```

适用：BSP、设备树、驱动、系统镜像集成。

## fpga-host

```text
project/
  fpga/
    rtl/
    constraints/
    sim/
  host/
    src/
    include/
  regs/
  scripts/
  tests/
  docs/
```

适用：FPGA + MCU/Linux host 协同。

## generic-library

```text
project/
  CMakeLists.txt
  src/
  include/
  examples/
  tests/
  docs/
```

适用：可复用算法库、驱动库、中间件。
