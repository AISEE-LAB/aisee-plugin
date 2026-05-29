# Hardware Architecture Checklist

Use only the sections relevant to the project type.

## Resource Domains

- MCU pins and alternate functions
- Peripheral instances: ADC, DAC, OPAMP, COMP, TIM, PWM, USART, SPI, I2C, USB, FDCAN, DMA
- Interrupt priorities and ISR restrictions
- Clock tree and peripheral clock sources
- Flash, RAM, heap, stack, linker/scatter, startup, vector table
- Debug, boot, reset, flash download, production programming
- Analog front-end, sensor, actuator, power, connector, test point
- Linux device tree, driver boundary, files, services, permissions
- FPGA register map, clock domains, DMA/data path, timing closure
- Mechanical, thermal, enclosure, cable, manufacturing constraints

## Architecture Questions

- Which resources are globally frozen?
- Which resources are shared and what is the arbitration rule?
- Which timing values come from hardware facts rather than assumptions?
- Which modules are allowed to allocate large static buffers?
- Which libraries are rejected due to Flash/RAM/CPU cost?
- Which failures must not publish stale or misleading results?
- Which changes require revisiting the architecture document?

## OpenSpec Mapping

Every architecture decision that affects implementation should map to at least one of:
- FR: user/device observable requirement
- HW: hardware resource or constraint
- FW: firmware module or interface
- RT: runtime/timing/memory constraint
- VER: verification evidence