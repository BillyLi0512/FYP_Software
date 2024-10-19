import cv2

def start_receive_stream(rtsp_url):
    # 打开RTSP视频流
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("无法连接到RTSP流")
        return

    print("开始接收视频流...")

    while True:
        # 读取每一帧
        ret, frame = cap.read()
        if not ret:
            print("无法接收视频流或视频流结束")
            break

        # 显示接收到的帧
        cv2.imshow('RTSP Video Stream', frame)

        # 按'q'退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    rtsp_stream_url = "rtsp://192.168.3.40:5000"  # 发送端的RTSP地址
    start_receive_stream(rtsp_stream_url)
