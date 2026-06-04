# Capability Checklist

按项目类型选择检查项，不要求全部使用。

## MCU / RTOS

- Flash/RAM/EEPROM/外部存储
- CPU 主频、FPU、DSP 指令、缓存
- ADC/DAC/比较器/OPAMP/PGA
- SPI/I2C/UART/CAN/USB/Ethernet
- DMA、定时器、PWM、编码器接口
- 中断数量与优先级
- 低功耗模式、唤醒源
- 调试下载方式、量产烧录方式
- SDK/HAL/LL/RTOS 成熟度

## Embedded Linux

- CPU/RAM/存储容量
- BSP、内核版本、设备树
- 启动时间、文件系统、升级机制
- 驱动可用性：I2C/SPI/UART/CAN/USB/Ethernet/GPIO/PWM/ADC
- CMake/Makefile/Yocto/Buildroot 选择
- 日志、守护进程、系统服务
- 安全更新、权限、远程维护

## FPGA / High-Speed Digital

- LUT/FF/BRAM/DSP 资源
- 时钟树、PLL、时序裕量
- IO 标准、电平、bank 电压
- 外部存储接口
- 高速串行接口
- 仿真、约束、时序收敛风险

## Analog / Sensor

- 输入范围、偏置、增益、带宽
- 噪声、漂移、温度影响
- 抗混叠、滤波、保护
- 采样同步、校准方式
- 传感器供电与接口

## Power / Actuator

- 电压/电流/功率范围
- 热设计与保护
- PWM/驱动器/反馈路径
- 故障检测与安全停机
- EMI/EMC 风险

## Connectivity

- 协议、吞吐、延迟
- 认证、配网、重连
- 天线/射频/布线
- 安全、升级、远程诊断

