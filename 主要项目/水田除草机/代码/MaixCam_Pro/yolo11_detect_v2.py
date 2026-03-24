"""
MaixCAM Pro 水瓶追踪系统 - 带卡尔曼滤波
功能：YOLO11检测 + 卡尔曼滤波平滑 + 串口发送坐标到下位机
"""

from maix import camera, display, image, time, app, uart, pinmap
from maix import nn
import math

# ==================== 配置区域 ====================
# 串口配置
UART_DEVICE = "/dev/ttyS0"
UART_BAUDRATE = 115200

# 模型配置
MODEL_PATH = "/root/models/yolo11n.mud"
TARGET_CLASS = "bottle"
TARGET_CLASS_ID = 1             # 1-水瓶，2-草，3-其他
CONFIDENCE_THRESHOLD = 0.5

# 卡尔曼滤波配置
KALMAN_PROCESS_NOISE = 0.03    # 过程噪声，越小越信任模型预测
KALMAN_MEASURE_NOISE = 0.1     # 测量噪声，越小越信任传感器(检测)数据
KALMAN_ESTIMATE_ERROR = 1.0     # 初始估计误差

# 追踪逻辑配置
PREDICTION_TIMEOUT_MS = 500     # 预测模式超时时间(丢失目标后持续预测多久)
SEND_INTERVAL_MS = 20           # 串口发送间隔(50Hz)
MIN_CONFIDENCE_FOR_UPDATE = 0.3 # 卡尔曼更新的最低置信度
COORD_RANGE = 1000              # 坐标偏差范围: -1000~1000

# 显示配置
SHOW_DISPLAY = True
DRAW_BOX = True
DRAW_TRAIL = True               # 是否绘制运动轨迹
TRAIL_LENGTH = 20               # 轨迹点数量

# ==================== 卡尔曼滤波器类 ====================
class KalmanFilter2D:
    """
    2D卡尔曼滤波器 (Constant Velocity Model - 恒定速度模型)
    状态向量: [x, y, vx, vy]  (位置x, 位置y, 速度x, 速度y)
    观测向量: [x, y]           (只观测位置)
    """
    
    def __init__(self, process_noise=0.03, measure_noise=0.1, estimate_error=1.0):
        # 初始化状态 [x, y, vx, vy]
        self.x = 0.0  # 位置X
        self.y = 0.0  # 位置Y
        self.vx = 0.0 # 速度X
        self.vy = 0.0 # 速度Y
        
        # 误差协方差矩阵 P (4x4)
        self.P = [
            [estimate_error, 0, 0, 0],
            [0, estimate_error, 0, 0],
            [0, 0, estimate_error, 0],
            [0, 0, 0, estimate_error]
        ]
        
        # 过程噪声协方差 Q
        self.Q = [
            [process_noise, 0, 0, 0],
            [0, process_noise, 0, 0],
            [0, 0, process_noise*0.1, 0],  # 速度噪声更小
            [0, 0, 0, process_noise*0.1]
        ]
        
        # 测量噪声协方差 R
        self.R = [
            [measure_noise, 0],
            [0, measure_noise]
        ]
        
        # 状态转移矩阵 F (恒定速度模型)
        self.dt = 1.0  # 时间步长，会在update中动态调整
        
        # 观测矩阵 H (只观测位置)
        self.H = [
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ]
        
        # 上一次更新时间
        self.last_update_time = time.ticks_ms()
        self.is_initialized = False
        
    def init(self, x, y):
        """初始化滤波器状态"""
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.last_update_time = time.ticks_ms()
        self.is_initialized = True
        
    def predict(self):
        """
        预测步骤：根据当前状态预测下一时刻位置
        返回: (predicted_x, predicted_y)
        """
        if not self.is_initialized:
            return None
            
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, self.last_update_time) / 1000.0  # 转换为秒
        if dt > 1.0:  # 防止时间跳变
            dt = 0.033  # 默认30fps
        
        self.dt = dt
        
        # 状态转移矩阵 F (根据dt动态构建)
        # [1, 0, dt, 0]
        # [0, 1, 0, dt]
        # [0, 0, 1,  0]
        # [0, 0, 0,  1]
        
        # 预测状态: X = F * X
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        
        # 预测误差协方差: P = F*P*F' + Q
        # 简化的协方差更新(忽略高阶项)
        self.P[0][0] += self.P[0][2] * dt + self.P[2][0] * dt + self.P[2][2] * dt * dt + self.Q[0][0]
        self.P[0][1] += self.P[0][3] * dt + self.P[2][1] * dt + self.P[2][3] * dt * dt
        self.P[1][0] += self.P[1][2] * dt + self.P[3][0] * dt + self.P[3][2] * dt * dt
        self.P[1][1] += self.P[1][3] * dt + self.P[3][1] * dt + self.P[3][3] * dt * dt + self.Q[1][1]
        self.P[0][2] += self.P[2][2] * dt
        self.P[0][3] += self.P[2][3] * dt
        self.P[1][2] += self.P[3][2] * dt
        self.P[1][3] += self.P[3][3] * dt
        
        self.x = new_x
        self.y = new_y
        
        return (int(self.x), int(self.y))
    
    def update(self, measured_x, measured_y):
        """
        更新步骤：融合观测数据修正预测
        参数: measured_x, measured_y - YOLO检测到的位置
        """
        if not self.is_initialized:
            self.init(measured_x, measured_y)
            return
            
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, self.last_update_time) / 1000.0
        
        # 计算卡尔曼增益 K = P*H' / (H*P*H' + R)
        # 简化的2x2矩阵求逆
        S = [
            [self.P[0][0] + self.R[0][0], self.P[0][1] + self.R[0][1]],
            [self.P[1][0] + self.R[1][0], self.P[1][1] + self.R[1][1]]
        ]
        
        det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
        if abs(det) < 1e-10:
            det = 1e-10
            
        # 卡尔曼增益
        K = [
            [self.P[0][0] * S[1][1] - self.P[0][1] * S[1][0], -self.P[0][0] * S[0][1] + self.P[0][1] * S[0][0]],
            [self.P[1][0] * S[1][1] - self.P[1][1] * S[1][0], -self.P[1][0] * S[0][1] + self.P[1][1] * S[0][0]],
            [self.P[2][0] * S[1][1] - self.P[2][1] * S[1][0], -self.P[2][0] * S[0][1] + self.P[2][1] * S[0][0]],
            [self.P[3][0] * S[1][1] - self.P[3][1] * S[1][0], -self.P[3][0] * S[0][1] + self.P[3][1] * S[0][0]]
        ]
        
        for i in range(4):
            K[i][0] /= det
            K[i][1] /= det
        
        # 计算残差 y = z - H*x
        y0 = measured_x - self.x
        y1 = measured_y - self.y
        
        # 更新状态 x = x + K*y
        self.x += K[0][0] * y0 + K[0][1] * y1
        self.y += K[1][0] * y0 + K[1][1] * y1
        self.vx += K[2][0] * y0 + K[2][1] * y1
        self.vy += K[3][0] * y0 + K[3][1] * y1
        
        # 更新协方差 P = (I - K*H) * P
        # 简化为直接减去
        for i in range(4):
            for j in range(4):
                self.P[i][j] -= K[i][0] * self.P[0][j] + K[i][1] * self.P[1][j]
        
        # 限制速度，防止发散
        max_speed = 5000  # 像素/秒
        self.vx = max(-max_speed, min(max_speed, self.vx))
        self.vy = max(-max_speed, min(max_speed, self.vy))
        
        self.last_update_time = current_time
        
    def get_position(self):
        """获取当前估计位置"""
        return (int(self.x), int(self.y))
    
    def get_velocity(self):
        """获取当前估计速度(像素/秒)"""
        return (self.vx, self.vy)
    
    def reset(self):
        """重置滤波器"""
        self.is_initialized = False
        self.vx = 0.0
        self.vy = 0.0

# ==================== 追踪管理器 ====================
class BottleTracker:
    """水瓶追踪管理器，整合检测、卡尔曼滤波和状态管理"""
    
    def __init__(self):
        self.kalman = KalmanFilter2D(
            process_noise=KALMAN_PROCESS_NOISE,
            measure_noise=KALMAN_MEASURE_NOISE,
            estimate_error=KALMAN_ESTIMATE_ERROR
        )
        self.state = "LOST"  # LOST, TRACKING, PREDICTING
        self.last_detection_time = 0
        self.prediction_count = 0
        self.max_predictions = int(PREDICTION_TIMEOUT_MS / 33)  # 约30fps下的帧数
        
        # 轨迹记录
        self.trail = []  # [(x,y), ...]
        
        # 当前目标信息
        self.target_score = 0.0
        self.target_w = 0
        self.target_h = 0
        
    def update(self, detector, img):
        """
        更新追踪状态
        返回: (success, x, y, is_prediction)
            success: 是否成功获取位置
            x, y: 目标位置(卡尔曼滤波后)
            is_prediction: 是否为预测值(非直接检测)
        """
        current_time = time.ticks_ms()
        
        # 1. 执行YOLO检测
        objs = detector.detect(img, conf_th=CONFIDENCE_THRESHOLD, iou_th=0.45)
        
        # 2. 寻找最佳匹配目标
        best_obj = None
        best_score = 0
        
        # 如果正在追踪，优先选择距离预测位置近的目标
        predicted_pos = self.kalman.predict() if self.kalman.is_initialized else None
        
        for obj in objs:
            class_name = detector.labels[obj.class_id]
            if TARGET_CLASS not in class_name and class_name not in TARGET_CLASS:
                continue
                
            # 计算匹配分数(置信度 + 距离惩罚)
            score = obj.score
            if predicted_pos and self.state != "LOST":
                # 计算与预测位置的距离
                obj_cx = obj.x + obj.w // 2
                obj_cy = obj.y + obj.h // 2
                dist = math.sqrt((obj_cx - predicted_pos[0])**2 + (obj_cy - predicted_pos[1])**2)
                # 距离越近分数越高，距离>200像素则大幅降低分数
                if dist < 200:
                    score += (200 - dist) / 200 * 0.5
                else:
                    score -= 0.3
            
            if score > best_score:
                best_score = score
                best_obj = obj
        
        # 3. 状态机处理
        is_prediction = False
        
        if best_obj and best_obj.score >= MIN_CONFIDENCE_FOR_UPDATE:
            # 检测到有效目标
            cx = best_obj.x + best_obj.w // 2
            cy = best_obj.y + best_obj.h // 2
            
            # 卡尔曼更新
            self.kalman.update(cx, cy)
            
            # 记录目标信息
            self.target_score = best_obj.score
            self.target_w = best_obj.w
            self.target_h = best_obj.h
            
            self.state = "TRACKING"
            self.last_detection_time = current_time
            self.prediction_count = 0
            
            # 更新轨迹
            pos = self.kalman.get_position()
            self.trail.append(pos)
            if len(self.trail) > TRAIL_LENGTH:
                self.trail.pop(0)
                
            return (True, pos[0], pos[1], False)
            
        else:
            # 未检测到目标，进入预测模式
            if self.state == "TRACKING" or self.state == "PREDICTING":
                if predicted_pos:
                    # 检查预测超时
                    if time.ticks_diff(current_time, self.last_detection_time) < PREDICTION_TIMEOUT_MS:
                        self.state = "PREDICTING"
                        self.prediction_count += 1
                        
                        # 在预测模式下继续预测
                        self.kalman.predict()
                        pos = self.kalman.get_position()
                        
                        # 轨迹也使用预测值
                        self.trail.append(pos)
                        if len(self.trail) > TRAIL_LENGTH:
                            self.trail.pop(0)
                            
                        is_prediction = True
                        return (True, pos[0], pos[1], True)
                    else:
                        # 预测超时，丢失目标
                        self.state = "LOST"
                        self.kalman.reset()
                        self.trail.clear()
                        return (False, 0, 0, False)
                else:
                    self.state = "LOST"
                    return (False, 0, 0, False)
            else:
                return (False, 0, 0, False)
    
    def get_trail(self):
        """获取运动轨迹"""
        return self.trail
    
    def get_state(self):
        """获取当前状态"""
        return self.state
    
    def get_velocity(self):
        """获取估计速度"""
        return self.kalman.get_velocity()

# ==================== 串口通信 ====================
def init_uart():
    """初始化串口"""
    serial = uart.UART(UART_DEVICE, UART_BAUDRATE)
    time.sleep_ms(100)
    print(f"UART initialized: {UART_DEVICE} @ {UART_BAUDRATE}bps")
    return serial

def clamp(value, lo, hi):
    return max(lo, min(hi, value))

def calc_norm_offset(px, py, img_w, img_h):
    """将像素坐标转换为相对中心偏差，范围约 -1000~1000"""
    nx = int((px - img_w // 2) * COORD_RANGE / (img_w / 2))
    ny = int((py - img_h // 2) * COORD_RANGE / (img_h / 2))
    return clamp(nx, -COORD_RANGE, COORD_RANGE), clamp(ny, -COORD_RANGE, COORD_RANGE)

def send_tracking_data(serial, class_id, norm_x, norm_y, flag):
    """
    协议：AA 55 21 CLASS XH XL YH YL FLAG CHECK 0D 0A
    CHECK = (CMD + CLASS + XH + XL + YH + YL + FLAG) & 0xFF
    FLAG: 0-未识别, 1-识别, 2-丢失(预测)
    """
    x = int(norm_x) & 0xFFFF
    y = int(norm_y) & 0xFFFF

    data = bytearray([
        0xAA, 0x55,             # 帧头
        0x21,                   # 命令字
        int(class_id) & 0xFF,   # 类别
        (x >> 8) & 0xFF, x & 0xFF,
        (y >> 8) & 0xFF, y & 0xFF,
        int(flag) & 0xFF,       # 状态
        0x00,                   # 校验和占位
        0x0D, 0x0A              # 帧尾
    ])

    data[9] = sum(data[2:9]) & 0xFF
    serial.write(bytes(data))

# ==================== 可视化 ====================
def draw_tracking_info(img, tracker, x, y, is_prediction):
    """绘制追踪信息"""
    trail = tracker.get_trail()
    state = tracker.get_state()
    vx, vy = tracker.get_velocity()
    
    # 绘制轨迹
    if DRAW_TRAIL and len(trail) > 1:
        for i in range(1, len(trail)):
            alpha = i / len(trail)
            color = image.Color.from_rgb(
                int(255 * (1-alpha)), 
                int(255 * alpha), 
                0
            )
            img.draw_line(trail[i-1][0], trail[i-1][1], trail[i][0], trail[i][1], 
                         color=color, thickness=2)
    
    # 绘制中心点
    if state != "LOST":
        color = image.COLOR_YELLOW if is_prediction else image.COLOR_GREEN
        size = 15 if is_prediction else 10
        img.draw_cross(x, y, color=color, size=size, thickness=2)
        
        # 绘制速度向量
        vx_draw = int(vx * 0.1)  # 缩放显示
        vy_draw = int(vy * 0.1)
        img.draw_arrow(x, y, x + vx_draw, y + vy_draw, 
                      color=image.COLOR_BLUE, thickness=2)
    
    # 绘制状态文字
    status_color = {
        "LOST": image.COLOR_RED,
        "TRACKING": image.COLOR_GREEN,
        "PREDICTING": image.COLOR_YELLOW
    }.get(state, image.COLOR_WHITE)
    
    info = f"State:{state} X:{x} Y:{y}"
    img.draw_string(10, 10, info, color=status_color, scale=1.5)
    
    vel_info = f"VX:{vx:.1f} VY:{vy:.1f}"
    img.draw_string(10, 35, vel_info, color=image.COLOR_BLUE, scale=1.2)

# ==================== 主程序 ====================
def main():
    print("=== MaixCAM Pro Bottle Tracker with Kalman Filter ===")
    
    # 初始化
    serial = init_uart()
    detector = nn.YOLO11(model=MODEL_PATH, dual_buff=True)
    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
    cam.skip_frames(30)
    disp = display.Display() if SHOW_DISPLAY else None
    
    tracker = BottleTracker()
    
    last_send_time = time.ticks_ms()
    frame_count = 0
    fps_time = time.ticks_ms()
    
    print("Running... Press Ctrl+C to stop")
    
    while not app.need_exit():
        img = cam.read()
        
        # 更新追踪
        success, x, y, is_prediction = tracker.update(detector, img)
        state = tracker.get_state()
        vx, vy = tracker.get_velocity()
        
        # 绘制检测结果(如果有)
        if success and not is_prediction:
            # 这里可以绘制YOLO原始检测框，但tracker.update已经消耗了objs
            # 如需绘制检测框，需要修改tracker返回原始obj
            pass
        
        # 可视化
        if disp:
            draw_tracking_info(img, tracker, x, y, is_prediction)
            disp.show(img)
        
        # 串口发送
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_send_time) >= SEND_INTERVAL_MS:
            flag = 0 if state == "LOST" else (1 if state == "TRACKING" else 2)
            if flag == 0:
                send_tracking_data(serial, 0, 0, 0, 0)
            else:
                norm_x, norm_y = calc_norm_offset(x, y, img.width(), img.height())
                send_tracking_data(serial, TARGET_CLASS_ID, norm_x, norm_y, flag)
            
            last_send_time = current_time
        
        # FPS计算
        frame_count += 1
        if time.ticks_diff(current_time, fps_time) >= 1000:
            print(f"FPS: {frame_count}, State: {state}")
            frame_count = 0
            fps_time = current_time

if __name__ == "__main__":
    main()
