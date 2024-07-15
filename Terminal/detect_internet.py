import cv2
from ultralytics import YOLO
from flask import Flask, Response, render_template_string
from cv2 import getTickCount, getTickFrequency

# 加载 YOLOv8 模型
model = YOLO("best.pt")

# 获取摄像头内容，参数 0 表示使用默认的摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
else:
    print("成功打开摄像头")

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

def generate_frames():
    while True:
        loop_start = getTickCount()
        success, frame = cap.read()  # 读取摄像头的一帧图像

        if not success:
            print("未成功获取图像帧")
            break

        results = model.predict(source=frame)  # 对当前帧进行目标检测并显示结果
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

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.3.210', port=8001)
