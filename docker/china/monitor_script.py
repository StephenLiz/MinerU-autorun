import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

# 输入目录
INPUT_DIR = "/home/gwongzaak/SMBservice/input"
# 输出目录
OUTPUT_DIR = "/home/gwongzaak/SMBservice/output"
# 缓存目录
CACHE_DIR = "/home/gwongzaak/SMBservice/cache"

# 激活虚拟环境
venv_activate = "/opt/mineru_venv/bin/activate"
subprocess.run(f"source {venv_activate}", shell=True, executable="/bin/bash")

# 打印调试信息
print("Debugging information:")
print(f"Python version: {subprocess.check_output(['python3', '--version']).decode().strip()}")
print(f"Pip version: {subprocess.check_output(['pip3', '--version']).decode().strip()}")
print(f"Magic-pdf path: {subprocess.check_output(['which', 'magic-pdf']).decode().strip()}")
print(f"inotifywait path: {subprocess.check_output(['which', 'inotifywait']).decode().strip()}")


# 定义支持的文件格式
SUPPORTED_FILE_FORMATS = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.ppt', '.pptx'}

print("开始监视文件夹...")

def clear_supported_files(directory):
    """清空指定目录中符合支持文件格式的文件"""
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lower() in SUPPORTED_FILE_FORMATS:
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
    # 提示文件夹已清空
    print(f"已清空{directory}中符合格式的文件.")

# 调用清空函数清空INPUT_DIR和CACHE_DIR中的文件
clear_supported_files(INPUT_DIR)
clear_supported_files(CACHE_DIR)