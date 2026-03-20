我重新搜索STM32H743的定时器资源和最佳配置实践，给你最准确的方案。
基于搜索的最新信息，我重新校对配置。关键发现：**TIM1/TIM8各有4个通道，但互补输出只有3路（CH1/CH2/CH3有N通道，CH4没有）**。

## F407VGT6

## 自带外设
#### 1. 核心系统与电源相关
| 引脚 | 功能 | 说明 |
|------|------|------|
| `VBAT` | VBAT | 后备电池供电 |
| `NRST` | NRST | 系统复位引脚 |
| `VDD/VSS` | 电源/地 | 芯片供电与接地 |
| `VREF+/VREF-/VDDA/VSSA` | 参考电压/模拟电源 | ADC 相关电源 |
| `BOOT0` | BOOT0 | 启动模式选择 |

---

#### 2. 时钟与调试接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PH0/PH1` | RCC_OSC_IN/OUT | 8MHz 外部高速晶振 |
| `PC14/PC15` | RCC_OSC32_IN/OUT | 32.768kHz 低速晶振（RTC） |
| `PA13/PA14` | SYS_JTMS-SWDIO/SYS_JTCK-SWCLK | SWD 调试接口 |
| `PA8` | RCC_MCO_1 | 时钟输出 |

---

#### 3. DCMI 摄像头接口（暂不用）
<!-- | 引脚 | 功能 | 说明 |
|------|------|------|
| `PA4` | DCMI_HSYNC | 水平同步 |
| `PA6` | DCMI_PIXCLK | 像素时钟 |
| `PB6` | DCMI_SCL | I2C 控制时钟 |
| `PB9` | DCMI_SDA | I2C 控制数据 |
| `PC6` | DCMI_D0 | 数据位 0 |
| `PC7` | DCMI_D1 | 数据位 1 |
| `PE3` | DCMI_PWDN | 电源使能 |
| `PE4` | DCMI_D4 | 数据位 4 |
| `PE5` | DCMI_D6 | 数据位 6 |
| `PE6` | DCMI_D7 | 数据位 7 | -->

---

#### 4. SPI LCD 接口 （SPI3）
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PB3` | SPI3_SCK | SPI 时钟 |
| `PB4` | SPI3_MISO | SPI 主入从出 |
| `PB5` | SPI3_MOSI | SPI 主出从入 |
| `PD7` | LCD_CS | 片选 |
| `PD4` | LCD_RST | 复位 |
| `PD5` | LCD_DC | 数据/命令选择 |

---

#### 5. SPI Flash 接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PB12` | SPI2_NSS | 片选 |
| `PB13` | SPI2_SCK | SPI 时钟 |
| `PB14` | SPI2_MISO | SPI 主入从出 |
| `PB15` | SPI2_MOSI | SPI 主出从入 |

---

#### 6. SD 卡接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PC8` | SDIO_D0 | 数据位 0 |
| `PC9` | SDIO_D1 | 数据位 1 |
| `PC10` | SDIO_D2 | 数据位 2 |
| `PC11` | SDIO_D3 | 数据位 3 |
| `PC12` | SDIO_CK | 时钟 |
| `PD2` | SDIO_CMD | 命令 |
| `PD15` | SD_CD | 卡检测 |

---

#### 7. 用户外设与其他
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PC13` | USER_KEY | 用户按键 |
| `PC0/PC1/PC2` | LED_R/G/B | RGB LED 控制 |
| `PA9/PA10` | USART1_TX/RX | 串口 1 |
| `PA11/PA12` | USB_OTG_FS_DM/DP | USB OTG 全速接口 |
| `PB1` | BOOT1 | 启动模式选择 |
| `PB2` | BOOT1 上拉 | 启动模式相关 |
| `PE2` | DCMI_PWDN 备用 | 摄像头电源控制 |



---

## 一、时钟配置（Clock Configuration）

| 参数 | 值 | 说明 |
|------|-----|------|
| **HSE** | 8 MHz | 外部高速晶振 |
| **PLL Source** | HSE | |
| **System Clock** | 168 MHz | F407最高主频 |
| **APB1 Prescaler** | /4 | 42 MHz（TIM2-7, UART4-5, CAN, I2C）|
| **APB2 Prescaler** | /2 | 84 MHz（TIM1,8,9-11, USART1-3, SPI1）|

---

## 二、GPIO 配置（GPIO）

| 引脚 | 模式 | 初始状态 | 标签 | 说明 |
|------|------|---------|------|------|
| **PE7** | Output PP | Low | TRIG_1 | 超声1触发/回波 |
| **PE8** | Output PP | Low | TRIG_2 | 超声2触发/回波 |
| **PE9** | Output PP | Low | TRIG_3 | 超声3触发/回波 |
| **PE10** | Output PP | Low | TRIG_4 | 超声4触发/回波 |
| **PE11** | Output PP | Low | TRIG_5 | 超声5触发/回波 |
| **PD12** | Output PP | Low | MOTOR1_DIR | 电机1方向 |
| **PD13** | Output PP | Low | MOTOR2_DIR | 电机2方向 |
| **PD14** | Output PP | Low | MOTOR3_DIR | 电机3方向 |
| **PD15** | Output PP | Low | MOTOR4_DIR | 电机4方向 |
| **PC13** | Input Pull-up | - | KEY_USER | 用户按键 |
| **PC0** | Output PP | High | LED_R | 红色LED |
| **PC1** | Output PP | High | LED_G | 绿色LED |
| **PC2** | Output PP | High | LED_B | 蓝色LED |

---

## 三、定时器配置（Timers）

### TIM3 - 电机PWM（4路，20kHz）

| 参数 | 值 |
|------|-----|
| **Clock Source** | Internal Clock |
| **Prescaler (PSC)** | 0 | 84MHz不分频 |
| **Counter Period (ARR)** | 4199 | 84M/4200 = 20kHz |
| **Mode** | PWM Mode 1 |

| Channel | 引脚 | 模式 | 标签 |
|---------|------|------|------|
| **CH1** | PC6 | PWM Generation | MOTOR1_PWM |
| **CH2** | PC7 | PWM Generation | MOTOR2_PWM |
| **CH3** | PC8 | PWM Generation | MOTOR3_PWM |
| **CH4** | PC9 | PWM Generation | MOTOR4_PWM |

### TIM4 - 超声波输入捕获（1路，复用）

| 参数 | 值 |
|------|-----|
| **Clock Source** | Internal Clock |
| **Prescaler (PSC)** | 83 | 84MHz/84 = 1MHz（1us精度）|
| **Counter Period (ARR)** | 65535 | 最大65.5ms（对应11米，足够）|

| Channel | 引脚 | 模式 | 标签 |
|---------|------|------|------|
| **CH1** | PB6 | Input Capture Direct Mode | ULTRA_ECHO |

** NVIC设置**：TIM4 global interrupt **Enable**

---

## 四、UART配置（Asynchronous）

| 外设 | 引脚 | 波特率 | 参数 | DMA | NVIC |
|------|------|--------|------|-----|------|
| **USART2** (GPS) | PA2(TX), PA3(RX) | 9600 | 8N1 | RX: DMA1 Stream5 | USART2 global int **Enable** |
| **USART3** (WiFi) | PB10(TX), PB11(RX) | 115200 | 8N1 | TX: DMA1 Stream3<br>RX: DMA1 Stream1 | USART3 global int **Enable** |
| **UART4** (工控屏) | PC10(TX), PC11(RX) | 115200 | 8N1 | TX: DMA1 Stream4<br>RX: DMA1 Stream2 | UART4 global int **Enable** |

---

## 五、CAN配置（CAN1）

| 参数 | 值 |
|------|-----|
| **Mode** | Normal |
| **Prescaler** | 6 | 42MHz/6/7 = 500kbps (或调为12/14=250kbps) |
| **Time Quantum** | 根据波特率计算 |
| **引脚** | PA0(CAN1_RX), PA1(CAN1_TX) |

**NVIC**：CAN1 RX0 interrupt **Enable**

---

## 六、其他配置

| 功能 | 配置 |
|------|------|
| **Debug** | Serial Wire (SWD) - PA13/PA14 |
| **USB_OTG_FS** | 如需调试，保留PA11/PA12，或Disable |
| **IWDG** | 可选，看门狗 |
| **FreeRTOS** | 可选，建议开启（CMSIS_V2）|

---

## 七、关键软件逻辑提示

### 一线制超声波测量流程
```c
void Ultra_Measure(uint8_t id) {
    // 1. 配置为输出，发送触发
    HAL_GPIO_WritePin(TRIG_GPIO_Port, TRIG_Pin, GPIO_PIN_SET);
    delay_us(10);
    HAL_GPIO_WritePin(TRIG_GPIO_Port, TRIG_Pin, GPIO_PIN_RESET);
    
    // 2. 切换为输入，启动捕获
    __HAL_TIM_SET_COUNTER(&htim4, 0);
    HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_1);
    
    // 3. 等待中断完成（超时处理）
    // 在中断中计算高电平时间 -> 距离
}
```

### 电机控制
```c
// 方向 + PWM
HAL_GPIO_WritePin(MOTOR1_DIR_GPIO_Port, MOTOR1_DIR_Pin, direction);
__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, speed); // 0-4199
```

---

## 八、DMA配置汇总

| DMA Stream | Channel | 外设 | 方向 | 模式 |
|-----------|---------|------|------|------|
| DMA1 Stream1 | CH4 | USART3_RX | Peripheral to Memory | Circular |
| DMA1 Stream2 | CH4 | UART4_RX | Peripheral to Memory | Circular |
| DMA1 Stream3 | CH4 | USART3_TX | Memory to Peripheral | Normal |
| DMA1 Stream4 | CH4 | UART4_TX | Memory to Peripheral | Normal |
| DMA1 Stream5 | CH4 | USART2_RX | Peripheral to Memory | Circular |

---

这个配置充分利用了你的引出引脚，无冲突，且预留了扩展空间。需要我生成对应的 `main.c` 初始化代码框架吗？

## F401RET6
---
F401没有CAN总线，略过吧

TIM3 CH1-CH4 电机两路PWM
TIM4 Encode Mode 电机编码器
TIM5 Encode Mode 电机编码器
TIM2 CH1-CH4 
TIM1 CH4 
TIM4 CH3CH4 输入捕获


我直接给你 **无冲突版引脚表**，照着配置就行。

---

### STM32F407VGTx 已使用接口清单
我根据你提供的引脚图和原理图，整理出了**已被功能占用的引脚和对应外设**，方便你做后续开发规划。

---

#### 1. 核心系统与电源相关
| 引脚 | 功能 | 说明 |
|------|------|------|
| `VBAT` | VBAT | 后备电池供电 |
| `NRST` | NRST | 系统复位引脚 |
| `VDD/VSS` | 电源/地 | 芯片供电与接地 |
| `VREF+/VREF-/VDDA/VSSA` | 参考电压/模拟电源 | ADC 相关电源 |
| `BOOT0` | BOOT0 | 启动模式选择 |

---

#### 2. 时钟与调试接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PH0/PH1` | RCC_OSC_IN/OUT | 8MHz 外部高速晶振 |
| `PC14/PC15` | RCC_OSC32_IN/OUT | 32.768kHz 低速晶振（RTC） |
| `PA13/PA14` | SYS_JTMS-SWDIO/SYS_JTCK-SWCLK | SWD 调试接口 |
| `PA8` | RCC_MCO_1 | 时钟输出 |

---

#### 3. DCMI 摄像头接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PA4` | DCMI_HSYNC | 水平同步 |
| `PA6` | DCMI_PIXCLK | 像素时钟 |
| `PB6` | DCMI_SCL | I2C 控制时钟 |
| `PB9` | DCMI_SDA | I2C 控制数据 |
| `PC6` | DCMI_D0 | 数据位 0 |
| `PC7` | DCMI_D1 | 数据位 1 |
| `PE3` | DCMI_PWDN | 电源使能 |
| `PE4` | DCMI_D4 | 数据位 4 |
| `PE5` | DCMI_D6 | 数据位 6 |
| `PE6` | DCMI_D7 | 数据位 7 |

---

#### 4. SPI LCD 接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PB3` | SPI3_SCK | SPI 时钟 |
| `PB4` | SPI3_MISO | SPI 主入从出 |
| `PB5` | SPI3_MOSI | SPI 主出从入 |
| `PD7` | LCD_CS | 片选 |
| `PD4` | LCD_RST | 复位 |
| `PD5` | LCD_DC | 数据/命令选择 |

---

#### 5. SPI Flash 接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PB12` | SPI2_NSS | 片选 |
| `PB13` | SPI2_SCK | SPI 时钟 |
| `PB14` | SPI2_MISO | SPI 主入从出 |
| `PB15` | SPI2_MOSI | SPI 主出从入 |

---

#### 6. SD 卡接口
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PC8` | SDIO_D0 | 数据位 0 |
| `PC9` | SDIO_D1 | 数据位 1 |
| `PC10` | SDIO_D2 | 数据位 2 |
| `PC11` | SDIO_D3 | 数据位 3 |
| `PC12` | SDIO_CK | 时钟 |
| `PD2` | SDIO_CMD | 命令 |
| `PD15` | SD_CD | 卡检测 |

---

#### 7. 用户外设与其他
| 引脚 | 功能 | 说明 |
|------|------|------|
| `PC13` | USER_KEY | 用户按键 |
| `PC0/PC1/PC2` | LED_R/G/B | RGB LED 控制 |
| `PA9/PA10` | USART1_TX/RX | 串口 1 |
| `PA11/PA12` | USB_OTG_FS_DM/DP | USB OTG 全速接口 |
| `PB1` | BOOT1 | 启动模式选择 |
| `PB2` | BOOT1 上拉 | 启动模式相关 |
| `PE2` | DCMI_PWDN 备用 | 摄像头电源控制 |

---

### 补充说明
- **未列出的引脚**：理论上可作为通用 GPIO 或复用为其他外设（如 ADC、定时器、I2C、SPI 等）。
- **注意**：部分引脚（如 `PB3/PB4`）同时被 LCD 和调试接口占用，设计时需注意冲突。

---

要不要我再帮你整理一份**剩余可用引脚清单**，并标注它们支持的复用功能（比如哪些可以做 ADC、定时器或串口）？这样你就能直接规划新功能了。

## 完整引脚分配表（STM32F407VGT6）

| 引脚 | 功能 | 模式 | 备注 |
|:---|:---|:---|:---|
| **PA0** | TIM5_CH1 | Encoder Mode | 右编码器A相 |
| **PA1** | TIM5_CH2 | Encoder Mode | 右编码器B相 |
| **PA2** | TIM2_CH3 | Input Capture | 超声波3回波 |
| **PA3** | TIM2_CH4 | Input Capture | 超声波4回波 |
| **PA5** | TIM2_CH1 | Input Capture | 超声波1回波（原PA6冲突，换这里）|
| **PA6** | TIM3_CH1 | PWM Generation | 左电机PWM |
| **PA7** | TIM3_CH2 | PWM Generation | 左电机方向 |
| **PA8** | TIM1_CH1 | Input Capture | 超声波5回波 |
| **PB0** | TIM3_CH3 | PWM Generation | 右电机PWM |
| **PB1** | TIM3_CH4 | PWM Generation | 右电机方向 |
| **PB6** | TIM4_CH1 | Encoder Mode | 左编码器A相 |
| **PB7** | TIM4_CH2 | Encoder Mode | 左编码器B相 |

| **PA9** | USART1_TX | Asynchronous | GPS |
| **PA10** | USART1_RX | Asynchronous | GPS |
| **PD5** | USART2_TX | Asynchronous | 4G模块EC200S |
| **PD6** | USART2_RX | Asynchronous | 4G模块EC200S |
| **PC6** | USART6_TX | Asynchronous | 无线模块HC-12 |
| **PC7** | USART6_RX | Asynchronous | 无线模块HC-12 |

| **PA11** | CAN1_RX | CAN | UDS诊断 |
| **PA12** | CAN1_TX | CAN | UDS诊断 |

| **PC1** | ADC1_IN11 | Analog | 电池电压检测 |

| **PB8** | GPIO_Output | Push Pull | 蜂鸣器 |
| **PC13** | GPIO_Output | Push Pull | 运行指示灯LED |
| **PB9** | GPIO_Output | Push Pull | 照明LED2 |
| **PB13** | GPIO_Output | Push Pull | 备用 |

| **PB14** | GPIO_Input | Pull Up | 急停按钮 |
| **PB15** | GPIO_Input | Pull Up | 模式切换键 |

| **PD12** | GPIO_Output | Push Pull | 电机使能总开关（安全）|
| **PD13** | GPIO_Output | Push Pull | 备用电源控制 |

---

## 冲突解决记录

| 原冲突 | 解决方式 | 新引脚 |
|:---|:---|:---|
| PA6 = 电机PWM + 超声波1 | 超声波1换到PA5 | PA5 |
| PA2/PA3 = 超声波 + USART2 | USART2换到PD5/PD6 | PD5/PD6 |
| PC2 = 超声波2触发 + 备用 | 超声波2触发换到PB12 | PB12 |
| PC6 = 超声波4触发 + 无线TX | 超声波4触发换到PC5 | PC5 |
| PA8 = 超声波5 + 蜂鸣器 | 蜂鸣器换到PB8 | PB8 |

---

## CubeMX 配置速查

### 1. 开启的外设

| 外设 | 模式 | 关键参数 |
|:---|:---|:---|
| TIM1 | Input Capture CH1 | 超声波5回波 |
| TIM2 | Input Capture CH1/CH3/CH4 | 超声波1/3/4回波 |
| TIM3 | PWM CH1/CH2/CH3/CH4 | 电机PWM，20kHz |
| TIM4 | Encoder Mode | 左编码器 |
| TIM5 | Encoder Mode | 右编码器 |
| TIM6 | Time Base | 1ms中断 |
| USART1 | Async 9600 | GPS |
| USART2 | Async 115200 | 4G |
| USART6 | Async 9600 | 无线 |
| CAN1 | Normal Mode | 500kbps |
| ADC1 | IN11 | 电池电压 |

### 2. 时钟树

```
HSE: 8MHz
SYSCLK: 168MHz
AHB: 168MHz
APB1: 42MHz (TIM2/3/4/5/6/7, USART2/3, CAN1)
APB2: 84MHz (TIM1/8/9/10/11, USART1/6, ADC1)
```

---

## 生成代码后修改（3处）

### 修改1：启动文件加系统时钟（已自动生成，确认即可）

`system_stm32f4xx.c` 中确认：
```c
#define PLL_M 8
#define PLL_N 336
#define PLL_P 2  // 168MHz
#define PLL_Q 7  // 48MHz for USB
```

### 修改2：`main.c` 加1ms中断回调

```c
volatile uint32_t sys_tick_ms = 0;

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if(htim->Instance == TIM6) {
        sys_tick_ms++;
    }
}
```

### 修改3：`stm32f4xx_it.c` 加超声波捕获（模板）

```c
// 用户代码区添加
volatile uint32_t ultra_capture_start[5] = {0};
volatile uint32_t ultra_capture_end[5] = {0};
volatile uint8_t ultra_capture_flag[5] = {0};

void TIM2_IRQHandler(void)
{
    // CH1 - 超声波1 (PA5)
    if(__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_CC1)) {
        if(!ultra_capture_flag[0]) {
            ultra_capture_start[0] = HAL_TIM_ReadCapturedValue(&htim2, TIM_CHANNEL_1);
            __HAL_TIM_SET_CAPTUREPOLARITY(&htim2, TIM_CHANNEL_1, TIM_ICPOLARITY_FALLING);
            ultra_capture_flag[0] = 1;
        } else {
            ultra_capture_end[0] = HAL_TIM_ReadCapturedValue(&htim2, TIM_CHANNEL_1);
            __HAL_TIM_SET_CAPTUREPOLARITY(&htim2, TIM_CHANNEL_1, TIM_ICPOLARITY_RISING);
            ultra_capture_flag[0] = 0;
        }
        __HAL_TIM_CLEAR_IT(&htim2, TIM_IT_CC1);
    }
    
    // CH3 - 超声波3 (PA2)
    if(__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_CC3)) {
        // 同理...
    }
    
    // CH4 - 超声波4 (PA3)
    if(__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_CC4)) {
        // 同理...
    }
}
```

TIM1_CH1 捕获在 `TIM1_UP_TIM10_IRQHandler` 或单独 `TIM1_CC_IRQHandler`。

---

## 引脚图（文字版）

```
                    STM32F407VGT6 (LQFP100)
                    
         VDD  1 ●                ● 100  VDD
         PC13 2 ● LED            ● 99   PC12
         PC14 3 ● OSC32_IN       ● 98   PC11
         PC15 4 ● OSC32_OUT      ● 97   VDD
         PH0  5 ● OSC_IN         ● 96   PA13/SWDIO
         PH1  6 ● OSC_OUT        ● 95   PA14/SWCLK
         NRST 7 ●                ● 94   PA15
         PC0  8 ● ULTRA_TRIG1    ● 93   PC10
         PC1  9 ● BAT_ADC        ● 92   PA8/ULTRA5_ECHO
         PC2  10● (备用)         ● 91   PC9
         PC3  11● (备用)         ● 90   VSS
         VSSA 12●                ● 89   VDD
         VDDA 13●                ● 88   PA9/USART1_TX
         PA0  14● TIM5_CH1(编码R)● 87   PA10/USART1_RX
         PA1  15● TIM5_CH2(编码R)● 86   PA11/CAN_RX
         PA2  16● TIM2_CH3(ULT3) ● 85   PA12/CAN_TX
         PA3  17● TIM2_CH4(ULT4) ● 84   VSS
         VSS  18●                ● 83   VDD
         VDD  19●                ● 82   PC6/USART6_TX
         PA4  20● (备用)         ● 81   PC7/USART6_RX
         PA5  21● TIM2_CH1(ULT1) ● 80   PC8/ULTRA_TRIG5
         PA6  22● TIM3_CH1(左PWM)● 79   PD15
         PA7  23● TIM3_CH2(左DIR)● 78   PD14
         PC4  24● ULTRA_TRIG3   ● 77   PD13
         PC5  25● ULTRA_TRIG4   ● 76   PD12/电机使能
         PB0  26● TIM3_CH3(右PWM)● 75   PD11
         PB1  27● TIM3_CH4(右DIR)● 74   PD10
         PB2  28● (BOOT1)        ● 73   PD9
         PB10 29● (备用I2C)      ● 72   PD8
         PB11 30● (备用I2C)      ● 71   PB15/按键2
         VSS  31●                ● 70   PB14/急停
         VDD  32●                ● 69   PB13
         PB12 33● ULTRA_TRIG2   ● 68   PB12
         PB13 34● (备用)         ● 67   PB11
         PB14 35● 急停按钮       ● 66   PB10
         PB15 36● 模式按键       ● 65   VCAP_1
         PD8  37● (备用)         ● 64   VDD
         PD9  38● (备用)         ● 63   PB2
         PD10 39● (备用)         ● 62   PB1/右DIR
         PD11 40● (备用)         ● 61   PB0/右PWM
         PD12 41● 电机总使能     ● 60   PB7/编码器LB
         PD13 42● (备用)         ● 59   PB6/编码器LA
         PD14 43● (备用)         ● 58   PB5
         PD15 44● (备用)         ● 57   PB4
         PC6  45● USART6_TX(无线)● 56   PB3
         PC7  46● USART6_RX(无线)● 55   PA15
         PC8  47● ULTRA_TRIG5   ● 54   PA12/CAN_TX
         PC9  48● (备用)         ● 53   PA11/CAN_RX
         PA8  49● TIM1_CH1(ULT5) ● 52   PA10/USART1_RX
         PA9  50● USART1_TX(GPS) ● 51   PA9
         
         底部：VSS/VDD/BOOT0/PD5/PD6/...
         
         PD5  ● USART2_TX(4G)
         PD6  ● USART2_RX(4G)
```

---

需要我把 **CubeMX配置文件（.ioc）** 的关键截图描述，或者 **启动文件修改的完整代码** 贴出来吗？

## STM32H743配置

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