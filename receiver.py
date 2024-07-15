import cv2
import socket
import numpy as np

def receive_video_realtime(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print(f"连接到服务器 {server_ip}:{server_port}")

    try:
        while True:
            # 接收图像大小
            size_data = client_socket.recv(4)
            if not size_data:
                print("未接收到数据大小，连接可能已关闭")
                break

            size = int.from_bytes(size_data, 'big')
            print(f"接收到数据大小: {size} 字节")

            # 接收图像数据
            data = b''
            while len(data) < size:
                to_read = size - len(data)
                data_chunk = client_socket.recv(4096 if to_read > 4096 else to_read)
                if not data_chunk:
                    print("数据块为空，连接可能已关闭")
                    break
                data += data_chunk

            if len(data) != size:
                print("接收到的数据大小与预期不符")
                continue

            # 解码图像并显示
            img = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
            if frame is None:
                print("图像解码失败")
                continue

            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        client_socket.close()
        cv2.destroyAllWindows()
        print("连接已关闭")

def receive_video(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    try:
        while True:
            # 接收图像大小
            size_data = client_socket.recv(4)
            if not size_data:
                print("not size_data")
                break

            size = int.from_bytes(size_data, 'big')

            # 接收图像数据
            data = b''
            while len(data) < size:
                to_read = size - len(data)
                data_chunk = client_socket.recv(4096 if to_read > 4096 else to_read)
                if not data_chunk:
                    print("Not datachunk")
                    break
                data += data_chunk

            if len(data) != size:
                print("接收到的数据大小不一致")
                continue

            # 解码图像并显示
            print("开始解码图像")
            img = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
            if frame is None:
                print("解码失败")
                continue
            print("解码完成！")
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        client_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    receive_video_realtime("192.168.3.210", 8000)