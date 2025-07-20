"""精度验证模块 - 计算识别精度指标"""
from typing import Dict, List, Tuple
import jiwer
import numpy as np
from difflib import SequenceMatcher

class AccuracyValidator:
    def __init__(self):
        self.transforms = jiwer.Compose([
            jiwer.ToLowerCase(),
            jiwer.RemoveWhiteSpace(replace_by_space=True),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.RemovePunctuation()
        ])
    
    def calculate_metrics(self, reference: str, hypothesis: str) -> Dict:
        """计算各种精度指标
        
        Args:
            reference: 参考文本
            hypothesis: 识别结果
            
        Returns:
            包含各种指标的字典
        """
        # 预处理文本
        ref_transformed = self.transforms(reference)
        hyp_transformed = self.transforms(hypothesis)
        
        # 计算WER (Word Error Rate)
        wer = jiwer.wer(ref_transformed, hyp_transformed)
        
        # 计算CER (Character Error Rate)
        cer = jiwer.cer(reference, hypothesis)
        
        # 计算其他指标
        metrics = {
            "wer": wer,
            "cer": cer,
            "wer_percent": wer * 100,
            "cer_percent": cer * 100,
            "similarity": self._calculate_similarity(reference, hypothesis),
            "word_accuracy": (1 - wer) * 100,
            "char_accuracy": (1 - cer) * 100
        }
        
        # 添加详细的错误分析
        errors = self._analyze_errors(reference, hypothesis)
        metrics.update(errors)
        
        return metrics
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _analyze_errors(self, reference: str, hypothesis: str) -> Dict:
        """分析错误类型"""
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        # 使用动态规划计算编辑操作
        operations = jiwer.compute_measures(reference, hypothesis)
        
        return {
            "substitutions": operations.get("substitutions", 0),
            "deletions": operations.get("deletions", 0),
            "insertions": operations.get("insertions", 0),
            "total_words": len(ref_words),
            "recognized_words": len(hyp_words)
        }
    
    def calculate_time_alignment_accuracy(self, 
                                        ref_segments: List[Dict], 
                                        hyp_segments: List[Dict],
                                        tolerance: float = 0.5) -> Dict:
        """计算时间对齐精度
        
        Args:
            ref_segments: 参考片段列表
            hyp_segments: 识别片段列表
            tolerance: 时间容差（秒）
            
        Returns:
            时间对齐指标
        """
        aligned_count = 0
        total_time_diff = 0
        
        for ref, hyp in zip(ref_segments, hyp_segments):
            start_diff = abs(ref["start"] - hyp["start"])
            end_diff = abs(ref["end"] - hyp["end"])
            
            if start_diff <= tolerance and end_diff <= tolerance:
                aligned_count += 1
            
            total_time_diff += start_diff + end_diff
        
        total_segments = len(ref_segments)
        
        return {
            "aligned_segments": aligned_count,
            "total_segments": total_segments,
            "alignment_accuracy": (aligned_count / total_segments) * 100 if total_segments > 0 else 0,
            "average_time_difference": total_time_diff / (2 * total_segments) if total_segments > 0 else 0
        }
    
    def generate_report(self, metrics: Dict) -> str:
        """生成可读的精度报告"""
        report = f"""
=== 语音识别精度报告 ===

基础指标:
- 词错误率 (WER): {metrics['wer_percent']:.2f}%
- 字符错误率 (CER): {metrics['cer_percent']:.2f}%
- 词准确率: {metrics['word_accuracy']:.2f}%
- 字符准确率: {metrics['char_accuracy']:.2f}%
- 文本相似度: {metrics['similarity']:.2f}

错误分析:
- 替换错误: {metrics.get('substitutions', 0)}
- 删除错误: {metrics.get('deletions', 0)}
- 插入错误: {metrics.get('insertions', 0)}
- 总词数: {metrics.get('total_words', 0)}
"""
        return report