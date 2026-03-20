#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/* 颜色配置：使用 16bit 色，后续在 flush 中转成 1bit OLED 数据。 */
#define LV_COLOR_DEPTH 16
#define LV_COLOR_16_SWAP 0

/* 内存池配置 */
#define LV_MEM_CUSTOM 0
#define LV_MEM_SIZE (32U * 1024U)
#define LV_MEM_ADR 0
#define LV_MEM_AUTO_DEFRAG 1

/* 刷新与输入读取周期（ms） */
#define LV_DISP_DEF_REFR_PERIOD 30
#define LV_INDEV_DEF_READ_PERIOD 30

/* 由外部时基喂 tick */
#define LV_TICK_CUSTOM 0

/* 日志与监控 */
#define LV_USE_LOG 0
#define LV_USE_PERF_MONITOR 0
#define LV_USE_MEM_MONITOR 0

/* 字体：仅开启本工程首版需要的字体 */
#define LV_FONT_MONTSERRAT_12 1
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_DEFAULT &lv_font_montserrat_14

/* 组件：首版 UI 需要的最小集合 */
#define LV_USE_LABEL 1
#define LV_USE_BTN 1
#define LV_USE_BAR 1

#endif /* LV_CONF_H */
