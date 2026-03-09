#include "menu_uimenlvg.h"
#include "oled_ui_mode.h"
#include "stm32f4xx_hal.h"

void MenuUiMenLvg_Init(void)
{
    OLED_UI_Init();
}

void MenuUiMenLvg_Run(void)
{
    OLED_UI_RunOnce();
    HAL_Delay(5);
}
