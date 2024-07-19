import torch
import torchvision
import os
# # 加载检查点
checkpoint = torch.load('best.pt', map_location=torch.device('cpu'))
#
# # 从字典中提取模型
# model = checkpoint['model']  # 根据字典的键来提取模型
# model.eval()  # 确保模型在评估模式
#
# # 打印模型结构
# print(model)
# 1. 载入PyTorch模型
model_path = 'best.pt'  # 你的.pt文件路径
model = torch.load(model_path, map_location=torch.device('cpu'))
model = checkpoint['model']  # 根据字典的键来提取模型
model.eval()  # 确保模型在评估模式
# 2. 确保模型使用的浮点精度为Float
model = model.float()
# 2. 创建一个示例输入张量
dummy_input = torch.randn(1, 3, 640, 640).float()  # 修改为你的模型的输入维度

# 3. 导出为ONNX格式
onnx_path = 'model.onnx'
torch.onnx.export(model, dummy_input, onnx_path, opset_version=11)

print(f"ONNX model saved to {onnx_path}")
