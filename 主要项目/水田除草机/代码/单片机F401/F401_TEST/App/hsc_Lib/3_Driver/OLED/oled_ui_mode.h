#ifndef OLED_UI_MODE_H
#define OLED_UI_MODE_H

#include "common.h"

void OLED_UI_Init(void);
void OLED_UI_RunOnce(void);
void OLED_UI_Tick1ms(void);
u8 OLED_UI_IsLvglMode(void);

#endif /* OLED_UI_MODE_H */
