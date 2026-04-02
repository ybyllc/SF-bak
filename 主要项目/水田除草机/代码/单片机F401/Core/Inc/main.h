/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "app_main.h"
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define PS2_DAT_Pin GPIO_PIN_0
#define PS2_DAT_GPIO_Port GPIOC
#define PS2_CMD_Pin GPIO_PIN_1
#define PS2_CMD_GPIO_Port GPIOC
#define PS2_CS_Pin GPIO_PIN_2
#define PS2_CS_GPIO_Port GPIOC
#define PS2_CLK_Pin GPIO_PIN_3
#define PS2_CLK_GPIO_Port GPIOC
#define ENCODE1_1_Pin GPIO_PIN_0
#define ENCODE1_1_GPIO_Port GPIOA
#define ENCODE1_2_Pin GPIO_PIN_1
#define ENCODE1_2_GPIO_Port GPIOA
#define B_L_1IN_Pin GPIO_PIN_4
#define B_L_1IN_GPIO_Port GPIOA
#define B_R_1IN_Pin GPIO_PIN_5
#define B_R_1IN_GPIO_Port GPIOA
#define B_L_1PWM_Pin GPIO_PIN_6
#define B_L_1PWM_GPIO_Port GPIOA
#define B_L_2IN_Pin GPIO_PIN_7
#define B_L_2IN_GPIO_Port GPIOA
#define F_L_1IN_Pin GPIO_PIN_4
#define F_L_1IN_GPIO_Port GPIOC
#define F_R_1IN_Pin GPIO_PIN_5
#define F_R_1IN_GPIO_Port GPIOC
#define B_R_2IN_Pin GPIO_PIN_0
#define B_R_2IN_GPIO_Port GPIOB
#define B_R_2PWM_Pin GPIO_PIN_1
#define B_R_2PWM_GPIO_Port GPIOB
#define OLED_PUSH_Pin GPIO_PIN_2
#define OLED_PUSH_GPIO_Port GPIOB
#define OLED_TR_A_Pin GPIO_PIN_12
#define OLED_TR_A_GPIO_Port GPIOB
#define OLED_TR_B_Pin GPIO_PIN_13
#define OLED_TR_B_GPIO_Port GPIOB
#define OLED_SDA_Pin GPIO_PIN_14
#define OLED_SDA_GPIO_Port GPIOB
#define OLED_SCL_Pin GPIO_PIN_15
#define OLED_SCL_GPIO_Port GPIOB
#define KEY_Pin GPIO_PIN_6
#define KEY_GPIO_Port GPIOC
#define LED_Pin GPIO_PIN_7
#define LED_GPIO_Port GPIOC
#define TOF_INT_Pin GPIO_PIN_8
#define TOF_INT_GPIO_Port GPIOC
#define TOF_SCL_Pin GPIO_PIN_9
#define TOF_SCL_GPIO_Port GPIOC
#define TOF_SDA_Pin GPIO_PIN_8
#define TOF_SDA_GPIO_Port GPIOA
#define D3_433_Pin GPIO_PIN_11
#define D3_433_GPIO_Port GPIOA
#define D2_433_Pin GPIO_PIN_12
#define D2_433_GPIO_Port GPIOA
#define ENCODE2_1_Pin GPIO_PIN_15
#define ENCODE2_1_GPIO_Port GPIOA
#define ENCODE2_2_Pin GPIO_PIN_3
#define ENCODE2_2_GPIO_Port GPIOB
#define D1_433_Pin GPIO_PIN_4
#define D1_433_GPIO_Port GPIOB
#define D0_433_Pin GPIO_PIN_5
#define D0_433_GPIO_Port GPIOB
#define F_L_1PWM_Pin GPIO_PIN_6
#define F_L_1PWM_GPIO_Port GPIOB
#define F_L_2IN_Pin GPIO_PIN_7
#define F_L_2IN_GPIO_Port GPIOB
#define F_R_2IN_Pin GPIO_PIN_8
#define F_R_2IN_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
