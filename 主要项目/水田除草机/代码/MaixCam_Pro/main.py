"""
MaixCAM Pro 水瓶追踪系统 - 带卡尔曼滤波
功能：YOLO11检测 + 卡尔曼滤波平滑 + 串口发送坐标到下位机
"""

from maix import camera, display, image, app, uart, pinmap,time
from maix import nn
import math

# ==================== 配置区域 ====================
# 串口配置
UART_DEVICE = "/dev/ttyS0"
UART_BAUDRATE = 115200

# 模型配置
MODEL_PATH = "/root/models/yolo11n.mud"
TARGET_CLASS = "bottle"         # 追踪的物体
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
        if dt <= 0:
            dt = 0.033
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
        p00, p01, p02, p03 = self.P[0]
        p10, p11, p12, p13 = self.P[1]
        p20, p21, p22, p23 = self.P[2]
        p30, p31, p32, p33 = self.P[3]

        self.P[0][0] = p00 + dt * (p02 + p20) + dt * dt * p22 + self.Q[0][0]
        self.P[0][1] = p01 + dt * (p03 + p21) + dt * dt * p23
        self.P[1][0] = p10 + dt * (p12 + p30) + dt * dt * p32
        self.P[1][1] = p11 + dt * (p13 + p31) + dt * dt * p33 + self.Q[1][1]
        self.P[0][2] = p02 + dt * p22
        self.P[0][3] = p03 + dt * p23
        self.P[1][2] = p12 + dt * p32
        self.P[1][3] = p13 + dt * p33
        self.P[2][0] = p20 + dt * p22
        self.P[2][1] = p21 + dt * p23
        self.P[2][2] = p22 + self.Q[2][2]
        self.P[2][3] = p23
        self.P[3][0] = p30 + dt * p32
        self.P[3][1] = p31 + dt * p33
        self.P[3][2] = p32
        self.P[3][3] = p33 + self.Q[3][3]
        
        self.x = new_x
        self.y = new_y
        self.last_update_time = current_time
        
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
        old_P = [row[:] for row in self.P]
        for i in range(4):
            for j in range(4):
                self.P[i][j] = old_P[i][j] - K[i][0] * old_P[0][j] - K[i][1] * old_P[1][j]
        
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
        self.max_predictions = max(1, int(PREDICTION_TIMEOUT_MS / 33))  # 约30fps下的帧数
        
        # 轨迹记录
        self.trail = []  # [(x,y), ...]
        
        # 当前目标信息
        self.target_score = 0.0
        self.target_w = 0
        self.target_h = 0
        self.target_label = "None"

    def _set_lost(self):
        """统一处理丢失状态，避免状态残留"""
        self.state = "LOST"
        self.kalman.reset()
        self.trail.clear()
        self.prediction_count = 0
        self.target_label = "None"
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
        best_label = "None"
        best_score = 0
        
        # 每帧只进行一次预测，避免状态被重复推进
        predicted_pos = None
        if self.kalman.is_initialized:
            self.kalman.predict()
            predicted_pos = self.kalman.get_position()
        
        for obj in objs:
            class_name = detector.labels[obj.class_id]
            if class_name != TARGET_CLASS:
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
                best_label = class_name
        
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
            self.target_label = best_label
            
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
                    elapsed_ms = time.ticks_diff(current_time, self.last_detection_time)
                    if elapsed_ms < PREDICTION_TIMEOUT_MS and self.prediction_count < self.max_predictions:
                        self.state = "PREDICTING"
                        self.prediction_count += 1
                        pos = self.kalman.get_position()
                        
                        # 轨迹也使用预测值
                        self.trail.append(pos)
                        if len(self.trail) > TRAIL_LENGTH:
                            self.trail.pop(0)
                            
                        is_prediction = True
                        return (True, pos[0], pos[1], True)
                    else:
                        # 预测超时，丢失目标
                        self._set_lost()
                        return (False, 0, 0, False)
                else:
                    self._set_lost()
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

    def get_target_info(self):
        """获取当前目标信息"""
        return (self.target_w, self.target_h, self.target_label)

# ==================== 串口通信 ====================

def clamp(value, lo, hi):
    return max(lo, min(hi, value))

def calc_norm_offset(px, py, img_w, img_h):
    """将像素坐标转换为相对中心偏差，范围约 -1000~1000"""
    nx = int((px - img_w // 2) * COORD_RANGE / (img_w / 2))
    ny = int((py - img_h // 2) * COORD_RANGE / (img_h / 2))
    return clamp(nx, -COORD_RANGE, COORD_RANGE), clamp(ny, -COORD_RANGE, COORD_RANGE)

def send_data(ser, result):
    """
    协议：AA 55 21 CLASS XH XL YH YL FLAG CHECK 0D 0A
    CHECK = (CMD + CLASS + XH + XL + YH + YL + FLAG) & 0xFF
    FLAG: 0-未识别, 1-识别, 2-丢失(预测)
    """
    def clamp(value, lo, hi):
        return max(lo, min(hi, value))

    flag_map = {"LOST": 0, "TRACKING": 1, "PREDICTING": 2}
    flag = flag_map.get(result['state'], 0)
    class_id = TARGET_CLASS_ID if flag != 0 else 0

    norm_x = clamp(int(result['norm_x']), -COORD_RANGE, COORD_RANGE) if flag != 0 else 0
    norm_y = clamp(int(result['norm_y']), -COORD_RANGE, COORD_RANGE) if flag != 0 else 0
    x = norm_x & 0xFFFF
    y = norm_y & 0xFFFF

    payload = bytearray([
        0xAA, 0x55,
        0x21,
        class_id & 0xFF,
        (x >> 8) & 0xFF, x & 0xFF,
        (y >> 8) & 0xFF, y & 0xFF,
        flag & 0xFF,
        0x00,
        0x0D, 0x0A
    ])

    payload[9] = sum(payload[2:9]) & 0xFF
    ser.write(bytes(payload))

# ==================== 可视化 ====================
def draw_tracking_info(img, tracker, x, y, is_prediction):
    """绘制追踪信息"""
    trail = tracker.get_trail()
    state = tracker.get_state()
    vx, vy = tracker.get_velocity()
    target_w, target_h, target_label = tracker.get_target_info()
    
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
    
    display_state = "NONE" if state == "LOST" else state
    info = f"State:{display_state}"
    img.draw_string(10, 10, info, color=status_color, scale=1.5)

    xywh_info = f"X:{x} Y:{y} W:{target_w} H:{target_h}"
    img.draw_string(10, 35, xywh_info, color=image.COLOR_YELLOW, scale=1.5)

    obj_info = f"O:{target_label}"
    img.draw_string(10, 60, obj_info, color=image.COLOR_YELLOW, scale=1.2)


# ==================== 主程序 ====================
def main():
    try:
        serial = uart.UART(UART_DEVICE, UART_BAUDRATE)
        detector = nn.YOLO11(model=MODEL_PATH, dual_buff=True)
        cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
        if SHOW_DISPLAY:
            disp = display.Display()
        else:
            disp = None
        tracker = BottleTracker()

        last_send = 0
        frame_count = 0
        fps_time = time.ticks_ms()

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
                try:
                    draw_tracking_info(img, tracker, x, y, is_prediction)
                    disp.show(img)
                except Exception:
                    pass
            
            # FPS计算
            frame_count += 1
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, fps_time) >= 1000:
                # print(f"FPS: {frame_count}, State: {state}")
                frame_count = 0
                fps_time = current_time

            # 串口发送
            if (time.time() - last_send) * 1000 > SEND_INTERVAL_MS:
                if state == "LOST":
                    result = {"state": "LOST", "norm_x": 0, "norm_y": 0}
                else:
                    norm_x, norm_y = calc_norm_offset(x, y, img.width(), img.height())
                    result = {"state": state, "norm_x": norm_x, "norm_y": norm_y}
                send_data(serial, result)
                last_send = time.time()


    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    main()
