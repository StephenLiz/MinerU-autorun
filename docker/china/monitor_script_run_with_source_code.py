import os
import time
import subprocess
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
            try:
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            except OSError as e:
                print(f"删除文件 {file_path} 失败: {e}")

    print(f"已清空{directory}中符合格式的文件.")


def wait_for_file_stable(file_path):
    """等待文件大小稳定"""
    last_size = -1
    while True:
        current_size = os.path.getsize(file_path)
        if current_size == last_size:
            break
        last_size = current_size
        time.sleep(4)
    print(f"文件 {file_path} 大小稳定。")


def process_files():
    """处理文件，移动至缓存并执行转换"""
    # 获取符合支持格式的文件列表，并忽略以 "._" 开头的文件
    input_files = [f for f in os.listdir(INPUT_DIR)
                   if os.path.splitext(f)[1].lower() in SUPPORTED_FILE_FORMATS and not f.startswith("._")]

    if not input_files:
        print("INPUT_DIR 中没有符合格式的文件，稍后再试。")
        return

    # 按最后修改时间排序，找到最旧的文件
    input_files.sort(key=lambda f: os.path.getmtime(os.path.join(INPUT_DIR, f)))
    oldest_file = input_files[0]
    print(f"最旧的文件是: {oldest_file}")

    # 等待文件大小稳定
    src_path = os.path.join(INPUT_DIR, oldest_file)
    wait_for_file_stable(src_path)

    # 移动文件到缓存目录
    dst_path = os.path.join(CACHE_DIR, oldest_file)
    try:
        shutil.move(src_path, dst_path)
        print(f"{oldest_file} 从 {INPUT_DIR} 移动到 {CACHE_DIR}")
    except (OSError, shutil.Error) as e:
        print(f"移动文件 {oldest_file} 失败: {e}")
        return

    # 等待移动后的文件大小稳定
    wait_for_file_stable(dst_path)

    # 执行文件转换
    output_path = OUTPUT_DIR  # 假设输出目录为 OUTPUT_DIR
    magic_pdf_command = f"magic-pdf -p '{dst_path}' -o '{output_path}'"
    print(f"执行命令: {magic_pdf_command}")

    try:
        subprocess.run(magic_pdf_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")

    # 改变 OUTPUT_DIR 的权限，让所有用户有权限删除 OUTPUT_DIR 及其子目录中的所有文件
    chmod_command = f"chmod -R 777 '{output_path}'"
    print(f"执行命令: {chmod_command}")

    try:
        subprocess.run(chmod_command, shell=True, check=True)
        print(f"已成功更改 {output_path} 的权限。")
    except subprocess.CalledProcessError as e:
        print(f"更改权限失败: {e}")

    # 删除缓存文件
    try:
        os.remove(dst_path)
        print(f"已删除缓存中的文件: {dst_path}")
    except OSError as e:
        print(f"删除缓存文件 {dst_path} 失败: {e}")


def monitor_file_status():
    """持续监控 INPUT_DIR 和 CACHE_DIR 的状态"""
    last_state = None  # 用于存储上一次的状态
    while True:
        # 获取符合支持格式的文件列表，并忽略以 "._" 开头的文件
        input_files = [f for f in os.listdir(INPUT_DIR)
                       if os.path.splitext(f)[1].lower() in SUPPORTED_FILE_FORMATS and not f.startswith("._")]
        cache_files = [f for f in os.listdir(CACHE_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED_FILE_FORMATS]

        # 确定当前状态
        if not input_files and not cache_files:
            current_state = "INPUT_DIR及CACHE_DIR均无支持的文件格式"
        elif input_files and not cache_files:
            current_state = "INPUT_DIR 有支持的文件，缓存区 CACHE_DIR 为空，开始移动支持的文件和执行转换支持的文件..."
            process_files()  # 调用处理文件的函数
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

