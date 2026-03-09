//=========================================???????================================================//
//      5V  ??DC 5V???
//     GND  ???
//======================================OLED???????????==========================================//
//????????????????IIC
//     SCL  ??PB13    // IIC??????
//     SDA  ??PB14    // IIC???????
//======================================OLED???????????==========================================//
//????????????????IIC????????????????
//=========================================????????=========================================//
//?????????????????????
//============================================================================================//

#ifndef __OLED_H
#define __OLED_H
#include "common.h"
#include "stdlib.h"

// ??????
#define X_WIDTH 128
#define Y_WIDTH 64

//-----------------OLED IIC??????----------------

#define OLED_SCLK_PIN   GPIO_PIN_15 // SCL ??????? PB15
#define OLED_SCLK_Clr() HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_RESET) // CLK
#define OLED_SCLK_Set() HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_SET)

#define OLED_SDIN_PIN   GPIO_PIN_14 // SDA ???????? PB14
#define OLED_SDIN_Clr() HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_RESET) // DIN
#define OLED_SDIN_Set() HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, GPIO_PIN_SET)

#define OLED_CMD 0  // ??????
#define OLED_DATA 1 // ??????

#define IIC_SLAVE_ADDR 0x78 // IIC slave device address // ?????? 1111000

// OLED????????
void OLED_WR_Byte(unsigned dat, unsigned cmd);
void OLED_Display_On(void);
void OLED_Display_Off(void);
void OLED_Init(void);
void OLED_Clear(unsigned dat);
void OLED_DrawPoint(u8 x, u8 y, u8 t);
void OLED_Fill(u8 x1, u8 y1, u8 x2, u8 y2, u8 dot);
void OLED_ShowChar(u8 x, u8 y, u8 chr, u8 Char_Size, u8 mode);
void OLED_ShowNum(u8 x, u8 y, u32 num, u8 len, u8 size);
void OLED_ShowString(u8 x, u8 y, const char *p, u8 Char_Size);
void OLED_ShowString_Reverse(u8 x, u8 y, const char *p, u8 Char_Size);// ???????????
void OLED_Set_Pos(unsigned char x, unsigned char y);
void OLED_ShowCHinese(u8 x, u8 y, u8 no);
void OLED_DrawBMP(unsigned char x0, unsigned char y0, unsigned char x1, unsigned char y1, unsigned char BMP[]);
void OLED_Refresh(void); // ???????OLED???(?????????????)

// OLED??????????
void OLED_DrawLine(u8 x1, u8 y1, u8 x2, u8 y2, u8 color);
void OLED_DrawRectangle(u8 x1, u8 y1, u8 x2, u8 y2, u8 color);
void OLED_DrawFillRectangle(u8 x1, u8 y1, u8 x2, u8 y2, u8 color);


// OLED????????
#define OLED_MODE 0
#define SIZE 8
#define XLevelL 0x00
#define XLevelH 0x10
#define Max_Column 128
#define Max_Row 64
#define Brightness 0xFF

#endif
