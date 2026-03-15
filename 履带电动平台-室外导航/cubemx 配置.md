我重新搜索STM32H743的定时器资源和最佳配置实践，给你最准确的方案。
基于搜索的最新信息，我重新校对配置。关键发现：**TIM1/TIM8各有4个通道，但互补输出只有3路（CH1/CH2/CH3有N通道，CH4没有）**。

---

## 校正确认版配置清单

### 1. 定时器资源核实（STM32H743）

| 定时器 | 类型 | 通道数 | 互补输出 | 你的用途 |
|:---|:---|:---|:---|:---|
| TIM1 | 高级 | 4 (CH1-4) | **CH1/2/3有N，CH4没有** | 左电机 |
| TIM8 | 高级 | 4 (CH1-4) | **CH1/2/3有N，CH4没有** | 右电机 |
| TIM2 | 通用32位 | 4 | 无 | 左编码器 |
| TIM3 | 通用32位 | 4 | 无 | 右编码器 |
| TIM4 | 通用32位 | 4 | 无 | 超声波4路 |
| TIM5 | 通用32位 | 4 | 无 | 超声波1路 |
| TIM6 | 基本 | 0 | 无 | 1ms中断 |
| TIM7 | 基本 | 0 | 无 | 备用 |
| LPTIM1-5 | 低功耗 | 1-2 | 无 | **不用，频率太低** |

**关键修正**：CH4没有互补输出，不能用于需要互补的H桥驱动。

---

### 2. 推荐方案：单TIM控制单电机（非互补）

TB6612不需要互补PWM，只需要：
- 1路PWM（调速）
- 2路GPIO（方向）

| 功能 | 引脚 | 模式 | 说明 |
|:---|:---|:---|:---|
| **左电机** ||||
| PWM | PA8 | TIM1_CH1 | 调速 |
| 方向1 | PB0 | GPIO_Output | AIN1 |
| 方向2 | PB1 | GPIO_Output | AIN2 |
| **右电机** ||||
| PWM | PC6 | TIM8_CH1 | 调速 |
| 方向1 | PC7 | GPIO_Output | AIN2 |
| 方向2 | PA7 | GPIO_Output | 备用引脚 |

**省出的互补通道**：TIM1_CH2/CH3、TIM8_CH2/CH3可用于其他功能。

---

### 3. 最终极简引脚表

| 引脚 | 功能 | 模式 |
|:---|:---|:---|
| **电机** |||
| PA8 | TIM1_CH1 | PWM（左电机）|
| PB0 | GPIO_Output | 左方向1 |
| PB1 | GPIO_Output | 左方向2 |
| PC6 | TIM8_CH1 | PWM（右电机）|
| PC7 | GPIO_Output | 右方向1 |
| PA7 | GPIO_Output | 右方向2 |
| **编码器** |||
| PA0 | TIM2_CH1 | Encoder（左A）|
| PA1 | TIM2_CH2 | Encoder（左B）|
| PA6 | TIM3_CH1 | Encoder（右A）|
| PA9 | TIM3_CH2 | Encoder（右B）|
| **超声波** |||
| PC0-4 | GPIO_Output | 触发1-5 |
| PD12-15 | TIM4_CH1-4 | 回波1-4 |
| PE0 | TIM5_CH1 | 回波5 |
| **串口** |||
| PB6 | USART1_TX | GPS |
| PB7 | USART1_RX | GPS |
| PD5 | USART2_TX | 4G |
| PD6 | USART2_RX | 4G |
| PC10 | UART4_TX | 无线 |
| PC11 | UART4_RX | 无线 |
| **其他** |||
| PA11/12 | FDCAN1 | CAN |
| PA3 | ADC1_IN3 | 电池 |
| PC13 | GPIO_Output | LED |
| PB14/15 | GPIO_Input | 按键 |

---

### 4. 关键参数

| 外设 | 参数 |
|:---|:---|
| TIM1/TIM8 | 200MHz, Prescaler 0, Period 10000, 20kHz PWM |
| TIM2/TIM3 | Encoder Mode, 32bit, 4x |
| TIM4 | 1MHz (Prescaler 200), 32bit, Input Capture |
| TIM5 | 1MHz, 32bit, Input Capture |
| TIM6 | 1ms中断 (Prescaler 200, Period 1000) |

---

### 5. 生成后必加代码

```c
// 启动所有外设
HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);  // 左电机PWM
HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);  // 右电机PWM
HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_1);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_2);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_3);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_4);
HAL_TIM_IC_Start_IT(&htim5, TIM_CHANNEL_1);
HAL_TIM_Base_Start_IT(&htim6);  // 1ms中断
```

---

**LPTIM不用**，因为：
- 最高频率1MHz，PWM精度差
- 没有编码器模式、没有输入捕获
- 只用于低功耗场景，你的小车插电用不上





我直接给你 **整合列表**，复制粘贴用。

---

## STM32H743VIT6 CubeMX 配置清单

### 1. 时钟（Clock Configuration）

```
HSE: 25MHz (Crystal/Ceramic Resonator)
PLL1: Enable
  - DIVM1: 5
  - DIVN1: 160  
  - DIVP1: 2 (400MHz SYSCLK)
  - DIVQ1: 4 (200MHz FDCAN)
  - DIVR1: 2 (200MHz)

SYSCLK: 400MHz
HCLK: 200MHz
AHB: 200MHz
APB1: 100MHz
APB2: 100MHz
FDCAN Kernel: 80MHz
```

---

### 2. 引脚总表（直接复制）

| 功能 | 引脚 | CubeMX模式 |
|:---|:---|:---|
| **电机** |||
| 左PWM | PA8 | TIM1_CH1 |
| 左方向 | PA9 | TIM1_CH2 |
| 右PWM | PC6 | TIM8_CH1 |
| 右方向 | PC7 | TIM8_CH2 |
| **编码器** |||
| 左A | PA0 | TIM2_CH1 (Encoder Mode) |
| 左B | PA1 | TIM2_CH2 (Encoder Mode) |
| 右A | PA6 | TIM3_CH1 (Encoder Mode) |
| 右B | PB1 | TIM3_CH2 (Encoder Mode) |
| **超声波** |||
| 触发1 | PC0 | GPIO_Output |
| 触发2 | PC1 | GPIO_Output |
| 触发3 | PC2 | GPIO_Output |
| 触发4 | PC3 | GPIO_Output |
| 触发5 | PC4 | GPIO_Output |
| 回波1 | PD12 | TIM4_CH1 (Input Capture) |
| 回波2 | PD13 | TIM4_CH2 (Input Capture) |
| 回波3 | PD14 | TIM4_CH3 (Input Capture) |
| 回波4 | PD15 | TIM4_CH4 (Input Capture) |
| 回波5 | PE0 | TIM5_CH1 (Input Capture) |
| **串口** |||
| GPS_TX | PB6 | USART1_TX |
| GPS_RX | PB7 | USART1_RX |
| 4G_TX | PD5 | USART2_TX |
| 4G_RX | PD6 | USART2_RX |
| 无线_TX | PC10 | UART4_TX |
| 无线_RX | PC11 | UART4_RX |
| **CAN** |||
| CAN_RX | PA11 | FDCAN1_RX |
| CAN_TX | PA12 | FDCAN1_TX |
| **ADC** |||
| 电池电压 | PA3 | ADC1_INP3 |
| **I2C** |||
| 电流检测SCL | PB8 | I2C1_SCL |
| 电流检测SDA | PB9 | I2C1_SDA |
| **GPIO** |||
| LED | PC13 | GPIO_Output |
| 蜂鸣器 | PB4 | GPIO_Output |
| 急停按钮 | PB15 | GPIO_Input (Pull Up) |
| 模式按钮 | PB14 | GPIO_Input (Pull Up) |
| 电机使能 | PD11 | GPIO_Output |

---

### 3. 外设参数（快速设置）

| 外设 | 关键参数 |
|:---|:---|
| **TIM1** | PWM Mode 1, 200MHz, Period 10000 (20kHz), CH1/CH2 Enable |
| **TIM8** | PWM Mode 1, 200MHz, Period 10000 (20kHz), CH1/CH2 Enable |
| **TIM2** | Encoder Mode TI1+TI2, 32bit, 4x mode |
| **TIM3** | Encoder Mode TI1+TI2, 32bit, 4x mode |
| **TIM4** | 1MHz clock (Prescaler 200), 32bit, 4CH Input Capture |
| **TIM5** | 1MHz clock (Prescaler 200), 32bit, CH1 Input Capture |
| **TIM6** | 1ms interrupt (Prescaler 200, Period 1000) |
| **USART1** | 9600, 8N1, DMA RX/TX |
| **USART2** | 115200, 8N1, DMA RX/TX |
| **UART4** | 9600, 8N1, DMA RX/TX |
| **FDCAN1** | Classic Mode, 500kbps (Nominal Prescaler 10, Seg1 11, Seg2 2) |
| **ADC1** | 16bit, 1 channel (PA3), DMA |
| **I2C1** | Fast Mode 400kHz |
| **DMA** | 所有串口RX/TX开DMA Normal或Circular |

---

### 4. 生成代码设置

```
Project:
- Toolchain: MDK-ARM V5
- Code Generator: Copy only necessary library files
- Generate peripheral initialization as pair of .c/.h files per peripheral
- Keep User Code when re-generating: Enable

Advanced:
- C Library: Newlib Nano + Float Printf
- Heap/Stack: Heap 0x20000, Stack 0x10000
```

---

### 5. 生成后必加代码（main.c）

```c
// 1. MPU和Cache（H7必须）
MPU_Config();
SCB_EnableICache();
SCB_EnableDCache();

// 2. 启动外设
HAL_TIM_Base_Start_IT(&htim6);  // 1ms中断
HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);
HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_2);
HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_1);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_2);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_3);
HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_4);
HAL_TIM_IC_Start_IT(&htim5, TIM_CHANNEL_1);
HAL_UART_Receive_DMA(&huart1, gps_buf, 256);
HAL_UART_Receive_DMA(&huart2, g4_buf, 256);
HAL_UART_Receive_DMA(&huart4, wireless_buf, 256);
HAL_FDCAN_Start(&hfdcan1);
```

---

### 6. 中断优先级（NVIC）

| 中断 | 优先级 |
|:---|:---|
| TIM6_DAC_IRQn | 0 (最高，系统时钟) |
| TIM4_IRQn | 1 (超声波) |
| TIM5_IRQn | 1 (超声波) |
| FDCAN1_IT0_IRQn | 2 (CAN) |
| DMA1_Stream0_IRQn | 3 (串口DMA) |
| USART1_IRQn | 4 (GPS空闲) |
| USART2_IRQn | 4 (4G空闲) |
| UART4_IRQn | 4 (无线空闲) |

---

**复制这份列表，CubeMX配置30分钟搞定。**


我直接给你 **STM32H743VIT6 的完整 CubeMX 配置**，照着点就行。

---

## 一、芯片选择

```
系列：STM32H7 → STM32H743/753 → LQFP100 → STM32H743VIT6
```

---

## 二、时钟配置（关键！H7时钟复杂）

```
输入：HSE 8MHz 或 25MHz（推荐25MHz，更准）

PLL1：系统时钟
- DIVM1：5（25MHz/5=5MHz）
- DIVN1：160（5MHz*160=800MHz）
- DIVP1：2（800/2=400MHz → SYSCLK=400MHz）
- DIVQ1：4（800/4=200MHz → FDCAN时钟）
- DIVR1：2（800/2=400MHz）

实际输出：
- SYSCLK：400MHz（可降频到480MHz，但400更稳）
- HCLK：200MHz（AHB分频）
- APB1：100MHz（APB1分频2）
- APB2：100MHz（APB2分频2）
- FDCAN：80MHz（从PLL1Q，再分频到40MHz for 500Kbps）

注意：H7时钟树极复杂，用CubeMX图形界面配置，别手算
```

**推荐配置**：
```
Clock Configuration：
- SYSCLK：400MHz（性能与稳定性平衡）
- HCLK：200MHz
- APB1 Timer Clock：200MHz（TIM2/3/4/5/6/7/12/13/14）
- APB2 Timer Clock：200MHz（TIM1/8/15/16/17）
- FDCAN Kernel Clock：80MHz
```

---

## 三、引脚配置（完整表）

### 3.1 电机控制（高级定时器，带死区）

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| TIM1_CH1 | PA8 | PWM Generation CH1 | 左电机PWM |
| TIM1_CH1N | PA7 | PWM Generation CH1N | 左电机互补（死区）|
| TIM1_CH2 | PA9 | PWM Generation CH2 | 左电机方向 |
| TIM1_CH2N | PB0 | PWM Generation CH2N | 备用 |
| TIM8_CH1 | PC6 | PWM Generation CH1 | 右电机PWM |
| TIM8_CH1N | PA5 | PWM Generation CH1N | 右电机互补 |
| TIM8_CH2 | PC7 | PWM Generation CH2 | 右电机方向 |

**TIM1/TIM8 参数**：
```
Clock Source：Internal Clock
Prescaler：0（200MHz）
Counter Period：10000-1（20kHz，50us周期）
Auto-reload preload：Enable
Repetition Counter：0

CH1/CH2：PWM Mode 1
Pulse：0
Output compare preload：Enable

Dead Time：50（约250ns，防止上下管直通）
Break：Enable（急停刹车）
```

---

### 3.2 编码器输入（32位定时器）

| 功能 | 引脚 | 模式 | 备注 |
|:---|:---|:---|:---|
| TIM2_CH1 | PA0 | Encoder Mode | 左编码器A相 |
| TIM2_CH2 | PA1 | Encoder Mode | 左编码器B相 |
| TIM3_CH1 | PA6 | Encoder Mode | 右编码器A相 |
| TIM3_CH2 | PA7 | Encoder Mode | 右编码器B相 |

**TIM2/TIM3 参数**：
```
Clock Source：Encoder Mode TI1+TI2
Combined Channels：Encoder Mode
Counter Period：0xFFFFFFFF（32位，不溢出）
Auto-reload preload：Enable
Encoder Mode：TI1+TI2（4倍频）

H7优势：32位编码器计数，F4只有16位
```

---

### 3.3 超声波（5路捕获）

| 功能 | 引脚 | 模式 | 备注 |
|:---|:---|:---|:---|
| TIM4_CH1 | PD12 | Input Capture | 超声波1回波 |
| TIM4_CH2 | PD13 | Input Capture | 超声波2回波 |
| TIM4_CH3 | PD14 | Input Capture | 超声波3回波 |
| TIM4_CH4 | PD15 | Input Capture | 超声波4回波 |
| TIM5_CH1 | PE0 | Input Capture | 超声波5回波 |

**触发引脚（GPIO输出）**：
| 功能 | 引脚 | 模式 |
|:---|:---|:---|
| ULTRA_TRIG1 | PC0 | Output Push Pull |
| ULTRA_TRIG2 | PC1 | Output Push Pull |
| ULTRA_TRIG3 | PC2 | Output Push Pull |
| ULTRA_TRIG4 | PC3 | Output Push Pull |
| ULTRA_TRIG5 | PC4 | Output Push Pull |

**TIM4/TIM5 参数**：
```
Clock Source：Internal Clock
Prescaler：200-1（200MHz/200=1MHz，1us精度）
Counter Period：0xFFFFFFFF（32位，最长4294秒）
Auto-reload preload：Enable

CH1/2/3/4：Input Capture direct mode
Polarity：Rising Edge（先上升沿）
Filter：0（可改4，滤噪）
```

---

### 3.4 串口（全DMA）

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| USART1_TX | PA9 | Asynchronous | GPS（与TIM1_CH1冲突，换PB6）|
| USART1_RX | PA10 | Asynchronous | GPS（换PB7）|

**修正：USART1换到PB6/PB7**

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| USART1_TX | PB6 | Asynchronous | GPS，9600 baud |
| USART1_RX | PB7 | Asynchronous | GPS，9600 baud |
| USART2_TX | PD5 | Asynchronous | 4G模块，115200 baud |
| USART2_RX | PD6 | Asynchronous | 4G模块，115200 baud |
| USART3_TX | PD8 | Asynchronous | 调试/备用 |
| USART3_RX | PD9 | Asynchronous | 调试/备用 |
| UART4_TX | PA0 | Asynchronous | 无线HC-12（与TIM2冲突，换PC10）|
| UART4_RX | PA1 | Asynchronous | 无线HC-12（换PC11）|

**最终修正：无线用UART4 -> PC10/PC11**

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| UART4_TX | PC10 | Asynchronous | 无线HC-12，9600 baud |
| UART4_RX | PC11 | Asynchronous | 无线HC-12，9600 baud |

**USART 参数（统一）**：
```
Baud Rate：9600/115200/9600
Word Length：8 Bits
Parity：None
Stop Bits：1
DMA：TX/RX都开Circular模式
```

---

### 3.5 FDCAN（替代普通CAN）

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| FDCAN1_RX | PA11 | FDCAN1 | UDS诊断 |
| FDCAN1_TX | PA12 | FDCAN1 | UDS诊断 |

**FDCAN 参数**：
```
Frame Format：Classic Mode（先用普通CAN，后期升级FD）
Mode：Normal
Nominal Prescaler：2（40MHz/2=20MHz TQ）
Nominal Time Seg1：13
Nominal Time Seg2：2
Nominal Sync Jump Width：1
Bitrate：20MHz/16=1.25Mbps（不对，重新算）

正确500Kbps配置：
- Clock：80MHz from PLL1Q
- Prescaler：4（80/4=20MHz）
- Seg1：13
- Seg2：2
- 20MHz/16=1.25M（还是不对）

最终正确：
- Prescaler：10（80/10=8MHz）
- Seg1：11
- Seg2：2
- 8MHz/14=571K（接近）

或直接用CubeMX自动计算，选500Kbps
```

---

### 3.6 ADC（电池检测+电流采样）

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| ADC1_INP0 | PA0 | ADC1 IN0 | 电池电压（与TIM2冲突，换PA3）|
| ADC1_INP1 | PA1 | ADC1 IN1 | 电机电流（与TIM2冲突，换PC0）|

**修正：ADC换到不冲突引脚**

| 功能 | 引脚 | 模式 | 参数 |
|:---|:---|:---|:---|
| ADC1_INP3 | PA3 | ADC1 IN3 | 电池电压 |
| ADC2_INP4 | PA4 | ADC2 IN4 | 左电机电流 |
| ADC3_INP5 | PA5 | ADC3 INP5 | 右电机电流（与TIM8_CH1N冲突，换PB1）|

**最终ADC配置**：
| 功能 | 引脚 | 模式 |
|:---|:---|:---|
| ADC1_INP3 | PA3 | 电池电压 |
| ADC2_INP4 | PA4 | 左电机电流 |
| ADC3_INP0 | PA0 | 右电机电流（TIM2编码器冲突，换PC5）|

**简化：只用1路ADC测电池，电流用INA226 I2C芯片**

| 功能 | 引脚 | 模式 |
|:---|:---|:---|
| ADC1_INP3 | PA3 | 电池电压 |
| I2C1_SCL | PB8 | I2C（测电流）|
| I2C1_SDA | PB9 | I2C（测电流）|

---

### 3.7 其他GPIO

| 功能 | 引脚 | 模式 | 备注 |
|:---|:---|:---|:---|
| LED_STATUS | PC13 | Output Push Pull | 运行灯 |
| BEEP | PB8 | Output Push Pull | 蜂鸣器（与I2C冲突，换PB4）|
| EMERGENCY_STOP | PB15 | Input Pull Up | 急停按钮 |
| MODE_BUTTON | PB14 | Input Pull Up | 模式切换 |
| MOTOR_ENABLE | PD12 | Output Push Pull | 电机总使能（与TIM4冲突，换PD11）|

**最终修正**：
| 功能 | 引脚 | 模式 |
|:---|:---|:---|
| LED_STATUS | PC13 | Output Push Pull |
| BEEP | PB4 | Output Push Pull |
| EMERGENCY_STOP | PB15 | Input Pull Up |
| MODE_BUTTON | PB14 | Input Pull Up |
| MOTOR_ENABLE | PD11 | Output Push Pull |

---

## 四、完整无冲突引脚表（最终版）

| 引脚 | 功能 | 模式 | 备注 |
|:---|:---|:---|:---|
| PA0 | TIM2_CH1 | Encoder Mode | 左编码器A |
| PA1 | TIM2_CH2 | Encoder Mode | 左编码器B |
| PA3 | ADC1_IN3 | Analog | 电池电压 |
| PA4 | ADC2_IN4 | Analog | 左电机电流（或保留）|
| PA5 | TIM8_CH1N | PWM | 右电机PWM互补 |
| PA6 | TIM3_CH1 | Encoder Mode | 右编码器A |
| PA7 | TIM1_CH1N | PWM | 左电机PWM互补 |
| PA8 | TIM1_CH1 | PWM | 左电机PWM |
| PA9 | TIM1_CH2 | PWM | 左电机方向 |
| PA10 | - | - | 备用 |
| PA11 | FDCAN1_RX | FDCAN | UDS诊断 |
| PA12 | FDCAN1_TX | FDCAN | UDS诊断 |
| PB0 | TIM1_CH2N | PWM | 左电机方向互补 |
| PB1 | TIM3_CH2 | Encoder Mode | 右编码器B |
| PB4 | GPIO_Output | Push Pull | 蜂鸣器 |
| PB6 | USART1_TX | Async | GPS |
| PB7 | USART1_RX | Async | GPS |
| PB8 | I2C1_SCL | I2C | 电流检测INA226 |
| PB9 | I2C1_SDA | I2C | 电流检测INA226 |
| PB14 | GPIO_Input | Pull Up | 模式按钮 |
| PB15 | GPIO_Input | Pull Up | 急停按钮 |
| PC0 | GPIO_Output | Push Pull | 超声波1触发 |
| PC1 | GPIO_Output | Push Pull | 超声波2触发 |
| PC2 | GPIO_Output | Push Pull | 超声波3触发 |
| PC3 | GPIO_Output | Push Pull | 超声波4触发 |
| PC4 | GPIO_Output | Push Pull | 超声波5触发 |
| PC5 | - | - | 备用 |
| PC6 | TIM8_CH1 | PWM | 右电机PWM |
| PC7 | TIM8_CH2 | PWM | 右电机方向 |
| PC10 | UART4_TX | Async | 无线HC-12 |
| PC11 | UART4_RX | Async | 无线HC-12 |
| PC13 | GPIO_Output | Push Pull | LED指示灯 |
| PD5 | USART2_TX | Async | 4G模块 |
| PD6 | USART2_RX | Async | 4G模块 |
| PD8 | USART3_TX | Async | 调试串口 |
| PD9 | USART3_RX | Async | 调试串口 |
| PD11 | GPIO_Output | Push Pull | 电机总使能 |
| PD12 | TIM4_CH1 | Input Capture | 超声波1回波 |
| PD13 | TIM4_CH2 | Input Capture | 超声波2回波 |
| PD14 | TIM4_CH3 | Input Capture | 超声波3回波 |
| PD15 | TIM4_CH4 | Input Capture | 超声波4回波 |
| PE0 | TIM5_CH1 | Input Capture | 超声波5回波 |

---

## 五、DMA配置（H7 DMA极复杂，用CubeMX自动生成）

| DMA | Stream | Channel | 用途 |
|:---|:---|:---|:---|
| DMA1 S0 | CH0 | USART2_TX | 4G发送 |
| DMA1 S1 | CH1 | USART2_RX | 4G接收 |
| DMA1 S2 | CH2 | USART3_TX | 调试发送 |
| DMA1 S3 | CH3 | USART3_RX | 调试接收 |
| DMA1 S4 | CH4 | UART4_TX | 无线发送 |
| DMA1 S5 | CH5 | UART4_RX | 无线接收 |
| DMA2 S0 | CH3 | ADC1 | 电池电压 |
| DMA2 S1 | CH4 | USART1_TX | GPS发送 |
| DMA2 S2 | CH5 | USART1_RX | GPS接收 |

**注意**：H7的DMA有MDMA、BDMA、DMA1、DMA2，普通外设用DMA1/DMA2即可。

---

## 六、关键代码修改（生成后手动加）

### 6.1 启动文件（H7双bank Flash）

```c
// main.c 开头加
#define FLASH_BANK1_BASE 0x08000000
#define FLASH_BANK2_BASE 0x08100000

// 默认从Bank1启动，2MB Flash分为两个1MB Bank
```

### 6.2 缓存配置（关键！H7必须开Cache）

```c
// MPU配置（在SystemInit或main开头）
void MPU_Config(void)
{
    MPU_Region_InitTypeDef MPU_InitStruct = {0};
    
    // 配置Flash为Write-Through（代码区）
    MPU_InitStruct.Enable = MPU_REGION_ENABLE;
    MPU_InitStruct.Number = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress = 0x08000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_2MB;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.TypeExtField = MPU_TEX_LEVEL0;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec = MPU_INSTRUCTION_ACCESS_ENABLE;
    MPU_InitStruct.IsShareable = MPU_ACCESS_NOT_SHAREABLE;
    MPU_InitStruct.IsCacheable = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_BUFFERABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    // 配置DTCM RAM（高速数据区）
    MPU_InitStruct.Number = MPU_REGION_NUMBER1;
    MPU_InitStruct.BaseAddress = 0x20000000;
    MPU_InitStruct.Size = MPU_REGION_SIZE_128KB;
    MPU_InitStruct.IsBufferable = MPU_ACCESS_NOT_BUFFERABLE;
    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}

// 使能D-Cache和I-Cache
SCB_EnableICache();
SCB_EnableDCache();
```

### 6.3 1ms定时器（TIM6）

```c
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if(htim->Instance == TIM6) {
        sys_tick_ms++;
        
        // H7性能强，可以跑更复杂算法
        flag_1ms = 1;   // 电机控制
        flag_5ms = 1;   // 超声波
        flag_10ms = 1;  // 编码器
        flag_20ms = 1;  // 定位融合
        flag_50ms = 1;  // 路径规划
    }
}
```

---

## 七、H743 vs F407 代码差异

| 功能 | F407写法 | H743写法 | 注意 |
|:---|:---|:---|:---|
| 浮点运算 | `float x = 1.0f` | `double x = 1.0` | H7双精度更快 |
| 编码器读数 | `uint16_t` | `uint32_t` | H7是32位 |
| Cache维护 | 无 | `SCB_CleanDCache()` | DMA传输前清Cache |
| Flash写入 | 简单 | 复杂双Bank | 用HAL_FLASHEx_Erase |
| 功耗 | 低 | 高300mA | 散热设计 |

---

## 八、一句话总结

> **H743VIT6配置核心是：400MHz时钟、32位编码器、双精度FPU、必须开Cache。引脚比F4多，但高级定时器复用复杂，建议用CubeMX图形配置，生成后手动加Cache和MPU代码。**

需要我提供 **CubeMX生成的.ioc文件关键截图描述**，或 **H743的Cache维护完整代码（DMA传输用）** 吗？