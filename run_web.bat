@echo off
REM 启动Web UI的脚本

echo === 启动 GBaseMeetSub Web UI ===

REM 检查虚拟环境
if not exist venv (
    echo 虚拟环境不存在，正在创建...
    call setup_env.bat
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖
echo 检查依赖...
pip install -r requirements.txt

REM 创建必要的目录
if not exist uploads mkdir uploads
if not exist output mkdir output
if not exist data mkdir data
if not exist logs mkdir logs

REM 初始化空的术语库文件（如果不存在）
if not exist data\terms.json (
    echo {} > data\terms.json
)

if not exist data\corrections_log.json (
    echo [] > data\corrections_log.json
)

REM 启动Flask应用
echo.
echo 启动Web服务器...
echo 访问 http://localhost:5000 使用系统
echo 按 Ctrl+C 停止服务器
echo.

python app.py