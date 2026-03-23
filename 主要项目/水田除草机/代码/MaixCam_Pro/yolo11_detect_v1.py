"""
MaixCAM Pro 水瓶识别 + 串口发送坐标
功能：使用YOLO11检测水瓶(bottle)，发送中心坐标(x,y)到下位机(STM32/Arduino等)
协议格式：帧头(0xAA,0x55) + X高字节 + X低字节 + Y高字节 + Y低字节 + 置信度 + 帧尾(0x5B)
"""

from maix import camera, display, image, time, app, uart, pinmap
from maix import nn

# ==================== 配置区域 ====================
# 串口配置
UART_DEVICE = "/dev/ttyS0"  # 默认UART0，使用A16(TX)/A17(RX)
UART_BAUDRATE = 115200      # 波特率，与下位机保持一致

# 模型配置
MODEL_PATH = "/root/models/yolo11n.mud"  # YOLO11模型路径，需包含bottle类别

# 检测配置
TARGET_CLASS = "bottle"     # 目标类别名称
CONFIDENCE_THRESHOLD = 0.5  # 置信度阈值
SEND_INTERVAL_MS = 50       # 发送间隔(ms)，避免串口阻塞

# 显示配置
SHOW_DISPLAY = True         # 是否显示画面
DRAW_BOX = True             # 是否绘制检测框

# ==================== 初始化 ====================
def init_uart():
    """初始化串口"""
    # 如需使用其他串口，先配置引脚功能
    # pinmap.set_pin_function("A19", "UART1_TX")
    # pinmap.set_pin_function("A18", "UART1_RX")
    
    serial = uart.UART(UART_DEVICE, UART_BAUDRATE)
    time.sleep_ms(100)  # 等待串口就绪
    print(f"UART initialized: {UART_DEVICE} @ {UART_BAUDRATE}bps")
    return serial

def init_model():
    """初始化YOLO11模型"""
    # dual_buff=True 启用双缓冲，提高推理效率
    detector = nn.YOLO11(model=MODEL_PATH, dual_buff=True)
    print(f"Model loaded: {MODEL_PATH}")
    print(f"Classes: {detector.labels}")
    return detector

def init_camera(detector):
    """初始化摄像头，使用模型要求的输入尺寸"""
    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
    cam.skip_frames(30)  # 跳过前30帧，等待自动曝光稳定
    print(f"Camera initialized: {detector.input_width()}x{detector.input_height()}")
    return cam

def init_display():
    """初始化显示"""
    if SHOW_DISPLAY:
        disp = display.Display()
        return disp
    return None

# ==================== 串口通信协议 ====================
def send_bottle_data(serial, x, y, confidence, width, height):
    """
    发送水瓶检测数据到下位机
    协议：0xAA 0x55 XH XL YH YL CONF W H CHECKSUM 0x5B
    
    Args:
        serial: UART对象
        x, y: 水瓶中心坐标(0-65535)
        confidence: 置信度(0-255)
        width, height: 检测框宽高
    """
    # 数据打包
    x = int(x) & 0xFFFF
    y = int(y) & 0xFFFF
    conf = int(confidence * 255) & 0xFF
    w = int(width) & 0xFF
    h = int(height) & 0xFF
    
    # 构建数据包
    data = bytearray([
        0xAA, 0x55,           # 帧头
        (x >> 8) & 0xFF,      # X高字节
        x & 0xFF,             # X低字节
        (y >> 8) & 0xFF,      # Y高字节
        y & 0xFF,             # Y低字节
        conf,                 # 置信度
        w,                    # 宽度
        h,                    # 高度
        0x00,                 # 校验和占位
        0x5B                  # 帧尾
    ])
    
    # 计算校验和(除帧头帧尾外所有字节之和的低8位)
    checksum = sum(data[2:9]) & 0xFF
    data[9] = checksum
    
    # 发送数据
    serial.write(bytes(data))
    
    # 可选：同时发送字符串格式方便调试
    debug_str = f"BOT:{x},{y},{conf},{w},{h}\n"
    serial.write_str(debug_str)

def send_no_target(serial):
    """发送无目标信号"""
    # 特殊包表示未检测到目标
    data = bytes([0xAA, 0x55, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x5B])
    serial.write(data)
    serial.write_str("BOT:NONE\n")

# ==================== 主程序 ====================
def main():
    print("=== MaixCAM Pro Bottle Tracker ===")
    
    # 初始化
    try:
        serial = init_uart()
        detector = init_model()
        cam = init_camera(detector)
        disp = init_display()
    except Exception as e:
        print(f"Init error: {e}")
        return
    
    # 检查目标类别是否存在
    if TARGET_CLASS not in detector.labels:
        print(f"Warning: '{TARGET_CLASS}' not in model classes!")
        print(f"Available: {detector.labels}")
    
    last_send_time = time.ticks_ms()
    frame_count = 0
    fps_time = time.ticks_ms()
    
    print("Running... Press Ctrl+C to stop")
    
    while not app.need_exit():
        # 读取图像
        img = cam.read()
        
        # YOLO11检测
        objs = detector.detect(img, conf_th=CONFIDENCE_THRESHOLD, iou_th=0.45)
        
        # 寻找最大的水瓶
        target_obj = None
        max_area = 0
        
        for obj in objs:
            # 修正：使用 detector.labels[obj.class_id] 获取类别名称，而不是 obj.class_name
            class_name = detector.labels[obj.class_id]
            
            # 匹配类别(支持部分匹配，如"bottle"匹配"water_bottle")
            if TARGET_CLASS in class_name or class_name in TARGET_CLASS:
                area = obj.w * obj.h
                if area > max_area:
                    max_area = area
                    target_obj = obj
        
        # 绘制检测结果
        if DRAW_BOX and target_obj:
            # 绘制检测框
            img.draw_rect(target_obj.x, target_obj.y, target_obj.w, target_obj.h, 
                         color=image.COLOR_RED, thickness=2)
            # 绘制中心点
            center_x = target_obj.x + target_obj.w // 2
            center_y = target_obj.y + target_obj.h // 2
            img.draw_cross(center_x, center_y, color=image.COLOR_GREEN, size=10)
            # 绘制标签 - 修正：使用 detector.labels 获取类别名
            label = f"{detector.labels[target_obj.class_id]}:{target_obj.score:.2f}"
            img.draw_string(target_obj.x, target_obj.y - 20, label, 
                          color=image.COLOR_WHITE, scale=1.5)
        
        # 计算FPS
        frame_count += 1
        if time.ticks_diff(time.ticks_ms(), fps_time) >= 1000:
            fps = frame_count
            print(f"FPS: {fps}")
            frame_count = 0
            fps_time = time.ticks_ms()
        
        # 串口发送(控制发送频率)
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_send_time) >= SEND_INTERVAL_MS:
            if target_obj:
                center_x = target_obj.x + target_obj.w // 2
                center_y = target_obj.y + target_obj.h // 2
                send_bottle_data(serial, center_x, center_y, 
                               target_obj.score, target_obj.w, target_obj.h)
                print(f"Sent: X={center_x}, Y={center_y}, Conf={target_obj.score:.2f}")
            else:
                send_no_target(serial)
                print("Sent: No target")
            
            last_send_time = current_time
        
        # 显示图像
        if disp:
            # 显示状态信息
            if target_obj:
                center_x = target_obj.x + target_obj.w // 2
                center_y = target_obj.y + target_obj.h // 2
                info = f"X:{center_x} Y:{center_y}"
                img.draw_string(10, 10, info, color=image.COLOR_GREEN, scale=2)
            else:
                img.draw_string(10, 10, "No Bottle", color=image.COLOR_RED, scale=2)
            
            disp.show(img)

if __name__ == "__main__":
    main()