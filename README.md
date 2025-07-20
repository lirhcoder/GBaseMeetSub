# 日语会议语音识别系统

具有自动术语积累功能的语音识别系统，专门优化日语会议记录处理。

## 特性

- 🎙️ 基于OpenAI Whisper的高精度日语识别
- 📚 自动术语积累机制 - 所有纠正自动记录为专用术语
- 🔧 模块化设计 - 各组件可独立测试和使用
- 📊 精度验证 - WER/CER等多维度评估
- 🚀 批量处理支持

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository>
cd speech-recognition-system

# 安装依赖
pip install -r requirements.txt

# 安装日语分词工具
python -m unidic download
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

```bash
# 运行交互式示例
python example_usage.py
```

## 测试

```bash
# 运行单元测试
python -m pytest tests/

# 测试特定模块
python tests/test_term_manager.py
```