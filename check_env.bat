@echo off
REM 环境检查脚本

echo === GBaseMeetSub 环境检查 ===
echo.

REM 检查Python
echo 检查Python安装...
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 找到 python 命令
    python --version
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] 找到 python3 命令
        python3 --version
    ) else (
        where py >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] 找到 py 命令
            py -3 --version
        ) else (
            echo [错误] 未找到Python
            echo 请从 https://www.python.org/downloads/ 下载安装Python 3.8+
        )
    )
)
echo.

REM 检查FFmpeg
echo 检查FFmpeg安装...
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] FFmpeg 已安装
    ffmpeg -version | findstr "ffmpeg version"
) else (
    echo [警告] FFmpeg 未安装
    echo 请从 https://ffmpeg.org/download.html 下载安装
    echo 或使用: winget install ffmpeg
)
echo.

REM 检查Git
echo 检查Git安装...
where git >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git 已安装
    git --version
) else (
    echo [警告] Git 未安装
)
echo.

REM 检查虚拟环境
echo 检查虚拟环境...
if exist venv (
    echo [OK] 虚拟环境已创建
) else (
    echo [提示] 虚拟环境未创建，运行 setup_env.bat 创建
)
echo.

REM 检查CUDA (可选)
echo 检查CUDA支持...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 检测到NVIDIA GPU
    nvidia-smi --query-gpu=name --format=csv,noheader
) else (
    echo [提示] 未检测到NVIDIA GPU，将使用CPU模式
)
echo.

echo === 检查完成 ===
echo.
echo 如果有错误或警告，请按照提示安装相应软件
echo 然后运行 setup_env.bat 设置开发环境
echo.
pause