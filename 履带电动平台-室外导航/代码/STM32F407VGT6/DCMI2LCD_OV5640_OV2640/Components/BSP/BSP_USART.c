/**
  ****************************(C) COPYRIGHT 2021 Boring_TECH*********************
  * @file       BSP_USART.c/h
  * @brief      将HAL库串口函数进行二次封装，并在串口中断中接收数据
  * @note      	
  * @history
  *  Version    Date            Author          Modification
  *  V3.0.0     2020.7.14     	              	1. done
  *
  @verbatim
  ==============================================================================

  ==============================================================================
  @endverbatim
  ****************************(C) COPYRIGHT 2021 Boring_TECH*********************
  */
#include "BSP_USART.h"


/* ------------------通过重定向将printf函数映射到串口1上-------------------*/
#if !defined(__MICROLIB)

//#pragma import(__use_no_semihosting)
__asm (".global __use_no_semihosting\n\t");
void _sys_exit(int x) //避免使用半主机模式
{
  x = x;
}
//__use_no_semihosting was requested, but _ttywrch was 
void _ttywrch(int ch)
{
    ch = ch;
}
//struct __FILE
//{
//  int handle;
//};
FILE __stdout;

#endif

#if defined ( __GNUC__ ) && !defined (__clang__) 
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif 
PUTCHAR_PROTOTYPE
{
  /* 实现串口发送一个字节数据的函数 */
  //serial_write(&serial1, (uint8_t)ch); //发送一个自己的数据到串口
	HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, 1000);
  return ch;
}



uint8_t rx1_buf;

/**
	* @brief          串口接收中断回调函数
  * @param[in]     	huart 串口序号
  * @retval         none
  */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	
	if(huart->Instance==USART1)
	{
		HAL_UART_Receive_IT(&huart1, &rx1_buf, 1);	
		
		HAL_UART_Transmit(&huart1, &rx1_buf, 1, 1000);

	}
	

}

/******************* (C) COPYRIGHT 2014 ANO TECH *****END OF FILE************/

