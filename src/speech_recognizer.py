"""语音识别模块 - 封装Whisper进行日语识别"""
import whisper
import numpy as np
from typing import Dict, Optional, List, Tuple
import torch

class SpeechRecognizer:
    def __init__(self, model_size: str = "large-v3", device: Optional[str] = None):
        """初始化语音识别器
        
        Args:
            model_size: Whisper模型大小
            device: 计算设备 (cuda/cpu)
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.model = whisper.load_model(model_size, device=device)
        
    def transcribe(self, audio_path: str, **kwargs) -> Dict:
        """识别音频文件
        
        Args:
            audio_path: 音频文件路径
            **kwargs: 其他Whisper参数
            
        Returns:
            识别结果字典
        """
        # 默认参数
        default_params = {
            "language": "ja",  # 日语
            "task": "transcribe",
            "verbose": False,
            "temperature": 0,  # 确定性输出
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "word_timestamps": True  # 词级时间戳
        }
        
        # 合并用户参数
        params = {**default_params, **kwargs}
        
        # 执行识别
        result = self.model.transcribe(audio_path, **params)
        
        return result
    
    def transcribe_segments(self, audio_path: str, 
                          segment_length: int = 30) -> List[Dict]:
        """分段识别长音频
        
        Args:
            audio_path: 音频文件路径
            segment_length: 每段长度（秒）
            
        Returns:
            分段识别结果列表
        """
        # 加载音频
        audio = whisper.load_audio(audio_path)
        duration = len(audio) / whisper.audio.SAMPLE_RATE
        
        segments = []
        for start in range(0, int(duration), segment_length):
            end = min(start + segment_length, duration)
            
            # 提取音频段
            start_sample = int(start * whisper.audio.SAMPLE_RATE)
            end_sample = int(end * whisper.audio.SAMPLE_RATE)
            audio_segment = audio[start_sample:end_sample]
            
            # 识别该段
            result = self.model.transcribe(
                audio_segment,
                language="ja",
                task="transcribe"
            )
            
            # 调整时间戳
            for segment in result["segments"]:
                segment["start"] += start
                segment["end"] += start
            
            segments.extend(result["segments"])
        
        return segments
    
    def detect_language(self, audio_path: str) -> Tuple[str, float]:
        """检测音频语言
        
        Returns:
            (语言代码, 置信度)
        """
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        mel = whisper.log_mel_spectrogram(audio).to(self.device)
        _, probs = self.model.detect_language(mel)
        
        lang = max(probs, key=probs.get)
        return lang, probs[lang]