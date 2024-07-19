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
import cv2
from ultralytics import YOLO, solutions
import Counting
from threading import Thread
import time
from time import sleep



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

def Get_video_realtime(model):
    # 加载 YOLOv8 模型
    model = YOLO(model)

    # 初始化 Picamera2
    picam2 = Picamera2()

    # 启动相机以获取控制信息
    picam2.start()

    # 创建视频存储文件夹
    if not os.path.exists('video'):
        os.makedirs('video')

    # w,h,fps = 640,480,30
    #
    # # Define points for a line or region of interest in the video frame
    # line_points = [(3 * w / 4, 0), (3 * w / 4, h)]  # Line coordinates
    #
    # # Specify classes to count, for example: person (0) and car (2)
    # classes_to_count = [0]  # Class IDs for person and car
    #
    # # Initialize the video writer to save the output video
    # video_writer = cv2.VideoWriter("object_counting_output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    #
    # # Initialize the Object Counter with visualization options and other parameters
    # counter = Counting.SubCounter(
    #     view_img=True,
    #     reg_pts=line_points,
    #     names=model.names,
    #     draw_tracks=True,
    #     line_thickness=2,
    # )

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
                frame = picam2.capture_array()
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

            # # Perform object tracking on the current frame, filtering by specified classes
            # tracks = model.track(frame, persist=True, show=False, classes=classes_to_count)
            #
            # # Use the Object Counter to count objects in the frame and get the annotated image
            # frame = counter.start_counting(frame, tracks)
            #
            # # 在帧上绘制检测结果
            # annotated_frame = tracks[0].plot()
            #
            # video_writer.write(frame)

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


