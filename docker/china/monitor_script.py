import os
import time
import shutil
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 监视目录
WATCH_DIR = "/input"
# 缓存目录
CACHE_DIR = "/cache"
# 输出目录
OUTPUT_DIR = "/output"

# 激活虚拟环境
venv_activate = "/opt/mineru_venv/bin/activate"
subprocess.run(f"source {venv_activate}", shell=True, executable="/bin/bash")

# 打印调试信息
print("Debugging information:", flush=True)
print(f"Python version: {subprocess.check_output(['python3', '--version']).decode().strip()}", flush=True)
print(f"Pip version: {subprocess.check_output(['pip3', '--version']).decode().strip()}", flush=True)
print(f"Magic-pdf path: {subprocess.check_output(['which', 'magic-pdf']).decode().strip()}", flush=True)
print(f"inotifywait path: {subprocess.check_output(['which', 'inotifywait']).decode().strip()}", flush=True)

# 确保缓存目录存在
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# 待处理文件队列
file_queue = []

class PDFHandler(FileSystemEventHandler):
    def on_closed(self, event):
        if not event.is_directory and event.src_path.endswith('.pdf'):
            file_path = event.src_path
            # 确保文件已经完全写入
            time.sleep(10)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                print(f"New PDF detected: {file_path}", flush=True)
                file_queue.append(file_path)
            else:
                print(f"File not valid or not a PDF: {file_path}", flush=True)

def process_files():
    while True:
        if file_queue:
            file_path = file_queue.pop(0)
            try:
                # 移动文件到缓存目录
                cache_file_path = os.path.join(CACHE_DIR, os.path.basename(file_path))
                shutil.move(file_path, cache_file_path)
                print(f"Moved {file_path} to {cache_file_path}", flush=True)

                # 调用 magic-pdf 处理 PDF 并生成 Markdown 格式文档
                cmd = f"magic-pdf -p \"{cache_file_path}\" -o \"{OUTPUT_DIR}\""
                print(f"Calling magic-pdf with command: {cmd}", flush=True)
                subprocess.run(cmd, shell=True, check=True)

                # 清空缓存目录
                for root, dirs, files in os.walk(CACHE_DIR):
                    for file in files:
                        os.remove(os.path.join(root, file))
                print(f"Cleared cache directory: {CACHE_DIR}", flush=True)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}", flush=True)
        else:
            time.sleep(1)

if __name__ == "__main__":
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    # 启动文件处理线程
    import threading
    process_thread = threading.Thread(target=process_files)
    process_thread.daemon = True
    process_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()