#ifndef OLED_LVGL_UI_H
#define OLED_LVGL_UI_H

#include "oled_ui_config.h"

#if OLED_UI_MODE == OLED_UI_MODE_LVGL
#include "lvgl/lvgl.h"

void OLED_LVGL_UI_Create(void);
void OLED_LVGL_UI_Update(void);
lv_group_t *OLED_LVGL_UI_GetGroup(void);
#endif

#endif /* OLED_LVGL_UI_H */
