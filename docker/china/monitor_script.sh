#!/bin/bash

# 监视目录
WATCH_DIR="/input"
# 输出目录
OUTPUT_DIR="/output"

# 激活虚拟环境
source /opt/mineru_venv/bin/activate

# 安装inotify-tools
apt-get update && apt-get install -y inotify-tools

# 打印调试信息
echo "Debugging information:"
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"
echo "Magic-pdf path: $(which magic-pdf)"
echo "inotifywait path: $(which inotifywait)"

# 监视指定目录
inotifywait -m -e close_write --format '%w%f' "$WATCH_DIR" | while read FILE
do
    # 确保文件已经完全写入
    sleep 30

    if [[ -f "$FILE" && "$FILE" == *.pdf && $(stat -c%s "$FILE") -gt 0 ]]; then
        echo "New PDF detected: $FILE"
        # 调用magic-pdf处理PDF并生成Markdown格式文档
        magic-pdf --input "$FILE" --output "$OUTPUT_DIR" --config /root/magic-pdf.json
        # 处理完成后删除已处理的PDF文档
        rm "$FILE"
    else
        echo "File not valid or not a PDF: $FILE"
    fi
done