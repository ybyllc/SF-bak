#include "oled_ui_mode.h"
#include "oled_ui_config.h"

#if OLED_UI_MODE == OLED_UI_MODE_LVGL
#include "oled_lvgl_port.h"
#include "oled_lvgl_ui.h"
#endif

void OLED_UI_Init(void)
{
#if OLED_UI_MODE == OLED_UI_MODE_LVGL
    OLED_LVGL_PortInit();
    OLED_LVGL_UI_Create();
    OLED_LVGL_PortBindGroup(OLED_LVGL_UI_GetGroup());
#endif
}

void OLED_UI_RunOnce(void)
{
#if OLED_UI_MODE == OLED_UI_MODE_LVGL
    OLED_LVGL_UI_Update();
    OLED_LVGL_PortRunOnce();
#endif
}

void OLED_UI_Tick1ms(void)
{
#if OLED_UI_MODE == OLED_UI_MODE_LVGL
    OLED_LVGL_PortTick1ms();
#endif
}

u8 OLED_UI_IsLvglMode(void)
{
#if OLED_UI_MODE == OLED_UI_MODE_LVGL
    return 1;
#else
    return 0;
#endif
}
