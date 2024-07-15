import sys
print(sys.path)
sys.path.append('/usr/lib/python3/dist-packages')
from picamera2 import Picamera2
import cv2
import numpy as np
import time


# 初始化 Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

# 定义视频编码器和输出文件
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 30.0, (640, 480))

start_time = time.time()
print("开始捕获视频")

while time.time() - start_time < 10:  # 捕获十秒
    # 捕获图像
    frame = picam2.capture_array()

    # 转换为 OpenCV 格式
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 写入视频文件
    out.write(frame)

    # 显示图像
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
out.release()
cv2.destroyAllWindows()
print("视频捕获结束并已保存")