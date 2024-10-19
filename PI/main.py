import cv2
import threading

def start_stream(video_file_path, stream_id):
    while True:

        # 检查传入的视频文件路径，如果为0则使用摄像头
        cap = cv2.VideoCapture(video_file_path if video_file_path != 0 else 0)

        if not cap.isOpened():
            print(f"无法打开视频文件或摄像头: {video_file_path}")
            return


        # 设置分辨率
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # 宽度
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # 高度
        cap.set(cv2.CAP_PROP_FPS, 30)  # 帧率

        # gstreamer命令，使用h264编码并通过RTSP传输
        gst_str = (
            'appsrc ! videoconvert ! '
            'x264enc speed-preset=ultrafast tune=zerolatency bitrate=1000 ! '
            'rtph264pay config-interval=1 pt=96 ! '
            'udpsink host=192.168.3.40 port={5000 + stream_id} auto-multicast=true'
        )

        # 使用gstreamer打开视频流
        out = cv2.VideoWriter(gst_str, cv2.CAP_GSTREAMER, 0, 30, (1920, 1080), True)

        if not out.isOpened():
            print("无法打开视频流")
            cap.release()
            return

        print(f"开始推流视频: {video_file_path} 到端口 {5000 + stream_id}...")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("视频播放完毕，重新开始推流...")
                break  # 结束当前推流，重新开始播放视频

            # 推送帧到网络
            out.write(frame)

            # 按'q'退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                out.release()
                cv2.destroyAllWindows()
                return  # 如果按'q'，终止推流并退出循环

        # 释放资源
        cap.release()
        out.release()

def thread_function(video_file_path, stream_id):
    start_stream(video_file_path, stream_id)

if __name__ == "__main__":
    print("树莓派视频流推送服务已开启.\n")

    # 询问用户要推流的视频数量
    num_streams = int(input("请输入需要推流的数量: "))

    # 存储每个视频文件路径或摄像头ID
    video_sources = []

    for i in range(num_streams):
        # 询问用户是使用摄像头还是视频文件
        source_type = input(f"推流 {i + 1}: 输入 'c' 使用摄像头，输入 'v' 使用视频文件: ").lower()

        if source_type == 'c':
            video_sources.append(0)  # 使用摄像头
        elif source_type == 'v':
            video_path = input(f"请输入视频文件 {i + 1} 的路径: ")
            video_sources.append(video_path)
        else:
            print("无效输入，请输入 'c' 或 'v'")
            exit(1)

    # 创建多线程来推流多个视频源
    threads = []
    for idx, video_source in enumerate(video_sources):
        t = threading.Thread(target=thread_function, args=(video_source, idx))
        threads.append(t)
        t.start()

    # 等待所有线程完成
    for t in threads:
        t.join()

    print("所有视频推流已完成。")

