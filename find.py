import os
import openvino
def find_mo_py(start_dir):
    for root, dirs, files in os.walk(start_dir):
        if "mo.py" in files:
            return os.path.join(root, "mo.py")
    return None

# 获取Conda环境路径
conda_env_path = os.environ['CONDA_PREFIX']
print(conda_env_path)
# 在Conda环境路径中查找mo.py
mo_path = find_mo_py(conda_env_path)
openvino_path = os.path.dirname(openvino.__file__)
print(openvino_path)
if mo_path:
    print(f"Found mo.py at: {mo_path}")
else:
    print("mo.py not found in the current Conda environment.")