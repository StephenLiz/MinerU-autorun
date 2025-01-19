import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

# 监视目录
WATCH_DIR = "/cache"
# 输入目录
INPUT_DIR = "/input"
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

# 待处理文件队列
file_queue = []


class PDFHandler(FileSystemEventHandler):
    def on_closed(self, event):
        if not event.is_directory and event.src_path.endswith('.pdf'):
            file_path = event.src_path
            # 确保文件已经完全写入
            time.sleep(10)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                print(f"New PDF detected: {file_path}")
                file_queue.append(file_path)
            else:
                print(f"File not valid or not a PDF: {file_path}")


def process_files():
    while True:
        if file_queue:
            file_path = file_queue.pop(0)
            # 移动文件到输入目录
            input_file_path = os.path.join(INPUT_DIR, os.path.basename(file_path))
            shutil.move(file_path, input_file_path)
            print(f"Moved PDF to input directory: {input_file_path}")

            # 调用magic-pdf处理PDF并生成Markdown格式文档
            cmd = f"magic-pdf -p \"{input_file_path}\" -o \"{OUTPUT_DIR}\""
            print(f"Calling magic-pdf with command: {cmd}")
            subprocess.run(cmd, shell=True, check=True)

            # 处理完成后删除已处理的PDF文档
            os.remove(input_file_path)
            print(f"Removed processed PDF: {input_file_path}")

        time.sleep(1)


if __name__ == "__main__":
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        process_files()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()