# PID算法实现计划

## 目标
创建一个最简单、最通用的PID控制算法文件，适用于STM32F4嵌入式系统。

## 设计原则
1. **简单性** - 代码简洁，易于理解和使用
2. **通用性** - 不依赖特定硬件，可移植到任何平台
3. **实用性** - 包含位置式和增量式两种PID算法
4. **可配置性** - 支持参数动态调整

## 文件结构

### 1. pid.h - 头文件
- PID结构体定义
- 函数声明
- 默认参数宏定义

### 2. pid.c - 实现文件
- PID初始化函数
- 位置式PID计算
- 增量式PID计算
- 参数设置函数
- 积分限幅和输出限幅处理

## 核心功能

### PID结构体
```c
typedef struct {
    float Kp, Ki, Kd;       // PID参数
    float setpoint;         // 目标值
    float error;            // 当前误差
    float last_error;       // 上次误差
    float integral;         // 积分累积
    float output;           // 输出值
    float output_max;       // 输出上限
    float output_min;       // 输出下限
    float integral_max;     // 积分上限（防饱和）
} PID_Controller;
```

### 主要函数
1. `PID_Init()` - 初始化PID控制器
2. `PID_Update()` - 更新PID计算（位置式）
3. `PID_UpdateIncremental()` - 更新PID计算（增量式）
4. `PID_SetParameters()` - 设置PID参数
5. `PID_Reset()` - 重置PID状态

## 特性
- 积分分离（可选）
- 输出限幅
- 积分限幅（防饱和）
- 支持浮点运算

## 使用示例
```c
PID_Controller pid;
PID_Init(&pid, 1.0f, 0.1f, 0.01f, -1000, 1000);
float output = PID_Update(&pid, target, actual);
```

## 计划步骤
1. 创建 pid.h 头文件
2. 创建 pid.c 实现文件
3. 提供使用示例代码
