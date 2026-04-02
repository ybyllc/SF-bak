## 重构目标
将 `soft_iic` 从宏定义引脚模式改为结构体模式，支持多个 I2C 实例同时使用。

## 修改内容

### 1. 重写 `soft_iic.h`
```c
// 定义结构体
typedef struct {
    GPIO_TypeDef *scl_port;    // SCL 端口
    uint16_t scl_pin;          // SCL 引脚
    GPIO_TypeDef *sda_port;    // SDA 端口
    uint16_t sda_pin;          // SDA 引脚
    uint8_t addr;              // 7位设备地址
    uint32_t delay_us;         // 延时参数
} soft_iic_t;

// 初始化函数
void soft_iic_init(soft_iic_t *iic, GPIO_TypeDef *scl_port, uint16_t scl_pin,
                   GPIO_TypeDef *sda_port, uint16_t sda_pin, uint8_t addr, uint32_t delay);

// 基础操作函数（接受结构体指针）
void soft_iic_start(soft_iic_t *iic);
void soft_iic_stop(soft_iic_t *iic);
uint8_t soft_iic_wait_ack(soft_iic_t *iic);
void soft_iic_send_byte(soft_iic_t *iic, uint8_t dat);
uint8_t soft_iic_read_byte(soft_iic_t *iic, uint8_t ack);

// 寄存器读写函数
void soft_iic_write_reg(soft_iic_t *iic, uint8_t reg, uint8_t dat);
uint8_t soft_iic_read_reg(soft_iic_t *iic, uint8_t reg);
uint16_t soft_iic_read_reg16(soft_iic_t *iic, uint8_t reg);
```

### 2. 重写 `soft_iic.c`
- 所有函数改为接受 `soft_iic_t *iic` 参数
- 使用结构体中的端口和引脚进行 GPIO 操作
- 保留 STM32 HAL 兼容性

### 3. 更新 `TOF_VL53L0X.c`
- 定义 I2C 实例：`static soft_iic_t tof_iic;`
- 初始化时调用：`soft_iic_init(&tof_iic, GPIOC, GPIO_PIN_9, GPIOA, GPIO_PIN_8, 0x29, 5);`
- 所有 I2C 操作改为使用 `&tof_iic` 参数

## 优势
1. **多实例支持**：可同时使用多个 I2C 总线（如 TOF 用一组引脚，陀螺仪用另一组）
2. **代码复用**：同一套 I2C 代码可用于不同设备
3. **配置灵活**：运行时动态配置引脚和地址
4. **向后兼容**：保留原有函数名风格，便于迁移