"""
MaixCAM Pro YOLO11 实时目标检测演示程序
功能：使用YOLO11模型进行实时物体检测，并在屏幕上显示检测结果
"""

# 导入必要的库
# camera: 摄像头控制模块，用于图像采集
# display: 显示控制模块，用于在屏幕上显示图像
# image: 图像处理模块，提供绘制图形、文字等功能
# nn: 神经网络模块，提供深度学习模型加载和推理功能
# app: 应用程序模块，提供程序退出检测等功能
from maix import camera, display, image, nn, app

# ==================== 初始化模型 ====================
# 加载YOLO11目标检测模型
# 参数说明：
#   model: 模型文件路径，.mud格式是MaixCAM专用的模型格式
#   dual_buff: 启用双缓冲模式，可以提高推理效率
#            True表示使用双缓冲，减少CPU等待GPU推理完成的时间
detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)

# ==================== 初始化摄像头 ====================
# 创建摄像头对象，自动根据模型需求设置参数
# detector.input_width(): 获取模型要求的输入图像宽度
# detector.input_height(): 获取模型要求的输入图像高度  
# detector.input_format(): 获取模型要求的图像格式(如RGB、BGR等)
# 这样设置可以确保摄像头输出的图像与模型输入要求匹配，无需额外转换
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())

# ==================== 初始化显示器 ====================
# 创建显示对象，用于在屏幕上实时显示处理后的图像
disp = display.Display()

# ==================== 主循环 ====================
# app.need_exit(): 检测是否需要退出程序
# 返回True的情况：用户按下按键、收到退出信号等
# 使用while循环持续处理视频流
while not app.need_exit():
    
    # 从摄像头读取一帧图像
    # img 是一个image对象，包含了图像数据和尺寸信息
    img = cam.read()
    
    # 使用YOLO11模型进行目标检测
    # 参数说明：
    #   img: 输入的图像
    #   conf_th: 置信度阈值，只有置信度>0.5的检测结果才会被保留
    #           范围0-1，值越高筛选越严格，误检越少但可能漏检
    #   iou_th: IOU(交并比)阈值，用于非极大值抑制(NMS)
    #          当两个检测框重叠度>0.45时，只保留置信度高的那个
    #          用于消除重叠的重复检测框
    # 返回值objs是一个列表，包含所有检测到的目标对象
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    
    # 遍历所有检测到的目标对象
    for obj in objs:
        # obj对象包含以下属性：
        #   obj.x: 检测框左上角的X坐标
        #   obj.y: 检测框左上角的Y坐标  
        #   obj.w: 检测框的宽度
        #   obj.h: 检测框的高度
        #   obj.class_id: 类别ID(整数索引)
        #   obj.score: 置信度分数(0-1)
        #   obj.class_name: 类别名称(字符串)
        
        # 在图像上绘制红色矩形检测框
        # 参数：左上角x, 左上角y, 宽度, 高度, 颜色
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        
        # 构建显示标签：类别名称 + 置信度
        # detector.labels: 模型中所有类别的名称列表
        # obj.class_id: 当前目标的类别索引
        # obj.score:.2f: 置信度保留2位小数
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        
        # 在检测框左上角绘制文字标签
        # 参数：x坐标, y坐标, 文字内容, 颜色
        # 文字背景会自动填充，确保文字清晰可见
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
    
    # 将处理后的图像显示到屏幕上
    # 这一步会将带有检测框和标签的图像输出到HDMI/LCD显示屏
    disp.show(img)

# 循环结束，程序退出
# 注意：这里没有显式释放资源，程序退出时系统会自动回收