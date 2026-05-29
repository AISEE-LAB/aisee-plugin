# Clock Contract Template

```markdown
# Clock Contract

## 1. Sources

| Source | Path / Function | Status |
|---|---|---|
| MCU configuration | .ioc / vendor config |  |
| Clock function | SystemClock_Config() |  |
| Oscillator config | HAL_RCC_OscConfig / equivalent |  |
| Bus clock config | HAL_RCC_ClockConfig / equivalent |  |
| Peripheral clock config | HAL_RCCEx_PeriphCLKConfig / equivalent |  |

## 2. Clock Tree

| Clock Item | Value | Source | Notes |
|---|---|---|---|
| Clock source | HSE / HSI / MSI / PLL / other |  |  |
| External crystal |  |  |  |
| SYSCLK |  |  |  |
| HCLK |  |  |  |
| PCLK1 |  |  |  |
| PCLK2 |  |  |  |
| APB1 prescaler |  |  |  |
| APB2 prescaler |  |  |  |

## 3. Peripheral Clocks

List only peripherals used by this project.

| Peripheral | Clock Source | Effective Clock | Dependent Modules | Notes |
|---|---|---|---|---|
| ADC |  |  |  |  |
| TIM |  |  |  |  |
| USART/UART |  |  |  |  |
| SPI |  |  |  |  |
| I2C |  |  |  |  |
| USB/FDCAN/SDIO/etc. |  |  |  |  |

## 4. Design Impact

| Area | Impact | Required Rule |
|---|---|---|
| delay/millis/micros |  |  |
| ADC sampling |  |  |
| TIM/PWM |  |  |
| UART baudrate |  |  |
| SPI/I2C speed |  |  |
| DMA pacing |  |  |
| RTOS tick |  |  |
| low power wakeup |  |  |

## 5. Change Rules

- Do not modify the clock configuration without updating this document.
- Any change to SYSCLK/HCLK/PCLK/peripheral clocks must re-check all dependent modules.
- Any ADC/TIM/PWM/UART/SPI/I2C/RTOS timing design must reference this document.

## 6. Re-Verification Checklist

- [ ] Build succeeds.
- [ ] Download/debug still works.
- [ ] System tick and delay functions are correct.
- [ ] UART baudrate is correct.
- [ ] ADC sampling rate or conversion timing is correct.
- [ ] TIM/PWM frequency is correct.
- [ ] SPI/I2C bus speed is correct.
- [ ] RTOS tick timing is correct, if used.

## 7. Missing Data

- [CLOCK-CONTRACT-MISSING]:
```
