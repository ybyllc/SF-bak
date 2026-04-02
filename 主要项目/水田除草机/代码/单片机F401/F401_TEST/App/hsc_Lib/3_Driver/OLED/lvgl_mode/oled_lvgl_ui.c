#include "oled_lvgl_ui.h"

#if OLED_UI_MODE == OLED_UI_MODE_LVGL

#include "lvgl/lvgl.h"
#include "encoder_knob.h"
#include <stdio.h>

static lv_obj_t *s_label_title = NULL;
static lv_obj_t *s_label_value = NULL;
static lv_obj_t *s_bar = NULL;
static lv_group_t *s_group = NULL;

static void oled_btn_event_cb(lv_event_t *e)
{
    lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_CLICKED)
    {
        lv_label_set_text(s_label_title, "LVGL Ready");
    }
}

void OLED_LVGL_UI_Create(void)
{
    lv_obj_t *scr = lv_scr_act();

    s_label_title = lv_label_create(scr);
    lv_label_set_text(s_label_title, "Tractor UI");
    lv_obj_align(s_label_title, LV_ALIGN_TOP_MID, 0, 2);

    s_label_value = lv_label_create(scr);
    lv_label_set_text(s_label_value, "EC11: 0");
    lv_obj_align(s_label_value, LV_ALIGN_TOP_LEFT, 2, 20);

    s_bar = lv_bar_create(scr);
    lv_obj_set_size(s_bar, 120, 12);
    lv_obj_align(s_bar, LV_ALIGN_TOP_LEFT, 4, 38);
    lv_bar_set_range(s_bar, -100, 100);
    lv_bar_set_value(s_bar, 0, LV_ANIM_OFF);

    lv_obj_t *btn = lv_btn_create(scr);
    lv_obj_set_size(btn, 64, 16);
    lv_obj_align(btn, LV_ALIGN_BOTTOM_MID, 0, -2);
    lv_obj_add_event_cb(btn, oled_btn_event_cb, LV_EVENT_ALL, NULL);

    lv_obj_t *btn_label = lv_label_create(btn);
    lv_label_set_text(btn_label, "ENTER");
    lv_obj_center(btn_label);

    s_group = lv_group_create();
    lv_group_add_obj(s_group, btn);
    lv_group_focus_obj(btn);
}

void OLED_LVGL_UI_Update(void)
{
    char text[24];
    int32_t count = Ec11_knob_Get_Count();
    int32_t bar_val = count % 201;

    if (bar_val > 100)
    {
        bar_val -= 201;
    }
    else if (bar_val < -100)
    {
        bar_val += 201;
    }

    lv_bar_set_value(s_bar, (int16_t)bar_val, LV_ANIM_OFF);
    snprintf(text, sizeof(text), "EC11: %ld", (long)count);
    lv_label_set_text(s_label_value, text);
}

lv_group_t *OLED_LVGL_UI_GetGroup(void)
{
    return s_group;
}

#endif
