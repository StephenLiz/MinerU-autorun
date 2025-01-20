import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

# 监视目录
WATCH_DIR = "/input"
# 输出目录
OUTPUT_DIR = "/output"
# 缓存目录
CACHE_DIR = "/cache"

# 确保缓存目录存在
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# 激活虚拟环境
venv_activate = "/opt/mineru_venv/bin/activate"
subprocess.run(f"source {venv_activate}", shell=True, executable="/bin/bash")

# 打印调试信息
print("Debugging information:")
print(f"Python version: {subprocess.check_output(['python3', '--version']).decode().strip()}")
print(f"Pip version: {subprocess.check_output(['pip3', '--version']).decode().strip()}")
print(f"Magic-pdf path: {subprocess.check_output(['which', 'magic-pdf']).decode().strip()}")
print(f"inotifywait path: {subprocess.check_output(['which', 'inotifywait']).decode().strip()}")

class PDFHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        print("PDFHandler initialized and ready to monitor files")

    def on_closed(self, event):
        print("运行on_closed函数")
        if not event.is_directory and event.src_path.endswith('.pdf'):
            file_path = event.src_path
            # 获取文件列表并按创建时间排序
            files = sorted([f for f in os.listdir(WATCH_DIR) if f.endswith('.pdf')], key=lambda x: os.path.getctime(os.path.join(WATCH_DIR, x)))
            for file_name in files:
                src_file = os.path.join(WATCH_DIR, file_name)
                dest_file = os.path.join(CACHE_DIR, file_name)
                # 移动文件
                shutil.move(src_file, dest_file)
                print(f"{file_name} 已从 {WATCH_DIR} 移动到 {CACHE_DIR}")

if __name__ == "__main__":
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()