# 蜂鸟灵-R1A\_M5N无线模块驱动开发计划

## 1. 模块概述

蜂鸟灵-R1A\_M5N是一款2.4G无线遥控接收模块，通过串口输出遥控数据帧。

### 1.1 硬件连接

* 仅使用D0串口接收数据（单工通信）

* 波特率：115200bps（根据规格书确认）

* 数据格式：8位数据位，1位停止位，无校验

### 1.2 数据帧格式（根据规格书）

典型数据帧结构：

* 帧头（2字节）：0xAA 0x55

* 数据长度（1字节）

* 按键数据（多位）

* 摇杆数据（多位）

* 校验和（1字节）

## 2. 驱动设计方案

### 2.1 文件结构

```
App/hsc_Lib/3_Driver/
├── hsc_r1a_m5n.h    # 头文件：配置、数据结构、接口声明
└── hsc_r1a_m5n.c    # 源文件：驱动实现
```

### 2.2 功能特性

1. **串口数据接收**：使用中断方式接收，支持帧解析
2. **按键状态获取**：提供当前按键状态查询接口
3. **摇杆数据获取**：提供摇杆ADC值读取接口
4. **按键事件检测**：支持单击、双击、长按检测
5. **信号丢失检测**：检测通信是否中断

### 2.3 配置参数（hsc\_r1a\_m5n.h）

```c
// 串口配置
#define R1A_M5N_UART_HANDLE     huart1      // 使用的串口句柄
#define R1A_M5N_UART_INSTANCE   USART1      // 串口实例

// 定时参数
#define R1A_M5N_CLICK_TIME      300         // 单击最大时间(ms)
#define R1A_M5N_DOUBLE_GAP      300         // 双击间隔最大时间(ms)
#define R1A_M5N_LONG_TIME       800         // 长按判定时间(ms)
#define R1A_M5N_LOST_TIME       500         // 信号丢失判定时间(ms)

// 数据帧配置
#define R1A_M5N_FRAME_HEAD1     0xAA        // 帧头第1字节
#define R1A_M5N_FRAME_HEAD2     0x55        // 帧头第2字节
#define R1A_M5N_FRAME_LEN       10          // 数据帧长度（根据实际规格调整）
```

### 2.4 数据结构

```c
// 按键定义（根据实际规格书定义）
typedef enum {
    R1A_KEY_UP = 0,         // 上
    R1A_KEY_DOWN,           // 下
    R1A_KEY_LEFT,           // 左
    R1A_KEY_RIGHT,          // 右
    R1A_KEY_A,              // A键
    R1A_KEY_B,              // B键
    R1A_KEY_C,              // C键
    R1A_KEY_D,              // D键
    R1A_KEY_NUM             // 按键数量
} R1A_KeyTypeDef;

// 按键事件类型
typedef enum {
    R1A_EVENT_NONE = 0,     // 无事件
    R1A_EVENT_CLICK,        // 单击
    R1A_EVENT_DOUBLE,       // 双击
    R1A_EVENT_LONG          // 长按
} R1A_KeyEventTypeDef;

// 摇杆数据结构
typedef struct {
    uint8_t lx;             // 左摇杆X (0-255, 128为中位)
    uint8_t ly;             // 左摇杆Y (0-255, 128为中位)
    uint8_t rx;             // 右摇杆X (0-255, 128为中位)
    uint8_t ry;             // 右摇杆Y (0-255, 128为中位)
} R1A_StickTypeDef;

// 模块状态结构
typedef struct {
    uint16_t key_state;             // 当前按键状态（位图）
    uint16_t key_last;              // 上次按键状态
    R1A_StickTypeDef stick;         // 摇杆数据
    uint32_t last_rx_time;          // 上次接收时间
    uint8_t is_connected;           // 连接状态
} R1A_StatusTypeDef;
```

### 2.5 API接口

```c
// 初始化
void R1A_M5N_Init(void);

// 数据接收处理（在中断回调中调用）
void R1A_M5N_ReceiveByte(uint8_t byte);

// 获取按键状态（位图）
uint16_t R1A_M5N_GetKeyState(void);

// 检测指定按键是否按下
uint8_t R1A_M5N_IsKeyPressed(R1A_KeyTypeDef key);

// 获取摇杆数据
void R1A_M5N_GetStick(R1A_StickTypeDef* stick);

// 检测按键事件（单击/双击/长按）
R1A_KeyEventTypeDef R1A_M5N_CheckKeyEvent(R1A_KeyTypeDef key);

// 检查连接状态
uint8_t R1A_M5N_IsConnected(void);

// 主循环处理（需定期调用，建议10ms周期）
void R1A_M5N_Process(void);
```

## 3. 实现要点

### 3.1 数据接收流程

1. 串口中断接收单字节数据
2. 状态机解析数据帧
3. 帧头匹配 → 数据接收 → 校验验证 → 数据更新

### 3.2 按键事件检测逻辑

* 使用状态机检测每个按键的按下/释放状态

* 记录按下时间和释放时间

* 根据时间间隔判定单击/双击/长按

### 3.3 信号丢失检测

* 记录每次成功接收数据的时间戳

* 超过R1A\_M5N\_LOST\_TIME未收到数据判定为丢失

## 4. 使用示例

```c
// 初始化
R1A_M5N_Init();

// 主循环（10ms周期）
void main_loop(void) {
    R1A_M5N_Process();
    
    // 检测按键A的单击
    if (R1A_M5N_CheckKeyEvent(R1A_KEY_A) == R1A_EVENT_CLICK) {
        // 处理单击事件
    }
    
    // 检测按键B的长按
    if (R1A_M5N_CheckKeyEvent(R1A_KEY_B) == R1A_EVENT_LONG) {
        // 处理长按事件
    }
    
    // 获取摇杆数据
    R1A_StickTypeDef stick;
    R1A_M5N_GetStick(&stick);
}
```

## 5. 集成说明

### 5.1 串口中断配置

在`usart.c`的`HAL_UART_RxCpltCallback`中调用：

```c
if(huart->Instance == R1A_M5N_UART_INSTANCE) {
    R1A_M5N_ReceiveByte(R1A_M5N_RX_BYTE);
    UART_Start_Receive_IT(huart, &R1A_M5N_RX_BYTE, 1);
}
```

### 5.2 定时调用

在10ms定时任务中调用`R1A_M5N_Process()`进行按键事件处理

## 6. 注意事项

1. 所有配置参数集中在.h文件，便于移植
2. 代码风格与项目现有驱动保持一致
3. 使用中文注释，便于维护
4. 考虑添加调试输出

