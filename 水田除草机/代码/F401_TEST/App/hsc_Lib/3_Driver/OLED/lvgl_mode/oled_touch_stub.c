#include "oled_touch_stub.h"

void OLED_TouchStub_Init(void)
{
    /* 触摸屏预留：当前硬件未接入触摸芯片。 */
}

#if OLED_UI_MODE == OLED_UI_MODE_LVGL
void OLED_TouchStub_Read(lv_indev_drv_t *drv, lv_indev_data_t *data)
{
    (void)drv;

    /* 触摸输入默认无事件，后续接入真实触摸芯片后替换。 */
    data->state = LV_INDEV_STATE_RELEASED;
    data->point.x = 0;
    data->point.y = 0;
}
#endif
