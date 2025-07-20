"""音频分片处理工具"""
import os
import subprocess
import json
from typing import List, Dict, Tuple
import math

class AudioSplitter:
    def __init__(self, chunk_duration: int = 60):
        """
        初始化音频分割器
        
        Args:
            chunk_duration: 每个片段的时长（秒），默认60秒
        """
        self.chunk_duration = chunk_duration
    
    def get_audio_duration(self, audio_path: str) -> float:
        """获取音频文件时长"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            audio_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception as e:
            print(f"获取音频时长失败: {e}")
            return 0
    
    def split_audio(self, audio_path: str, output_dir: str) -> List[Dict]:
        """
        将音频文件分割成多个片段
        
        Returns:
            片段信息列表，每个包含 {filename, start_time, end_time, duration}
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取总时长
        total_duration = self.get_audio_duration(audio_path)
        if total_duration == 0:
            return []
        
        # 计算需要多少个片段
        num_chunks = math.ceil(total_duration / self.chunk_duration)
        chunks = []
        
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        
        for i in range(num_chunks):
            start_time = i * self.chunk_duration
            end_time = min((i + 1) * self.chunk_duration, total_duration)
            duration = end_time - start_time
            
            # 输出文件名
            output_file = os.path.join(output_dir, f"{base_name}_chunk_{i:03d}.mp3")
            
            # FFmpeg命令分割音频
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'mp3',
                '-ar', '16000',  # 16kHz采样率，适合语音识别
                '-ac', '1',      # 单声道
                '-y',            # 覆盖已存在的文件
                output_file
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                chunks.append({
                    'index': i,
                    'filename': output_file,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration
                })
            except subprocess.CalledProcessError as e:
                print(f"分割片段 {i} 失败: {e}")
        
        return chunks
    
    def merge_subtitles(self, subtitle_segments: List[List[Dict]]) -> List[Dict]:
        """
        合并多个片段的字幕，调整时间戳
        
        Args:
            subtitle_segments: 每个片段的字幕列表
            
        Returns:
            合并后的完整字幕
        """
        merged = []
        
        for chunk_idx, segments in enumerate(subtitle_segments):
            # 获取该片段的起始时间偏移
            time_offset = chunk_idx * self.chunk_duration
            
            for segment in segments:
                # 调整时间戳
                adjusted_segment = segment.copy()
                adjusted_segment['start'] += time_offset
                adjusted_segment['end'] += time_offset
                merged.append(adjusted_segment)
        
        return merged