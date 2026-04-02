#ifndef OLED_LVGL_PORT_H
#define OLED_LVGL_PORT_H

#include "oled_ui_config.h"

#if OLED_UI_MODE == OLED_UI_MODE_LVGL

void OLED_LVGL_PortInit(void);
void OLED_LVGL_PortRunOnce(void);
void OLED_LVGL_PortTick1ms(void);
void OLED_LVGL_PortBindGroup(void *group_obj);

#endif

#endif /* OLED_LVGL_PORT_H */
