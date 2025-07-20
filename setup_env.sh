#!/bin/bash
# 虚拟环境设置脚本

echo "=== 设置GBaseMeetSub开发环境 ==="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "Python版本检查通过: $python_version"

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 安装开发依赖
if [ -f "requirements-dev.txt" ]; then
    echo "安装开发依赖..."
    pip install -r requirements-dev.txt
fi

# 验证日语分词工具安装
echo "验证日语分词工具..."
python -c "import fugashi; print('日语分词工具安装成功')" 2>/dev/null || echo "日语分词工具安装可能有问题，但可以继续"

# 创建必要的目录
echo "创建项目目录..."
mkdir -p data output logs

# 初始化空的术语库文件
if [ ! -f "data/terms.json" ]; then
    echo "{}" > data/terms.json
    echo "创建空术语库文件"
fi

if [ ! -f "data/corrections_log.json" ]; then
    echo "[]" > data/corrections_log.json
    echo "创建空纠正日志文件"
fi

echo ""
echo "=== 环境设置完成 ==="
echo "使用以下命令激活虚拟环境:"
echo "  source venv/bin/activate"
echo ""
echo "使用以下命令退出虚拟环境:"
echo "  deactivate"