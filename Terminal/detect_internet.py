import cv2
from ultralytics import YOLO
from flask import Flask, Response, render_template_string
from cv2 import getTickCount, getTickFrequency
import sys
sys.path.append('/usr/lib/python3/dist-packages')
from picamera2 import Picamera2, Preview
import time
import os
from datetime import datetime
import camera
# 加载 YOLOv8 模型
model = YOLO("best.pt")

# 初始化 Picamera2
picam2 = camera.Camera()
picam2.start()
# 创建视频存储文件夹
if not os.path.exists('video'):
    os.makedirs('video')

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

def Get_video_realtime():
    start_time = time.time()
    video_writer = None
    while True:
            current_time = time.time()
            loop_start = getTickCount()

            # 如果视频写入对象不存在或已经运行了超过10分钟，创建一个新的视频写入对象
            if video_writer is None or (current_time - start_time) >= 30:
                if video_writer is not None:
                    video_writer.release()

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                video_filename = f'video/{timestamp}.avi'  # 使用 AVI 格式
                video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
                start_time = current_time

            # 捕获图像
            try:
                frame = picam2.capture_frame()
                if frame is None:
                    print("Captured frame is None, skipping...")
                    continue
            except Exception as e:
                print(f"Error capturing frame: {e}")
                continue

            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 将帧写入视频文件
            video_writer.write(frame_bgr)

            results = model.predict(source=frame_bgr)  # 对当前帧进行目标检测并显示结果
            annotated_frame = results[0].plot()
            print("成功完成yolo8推理。")
            # 计算 FPS
            loop_time = getTickCount() - loop_start
            total_time = loop_time / getTickFrequency()
            FPS = int(1 / total_time)

            # 在图像左上角添加FPS文本
            fps_text = f"FPS: {FPS:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(annotated_frame, fps_text, (10, 30), font, 1, (0, 0, 255), 2)

            # 编码为 JPEG 格式
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # 确保在程序结束时释放视频写入对象
    if video_writer is not None:
        video_writer.release()
@app.route('/video')
def video():
    return Response(Get_video_realtime(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.3.210', port=8001)
