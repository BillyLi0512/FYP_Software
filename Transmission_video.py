import cv2
import socket

#此函数仅测试使用，用于捕获本地摄像头，并做显示
def capture_video_from_camera(camera_index=1, window_name='frame'):
    # 打开摄像头
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        print(f"无法打开摄像头 {camera_index}")
        return

    while True:
        # 读取采集到的一帧视频数据
        ret, frame = capture.read()
        if not ret:
            print("无法读取视频帧")
            break

        # 展示采集到的视频数据
        cv2.imshow(window_name, frame)

        # 按q键退出
        if cv2.waitKey(1) == ord('q'):
            break

    # 释放资源
    capture.release()
    cv2.destroyAllWindows()

def send_video_realtime():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 8001))
    server_socket.listen(1)

    print("等待客户端连接...")
    client_socket, client_address = server_socket.accept()
    print(f"客户端 {client_address} 已连接")

    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    print("摄像头已打开，开始捕获视频")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("无法读取帧")
                break

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = imgencode.tobytes()
            size = len(data)

            try:
                # 发送数据大小
                client_socket.sendall(size.to_bytes(4, 'big'))
                print(f"发送数据大小: {size} 字节")
                # 发送图像数据
                client_socket.sendall(data)
                print("图像数据已发送")
            except Exception as e:
                print(f"发送数据时出错: {e}")
                break
    finally:
        cap.release()
        client_socket.close()
        server_socket.close()
        print("连接关闭，程序结束")