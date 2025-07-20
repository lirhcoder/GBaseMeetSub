#!/bin/bash
# 启动Web UI的脚本

echo "=== 启动 GBaseMeetSub Web UI ==="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    ./setup_env.sh
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "检查依赖..."
pip install -r requirements.txt

# 创建必要的目录
mkdir -p uploads output data logs

# 初始化空的术语库文件（如果不存在）
if [ ! -f "data/terms.json" ]; then
    echo "{}" > data/terms.json
fi

if [ ! -f "data/corrections_log.json" ]; then
    echo "[]" > data/corrections_log.json
fi

# 启动Flask应用
echo ""
echo "启动Web服务器..."
echo "访问 http://localhost:5000 使用系统"
echo "按 Ctrl+C 停止服务器"
echo ""

python app.py