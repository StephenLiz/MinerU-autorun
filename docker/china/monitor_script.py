import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 监视目录
WATCH_DIR = "/input"
# 输出目录
OUTPUT_DIR = "/output"

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
        print("Hello world")

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