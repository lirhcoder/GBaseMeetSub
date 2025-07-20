@echo off
chcp 65001 >nul 2>&1
REM 同步文件到测试目录

echo === 同步文件到测试目录 ===
echo.

set SOURCE_DIR=C:\development\shimiz-konwledge
set TEST_DIR=C:\development\GBaseMeetSub

echo 源目录: %SOURCE_DIR%
echo 测试目录: %TEST_DIR%
echo.

REM 复制Python文件
echo 复制Python文件...
xcopy "%SOURCE_DIR%\app.py" "%TEST_DIR%\" /Y
xcopy "%SOURCE_DIR%\requirements.txt" "%TEST_DIR%\" /Y
xcopy "%SOURCE_DIR%\requirements-dev.txt" "%TEST_DIR%\" /Y 2>nul

REM 复制源代码目录
echo 复制源代码...
xcopy "%SOURCE_DIR%\src\*.*" "%TEST_DIR%\src\" /Y /E

REM 复制模板文件
echo 复制模板文件...
xcopy "%SOURCE_DIR%\templates\*.*" "%TEST_DIR%\templates\" /Y /E

REM 复制静态文件
echo 复制静态文件...
xcopy "%SOURCE_DIR%\static\*.*" "%TEST_DIR%\static\" /Y /E /S

REM 复制批处理脚本
echo 复制脚本文件...
xcopy "%SOURCE_DIR%\*.bat" "%TEST_DIR%\" /Y
xcopy "%SOURCE_DIR%\*.sh" "%TEST_DIR%\" /Y 2>nul

REM 复制配置文件
echo 复制配置文件...
xcopy "%SOURCE_DIR%\.env.example" "%TEST_DIR%\" /Y 2>nul
xcopy "%SOURCE_DIR%\pyproject.toml" "%TEST_DIR%\" /Y 2>nul
xcopy "%SOURCE_DIR%\.gitignore" "%TEST_DIR%\" /Y

echo.
echo === 同步完成 ===
echo 现在可以在测试目录运行: run_web.bat
echo.
pause