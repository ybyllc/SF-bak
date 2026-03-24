"""
yolo11_detect_v4.py - 水瓶追踪最终优化版
改进点：
1. 目标锁定：结合位置连续性、置信度和大小进行综合筛选。
2. 坐标归一化：输出 (-1000, 1000) 的偏移量，直接对接下位机 PID。
3. 距离评估：通过 Bounding Box 的面积和高度评估距离。
4. 串口协议：统一为 AA 55 21 CLASS XH XL YH YL FLAG CHECK 0D 0A。
"""

from maix import camera, display, image, app, uart, nn
import time
import math
from kalman import KalmanFilter2D

# ==================== 配置区域 ====================
UART_DEVICE = "/dev/ttyS0"
UART_BAUDRATE = 115200

MODEL_PATH = "/root/models/yolo11n.mud"
TARGET_CLASS = "bottle"
TARGET_CLASS_ID = 1  # 1-水瓶，2-草，3-其他
CONFIDENCE_THRESHOLD = 0.45  # 稍微调低，靠卡尔曼滤波维持稳定性
IOU_THRESHOLD = 0.45

# 卡尔曼参数优化：增加过程噪声以应对水面不规则运动
KALMAN_PROCESS_NOISE = 0.05
KALMAN_MEASURE_NOISE = 0.15
KALMAN_ESTIMATE_ERROR = 1.0

# 追踪逻辑
PREDICTION_TIMEOUT_MS = 800     # 允许丢失时间稍长，应对水草被遮挡
MAX_PREDICTION_FRAMES = 25
MIN_AREA_THRESHOLD = 400        # 过滤过小的干扰物（像素面积）

# 串口配置
SEND_INTERVAL_MS = 20           # 50Hz

# 归一化坐标量程 (例如 -1000 到 1000)
COORD_RANGE = 1000

# ==================== 追踪管理器 ====================
class BottleTracker:
    def __init__(self):
        self.kalman = KalmanFilter2D(
            process_noise=KALMAN_PROCESS_NOISE,
            measure_noise=KALMAN_MEASURE_NOISE,
            estimate_error=KALMAN_ESTIMATE_ERROR
        )
        self.state = "LOST"
        self.last_detection_time = 0
        self.prediction_count = 0
        self.trail = []

        # 缓存上一帧的目标尺寸，用于预测模式
        self.last_w = 0
        self.last_h = 0
        self.target_score = 0.0
        self.kalman_pos = (0, 0)

    def get_match_score(self, obj, predicted_pos, img_center):
        """综合评估目标匹配度"""
        cx = obj.x + obj.w // 2
        cy = obj.y + obj.h // 2

        # 1. 基础置信度
        score = obj.score * 1.0

        # 2. 位置连续性评分 (距离上次预测位置越近分数越高)
        if predicted_pos:
            dist = math.sqrt((cx - predicted_pos[0])**2 + (cy - predicted_pos[1])**2)
            score += max(0, (1.0 - dist / 300.0)) * 0.8

        # 3. 居中偏好 (水田作业通常追踪视野中心的目标)
        dist_to_center = math.sqrt((cx - img_center[0])**2 + (cy - img_center[1])**2)
        score += max(0, (1.0 - dist_to_center / 500.0)) * 0.3

        # 4. 尺寸合理性 (过滤极小噪点)
        if obj.w * obj.h < MIN_AREA_THRESHOLD:
            score -= 1.0

        return score

    def update(self, detector, img):
        current_time = time.time()
        img_w, img_h = img.width(), img.height()
        img_center = (img_w // 2, img_h // 2)

        # 1. 检测
        objs = detector.detect(img, conf_th=CONFIDENCE_THRESHOLD, iou_th=IOU_THRESHOLD)

        # 2. 预测
        predicted_pos = self.kalman.predict() if self.kalman.is_initialized else None

        # 3. 筛选最符合的目标
        best_obj = None
        highest_match = -1.0

        for obj in objs:
            class_name = detector.labels[obj.class_id]
            if TARGET_CLASS not in class_name and class_name not in TARGET_CLASS:
                continue

            m_score = self.get_match_score(obj, predicted_pos, img_center)
            if m_score > highest_match:
                highest_match = m_score
                best_obj = obj

        # 4. 状态机逻辑
        res_pos = predicted_pos or img_center
        is_pred = False

        if best_obj:
            # 成功检测
            cx = best_obj.x + best_obj.w // 2
            cy = best_obj.y + best_obj.h // 2
            self.kalman.update(cx, cy)
            self.state = "TRACKING"
            self.last_detection_time = current_time
            self.prediction_count = 0
            self.last_w, self.last_h = best_obj.w, best_obj.h
            self.target_score = best_obj.score
            res_pos = (cx, cy)
        else:
            # 丢失，尝试进入预测模式
            if self.state in ["TRACKING", "PREDICTING"]:
                dt_ms = (current_time - self.last_detection_time) * 1000
                if dt_ms < PREDICTION_TIMEOUT_MS and self.prediction_count < MAX_PREDICTION_FRAMES:
                    self.state = "PREDICTING"
                    self.prediction_count += 1
                    is_pred = True
                    if predicted_pos: res_pos = predicted_pos
                else:
                    self.state = "LOST"
                    self.kalman.reset()
            else:
                self.state = "LOST"

        self.kalman_pos = res_pos

        # 5. 坐标归一化 (转换为 -1000 到 1000)
        norm_x = int((res_pos[0] - img_center[0]) * COORD_RANGE / (img_w / 2))
        norm_y = int((res_pos[1] - img_center[1]) * COORD_RANGE / (img_h / 2))

        return {
            'state': self.state,
            'norm_x': norm_x,
            'norm_y': norm_y,
            'w': self.last_w if self.state != "LOST" else 0,
            'h': self.last_h if self.state != "LOST" else 0,
            'is_prediction': is_pred,
            'raw_obj': best_obj
        }

# ==================== 串口与主程序 ====================
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

def main():
    try:
        ser = uart.UART(UART_DEVICE, UART_BAUDRATE)
        detector = nn.YOLO11(model=MODEL_PATH, dual_buff=True)
        cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
        disp = display.Display()
        tracker = BottleTracker()

        last_send = 0

        while not app.need_exit():
            img = cam.read()
            res = tracker.update(detector, img)

            # 可视化增强
            if res['state'] != "LOST":
                color = image.COLOR_YELLOW if res['is_prediction'] else image.COLOR_GREEN
                img.draw_cross(img.width()//2, img.height()//2, color=image.COLOR_WHITE, size=10)
                kx, ky = tracker.kalman_pos
                img.draw_rect(int(kx-res['w']//2), int(ky-res['h']//2), res['w'], res['h'], color=color, thickness=2)
                img.draw_string(10, 10, f"X:{res['norm_x']} H:{res['h']} S:{res['state']}", color=color, scale=1.5)
            else:
                img.draw_string(10, 10, "STATE: LOST", color=image.COLOR_RED, scale=1.5)

            # 定时发送
            if (time.time() - last_send) * 1000 > SEND_INTERVAL_MS:
                send_data(ser, res)
                last_send = time.time()

            disp.show(img)

    except Exception as e:
        print(f"[Error] {e}")

if __name__ == "__main__":
    main()
