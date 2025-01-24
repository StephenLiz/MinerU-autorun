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

def monitor_file_status():
    """持续监控 INPUT_DIR 和 CACHE_DIR 的状态"""
    last_state = None  # 用于存储上一次的状态
    while True:
        input_files = [f for f in os.listdir(INPUT_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED_FILE_FORMATS]
        cache_files = [f for f in os.listdir(CACHE_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED_FILE_FORMATS]

        # 确定当前状态
        if not input_files and not cache_files:
            current_state = "INPUT_DIR及CACHE_DIR均无支持的文件格式"
        elif input_files and not cache_files:
            current_state = "INPUT_DIR 有支持的文件，缓存区 CACHE_DIR 为空，开始移动支持的文件和执行转换支持的文件..."
        elif not input_files and cache_files:
            current_state = "CACHE_DIR 有支持的文件，INPUT_DIR 为空，对最后一个支持的文件执行转换..."
        else:
            current_state = "INPUT_DIR及CACHE_DIR均有支持的文件，等待逐一处理支持的文件..."

        # 若状态改变则输出
        if current_state != last_state:
            print(current_state)
            last_state = current_state  # 更新上一次的状态

        time.sleep(5)  # 每5秒检查一次状态

# 调用清空函数清空INPUT_DIR和CACHE_DIR中的文件
clear_supported_files(INPUT_DIR)
clear_supported_files(CACHE_DIR)

# 开始监控文件状态
monitor_file_status()