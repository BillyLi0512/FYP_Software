import cv2
import numpy as np
from openvino.runtime import Core



# 加载 ONNX 模型
model_path = 'model.onnx'  # 你的 ONNX 模型路径
core = Core()
model = core.read_model(model_path)
compiled_model = core.compile_model(model=model, device_name="CPU")
infer_request = compiled_model.create_infer_request()
print("成功读取onnx模型！")
# 获取输入名称（可能是一个集合，取第一个名称）
input_name = list(compiled_model.input(0).names)[0]

# 捕获摄像头视频流
cap = cv2.VideoCapture(1)  # 指定摄像头索引，0 表示第一个摄像头
print("打开摄像头")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 将图像调整为模型期望的输入格式
    input_data = cv2.resize(frame, (640, 640))  # 调整为 YOLOv8 的输入尺寸
    input_data = input_data.transpose((2, 0, 1))  # 调整通道顺序，从 HWC 到 CHW
    input_data = input_data[np.newaxis, ...]  # 添加批次维度
    input_data = input_data.astype(np.float32)  # 确保数据类型为 float32

    # 输入数据归一化到模型期望的范围
    input_data /= 255.0

    # 执行推理
    input_tensor = {input_name: input_data}
    result = infer_request.infer(inputs=input_tensor)

    # 解析推理结果
    output = result[next(iter(result))]
    output = output.squeeze()  # 移除批次维度

    # 获取检测框坐标、类别和置信度
    boxes = output[:, :4]
    scores = output[:, 4]
    class_ids = np.argmax(output[:, 5:], axis=1)

    # 绘制检测框
    for box, score, class_id in zip(boxes, scores, class_ids):
        if score > 0.5:  # 只绘制置信度大于 0.5 的检测框
            x1, y1, x2, y2 = box
            x1 = int(x1 * frame.shape[1])
            y1 = int(y1 * frame.shape[0])
            x2 = int(x2 * frame.shape[1])
            y2 = int(y2 * frame.shape[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Class {class_id}: {score:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 显示结果
    cv2.imshow('Inference Result', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# 清理
cap.release()
cv2.destroyAllWindows()