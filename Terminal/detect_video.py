import cv2
from ultralytics import YOLO
from threading import Thread
def detect_video(model_path, video_path, output_path='output.mp4'):
    # 加载 YOLO 模型
    model = YOLO(model_path)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 获取视频的宽度、高度和帧率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 定义视频编解码器并创建 VideoWriter 对象
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 使用 YOLO 模型进行推理
        results = model.predict(source=frame, show=False)  # 关闭显示窗口

        # 获取推理结果并绘制到帧上
        annotated_frame = results[0].plot()

        # 将处理后的帧写入输出视频文件
        out.write(annotated_frame)

        # # 可选：在窗口中显示处理后的帧
        # cv2.imshow('frame', annotated_frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # 释放视频捕获和写入对象
    cap.release()
    out.release()
    # cv2.destroyAllWindows()
    print("The process of video:"+video_path+" is finished.")

if __name__ == '__main__':

    thread1 = Thread(target=detect_video, args=('best.pt', '1.mp4', 'output_video_1.avi'))  # 线程1
    thread2 = Thread(target=detect_video, args=('best.pt', '2.mp4', 'output_video_2.avi'))  # 线程2

    thread1.start()  # 线程1启动
    thread2.start()  # 任务2启动
    thread2.join()  # 等待线程2
    thread1.join()  # 等待线程1完成线程