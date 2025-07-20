"""使用示例 - 展示如何使用语音识别系统"""
from src.main_pipeline import SpeechProcessingPipeline

def simple_example():
    """简单使用示例"""
    # 创建处理管道
    pipeline = SpeechProcessingPipeline({
        "model_size": "large-v3"  # 或 "medium" 以提高速度
    })
    
    # 处理音频文件
    result = pipeline.process_audio(
        audio_path="meeting.mp4",
        output_dir="output",
        subtitle_format="srt"
    )
    
    print(f"处理完成！")
    print(f"字幕文件: {result['subtitle_path']}")
    print(f"修正了 {result['corrections_count']} 个术语")

def learning_example():
    """展示术语学习功能"""
    pipeline = SpeechProcessingPipeline()
    
    # 用户反馈纠正
    pipeline.learn_from_feedback(
        original="じんこうちのう",  # 错误识别
        corrected="人工知能",        # 正确术语
        context="AI技術に関する討論"
    )
    
    # 下次处理会自动应用这个纠正
    result = pipeline.process_audio("another_meeting.mp4")

def batch_processing_example():
    """批量处理示例"""
    import glob
    
    pipeline = SpeechProcessingPipeline()
    
    # 获取所有MP4文件
    video_files = glob.glob("meetings/*.mp4")
    
    for video_file in video_files:
        print(f"处理: {video_file}")
        result = pipeline.process_audio(video_file)
        
        # 显示高频术语
        print("高频术语:")
        for term, info in result["high_freq_terms"].items():
            print(f"  {term} -> {info['correct']} (出现{info['frequency']}次)")

def validation_example():
    """精度验证示例"""
    pipeline = SpeechProcessingPipeline()
    
    # 设置参考文本（如果有的话）
    reference_text = """
    本日の会議では、人工知能技術の最新動向について討論します。
    特に、自然言語処理と機械学習の応用について話し合います。
    """
    
    pipeline.set_reference_text(reference_text)
    
    # 处理并验证
    result = pipeline.process_audio(
        "meeting.mp4",
        validate=True
    )
    
    # 显示精度指标
    if result["metrics"]:
        print("识别精度:")
        print(f"  原始WER: {result['metrics']['original']['wer_percent']:.2f}%")
        print(f"  修正后WER: {result['metrics']['corrected']['wer_percent']:.2f}%")

def interactive_correction():
    """交互式纠正示例"""
    pipeline = SpeechProcessingPipeline()
    
    # 处理音频
    result = pipeline.process_audio("meeting.mp4")
    
    # 显示识别结果供用户检查
    for i, segment in enumerate(result["segments"][:5]):  # 显示前5个片段
        print(f"\n片段 {i+1}:")
        print(f"时间: {segment['start']:.2f}s - {segment['end']:.2f}s")
        print(f"原始: {segment.get('original_text', segment['text'])}")
        print(f"修正: {segment['text']}")
        
        # 模拟用户输入纠正
        user_correction = input("如需纠正请输入(回车跳过): ")
        if user_correction:
            # 学习用户的纠正
            pipeline.learn_from_feedback(
                segment['text'], 
                user_correction,
                context=segment.get('original_text', '')
            )

if __name__ == "__main__":
    # 选择要运行的示例
    print("语音识别系统示例")
    print("1. 简单使用")
    print("2. 术语学习")
    print("3. 批量处理")
    print("4. 精度验证")
    print("5. 交互式纠正")
    
    choice = input("选择示例 (1-5): ")
    
    if choice == "1":
        simple_example()
    elif choice == "2":
        learning_example()
    elif choice == "3":
        batch_processing_example()
    elif choice == "4":
        validation_example()
    elif choice == "5":
        interactive_correction()