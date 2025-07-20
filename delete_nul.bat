@echo off
REM 删除错误创建的nul文件的脚本

echo 尝试删除nul文件...

REM 方法1：使用del命令
del "\\?\%cd%\nul" 2>nul:

REM 方法2：使用特殊路径
del "\\.\%cd%\nul" 2>nul:

REM 方法3：重命名后删除
ren nul nul_temp 2>nul:
if exist nul_temp (
    del nul_temp
    echo nul文件已删除
) else (
    echo nul文件可能已经被删除或不存在
)

pause