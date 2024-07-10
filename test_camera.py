import cv2

cap = cv2.VideoCapture('/dev/video0')

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("摄像头已打开，开始捕获视频")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("无法读取帧")
        continue

    print("读取到一帧")

    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()