# 日语会议语音识别系统 (GBaseMeetSub)

具有自动术语积累功能的语音识别系统，专门优化日语会议记录处理。

## 特性

- 🎙️ 基于OpenAI Whisper的高精度日语识别
- 📚 自动术语积累机制 - 所有纠正自动记录为专用术语
- 🔧 模块化设计 - 各组件可独立测试和使用
- 📊 精度验证 - WER/CER等多维度评估
- 🚀 批量处理支持
- 🔒 虚拟环境隔离开发
- ⚡ 分片处理 - 长音频自动分割处理，提高效率
- 🎵 音频预览 - 处理过程中可以播放音频
- 📝 实时字幕预览 - 边处理边查看识别结果

## 系统要求

- Python 3.8 或更高版本
- FFmpeg (用于音频处理)
- 4GB+ RAM (运行large模型需要更多)
- (可选) NVIDIA GPU 用于加速

## 快速开始

### 环境设置

#### Linux/MacOS
```bash
# 克隆项目
git clone https://github.com/lirhcoder/GBaseMeetSub.git
cd GBaseMeetSub

# 运行环境设置脚本
chmod +x setup_env.sh
./setup_env.sh

# 或手动设置
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows
```batch
# 克隆项目
git clone https://github.com/lirhcoder/GBaseMeetSub.git
cd GBaseMeetSub

# 运行环境设置脚本
setup_env.bat

# 或手动设置
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 开发环境

对于开发者，请额外安装开发依赖：
```bash
pip install -r requirements-dev.txt
```

### 基础使用

```python
from src.main_pipeline import SpeechProcessingPipeline

# 创建处理管道
pipeline = SpeechProcessingPipeline()

# 处理音频文件
result = pipeline.process_audio("meeting.mp4")
```

### 术语学习

```python
# 用户纠正会自动学习
pipeline.learn_from_feedback(
    original="错误识别",
    corrected="正确术语",
    context="会议上下文"
)
```

## 模块说明

- **term_manager.py**: 术语管理核心，自动记录和学习
- **speech_recognizer.py**: Whisper封装，支持分段处理
- **term_corrector.py**: 高效术语修正，使用Trie树优化
- **subtitle_generator.py**: 多格式字幕生成
- **accuracy_validator.py**: 精度评估工具

## 术语库格式

```json
{
  "原词": {
    "correct": "正确词",
    "frequency": 5,
    "confidence": 0.95,
    "contexts": ["上下文1", "上下文2"],
    "auto_learned": true
  }
}
```

## 运行示例

### Web UI（推荐）

快速启动Web界面：
```bash
# Linux/MacOS
chmod +x run_web.sh
./run_web.sh

# Windows
run_web.bat
```

然后在浏览器中访问 http://localhost:5000

Web UI功能：
- 拖拽上传音频文件
- 实时显示处理进度
- 下载生成的字幕文件
- 管理和添加术语库
- 查看修正示例

### 命令行使用

确保已激活虚拟环境：
```bash
# Linux/MacOS
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

运行示例程序：
```bash
# 运行交互式示例
python example_usage.py

# 或直接处理文件
python -m src.main_pipeline --audio meeting.mp4 --output output/
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html

# 运行特定测试
python -m pytest tests/test_term_manager.py
```

## 开发指南

### 代码风格

项目使用以下工具保证代码质量：
```bash
# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/

# import排序
isort src/ tests/
```

### 虚拟环境管理

```bash
# 更新依赖后重新生成requirements.txt
pip freeze > requirements.txt

# 退出虚拟环境
deactivate

# 删除虚拟环境（如需重建）
rm -rf venv/  # Linux/MacOS
rmdir /s venv  # Windows
```

## 故障排除

1. **FFmpeg未安装**
   - Linux: `sudo apt install ffmpeg`
   - MacOS: `brew install ffmpeg`
   - Windows: 从 https://ffmpeg.org/download.html 下载

2. **CUDA相关错误**
   - 确保安装了与PyTorch版本匹配的CUDA
   - 或使用CPU版本：修改requirements.txt中的torch版本

3. **内存不足**
   - 使用较小的模型：将`large-v3`改为`medium`或`small`

4. **日语显示问题**
   - 确保终端支持UTF-8编码
   - Windows: 使用`chcp 65001`命令