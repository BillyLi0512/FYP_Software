import cv2

def main():
    cap = cv2.VideoCapture(0)  # 从摄像头获取视频流
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    # 使用GStreamer管道来发送视频流
    gst_pipeline = (
        "appsrc ! "
        "videoconvert ! "
        "jpegenc ! "
        "rtpjpegpay ! "
        "udpsink host=127.0.0.1 port=8554"
    )
    out = cv2.VideoWriter(gst_pipeline, cv2.CAP_GSTREAMER, 0, 25, (640, 480), True)

    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        out.write(frame)

        cv2.imshow('server', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()