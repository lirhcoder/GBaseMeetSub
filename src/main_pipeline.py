"""主流程 - 集成所有模块的完整处理流程"""
from typing import Dict, Optional
import os
import sys
import logging
from .speech_recognizer import SpeechRecognizer
from .term_manager import TermManager
from .term_corrector import TermCorrector
from .subtitle_generator import SubtitleGenerator
from .accuracy_validator import AccuracyValidator

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechProcessingPipeline:
    def __init__(self, config: Optional[Dict] = None):
        """初始化处理流程
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 初始化各模块
        self.recognizer = SpeechRecognizer(
            model_size=self.config.get("model_size", "large-v3")
        )
        
        # 使用项目根目录下的data文件夹
        data_dir = os.path.join(PROJECT_ROOT, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        terms_file = os.path.join(data_dir, 'terms.json')
        log_file = os.path.join(data_dir, 'corrections_log.json')
        
        self.term_manager = TermManager(terms_file, log_file)
        self.corrector = TermCorrector(self.term_manager)
        self.subtitle_gen = SubtitleGenerator()
        self.validator = AccuracyValidator()
        
    def process_audio(self, audio_path: str, output_dir: str = "output",
                     subtitle_format: str = "srt", validate: bool = True) -> Dict:
        """处理音频文件的完整流程
        
        Args:
            audio_path: 音频文件路径
            output_dir: 输出目录
            subtitle_format: 字幕格式
            validate: 是否进行精度验证
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理: {audio_path}")
        
        # 1. 语音识别
        logger.info("执行语音识别...")
        result = self.recognizer.transcribe(audio_path)
        segments = result["segments"]
        
        # 2. 术语修正
        logger.info("应用术语修正...")
        corrected_segments = []
        all_corrections = []
        
        for segment in segments:
            corrected_text, corrections = self.corrector.correct_text(
                segment["text"],
                record_corrections=True
            )
            
            corrected_segment = segment.copy()
            corrected_segment["text"] = corrected_text
            corrected_segment["original_text"] = segment["text"]
            corrected_segments.append(corrected_segment)
            
            if corrections:
                all_corrections.extend(corrections)
        
        # 3. 生成字幕
        logger.info(f"生成{subtitle_format}格式字幕...")
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        subtitle_path = os.path.join(output_dir, f"{base_name}.{subtitle_format}")
        
        if subtitle_format == "srt":
            self.subtitle_gen.generate_srt(corrected_segments, subtitle_path)
        elif subtitle_format == "vtt":
            self.subtitle_gen.generate_vtt(corrected_segments, subtitle_path)
        else:
            self.subtitle_gen.generate_txt(corrected_segments, subtitle_path)
        
        # 4. 精度验证（如果需要）
        metrics = {}
        if validate and hasattr(self, '_reference_text'):
            logger.info("计算精度指标...")
            recognized_text = " ".join([s["text"] for s in segments])
            corrected_text = " ".join([s["text"] for s in corrected_segments])
            
            metrics = {
                "original": self.validator.calculate_metrics(
                    self._reference_text, recognized_text
                ),
                "corrected": self.validator.calculate_metrics(
                    self._reference_text, corrected_text
                )
            }
        
        # 5. 返回结果
        result = {
            "audio_path": audio_path,
            "subtitle_path": subtitle_path,
            "segments": corrected_segments,
            "corrections_count": len(all_corrections),
            "corrections": all_corrections[:10],  # 前10个修正示例
            "metrics": metrics,
            "high_freq_terms": self.term_manager.get_high_frequency_terms()
        }
        
        logger.info(f"处理完成! 字幕已保存至: {subtitle_path}")
        logger.info(f"共进行了 {len(all_corrections)} 处术语修正")
        
        return result
    
    def set_reference_text(self, reference_text: str):
        """设置参考文本用于精度验证"""
        self._reference_text = reference_text
    
    def learn_from_feedback(self, original: str, corrected: str, context: str = None):
        """从用户反馈中学习新术语"""
        self.term_manager.add_correction(
            original, corrected, 
            context=context,
            confidence=1.0  # 用户反馈具有最高置信度
        )
        # 重建修正器的Trie树
        self.corrector._build_trie()
        logger.info(f"已学习新术语: {original} -> {corrected}")