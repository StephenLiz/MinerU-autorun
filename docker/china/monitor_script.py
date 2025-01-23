import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.input_dir_empty = True
        self.cache_dir_empty = True
        self.last_empty_message = False  # 标志位，防止重复打印

    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            # 过滤系统生成的临时文件（以 "._" 开头的文件）
            if filename.startswith('._'):
                return

            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.ppt', '.pptx')):
                # 只在第一次出现新文件时打印
                if event.src_path.startswith(INPUT_DIR):
                    print(f"INPUT_DIR有名为{filename}的新文件产生")
                    self.input_dir_empty = False
                    self.handle_new_file_input(filename)  # 调用处理函数
                elif event.src_path.startswith(CACHE_DIR):
                    print(f"CACHE_DIR有名为{filename}的新文件产生")
                    self.cache_dir_empty = False
                    self.handle_new_file_cache(filename)  # 调用处理函数

                # 只有成功检测到有效文件时，重置上一个空文件信息
                self.last_empty_message = False

    def check_empty_directories(self):
        if self.input_dir_empty and self.cache_dir_empty and not self.last_empty_message:
            print("INPUT_DIR及CACHE_DIR均无文件")
            self.last_empty_message = True  # 设置标志位，防止重复打印

    def handle_new_file_input(self, filename):
        # 处理 INPUT_DIR 中的文件
        print(f"处理INPUT_DIR中的文件: {filename}")

    def handle_new_file_cache(self, filename):
        # 处理 CACHE_DIR 中的文件
        print(f"处理CACHE_DIR中的文件: {filename}")

def clear_directory(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.ppt', '.pptx')):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"已删除文件: {file_path}")

if __name__ == "__main__":
    # 清空输入和缓存目录中的所有MinerU支持的文件
    clear_directory(INPUT_DIR)
    clear_directory(CACHE_DIR)

    event_handler = MyHandler()
    observer = Observer()

    observer.schedule(event_handler, INPUT_DIR, recursive=True)
    observer.schedule(event_handler, CACHE_DIR, recursive=True)

    try:
        observer.start()
        print("开始监视文件夹...")
        while True:
            time.sleep(1)
            event_handler.check_empty_directories()
            # 每次检查后重置目录的空状态
            event_handler.input_dir_empty = True
            event_handler.cache_dir_empty = True
    except KeyboardInterrupt:
        observer.stop()
    observer.join()