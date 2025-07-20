@echo off
chcp 65001 >nul 2>&1
echo === 停止所有Flask/Python进程 ===
echo.

echo 查找Python进程...
tasklist | findstr python
echo.

echo 是否要终止所有Python进程? (这会停止所有Python程序)
echo 按 Ctrl+C 取消，或按任意键继续...
pause >nul

echo.
echo 终止Python进程...
taskkill /F /IM python.exe 2>nul
echo.

echo 完成！现在可以重新启动Flask应用
pause