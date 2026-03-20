#include "TOF_VL53L0X.h"
#include "soft_iic.h"
#include <stdio.h>
#include <string.h>

// I2C ???
static soft_iic_t tof_iic;

// Xshut ??????? - ??? PC6
#define VL53L0X_Xshut(n)  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_6, (n)?GPIO_PIN_SET:GPIO_PIN_RESET)

// INT ?????? - ??? PC8
#define VL53L0X_INT()     HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8)

// ?????????
#define REG_IDENTIFICATION_MODEL_ID     0xC0
#define REG_IDENTIFICATION_REVISION_ID  0xC2
#define REG_PRE_RANGE_CONFIG_VCSEL_PERIOD   0x50
#define REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD 0x70
#define REG_SYSRANGE_START              0x00
#define REG_SYSTEM_SEQUENCE_CONFIG      0x01
#define REG_RESULT_INTERRUPT_STATUS     0x13
#define REG_RESULT_RANGE_STATUS         0x14
#define REG_I2C_SLAVE_DEVICE_ADDRESS    0x8A
#define REG_VHV_CONFIG_PAD_SCL_SDA_EXTSUP_HV  0x89

// ??NVM???§µ????? - ??????
#define NVM_REF_SPAD_OFFSET             0xC0  // SPAD §µ????????
#define NVM_PART_TO_PART_RANGE_OFFSET   0xF8  // ??????§µ????

static void VL_WriteByte(u8 reg, u8 dat)
{
    soft_iic_write_reg(&tof_iic, reg, dat);
}

static u8 VL_ReadByte(u8 reg)
{
    return soft_iic_read_reg(&tof_iic, reg);
}

static u16 VL_ReadWord(u8 reg)
{
    return soft_iic_read_reg16(&tof_iic, reg);
}

static void VL_WriteWord(u8 reg, u16 dat)
{
    soft_iic_write_reg16(&tof_iic, reg, dat);
}

static void VL_WriteDWord(u8 reg, u32 dat)
{
    soft_iic_start(&tof_iic);
    soft_iic_send_byte(&tof_iic, (tof_iic.addr << 1) & 0xFE);
    if (soft_iic_wait_ack(&tof_iic)) { soft_iic_stop(&tof_iic); return; }
    soft_iic_send_byte(&tof_iic, reg);
    if (soft_iic_wait_ack(&tof_iic)) { soft_iic_stop(&tof_iic); return; }
    soft_iic_send_byte(&tof_iic, (dat >> 24) & 0xFF);
    soft_iic_wait_ack(&tof_iic);
    soft_iic_send_byte(&tof_iic, (dat >> 16) & 0xFF);
    soft_iic_wait_ack(&tof_iic);
    soft_iic_send_byte(&tof_iic, (dat >> 8) & 0xFF);
    soft_iic_wait_ack(&tof_iic);
    soft_iic_send_byte(&tof_iic, dat & 0xFF);
    soft_iic_wait_ack(&tof_iic);
    soft_iic_stop(&tof_iic);
}

/* ??? I2C ??? */
static void VL_SetAddress(u8 new_addr)
{
    VL_WriteByte(REG_I2C_SLAVE_DEVICE_ADDRESS, new_addr >> 1);
    delay_ms(10);
}

/* ?????¦Ë */
static void VL_Reset(void)
{
    VL53L0X_Xshut(0);
    delay_ms(100);  // ???? 100ms
    VL53L0X_Xshut(1);
    delay_ms(150);  // ???????
}

/* ???????? - ?????õô???????? */
static u8 VL_DataInit(void)
{
    u8 val;
    
    // ???? 2.8V ????????? - ???
    // ?????? 2.8V ?????????????
    // VL_WriteByte(REG_VHV_CONFIG_PAD_SCL_SDA_EXTSUP_HV, 
    //              VL_ReadByte(REG_VHV_CONFIG_PAD_SCL_SDA_EXTSUP_HV) | 0x01);
    
    // ???? I2C ????
    VL_WriteByte(0x88, 0x00);
    
    // ????????
    VL_WriteByte(REG_SYSRANGE_START, 0x01);
    delay_ms(10);
    VL_WriteByte(REG_SYSRANGE_START, 0x00);
    delay_ms(10);
    
    // ??¦Ë???
    VL_WriteByte(0x80, 0x01);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x00, 0x00);
    VL_WriteByte(0x91, VL_ReadByte(0x91));  // ?????
    VL_WriteByte(0x00, 0x01);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x80, 0x00);
    
    return 0;
}

/* ???????? - ????§µ????? */
static u8 VL_StaticInit(void)
{
    u8 spad_count = 0;
    u8 spad_type_aperture = 0;
    u8 ref_spad_map[6] = {0};
    u8 first_spad = 0;
    u8 spads_enabled = 0;
    u8 i = 0;
    
    // ?? NVM ????¦Ï? SPAD ???? - 0xC0???
    // ???????????????????????? NVM
    // ???????????§µ?????
    
    // ????õô???
    u8 val1 = VL_ReadByte(0xC0);
    u8 val2 = VL_ReadByte(0xC1);
    printf("NVM SPAD Info: 0xC0=0x%02X, 0xC1=0x%02X\r\n", val1, val2);
    
    // ???? SPAD ???? - ????ST?¦Ï?????
    // ????? VL53L0X ?? 12 ?? Aperture SPAD
    
    // §Õ??¦Ï? SPAD ????
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x4F, 0x00);  // ?¦Ï? SPAD ??????
    VL_WriteByte(0x4E, 0x2C);  // SPAD ?????????44??
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0xB6, 0xB4);  // ?¦Ï? SPAD ???
    
    // §Õ?? SPAD ??? - ????ST API
    u8 spad_map[6] = {0xCE, 0xCF, 0xFF, 0xFF, 0xFF, 0xFF};
    for (i = 0; i < 6; i++) {
        VL_WriteByte(0xB0 + i, spad_map[i]);
    }
    
    // ???? ST API ?????????
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x00, 0x00);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x09, 0x04);
    VL_WriteByte(0x10, 0x00);
    VL_WriteByte(0x11, 0x00);
    VL_WriteByte(0x24, 0x01);
    VL_WriteByte(0x25, 0xFF);
    VL_WriteByte(0x75, 0x00);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x4E, 0x2C);
    VL_WriteByte(0x48, 0x00);
    VL_WriteByte(0x30, 0x20);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x30, 0x09);
    VL_WriteByte(0x54, 0x00);
    VL_WriteByte(0x31, 0x04);
    VL_WriteByte(0x32, 0x03);
    VL_WriteByte(0x40, 0x83);
    VL_WriteByte(0x46, 0x25);
    VL_WriteByte(0x60, 0x00);
    VL_WriteByte(0x27, 0x00);
    VL_WriteByte(0x50, 0x06);
    VL_WriteByte(0x51, 0x00);
    VL_WriteByte(0x52, 0x96);
    VL_WriteByte(0x56, 0x08);
    VL_WriteByte(0x57, 0x30);
    VL_WriteByte(0x61, 0x00);
    VL_WriteByte(0x62, 0x00);
    VL_WriteByte(0x64, 0x00);
    VL_WriteByte(0x65, 0x00);
    VL_WriteByte(0x66, 0xA0);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x22, 0x32);
    VL_WriteByte(0x47, 0x14);
    VL_WriteByte(0x49, 0xFF);
    VL_WriteByte(0x4A, 0x00);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x7A, 0x0A);
    VL_WriteByte(0x7B, 0x00);
    VL_WriteByte(0x78, 0x21);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x23, 0x34);
    VL_WriteByte(0x42, 0x00);
    VL_WriteByte(0x44, 0xFF);
    VL_WriteByte(0x45, 0x26);
    VL_WriteByte(0x46, 0x05);
    VL_WriteByte(0x40, 0x40);
    VL_WriteByte(0x0E, 0x06);
    VL_WriteByte(0x20, 0x1A);
    VL_WriteByte(0x43, 0x40);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x34, 0x03);
    VL_WriteByte(0x35, 0x44);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x31, 0x04);
    VL_WriteByte(0x4B, 0x09);
    VL_WriteByte(0x4C, 0x05);
    VL_WriteByte(0x4D, 0x04);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x44, 0x00);
    VL_WriteByte(0x45, 0x20);
    VL_WriteByte(0x47, 0x08);
    VL_WriteByte(0x48, 0x28);
    VL_WriteByte(0x67, 0x00);
    VL_WriteByte(0x70, 0x04);
    VL_WriteByte(0x71, 0x01);
    VL_WriteByte(0x72, 0xFE);
    VL_WriteByte(0x76, 0x00);
    VL_WriteByte(0x77, 0x00);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x0D, 0x01);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x80, 0x01);
    VL_WriteByte(0x01, 0xF8);
    VL_WriteByte(0xFF, 0x01);
    VL_WriteByte(0x8E, 0x01);
    VL_WriteByte(0x00, 0x01);
    VL_WriteByte(0xFF, 0x00);
    VL_WriteByte(0x80, 0x00);
    
    // ???? GPIO
    VL_WriteByte(0x0A, 0x04);
    VL_WriteByte(0x84, 0x00);
    VL_WriteByte(0x0B, 0x01);
    
    return 0;
}

/* ???¨°????????? */
static u8 VL_SetMeasurementTimingBudgetMicroSeconds(u32 budget_us)
{
    // ????? - ??????
    // ???¦¶ VCSEL ????
    VL_WriteByte(REG_PRE_RANGE_CONFIG_VCSEL_PERIOD, 0x0A);
    // ?????¦¶ VCSEL ????  
    VL_WriteByte(REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD, 0x08);
    
    // ???¨®??
    VL_WriteByte(0x1A, 0x0B);  // ?????¦¶???
    VL_WriteByte(0x1B, 0x00);
    
    return 0;
}

/* ??§Ó¦Ï?§µ? */
static u8 VL_PerformRefCalibration(void)
{
    u8 val;
    
    // VHV §µ?
    VL_WriteByte(0x01, 0x01);  // SYSRANGE_START: VHV §µ?
    delay_ms(100);
    do {
        val = VL_ReadByte(0x00);
    } while (val & 0x01);
    
    // Phase §µ?
    VL_WriteByte(0x01, 0x02);  // SYSRANGE_START: Phase §µ?
    delay_ms(100);
    do {
        val = VL_ReadByte(0x00);
    } while (val & 0x01);
    
    return 0;
}

/* ???????????? */
static void VL_ConfigureContinuous(void)
{
    // ????????????????100ms???
    VL_WriteWord(0x01, 0x0064);  // 100ms ???
}

/* ??????????? */
u8 VL53L0X_Init(void)
{
    u8 id;
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // ??? GPIOC ???
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // ????? Xshut ???? (PC6) - ?????
    GPIO_InitStruct.Pin = GPIO_PIN_6;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // ????? INT ???? (PC8) - ??????
    GPIO_InitStruct.Pin = GPIO_PIN_8;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // ?????¦Ë
    VL_Reset();
    
    // ????????? IIC
    soft_iic_init(&tof_iic, GPIOC, GPIO_PIN_9, GPIOA, GPIO_PIN_8, 0x29, 5);
    delay_ms(10);

    // ???§à? ID
    id = VL_ReadByte(REG_IDENTIFICATION_MODEL_ID);
    if(id != 0xEE) {
        printf("TOF_Init: Chip ID error: 0x%02X\r\n", id);
        return 1;
    }
    printf("TOF_Init: Chip ID OK: 0x%02X\r\n", id);

    // ????????
    if (VL_DataInit() != 0) {
        printf("TOF_Init: Data init failed\r\n");
        return 2;
    }
    
    // ????????
    if (VL_StaticInit() != 0) {
        printf("TOF_Init: Static init failed\r\n");
        return 3;
    }
    
    // ???? 33ms ??????????
    if (VL_SetMeasurementTimingBudgetMicroSeconds(33000) != 0) {
        printf("TOF_Init: Timing budget failed\r\n");
        return 4;
    }
    
    // ?¦Ï?§µ?
    VL_PerformRefCalibration();
    
    // ????????????
    VL_ConfigureContinuous();
    
    // ????????
    VL_WriteByte(REG_SYSTEM_SEQUENCE_CONFIG, 0xE8);
    delay_ms(10);
    
    printf("TOF_Init: Initialization completed\r\n");
    return 0;
}

/* ???¦Â?? - ????? */
u16 VL53L0X_ReadDistance(void)
{
    u16 dist = 0xFFFF;
    u16 timeout = 1000;  // 10???(1000 * 10ms)
    u8 status;
    
    // ????????
    VL_WriteByte(REG_SYSRANGE_START, 0x01);
    delay_ms(10);
    VL_WriteByte(REG_SYSRANGE_START, 0x00);
    delay_ms(10);
    
    // ????§Ø?
    VL_WriteByte(0x0B, 0x01);
    delay_ms(5);
    
    // ???????¦Â??(bit 0 = 1)
    VL_WriteByte(REG_SYSRANGE_START, 0x01);
    
    // ?????????? - ????§Ø?
    do {
        delay_ms(10);
        status = VL_ReadByte(REG_RESULT_INTERRUPT_STATUS);
        if ((status & 0x07) != 0) break;  // ?§Ó??????
    } while (--timeout);
    
    if (timeout == 0) {
        printf("VL53L0X: Measurement timeout\r\n");
        VL_WriteByte(0x0B, 0x01);
        return 0xFFFF;
    }
    
    // ???????(RESULT_RANGE_STATUS + 10??)
    dist = VL_ReadWord(REG_RESULT_RANGE_STATUS + 10);
    
    // ????§Ø?
    VL_WriteByte(0x0B, 0x01);
    
    // ?????§¹??
    if (dist == 0 || dist > 8190) {
        printf("VL53L0X: Invalid distance %d mm (status=0x%02X)\r\n", dist, status);
        return 0xFFFF;
    }
    
    printf("VL53L0X: Distance = %d mm\r\n", dist);
    return dist;
}

/* ??? TOF ?????? */
u8 VL53L0X_IsReady(void)
{
    u8 id = VL_ReadByte(REG_IDENTIFICATION_MODEL_ID);
    return (id == 0xEE) ? 1 : 0;
}

/* ??? INT ?????? */
u8 VL53L0X_ReadINT(void)
{
    return VL53L0X_INT();
}

/**
 * @brief TOF ??????????
 */
u16 TOF_QuickTest(void)
{
    return VL53L0X_ReadDistance();
}

/**
 * @brief TOF ?????????
 */
u8 TOF_DiagnosticTest(void)
{
    u8 result = 0;
    u8 id = 0;
    u16 distance = 0;
    u8 i;
    
    printf("\r\n=== TOF VL53L0X ?????? ===\r\n");
    
    // 1. ?????¦Ë????
    printf("1. ?????¦Ë????...\r\n");
    VL_Reset();
    printf("   [OK] ?????¦Ë???\r\n");
    
    // 2. I2C ??????
    printf("2. I2C ??????...\r\n");
    id = VL_ReadByte(REG_IDENTIFICATION_MODEL_ID);
    printf("   §à? ID: 0x%02X ", id);
    if (id == 0xEE) {
        printf("[OK] ???\r\n");
    } else {
        printf("[ERR] ???? (?? 0xEE)\r\n");
        result = 1;
    }
    
    // 3. ?·Ú???
    printf("3. ?·Ú???: Rev=0x%02X\r\n", VL_ReadByte(REG_IDENTIFICATION_REVISION_ID));
    
    // 4. ???????§Õ????
    printf("4. ???????§Õ????...\r\n");
    VL_WriteByte(0x75, 0x55);
    delay_ms(5);
    u8 read_val = VL_ReadByte(0x75);
    printf("   §Õ??: 0x55, ???: 0x%02X %s\r\n", read_val, 
           (read_val == 0x55) ? "[OK]" : "[ERR]");
    
    // 5. ?????????
    printf("5. ?????????:\r\n");
    printf("   ????????: 0x%02X\r\n", VL_ReadByte(REG_SYSTEM_SEQUENCE_CONFIG));
    printf("   ???¦¶VCSEL: 0x%02X\r\n", VL_ReadByte(REG_PRE_RANGE_CONFIG_VCSEL_PERIOD));
    printf("   ?????¦¶VCSEL: 0x%02X\r\n", VL_ReadByte(REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD));
    
    // 6. ???¦Â?????
    printf("6. ???¦Â?????...\r\n");
    
    // ????§Ø?
    VL_WriteByte(0x0B, 0x01);
    delay_ms(10);
    
    // ????????
    printf("   ????????...\r\n");
    VL_WriteByte(REG_SYSRANGE_START, 0x01);
    
    // ??????????
    u16 timeout = 500;
    u8 int_status = 0;
    u8 range_status = 0;
    
    while (timeout--) {
        delay_ms(10);
        int_status = VL_ReadByte(REG_RESULT_INTERRUPT_STATUS);
        range_status = VL_ReadByte(REG_RESULT_RANGE_STATUS);
        
        if ((int_status & 0x07) != 0) {
            printf("   [OK] ??????? (int=0x%02X, range=0x%02X)\r\n", int_status, range_status);
            break;
        }
    }
    
    if (timeout == 0) {
        printf("   [ERR] ???????\r\n");
        result = 1;
    } else {
        // ???????
        distance = VL_ReadWord(REG_RESULT_RANGE_STATUS + 10);
        printf("   ????????: %d mm\r\n", distance);
        
        // ???????
        printf("   ???????????: ");
        u8 result_type = int_status & 0x07;
        switch(result_type) {
            case 1: printf("Range valid\r\n"); break;
            case 2: printf("Sigma fail\r\n"); break;
            case 3: printf("Signal fail\r\n"); break;
            case 4: printf("Min range fail\r\n"); break;
            case 5: printf("Phase fail\r\n"); break;
            case 6: printf("Hardware fail\r\n"); break;
            default: printf("No result (0x%02X)\r\n", int_status); break;
        }
        
        if (int_status & 0x40) printf("   [WARN] Wrap around detected\r\n");
        if (int_status & 0x20) printf("   [WARN] Signal fail detected\r\n");
        
        if (distance > 0 && distance < 8190) {
            printf("   [OK] ??????§¹: %d mm\r\n", distance);
        } else {
            printf("   [ERR] ??????§¹\r\n");
            result = 1;
        }
    }
    
    // ????§Ø?
    VL_WriteByte(0x0B, 0x01);
    
    // 7. ??????????
    printf("7. ?????????? (3??)...\r\n");
    u8 success_count = 0;
    for (i = 0; i < 3; i++) {
        distance = VL53L0X_ReadDistance();
        if (distance != 0xFFFF) {
            printf("   [%d] %d mm [OK]\r\n", i+1, distance);
            success_count++;
        } else {
            printf("   [%d] ???\r\n", i+1);
        }
        delay_ms(200);
    }
    
    printf("   ?????: %d/3\r\n", success_count);
    if (success_count == 0) result = 1;
    
    printf("\r\n=== ???? %s ===\r\n", result ? "???" : "???");
    return result;
}

/**
 * @brief ??? TOF ????????
 */
void TOF_ReadStatusInfo(void)
{
    printf("\r\n=== TOF ????? ===\r\n");
    printf("INT????: %s\r\n", VL53L0X_ReadINT() ? "??" : "??");
    printf("?§Ø???: 0x%02X\r\n", VL_ReadByte(REG_RESULT_INTERRUPT_STATUS));
    printf("?????: 0x%02X\r\n", VL_ReadByte(REG_RESULT_RANGE_STATUS));
    printf("????¦¶: 0x%02X\r\n", VL_ReadByte(REG_SYSRANGE_START));
    printf("????????: 0x%02X\r\n", VL_ReadByte(REG_SYSTEM_SEQUENCE_CONFIG));
    printf("§à?ID: 0x%02X\r\n", VL_ReadByte(REG_IDENTIFICATION_MODEL_ID));
}
