"""增强的处理管道 - 支持分片处理和实时进度"""
import os
import time
from typing import Dict, List, Optional, Callable
import logging
from .audio_splitter import AudioSplitter
from .speech_recognizer import SpeechRecognizer
from .term_manager import TermManager
from .term_corrector import TermCorrector
from .subtitle_generator import SubtitleGenerator

logger = logging.getLogger(__name__)

class EnhancedPipeline:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.chunk_duration = self.config.get('chunk_duration', 60)  # 60秒片段
        
        # 初始化组件
        self.splitter = AudioSplitter(self.chunk_duration)
        self.recognizer = SpeechRecognizer(
            model_size=self.config.get('model_size', 'medium')  # 默认使用medium以提高速度
        )
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        terms_file = os.path.join(data_dir, 'terms.json')
        log_file = os.path.join(data_dir, 'corrections_log.json')
        
        self.term_manager = TermManager(terms_file, log_file)
        self.corrector = TermCorrector(self.term_manager)
        self.subtitle_gen = SubtitleGenerator()
        
        # 进度信息
        self.progress_info = {
            'status': 'idle',
            'current_chunk': 0,
            'total_chunks': 0,
            'current_progress': 0,
            'message': '',
            'partial_results': []
        }
    
    def process_audio_chunked(self, 
                            audio_path: str, 
                            output_dir: str,
                            progress_callback: Optional[Callable] = None,
                            subtitle_format: str = 'srt') -> Dict:
        """
        分片处理音频文件
        
        Args:
            audio_path: 音频文件路径
            output_dir: 输出目录
            progress_callback: 进度回调函数
            subtitle_format: 字幕格式
            
        Returns:
            处理结果
        """
        start_time = time.time()
        os.makedirs(output_dir, exist_ok=True)
        
        # 临时目录存储音频片段
        temp_dir = os.path.join(output_dir, 'temp_chunks')
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # 1. 分割音频
            self._update_progress(5, '正在分析音频文件...', progress_callback)
            chunks = self.splitter.split_audio(audio_path, temp_dir)
            
            if not chunks:
                raise Exception("音频分割失败")
            
            self.progress_info['total_chunks'] = len(chunks)
            logger.info(f"音频已分割为 {len(chunks)} 个片段")
            
            # 2. 逐片段处理
            all_segments = []
            all_corrections = []
            
            for i, chunk in enumerate(chunks):
                self.progress_info['current_chunk'] = i + 1
                chunk_progress = 10 + (80 * i // len(chunks))
                
                self._update_progress(
                    chunk_progress,
                    f'处理片段 {i+1}/{len(chunks)} ({chunk["start_time"]:.0f}s-{chunk["end_time"]:.0f}s)...',
                    progress_callback
                )
                
                # 识别该片段
                chunk_result = self.recognizer.transcribe(chunk['filename'])
                segments = chunk_result.get('segments', [])
                
                # 调整时间戳
                for segment in segments:
                    segment['start'] += chunk['start_time']
                    segment['end'] += chunk['start_time']
                
                # 应用术语修正
                corrected_segments = []
                for segment in segments:
                    corrected_text, corrections = self.corrector.correct_text(
                        segment['text'],
                        record_corrections=True
                    )
                    
                    corrected_segment = segment.copy()
                    corrected_segment['text'] = corrected_text
                    corrected_segment['original_text'] = segment['text']
                    corrected_segments.append(corrected_segment)
                    
                    if corrections:
                        all_corrections.extend(corrections)
                
                all_segments.extend(corrected_segments)
                
                # 保存部分结果供预览
                self.progress_info['partial_results'] = all_segments
                
                # 更新进度
                chunk_progress = 10 + (80 * (i + 1) // len(chunks))
                self._update_progress(
                    chunk_progress,
                    f'完成片段 {i+1}/{len(chunks)}',
                    progress_callback
                )
            
            # 3. 生成字幕文件
            self._update_progress(90, '生成字幕文件...', progress_callback)
            
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            subtitle_path = os.path.join(output_dir, f"{base_name}.{subtitle_format}")
            
            if subtitle_format == 'srt':
                self.subtitle_gen.generate_srt(all_segments, subtitle_path)
            elif subtitle_format == 'vtt':
                self.subtitle_gen.generate_vtt(all_segments, subtitle_path)
            else:
                self.subtitle_gen.generate_txt(all_segments, subtitle_path)
            
            # 4. 清理临时文件
            self._update_progress(95, '清理临时文件...', progress_callback)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # 5. 完成
            processing_time = time.time() - start_time
            self._update_progress(100, '处理完成！', progress_callback)
            
            return {
                'success': True,
                'audio_path': audio_path,
                'subtitle_path': subtitle_path,
                'segments': all_segments,
                'corrections_count': len(all_corrections),
                'corrections': all_corrections[:10],
                'processing_time': processing_time,
                'chunks_processed': len(chunks),
                'high_freq_terms': list(self.term_manager.get_high_frequency_terms().items())[:10]
            }
            
        except Exception as e:
            logger.error(f"处理失败: {e}")
            self._update_progress(0, f'处理失败: {str(e)}', progress_callback)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_progress(self, progress: int, message: str, callback: Optional[Callable] = None):
        """更新进度信息"""
        self.progress_info['current_progress'] = progress
        self.progress_info['message'] = message
        self.progress_info['status'] = 'processing' if progress < 100 else 'completed'
        
        if callback:
            callback(self.progress_info)
    
    def get_progress(self) -> Dict:
        """获取当前进度信息"""
        return self.progress_info.copy()