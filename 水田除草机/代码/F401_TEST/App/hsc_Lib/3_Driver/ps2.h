#ifndef __PS2_H
#define __PS2_H
#include "main.h"
#include "common.h"

/*********************************************************
Copyright (C), 2015-2025, YFRobot.
www.yfrobot.com
File??PS2????????
Author??pinggai    Version:1.0     Data:2015/05/16
Description: PS2????????
**********************************************************/ 

// PS2???????
#define PS2_DI_PORT     GPIOC
#define PS2_DI_PIN      GPIO_PIN_0    // ???? DAT
#define PS2_DO_PORT     GPIOC
#define PS2_DO_PIN      GPIO_PIN_1    // ??? CMD
#define PS2_CS_PORT     GPIOC
#define PS2_CS_PIN      GPIO_PIN_2    // ??? CS
#define PS2_CLK_PORT    GPIOC
#define PS2_CLK_PIN     GPIO_PIN_3    // ??? CLK

#define PS2_Delayus(n) Delay_us(n)

// ???HAL????????GPIO
#define DI   HAL_GPIO_ReadPin(PS2_DI_PORT, PS2_DI_PIN)           //???? DAT

#define DO_H HAL_GPIO_WritePin(PS2_DO_PORT, PS2_DO_PIN, GPIO_PIN_SET)        //????¦Ë??
#define DO_L HAL_GPIO_WritePin(PS2_DO_PORT, PS2_DO_PIN, GPIO_PIN_RESET)        //????¦Ë??

#define CS_H HAL_GPIO_WritePin(PS2_CS_PORT, PS2_CS_PIN, GPIO_PIN_SET)       //CS????
#define CS_L HAL_GPIO_WritePin(PS2_CS_PORT, PS2_CS_PIN, GPIO_PIN_RESET)       //CS????

#define CLK_H HAL_GPIO_WritePin(PS2_CLK_PORT, PS2_CLK_PIN, GPIO_PIN_SET)      //???????
#define CLK_L HAL_GPIO_WritePin(PS2_CLK_PORT, PS2_CLK_PIN, GPIO_PIN_RESET)      //???????


//????????
#define PSB_SELECT      1
#define PSB_L3          2   //?????
#define PSB_R3          3   //?????
#define PSB_START       4
#define PSB_PAD_UP      5   //??
#define PSB_PAD_RIGHT   6   //??
#define PSB_PAD_DOWN    7   //??
#define PSB_PAD_LEFT    8   //??
#define PSB_L2          9
#define PSB_R2          10
#define PSB_L1          11
#define PSB_R1          12
#define PSB_GREEN       13
#define PSB_RED         14  //B
#define PSB_BLUE        15  //A
#define PSB_PINK        16  //X
#define PSB_TRIANGLE    13  //Y
#define PSB_CIRCLE      14
#define PSB_CROSS       15
#define PSB_SQUARE      26

//#define WHAMMY_BAR		8

//These are stick values
#define PSS_RX 5                //?????X??????
#define PSS_RY 6
#define PSS_LX 7
#define PSS_LY 8



extern u8 Data[9];
extern u16 MASK[16];
extern u16 Handkey;

void PS2_Init(void);
u8 PS2_RedLight(void);//?§Ø??????????
void PS2_ReadData(void);
void PS2_Cmd(u8 CMD);		  //
u8 PS2_DataKey(void);		  //??????
u8 PS2_AnologData(u8 button); //???????????????
void PS2_ClearData(void);	  //????????????

void PS2_SetInit(void);
void PS2_Vibration(u8 motor1,u8 motor2);

#endif



