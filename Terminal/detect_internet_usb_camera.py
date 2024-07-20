from flask import Flask, render_template_string, Response
import cv2
import time
from datetime import datetime
import os
from ultralytics import YOLO  # 假设你在使用ultralytics YOLO库

app = Flask(__name__)

# 添加根路由
@app.route('/')
def index():
    # 提供一个简单的页面，包含一个嵌入的视频流
    return render_template_string('''
    <html>
    <head>
        <title>视频流</title>
    </head>
    <body>
        <h1>实时视频流</h1>
        <img src="{{ url_for('video') }}">
    </body>
    </html>
    ''')

def Get_video_realtime(model_path):
    # 加载 YOLOv8 模型
    model = YOLO(model_path)

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    # 创建视频存储文件夹
    if not os.path.exists('video'):
        os.makedirs('video')

    start_time = time.time()
    video_writer = None

    while True:
        current_time = time.time()

        # 如果视频写入对象不存在或已经运行了超过10分钟，创建一个新的视频写入对象
        if video_writer is None or (current_time - start_time) >= 30:
            if video_writer is not None:
                video_writer.release()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_filename = f'video/{timestamp}.avi'  # 使用 AVI 格式
            video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
            start_time = current_time

        # 捕获图像
        ret, frame = cap.read()
        if not ret:
            print("无法读取帧，跳过...")
            continue

        # 将帧写入视频文件
        video_writer.write(frame)

        results = model.predict(source=frame)  # 对当前帧进行目标检测并显示结果
        annotated_frame = results[0].plot()

        print("成功完成yolo8推理。")

        # 编码为 JPEG 格式
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # 确保在程序结束时释放视频写入对象
    if video_writer is not None:
        video_writer.release()
    cap.release()

@app.route('/video')
def video():
    return Response(Get_video_realtime("path/to/your/yolo_model.pt"), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.3.210', port=8001)