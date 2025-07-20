"""Flask Web UI for GBaseMeetSub"""
import os
import sys
import json
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
    print(f"{'='*50}\n")
    
    # 开发模式运行
    app.run(debug=True, host='0.0.0.0', port=5000)