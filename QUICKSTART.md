# 快速开始指南

## Windows 用户

### 1. 环境检查
首先运行环境检查脚本：
```batch
check_env.bat
```

### 2. 安装Python（如果需要）
如果系统没有Python，请安装：

**方法1：官网下载**
- 访问 https://www.python.org/downloads/
- 下载Python 3.8或更高版本
- 安装时勾选 "Add Python to PATH"

**方法2：使用包管理器**
```batch
# 使用 winget (Windows 11)
winget install Python.Python.3.11

# 使用 chocolatey
choco install python

# 使用 scoop
scoop install python
```

### 3. 设置项目环境
```batch
# 克隆项目
git clone https://github.com/lirhcoder/GBaseMeetSub.git
cd GBaseMeetSub

# 设置虚拟环境
setup_env.bat
```

### 4. 启动Web UI
```batch
run_web.bat
```

然后访问 http://localhost:5000

## 常见问题

### Q: 提示 "python 不是内部或外部命令"
A: Python未正确安装或未添加到PATH。重新安装Python时勾选"Add Python to PATH"

### Q: 创建虚拟环境失败
A: 尝试以下命令：
```batch
# 方法1：使用python命令
python -m venv venv

# 方法2：使用py命令
py -3 -m venv venv

# 方法3：手动指定Python路径
C:\Users\[用户名]\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

### Q: pip安装包很慢
A: 使用国内镜像源：
```batch
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: Whisper模型下载失败
A: 模型文件较大，确保网络稳定。也可以手动下载模型文件放到 `~/.cache/whisper/` 目录

## Linux/MacOS 用户

### 1. 安装依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg git

# MacOS
brew install python ffmpeg git
```

### 2. 设置项目
```bash
# 克隆项目
git clone https://github.com/lirhcoder/GBaseMeetSub.git
cd GBaseMeetSub

# 设置虚拟环境
chmod +x setup_env.sh
./setup_env.sh
```

### 3. 启动Web UI
```bash
./run_web.sh
```

## 快速测试

1. 准备一个MP4格式的日语会议录音
2. 在Web界面上传文件
3. 选择模型大小（建议先用"small"快速测试）
4. 等待处理完成
5. 下载生成的字幕文件

## 下一步

- 查看 [README.md](README.md) 了解更多功能
- 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 参与开发
- 在 [Issues](https://github.com/lirhcoder/GBaseMeetSub/issues) 报告问题