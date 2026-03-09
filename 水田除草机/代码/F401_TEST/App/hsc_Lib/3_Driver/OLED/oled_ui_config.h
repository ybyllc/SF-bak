#ifndef OLED_UI_CONFIG_H
#define OLED_UI_CONFIG_H

/*
 * OLED 显示模式配置
 * 0: 传统 OLED_GRAM + OLED_* 接口
 * 1: LVGL + u8g2 模式
 */
#define OLED_UI_MODE_TRADITIONAL 0
#define OLED_UI_MODE_LVGL        1

#ifndef OLED_UI_MODE
#define OLED_UI_MODE OLED_UI_MODE_TRADITIONAL
#endif

/*
 * 遥控器功能开关
 * 0: 不编译 remote_key 相关逻辑
 * 1: 编译并启用 remote_key 相关逻辑
 */
#ifndef ENABLE_REMOTE_KEY
#define ENABLE_REMOTE_KEY 0
#endif

#endif /* OLED_UI_CONFIG_H */
