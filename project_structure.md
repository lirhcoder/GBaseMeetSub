# 项目目录结构

```
speech-recognition-system/
├── src/
│   ├── __init__.py
│   ├── audio_processor.py      # 音频处理模块
│   ├── speech_recognizer.py    # 语音识别模块
│   ├── term_manager.py         # 术语管理模块
│   ├── term_corrector.py       # 术语修正模块
│   ├── accuracy_validator.py   # 精度验证模块
│   └── subtitle_generator.py   # 字幕生成模块
├── data/
│   ├── terms.json             # 术语库
│   └── corrections_log.json   # 纠正记录
├── tests/
│   ├── test_audio_processor.py
│   ├── test_speech_recognizer.py
│   ├── test_term_manager.py
│   └── test_integration.py
├── config/
│   └── config.yaml            # 配置文件
├── requirements.txt
├── setup.py
└── README.md
```