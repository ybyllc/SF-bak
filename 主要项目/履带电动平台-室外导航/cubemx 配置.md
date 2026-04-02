# CubeMX 配置笔记

## 1. 工程总览

| 芯片 | 工程文件 | 当前工程名 | 时钟配置（当前 `.ioc`） |
|---|---|---|---|
| STM32F401RCT6 | `代码/F401.ioc` | `F401_TEST` | SYSCLK 48MHz（HSE=8MHz） |
| STM32F407VGT6 | `代码/STM32F407VGT6/STM32F407VGT6.ioc` | `STM32F407VGT6` | SYSCLK 168MHz（HSE=8MHz） |
| STM32H743VIT6TR | `软件/f743.ioc` | `f743` | SYSCLK 64MHz（HSE=25MHz） |

---

## 2. STM32F401RCT6（`代码/F401.ioc`）

### 2.1 已启用外设
- ADC1（VBAT）
- TIM1 / TIM2 / TIM3 / TIM4 / TIM5
- USART1 / USART2
- DMA（串口收发）
- RTC / SYS / NVIC

### 2.2 时钟关键参数
- `SYSCLK = 48MHz`
- `AHB = 48MHz`
- `APB1 = 24MHz`（定时器时钟 48MHz）
- `APB2 = 48MHz`
- PLL：`M=4, N=96, P=4`

### 2.3 串口与 DMA
| 外设 | 引脚 | DMA |
|---|---|---|
| USART1 | PA9 / PA10 | RX: DMA2_Stream2, TX: DMA2_Stream7 |
| USART2 | PA2 / PA3 | RX: DMA1_Stream5, TX: DMA1_Stream6 |

### 2.4 主要定时器用途（按当前标签）
| 定时器 | 通道/模式 | 引脚 |
|---|---|---|
| TIM5 | CH1/CH2（编码器） | PA0, PA1 |
| TIM2 | CH1/CH2（编码器） | PA15, PB3 |
| TIM3 | CH1/CH3/CH4（PWM） | PA6, PB0, PB1 |
| TIM4 | CH1（PWM） | PB6 |

### 2.5 关键 GPIO（按标签分组）
- 电机相关：`PA4/PA5/PA7/PC4/PC5/PB7/PB8`
- 433 输入：`PA11/PA12/PB4/PB5`
- OLED/按键：`PB2/PB12/PB13/PB14/PB15/PC6`
- 其他：`PC7(LED), PB9(EXTI9)`

---

## 3. STM32F407VGT6（`代码/STM32F407VGT6/STM32F407VGT6.ioc`）

### 3.1 已启用外设
- CAN1
- TIM1 / TIM3 / TIM4
- UART4 / USART1 / USART2 / USART3
- SPI2 / SPI3 / I2C1 / SDIO / USB_OTG_FS
- DMA / FreeRTOS / RTC / SYS / NVIC

### 3.2 时钟关键参数
- `SYSCLK = 168MHz`
- `AHB = 168MHz`
- `APB1 = 42MHz`（定时器时钟 84MHz）
- `APB2 = 84MHz`（定时器时钟 168MHz）
- PLL：`M=4, N=168, Q=7`

### 3.3 通讯接口
| 外设 | 引脚 |
|---|---|
| UART4 | PA0 / PA1 |
| USART1 | PA9 / PA10 |
| USART2 | PA2 / PA3 |
| USART3 | PD8 / PB11 |
| CAN1 | PD0 / PD1 |
| USB OTG FS | PA11 / PA12 |

### 3.4 存储/显示相关
| 功能 | 引脚 |
|---|---|
| SPI3（LCD） | PB3(SCK), PB5(MOSI), PB4(DC), PD7(CS), PD4(RST), PD3(BLK) |
| SPI2（Flash） | PB10(SCK), PB14(MISO), PB15(MOSI) |
| SDIO | PC8/PC9/PC10/PC11/PC12 + PD2(CMD) + PD15(SD_CD) |
| I2C1 | PB8(SCL), PB9(SDA) |

### 3.5 定时器与关键 IO
| 功能 | 引脚 |
|---|---|
| TIM3 PWM CH1~CH4 | PA6, PA7, PB0, PB1 |
| TIM4 输入捕获 CH1~CH3 | PD12, PD13, PD14 |
| TIM1 CH1~CH4 | PE9, PE11, PE13, PE14 |
| 其他 | PE3(DCMI_PWDN), PB7(DCMI_VSYNC), PC13(KEY标签) |

### 3.6 DMA 请求（当前工程）
- USART2_RX
- USART3_RX / USART3_TX
- UART4_RX / UART4_TX
- I2C1_RX / I2C1_TX

---

## 4. STM32H743VIT6TR（`软件/f743.ioc`）

### 4.1 已启用外设
- FDCAN1
- TIM1 / TIM2 / TIM4 / TIM5 / TIM8
- USART1 / USART2 / UART4
- SPI1 / SPI4 / SDMMC1 / USB_OTG_FS
- ADC1 / RTC / SYS / NVIC

### 4.2 时钟关键参数（当前工程）
- `SYSCLK = 64MHz`
- `HCLK = 64MHz`
- `APB1 = 32MHz`
- `APB2 = 32MHz`
- `HSE = 25MHz`

> 说明：此 `.ioc` 当前是低频验证配置，不是之前笔记里的 400MHz 版本。

### 4.3 通讯与总线
| 外设 | 引脚 |
|---|---|
| USART1 | PB14 / PB15 |
| USART2 | PA2 / PA3 |
| UART4 | PB9(TX) / PB8(RX) |
| FDCAN1 | PD0(RX) / PD1(TX) |

### 4.4 定时器/采样/存储
| 功能 | 引脚 |
|---|---|
| TIM8 CH1/CH2 | PC6, PC7 |
| TIM1 CH1/CH2N | PE9, PE10 |
| TIM4 CH1~CH4 输入捕获 | PD12, PD13, PD14, PD15 |
| TIM5 CH1 | PA0 |
| TIM2 CH1/CH2 | PA5, PA1 |
| ADC1_INP3 | PA6 |
| SDMMC1 | PC8/PC9/PC10/PC11/PC12 + PD2 |
| SPI1 | PB3(SCK), PB4(MISO), PD7(MOSI) |
| SPI4 | PE12(SCK), PE5(MISO), PE14(MOSI) |

### 4.5 当前可见问题
- `FDCAN1.CalculateBaudRateNominal = 1041666`，不是常用 500kbps。
- 未见串口 DMA 请求项（如需高吞吐，建议补 DMA 配置）。

---

## 5. 统一维护规则（建议）

1. 新增芯片时，先在本文件“工程总览”补一行，再建独立章节。  
2. 每个芯片只保留一套“当前生效配置”（以 `.ioc` 为准），历史方案放到“变更记录”。  
3. 引脚表中“功能名”优先写业务名（如 `MOTOR_L_PWM`），同时附外设通道（如 `TIM3_CH1`）。  
4. 每次改完 `.ioc` 后同步更新：时钟、串口、定时器、DMA 四部分。  
5. 生成代码前后都做一次冲突检查（尤其是定时器复用、SWD、USB、SDIO）。

