"""字幕生成模块 - 生成SRT/VTT格式字幕"""
from typing import List, Dict, Tuple
import os
from datetime import timedelta

class SubtitleGenerator:
    def __init__(self):
        self.supported_formats = ["srt", "vtt", "txt"]
    
    def generate_srt(self, segments: List[Dict], output_path: str):
        """生成SRT格式字幕
        
        Args:
            segments: 包含text, start, end的片段列表
            output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                # 序号
                f.write(f"{i}\n")
                
                # 时间戳
                start_time = self._seconds_to_srt_time(segment['start'])
                end_time = self._seconds_to_srt_time(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # 文本
                f.write(f"{segment['text'].strip()}\n\n")
    
    def generate_vtt(self, segments: List[Dict], output_path: str):
        """生成WebVTT格式字幕"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for segment in segments:
                start_time = self._seconds_to_vtt_time(segment['start'])
                end_time = self._seconds_to_vtt_time(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
    
    def generate_txt(self, segments: List[Dict], output_path: str, 
                    include_timestamps: bool = True):
        """生成纯文本格式"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for segment in segments:
                if include_timestamps:
                    timestamp = self._seconds_to_readable_time(segment['start'])
                    f.write(f"[{timestamp}] {segment['text'].strip()}\n")
                else:
                    f.write(f"{segment['text'].strip()}\n")
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """转换为SRT时间格式 (00:00:00,000)"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = td.total_seconds() % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """转换为VTT时间格式 (00:00:00.000)"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = td.total_seconds() % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def _seconds_to_readable_time(self, seconds: float) -> str:
        """转换为可读时间格式"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def merge_short_segments(self, segments: List[Dict], 
                           min_duration: float = 2.0) -> List[Dict]:
        """合并过短的片段"""
        merged = []
        buffer = None
        
        for segment in segments:
            duration = segment['end'] - segment['start']
            
            if duration < min_duration and buffer is None:
                buffer = segment.copy()
            elif buffer is not None:
                # 合并到缓冲区
                buffer['end'] = segment['end']
                buffer['text'] += ' ' + segment['text']
                
                # 检查合并后的长度
                if buffer['end'] - buffer['start'] >= min_duration:
                    merged.append(buffer)
                    buffer = None
            else:
                merged.append(segment)
        
        # 处理最后的缓冲区
        if buffer is not None:
            merged.append(buffer)
        
        return merged