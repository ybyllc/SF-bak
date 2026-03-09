# OLED Dual-Mode (Traditional + LVGL) Keil 接入说明

## 1. 方案概述
- 传统模式: 继续使用 `OLED_*` 接口和原菜单页。
- LVGL 模式: 使用 `u8g2 + LVGL`，保留 EC11 编码器输入，触摸先用 stub 预留。
- 模式切换文件: `App/hsc_Lib/3_Driver/OLED/oled_ui_config.h`

## 2. 已新增的业务文件
- `App/hsc_Lib/2_Control/menu_uimenlvg.c`
- `App/hsc_Lib/2_Control/menu_uimenlvg.h`
- `App/hsc_Lib/3_Driver/OLED/oled_ui_config.h`
- `App/hsc_Lib/3_Driver/OLED/oled_ui_mode.h`
- `App/hsc_Lib/3_Driver/OLED/lv_conf.h`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_ui_mode.c`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_port.c`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_port.h`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.c`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.h`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_touch_stub.c`
- `App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_touch_stub.h`

## 3. Keil 里必须加入的 `.c` 文件

### 3.1 本次移植层文件
- `../App/hsc_Lib/2_Control/menu_uimenlvg.c`
- `../App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_ui_mode.c`
- `../App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_port.c`
- `../App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_lvgl_ui.c`
- `../App/hsc_Lib/3_Driver/OLED/lvgl_mode/oled_touch_stub.c`

### 3.2 LVGL 内核文件
- 把 `../App/hsc_Lib/3_Driver/OLED/lvgl/src` 下所有 `.c` 加入工程。

### 3.3 u8g2 文件
- 推荐做法: 把 `../App/hsc_Lib/3_Driver/OLED/u8g2` 下所有 `.c` 加入工程，排除:
  - `mui.c`
  - `mui_u8g2.c`
  - `u8log.c`
  - `u8log_u8g2.c`
  - `u8log_u8x8.c`

## 4. Keil Include Paths
在 Target Options -> C/C++ -> Include Paths 增加:
- `../App/hsc_Lib/3_Driver/OLED`
- `../App/hsc_Lib/3_Driver/OLED/lvgl`
- `../App/hsc_Lib/3_Driver/OLED/u8g2`
- `../App/hsc_Lib/3_Driver/OLED/lvgl_mode`

## 5. 模式切换
编辑 `App/hsc_Lib/3_Driver/OLED/oled_ui_config.h`:
- 传统模式:
  - `#define OLED_UI_MODE OLED_UI_MODE_TRADITIONAL`
- LVGL 模式:
  - `#define OLED_UI_MODE OLED_UI_MODE_LVGL`

## 6. Remote Key 开关
同文件内:
- 关闭: `#define ENABLE_REMOTE_KEY 0`
- 开启: `#define ENABLE_REMOTE_KEY 1`

说明: 现在默认关闭；原功能文件保留，后续可直接再开。

## 7. 关键调用链（已接好）
- `Menu_Init()/Menu_Run()` 已分流到传统或 LVGL 模式。
- `SysTick_Handler()` 已接入 `OLED_UI_Tick1ms()` 供 LVGL tick 使用。
- `App_Init()` 保持传统启动流程，LVGL 模式只保留必须初始化。
