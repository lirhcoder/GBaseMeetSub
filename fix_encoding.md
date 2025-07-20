# 解决 VSCode 中批处理文件乱码问题

## 已实施的解决方案

1. **批处理文件添加了 UTF-8 编码设置**
   - 所有 .bat 文件开头添加了 `chcp 65001 >nul 2>&1`
   - 这会将代码页切换到 UTF-8 (65001)

2. **VSCode 配置文件**
   - 创建了 `.vscode/settings.json`
   - 设置终端默认使用 UTF-8 编码

## 其他解决方法

### 方法1：更改 VSCode 终端编码
1. 打开 VSCode 设置 (Ctrl+,)
2. 搜索 "terminal.integrated.shellArgs.windows"
3. 添加参数：`["/K", "chcp 65001"]`

### 方法2：更改系统默认编码
1. 打开"控制面板" → "区域" → "管理"
2. 点击"更改系统区域设置"
3. 勾选"Beta: 使用 Unicode UTF-8 提供全球语言支持"
4. 重启计算机

### 方法3：使用 PowerShell 代替 CMD
在 VSCode 终端中切换到 PowerShell：
- 点击终端右上角的下拉箭头
- 选择 "Select Default Profile"
- 选择 "PowerShell"

### 方法4：临时解决方案
每次打开终端后手动执行：
```cmd
chcp 65001
```

## 验证编码是否正确
运行以下命令查看当前代码页：
```cmd
chcp
```
应该显示：`Active code page: 65001`

## 注意事项
- UTF-8 编码 (65001) 可能会导致某些老旧程序出现兼容性问题
- 如果遇到问题，可以切换回默认编码：`chcp 936`（简体中文 GBK）