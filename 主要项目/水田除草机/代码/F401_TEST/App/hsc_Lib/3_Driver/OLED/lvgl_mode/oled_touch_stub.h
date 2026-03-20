#ifndef OLED_TOUCH_STUB_H
#define OLED_TOUCH_STUB_H

#include "oled_ui_config.h"

#if OLED_UI_MODE == OLED_UI_MODE_LVGL
#include "lvgl/lvgl.h"
#endif

void OLED_TouchStub_Init(void);

#if OLED_UI_MODE == OLED_UI_MODE_LVGL
void OLED_TouchStub_Read(lv_indev_drv_t *drv, lv_indev_data_t *data);
#endif

#endif /* OLED_TOUCH_STUB_H */
