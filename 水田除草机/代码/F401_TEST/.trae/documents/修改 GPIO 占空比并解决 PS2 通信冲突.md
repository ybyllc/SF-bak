## 问题分析
GPIO 测试页面会持续输出 PWM 信号到 PC0-PC3 引脚。当切换到 PS2 测试页面时：
1. PS2 初始化会重新配置引脚（PC0 输入，PC1/PC2/PC3 输出）
2. 但 GPIO 测试的 `gpio_initialized = 1`，如果再次进入 GPIO 测试不会重新初始化
3. 关键是离开 GPIO 测试页面时，应该停止 PWM 并将引脚设为高电平

## 解决方案

### 方案：在 GPIO 测试页面添加页面状态检查
修改 `Menu_DisplayGPIOTestPage` 函数：

1. 每次进入函数时，先检查 `menuState.currentPage` 是否仍然是 `MENU_PAGE_GPIO_TEST`
2. 如果不是（说明已经切换到其他页面），则：
   - 将所有引脚设为高电平
   - 重置 `gpio_initialized = 0`
   - 返回，不再执行 PWM

3. 添加一个静态变量记录上一次页面状态，检测到页面变化时执行清理

### 代码修改
在 menu.c 中修改 `Menu_DisplayGPIOTestPage` 函数：

```c
static void Menu_DisplayGPIOTestPage(void) {
    static MenuPageType last_page = MENU_PAGE_MAIN;
    
    // 检测页面切换（从 GPIO_TEST 切换到其他页面）
    if (last_page == MENU_PAGE_GPIO_TEST && menuState.currentPage != MENU_PAGE_GPIO_TEST) {
        // 停止 PWM，将引脚设为高电平
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_SET);
        gpio_initialized = 0;
    }
    last_page = menuState.currentPage;
    
    // 如果当前不是 GPIO_TEST 页面，直接返回
    if (menuState.currentPage != MENU_PAGE_GPIO_TEST) {
        return;
    }
    
    // 初始化GPIO（首次进入）
    if (!gpio_initialized) {
        Menu_InitGPIOTest();
    }
    
    // ... 原有 PWM 代码 ...
}
```

这样当离开 GPIO 测试页面时，引脚会被设为高电平，PS2 通信可以正常工作。