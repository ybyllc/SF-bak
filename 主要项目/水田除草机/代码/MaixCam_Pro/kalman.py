"""
kalman.py - 2D卡尔曼滤波器模块 (Constant Velocity Model)
用于目标追踪，预测位置和平滑轨迹
"""

import time
import math


class KalmanFilter2D:
    """
    2D卡尔曼滤波器 (恒定速度模型)
    状态向量: [x, y, vx, vy]  (位置x, 位置y, 速度x, 速度y)
    观测向量: [x, y]           (只观测位置)
    """
    
    def __init__(self, process_noise=0.03, measure_noise=0.1, estimate_error=1.0):
        """
        初始化卡尔曼滤波器
        
        Args:
            process_noise: 过程噪声，越小越信任模型预测 (默认0.03)
            measure_noise: 测量噪声，越小越信任传感器检测 (默认0.1)
            estimate_error: 初始估计误差 (默认1.0)
        """
        # 状态向量 [x, y, vx, vy]
        self.x = 0.0  # 位置X
        self.y = 0.0  # 位置Y
        self.vx = 0.0 # 速度X (像素/秒)
        self.vy = 0.0 # 速度Y (像素/秒)
        
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
            [0, 0, process_noise * 0.1, 0],  # 速度噪声更小
            [0, 0, 0, process_noise * 0.1]
        ]
        
        # 测量噪声协方差 R
        self.R = [
            [measure_noise, 0],
            [0, measure_noise]
        ]
        
        # 时间步长
        self.dt = 1.0
        
        # 上一次更新时间
        self.last_update_time = time.ticks_ms()
        self.is_initialized = False
        
    def init(self, x, y):
        """
        初始化滤波器状态
        
        Args:
            x, y: 初始位置坐标
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.last_update_time = time.ticks_ms()
        self.is_initialized = True
        
    def predict(self):
        """
        预测步骤：根据当前状态预测下一时刻位置
        
        Returns:
            (predicted_x, predicted_y): 预测的位置坐标，如果未初始化返回None
        """
        if not self.is_initialized:
            return None
            
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, self.last_update_time) / 1000.0  # 转换为秒
        
        # 限制时间差，防止跳变
        if dt > 1.0:
            dt = 0.033  # 默认30fps
        if dt < 0.001:
            dt = 0.001
            
        self.dt = dt
        
        # 预测状态: X = F * X
        # x = x + vx * dt
        # y = y + vy * dt
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        
        # 简化的协方差更新: P = F*P*F' + Q
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
        
        Args:
            measured_x, measured_y: YOLO检测到的位置
        """
        if not self.is_initialized:
            self.init(measured_x, measured_y)
            return
            
        current_time = time.ticks_ms()
        
        # 计算卡尔曼增益 K = P*H' * inv(H*P*H' + R)
        # S = H*P*H' + R (2x2矩阵)
        S = [
            [self.P[0][0] + self.R[0][0], self.P[0][1] + self.R[0][1]],
            [self.P[1][0] + self.R[1][0], self.P[1][1] + self.R[1][1]]
        ]
        
        # 2x2矩阵求逆
        det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
        if abs(det) < 1e-10:
            det = 1e-10
            
        # 卡尔曼增益 K (4x2矩阵)
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
        
        # 限制速度，防止发散
        max_speed = 5000  # 像素/秒
        self.vx = max(-max_speed, min(max_speed, self.vx))
        self.vy = max(-max_speed, min(max_speed, self.vy))
        
        # 更新协方差 P = (I - K*H) * P
        for i in range(4):
            for j in range(4):
                self.P[i][j] -= K[i][0] * self.P[0][j] + K[i][1] * self.P[1][j]
        
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
        self.P = [
            [1.0, 0, 0, 0],
            [0, 1.0, 0, 0],
            [0, 0, 1.0, 0],
            [0, 0, 0, 1.0]
        ]