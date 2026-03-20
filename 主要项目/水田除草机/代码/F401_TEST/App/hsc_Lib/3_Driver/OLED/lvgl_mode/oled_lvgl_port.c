#include "oled_lvgl_port.h"

#if OLED_UI_MODE == OLED_UI_MODE_LVGL

#include "lvgl/lvgl.h"
#include "u8g2/u8g2.h"
#include "oled.h"
#include "encoder_knob.h"
#include "oled_touch_stub.h"

#define OLED_LVGL_HOR_RES 128
#define OLED_LVGL_VER_RES 64

static u8g2_t s_u8g2;
static lv_disp_draw_buf_t s_lv_draw_buf;
static lv_disp_drv_t s_lv_disp_drv;
static lv_indev_drv_t s_lv_indev_drv;
static lv_indev_t *s_lv_indev_enc = NULL;
static lv_color_t s_lv_buf[OLED_LVGL_HOR_RES * 16];
static int32_t s_last_enc_count = 0;
static u8 s_lvgl_inited = 0;

static void oled_lvgl_gpio_init(void)
{
    GPIO_InitTypeDef gpio_init = {0};

    __HAL_RCC_GPIOB_CLK_ENABLE();
    gpio_init.Pin = OLED_SCLK_PIN | OLED_SDIN_PIN;
    gpio_init.Mode = GPIO_MODE_OUTPUT_PP;
    gpio_init.Pull = GPIO_NOPULL;
    gpio_init.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOB, &gpio_init);

    OLED_SCLK_Set();
    OLED_SDIN_Set();
}

static uint8_t oled_u8x8_gpio_and_delay_cb(u8x8_t *u8x8, uint8_t msg, uint8_t arg_int, void *arg_ptr)
{
    (void)u8x8;
    (void)arg_ptr;

    switch (msg)
    {
    case U8X8_MSG_GPIO_AND_DELAY_INIT:
        return 1;
    case U8X8_MSG_DELAY_MILLI:
        HAL_Delay(arg_int);
        return 1;
    case U8X8_MSG_DELAY_10MICRO:
        while (arg_int--)
        {
            delay_us(10);
        }
        return 1;
    case U8X8_MSG_DELAY_100NANO:
        return 1;
    case U8X8_MSG_GPIO_I2C_CLOCK:
        if (arg_int)
        {
            OLED_SCLK_Set();
        }
        else
        {
            OLED_SCLK_Clr();
        }
        return 1;
    case U8X8_MSG_GPIO_I2C_DATA:
        if (arg_int)
        {
            OLED_SDIN_Set();
        }
        else
        {
            OLED_SDIN_Clr();
        }
        return 1;
    default:
        return 0;
    }
}

static uint8_t oled_pixel_to_mono(lv_color_t c)
{
#if LV_COLOR_DEPTH == 16
    uint16_t c16 = c.full;
    uint16_t r = (c16 >> 11) & 0x1F;
    uint16_t g = (c16 >> 5) & 0x3F;
    uint16_t b = c16 & 0x1F;
    uint16_t luma = (uint16_t)(r * 38U + g * 75U + b * 15U);
    return (u8)(luma > 1200U);
#else
    return (u8)(c.full != 0);
#endif
}

static void oled_lvgl_flush_cb(lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p)
{
    int32_t x;
    int32_t y;
    uint8_t *mono_buf = u8g2_GetBufferPtr(&s_u8g2);

    for (y = area->y1; y <= area->y2; y++)
    {
        for (x = area->x1; x <= area->x2; x++)
        {
            uint16_t index = (uint16_t)x + ((uint16_t)y >> 3) * OLED_LVGL_HOR_RES;
            uint8_t bit = (uint8_t)(1U << ((uint8_t)y & 0x07U));

            if (oled_pixel_to_mono(*color_p))
            {
                mono_buf[index] |= bit;
            }
            else
            {
                mono_buf[index] &= (uint8_t)(~bit);
            }
            color_p++;
        }
    }

    if (lv_disp_flush_is_last(disp_drv))
    {
        u8g2_SendBuffer(&s_u8g2);
    }
    lv_disp_flush_ready(disp_drv);
}

static void oled_lvgl_encoder_read_cb(lv_indev_drv_t *drv, lv_indev_data_t *data)
{
    int32_t now_count;
    int32_t diff;

    (void)drv;

    now_count = Ec11_knob_Get_Count();
    diff = now_count - s_last_enc_count;
    s_last_enc_count = now_count;

    if (diff > 20)
    {
        diff = 20;
    }
    else if (diff < -20)
    {
        diff = -20;
    }

    data->enc_diff = (int16_t)diff;
    data->state = (Ec11_knob_Key_GetState() == 0) ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

void OLED_LVGL_PortInit(void)
{
    if (s_lvgl_inited)
    {
        return;
    }

    oled_lvgl_gpio_init();

    u8g2_Setup_ssd1306_128x64_noname_f(&s_u8g2, U8G2_R0, u8x8_byte_sw_i2c, oled_u8x8_gpio_and_delay_cb);
    u8g2_InitDisplay(&s_u8g2);
    u8g2_SetPowerSave(&s_u8g2, 0);
    u8g2_ClearBuffer(&s_u8g2);
    u8g2_SendBuffer(&s_u8g2);

    lv_init();

    lv_disp_draw_buf_init(&s_lv_draw_buf, s_lv_buf, NULL, (uint32_t)(OLED_LVGL_HOR_RES * 16));

    lv_disp_drv_init(&s_lv_disp_drv);
    s_lv_disp_drv.hor_res = OLED_LVGL_HOR_RES;
    s_lv_disp_drv.ver_res = OLED_LVGL_VER_RES;
    s_lv_disp_drv.flush_cb = oled_lvgl_flush_cb;
    s_lv_disp_drv.draw_buf = &s_lv_draw_buf;
    lv_disp_drv_register(&s_lv_disp_drv);

    lv_indev_drv_init(&s_lv_indev_drv);
    s_lv_indev_drv.type = LV_INDEV_TYPE_ENCODER;
    s_lv_indev_drv.read_cb = oled_lvgl_encoder_read_cb;
    s_lv_indev_enc = lv_indev_drv_register(&s_lv_indev_drv);

    OLED_TouchStub_Init();
    s_lvgl_inited = 1;
}

void OLED_LVGL_PortRunOnce(void)
{
    lv_timer_handler();
}

void OLED_LVGL_PortTick1ms(void)
{
    if (s_lvgl_inited)
    {
        lv_tick_inc(1);
    }
}

void OLED_LVGL_PortBindGroup(void *group_obj)
{
    if ((s_lv_indev_enc != NULL) && (group_obj != NULL))
    {
        lv_indev_set_group(s_lv_indev_enc, (lv_group_t *)group_obj);
    }
}

#endif
