@echo off
REM Windows虚拟环境设置脚本

echo === 设置GBaseMeetSub开发环境 ===

REM 检查Python命令
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :check_version
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :check_version
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto :check_version
)

echo 错误: 未找到Python，请先安装Python 3.8或更高版本
echo 请访问 https://www.python.org/downloads/ 下载安装
exit /b 1

:check_version
echo 使用Python命令: %PYTHON_CMD%
%PYTHON_CMD% --version

REM 创建虚拟环境
echo 创建虚拟环境...
%PYTHON_CMD% -m venv venv

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo 升级pip...
%PYTHON_CMD% -m pip install --upgrade pip

REM 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt

REM 安装开发依赖
if exist requirements-dev.txt (
    echo 安装开发依赖...
    pip install -r requirements-dev.txt
)

REM 验证日语分词工具安装
echo 验证日语分词工具...
%PYTHON_CMD% -c "import fugashi; print('日语分词工具安装成功')" 2>nul:
if errorlevel 1 (
    echo 日语分词工具安装可能有问题，但可以继续
)

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