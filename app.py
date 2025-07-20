"""Flask Web UI for GBaseMeetSub"""
import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import uuid
from src.main_pipeline import SpeechProcessingPipeline

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# 确保必要的目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# 存储处理任务状态
processing_tasks = {}

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'wav', 'm4a', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/test')
def test():
    """测试路由"""
    return "Server is running! Current directory: " + os.getcwd()

@app.route('/')
def index():
    """主页"""
    try:
        return render_template('index.html')
    except Exception as e:
        # 如果模板找不到，返回错误信息
        return f"Error: {str(e)}<br>Current directory: {os.getcwd()}<br>Template path: {os.path.join(os.getcwd(), 'templates')}"

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'audio' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存文件
        base_name = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        saved_filename = f"{base_name}_{timestamp}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        # 获取处理选项
        model_size = request.form.get('model_size', 'medium')
        subtitle_format = request.form.get('subtitle_format', 'srt')
        
        # 初始化任务状态
        processing_tasks[task_id] = {
            'status': 'processing',
            'progress': 0,
            'filename': filename,
            'filepath': filepath,
            'start_time': datetime.now().isoformat(),
            'model_size': model_size,
            'subtitle_format': subtitle_format
        }
        
        # 在后台线程中处理
        thread = threading.Thread(
            target=process_audio_task,
            args=(task_id, filepath, model_size, subtitle_format)
        )
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': '文件上传成功，开始处理...'
        })
    
    return jsonify({'error': '不支持的文件格式'}), 400

def process_audio_task(task_id, filepath, model_size, subtitle_format):
    """后台处理音频任务"""
    try:
        # 更新进度
        processing_tasks[task_id]['progress'] = 10
        processing_tasks[task_id]['status_message'] = '初始化语音识别模型...'
        
        # 创建处理管道
        pipeline = SpeechProcessingPipeline({
            'model_size': model_size
        })
        
        processing_tasks[task_id]['progress'] = 20
        processing_tasks[task_id]['status_message'] = '开始语音识别...'
        
        # 处理音频
        result = pipeline.process_audio(
            audio_path=filepath,
            output_dir=app.config['OUTPUT_FOLDER'],
            subtitle_format=subtitle_format,
            validate=False
        )
        
        processing_tasks[task_id]['progress'] = 90
        processing_tasks[task_id]['status_message'] = '生成字幕文件...'
        
        # 保存结果
        processing_tasks[task_id].update({
            'status': 'completed',
            'progress': 100,
            'status_message': '处理完成！',
            'result': {
                'subtitle_path': result['subtitle_path'],
                'segments_count': len(result['segments']),
                'corrections_count': result['corrections_count'],
                'corrections': result['corrections'][:5],  # 前5个修正示例
                'high_freq_terms': list(result['high_freq_terms'].items())[:10]
            },
            'end_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        processing_tasks[task_id].update({
            'status': 'error',
            'error': str(e),
            'end_time': datetime.now().isoformat()
        })

@app.route('/status/<task_id>')
def get_status(task_id):
    """获取任务状态"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(processing_tasks[task_id])

@app.route('/download/<task_id>')
def download_subtitle(task_id):
    """下载字幕文件"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = processing_tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({'error': '任务尚未完成'}), 400
    
    subtitle_path = task['result']['subtitle_path']
    if os.path.exists(subtitle_path):
        return send_file(subtitle_path, as_attachment=True)
    
    return jsonify({'error': '文件不存在'}), 404

@app.route('/terms')
def get_terms():
    """获取术语库"""
    try:
        with open('data/terms.json', 'r', encoding='utf-8') as f:
            terms = json.load(f)
        return jsonify(terms)
    except FileNotFoundError:
        return jsonify({})

@app.route('/add_correction', methods=['POST'])
def add_correction():
    """添加术语纠正"""
    data = request.json
    original = data.get('original')
    corrected = data.get('corrected')
    context = data.get('context', '')
    
    if not original or not corrected:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 使用术语管理器添加纠正
    from src.term_manager import TermManager
    term_manager = TermManager()
    term_manager.add_correction(original, corrected, context, confidence=1.0)
    
    return jsonify({
        'message': '术语已添加',
        'term': {
            'original': original,
            'corrected': corrected
        }
    })

@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    """清理上传的文件（开发用）"""
    import shutil
    try:
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['UPLOAD_FOLDER'])
        return jsonify({'message': '清理完成'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 开发模式运行
    app.run(debug=True, host='0.0.0.0', port=5000)