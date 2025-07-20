@echo off
chcp 65001 >nul 2>&1
echo === 检查端口占用情况 ===
echo.

echo 检查5000端口:
netstat -ano | findstr :5000
echo.

echo 检查3000端口:
netstat -ano | findstr :3000
echo.

echo 如果看到LISTENING状态，说明端口被占用
echo 最后一列的数字是进程ID(PID)
echo.

echo 要查看是哪个程序占用端口，使用:
echo tasklist /FI "PID eq [进程ID]"
echo.
pause