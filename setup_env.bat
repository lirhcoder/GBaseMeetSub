@echo off
REM Windows虚拟环境设置脚本

echo === 设置GBaseMeetSub开发环境 ===

REM 检查Python版本
python --version 2>nul
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    exit /b 1
)

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv venv

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt

REM 安装开发依赖
if exist requirements-dev.txt (
    echo 安装开发依赖...
    pip install -r requirements-dev.txt
)

REM 下载日语分词数据
echo 下载日语分词数据...
python -m unidic download

REM 创建必要的目录
echo 创建项目目录...
if not exist data mkdir data
if not exist output mkdir output
if not exist logs mkdir logs

REM 初始化空的术语库文件
if not exist data\terms.json (
    echo {} > data\terms.json
    echo 创建空术语库文件
)

if not exist data\corrections_log.json (
    echo [] > data\corrections_log.json
    echo 创建空纠正日志文件
)

echo.
echo === 环境设置完成 ===
echo 使用以下命令激活虚拟环境:
echo   venv\Scripts\activate.bat
echo.
echo 使用以下命令退出虚拟环境:
echo   deactivate