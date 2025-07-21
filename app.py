"""Flask Web UI for GBaseMeetSub"""
import os
import sys
import json
import time
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import uuid

# 获取应用根目录
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# 确保src目录在Python路径中
sys.path.insert(0, APP_ROOT)

# 现在导入项目模块
from src.main_pipeline import SpeechProcessingPipeline
from src.enhanced_pipeline import EnhancedPipeline

# 创建Flask应用，指定模板和静态文件的绝对路径
app = Flask(__name__,
            template_folder=os.path.join(APP_ROOT, 'templates'),
            static_folder=os.path.join(APP_ROOT, 'static'),
            static_url_path='/static')

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(APP_ROOT, 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(APP_ROOT, 'output')
app.config['DATA_FOLDER'] = os.path.join(APP_ROOT, 'data')

# 确保必要的目录存在
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['DATA_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# 存储处理任务状态
processing_tasks = {}

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'wav', 'm4a', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    # 先测试是否能访问路由
    if request.args.get('test'):
        return "路由正常工作！"
    
    # 检查模板文件
    template_path = os.path.join(app.template_folder, 'index.html')
    if not os.path.exists(template_path):
        return f"错误：模板文件不存在！<br>查找路径: {template_path}<br>模板目录: {app.template_folder}"
    
    try:
        return render_template('index.html')
    except Exception as e:
        return f"模板渲染错误：{str(e)}"

@app.route('/favicon.ico')
def favicon():
    """返回空的favicon以避免404"""
    return '', 204

@app.route('/hello')
def hello():
    """简单测试路由"""
    return "Hello from GBaseMeetSub!"


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
        start_time = float(request.form.get('start_time', 0))
        
        # 检查是否有已上传的字幕
        existing_subtitle = None
        if 'existing_subtitle' in request.files:
            subtitle_file = request.files['existing_subtitle']
            if subtitle_file and subtitle_file.filename:
                existing_subtitle = subtitle_file.read().decode('utf-8')
        
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
            args=(task_id, filepath, model_size, subtitle_format, start_time, existing_subtitle)
        )
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': '文件上传成功，开始处理...'
        })
    
    return jsonify({'error': '不支持的文件格式'}), 400

def process_audio_task(task_id, filepath, model_size, subtitle_format, start_time=0, existing_subtitle=None):
    """后台处理音频任务"""
    try:
        # 进度回调函数
        def update_progress(progress_info):
            task_update = {
                'progress': progress_info['current_progress'],
                'status_message': progress_info['message'],
                'current_chunk': progress_info.get('current_chunk', 0),
                'total_chunks': progress_info.get('total_chunks', 0),
                'chunk_start_time': datetime.now().isoformat()  # 记录当前片段开始时间
            }
            
            # 保存所有片段，而不是只保存最后几个
            if 'partial_results' in progress_info:
                task_update['partial_segments'] = progress_info['partial_results']
            
            # 添加时间统计信息
            if 'chunk_times' in progress_info:
                task_update['chunk_times'] = progress_info['chunk_times']
                
            processing_tasks[task_id].update(task_update)
            
            # 检查是否暂停或取消
            while processing_tasks[task_id].get('paused', False):
                time.sleep(1)  # 暂停时等待
                if processing_tasks[task_id].get('cancelled', False):
                    raise Exception('处理已取消')
            
            if processing_tasks[task_id].get('cancelled', False):
                raise Exception('处理已取消')
        
        # 创建增强处理管道
        pipeline = EnhancedPipeline({
            'model_size': model_size,
            'chunk_duration': 30,  # 30秒片段，更快的初始反馈
            'start_time': start_time,
            'existing_subtitle': existing_subtitle
        })
        
        # 处理音频
        result = pipeline.process_audio_chunked(
            audio_path=filepath,
            output_dir=app.config['OUTPUT_FOLDER'],
            progress_callback=update_progress,
            subtitle_format=subtitle_format
        )
        
        if result['success']:
            # 保存结果
            processing_tasks[task_id].update({
                'status': 'completed',
                'progress': 100,
                'status_message': '处理完成！',
                'result': {
                    'subtitle_path': result['subtitle_path'],
                    'segments_count': len(result['segments']),
                    'corrections_count': result['corrections_count'],
                    'corrections': result['corrections'][:5],
                    'high_freq_terms': result['high_freq_terms'],
                    'processing_time': result['processing_time'],
                    'chunks_processed': result['chunks_processed']
                },
                'segments': result['segments'],  # 保存所有片段供预览
                'end_time': datetime.now().isoformat()
            })
        else:
            raise Exception(result.get('error', '处理失败'))
        
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
        terms_file = os.path.join(app.config['DATA_FOLDER'], 'terms.json')
        with open(terms_file, 'r', encoding='utf-8') as f:
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
    
    # 使用术语管理器添加纠正，传入正确的路径
    from src.term_manager import TermManager
    terms_file = os.path.join(app.config['DATA_FOLDER'], 'terms.json')
    log_file = os.path.join(app.config['DATA_FOLDER'], 'corrections_log.json')
    term_manager = TermManager(terms_file, log_file)
    term_manager.add_correction(original, corrected, context, confidence=1.0)
    
    return jsonify({
        'message': '术语已添加',
        'term': {
            'original': original,
            'corrected': corrected
        }
    })

@app.route('/preview/<task_id>')
def preview_audio(task_id):
    """获取音频文件用于预览"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = processing_tasks[task_id]
    audio_path = task.get('filepath')
    
    if audio_path and os.path.exists(audio_path):
        # 返回音频文件，支持范围请求（用于拖动进度条）
        return send_file(audio_path, mimetype='audio/mpeg', as_attachment=False)
    
    return jsonify({'error': '音频文件不存在'}), 404

@app.route('/preview_subtitles/<task_id>')
def preview_subtitles(task_id):
    """获取实时字幕预览"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = processing_tasks[task_id]
    
    # 返回当前已处理的片段
    preview_data = {
        'status': task.get('status'),
        'progress': task.get('progress', 0),
        'current_chunk': task.get('current_chunk', 0),
        'total_chunks': task.get('total_chunks', 0),
        'segments': task.get('partial_segments', []),
        'status_message': task.get('status_message', '')
    }
    
    # 如果已完成，返回所有片段
    if task.get('status') == 'completed' and 'segments' in task:
        preview_data['segments'] = task['segments']
    
    return jsonify(preview_data)

@app.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    """分析音频文件，返回分片信息"""
    if 'audio' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 临时保存文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            
            try:
                # 获取音频时长
                from src.audio_splitter import AudioSplitter
                splitter = AudioSplitter(30)  # 30秒分片
                duration = splitter.get_audio_duration(tmp_file.name)
                
                # 计算分片
                chunks = []
                chunk_duration = 30
                for i in range(0, int(duration), chunk_duration):
                    start = i
                    end = min(i + chunk_duration, duration)
                    chunks.append({
                        'index': len(chunks),
                        'start': start,
                        'end': end,
                        'label': f'{start}秒 - {end}秒 (片段{len(chunks)+1})'
                    })
                
                return jsonify({
                    'duration': duration,
                    'chunks': chunks,
                    'chunk_duration': chunk_duration
                })
                
            finally:
                # 清理临时文件
                os.unlink(tmp_file.name)
    
    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/pause/<task_id>', methods=['POST'])
def pause_task(task_id):
    """暂停处理任务"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    processing_tasks[task_id]['paused'] = True
    processing_tasks[task_id]['status'] = 'paused'
    return jsonify({'message': '任务已暂停'})

@app.route('/resume/<task_id>', methods=['POST'])
def resume_task(task_id):
    """继续处理任务"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    processing_tasks[task_id]['paused'] = False
    processing_tasks[task_id]['status'] = 'processing'
    return jsonify({'message': '任务已继续'})

@app.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """取消处理任务"""
    if task_id not in processing_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    processing_tasks[task_id]['cancelled'] = True
    processing_tasks[task_id]['status'] = 'cancelled'
    return jsonify({'message': '任务已取消'})

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
    # 显示启动信息
    print(f"\n{'='*50}")
    print(f"GBaseMeetSub Web UI 启动中...")
    print(f"{'='*50}")
    print(f"应用根目录: {APP_ROOT}")
    print(f"模板目录: {os.path.join(APP_ROOT, 'templates')}")
    print(f"静态文件目录: {os.path.join(APP_ROOT, 'static')}")
    print(f"数据目录: {app.config['DATA_FOLDER']}")
    print(f"上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"输出目录: {app.config['OUTPUT_FOLDER']}")
    print(f"{'='*50}")
    print(f"访问: http://localhost:8888")
    print(f"{'='*50}\n")
    
    # 使用8888端口避免冲突
    app.run(debug=True, host='127.0.0.1', port=8888)