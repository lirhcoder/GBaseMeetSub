// 全局变量
let selectedFile = null;
let currentTaskId = null;
let statusInterval = null;

// DOM元素
const uploadArea = document.getElementById('uploadArea');
const audioFile = document.getElementById('audioFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const processBtn = document.getElementById('processBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const statusMessage = document.getElementById('statusMessage');
const resultSection = document.getElementById('resultSection');
const downloadBtn = document.getElementById('downloadBtn');
const newTaskBtn = document.getElementById('newTaskBtn');

// 文件上传相关
uploadArea.addEventListener('click', () => audioFile.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

audioFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    const allowedTypes = ['audio/mp4', 'audio/mpeg', 'audio/wav', 'audio/x-m4a', 'video/mp4', 'video/webm'];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp4|mp3|wav|m4a|webm)$/i)) {
        alert('请选择支持的音频格式文件！');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'block';
    processBtn.disabled = false;
}

// 处理按钮
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('audio', selectedFile);
    formData.append('model_size', document.getElementById('modelSize').value);
    formData.append('subtitle_format', document.getElementById('subtitleFormat').value);
    
    processBtn.disabled = true;
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentTaskId = data.task_id;
            startStatusPolling();
        } else {
            alert('上传失败: ' + data.error);
            resetUI();
        }
    } catch (error) {
        alert('网络错误: ' + error.message);
        resetUI();
    }
});

// 状态轮询
function startStatusPolling() {
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch(`/status/${currentTaskId}`);
            const data = await response.json();
            
            updateProgress(data);
            
            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(statusInterval);
                
                if (data.status === 'completed') {
                    showResults(data);
                } else {
                    alert('处理失败: ' + data.error);
                    resetUI();
                }
            }
        } catch (error) {
            clearInterval(statusInterval);
            alert('获取状态失败: ' + error.message);
            resetUI();
        }
    }, 1000);
}

// 更新进度
function updateProgress(data) {
    const progress = data.progress || 0;
    progressFill.style.width = progress + '%';
    progressFill.textContent = progress + '%';
    statusMessage.textContent = data.status_message || '处理中...';
    
    // 显示片段信息
    if (data.current_chunk && data.total_chunks) {
        document.getElementById('chunkInfo').textContent = 
            `片段: ${data.current_chunk}/${data.total_chunks}`;
    }
    
    // 显示音频播放器
    if (progress > 5 && !document.getElementById('audioPlayer').src) {
        document.getElementById('audioPreview').style.display = 'block';
        document.getElementById('audioPlayer').src = `/preview/${currentTaskId}`;
    }
    
    // 开始字幕预览轮询
    if (progress > 10 && !window.subtitleInterval) {
        document.getElementById('subtitlePreview').style.display = 'block';
        startSubtitlePreview();
    }
}

// 显示结果
function showResults(data) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    // 基本信息
    document.getElementById('segmentsCount').textContent = data.result.segments_count;
    document.getElementById('correctionsCount').textContent = data.result.corrections_count;
    
    // 修正示例
    if (data.result.corrections && data.result.corrections.length > 0) {
        document.getElementById('correctionsExample').style.display = 'block';
        const tbody = document.querySelector('#correctionsTable tbody');
        tbody.innerHTML = '';
        
        data.result.corrections.forEach(correction => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = correction.original;
            row.insertCell(1).textContent = correction.correct;
        });
    }
    
    // 下载按钮
    downloadBtn.onclick = () => {
        window.location.href = `/download/${currentTaskId}`;
    };
}

// 新任务按钮
newTaskBtn.addEventListener('click', () => {
    resetUI();
});

// 字幕预览
function startSubtitlePreview() {
    window.subtitleInterval = setInterval(async () => {
        try {
            const response = await fetch(`/preview_subtitles/${currentTaskId}`);
            const data = await response.json();
            
            if (data.segments && data.segments.length > 0) {
                updateSubtitleDisplay(data.segments);
            }
            
            // 如果任务完成，停止轮询
            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(window.subtitleInterval);
                window.subtitleInterval = null;
            }
        } catch (error) {
            console.error('字幕预览错误:', error);
        }
    }, 2000); // 每2秒更新一次
}

// 更新字幕显示
function updateSubtitleDisplay(segments) {
    const container = document.getElementById('subtitleContent');
    const lastSegments = segments.slice(-10); // 显示最后10条
    
    container.innerHTML = lastSegments.map(segment => `
        <div class="subtitle-item">
            <div class="subtitle-time">${formatTime(segment.start)} - ${formatTime(segment.end)}</div>
            <div class="subtitle-text">${segment.text}</div>
        </div>
    `).join('');
    
    // 自动滚动到底部
    container.scrollTop = container.scrollHeight;
}

// 格式化时间
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// 重置UI
function resetUI() {
    selectedFile = null;
    currentTaskId = null;
    audioFile.value = '';
    fileInfo.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    processBtn.disabled = true;
    progressFill.style.width = '0%';
    
    // 清除音频和字幕预览
    document.getElementById('audioPreview').style.display = 'none';
    document.getElementById('audioPlayer').src = '';
    document.getElementById('subtitlePreview').style.display = 'none';
    document.getElementById('subtitleContent').innerHTML = '';
    document.getElementById('chunkInfo').textContent = '';
    
    if (statusInterval) {
        clearInterval(statusInterval);
    }
    
    if (window.subtitleInterval) {
        clearInterval(window.subtitleInterval);
        window.subtitleInterval = null;
    }
}

// 术语管理
const viewTermsBtn = document.getElementById('viewTermsBtn');
const addTermBtn = document.getElementById('addTermBtn');
const termsList = document.getElementById('termsList');
const addTermForm = document.getElementById('addTermForm');

viewTermsBtn.addEventListener('click', async () => {
    if (termsList.style.display === 'none') {
        // 加载术语库
        try {
            const response = await fetch('/terms');
            const terms = await response.json();
            
            const tbody = document.querySelector('#termsTable tbody');
            tbody.innerHTML = '';
            
            Object.entries(terms).forEach(([original, info]) => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = original;
                row.insertCell(1).textContent = info.correct;
                row.insertCell(2).textContent = info.frequency || 0;
                row.insertCell(3).textContent = (info.confidence * 100).toFixed(0) + '%';
            });
            
            termsList.style.display = 'block';
        } catch (error) {
            alert('加载术语库失败: ' + error.message);
        }
    } else {
        termsList.style.display = 'none';
    }
});

addTermBtn.addEventListener('click', () => {
    addTermForm.style.display = addTermForm.style.display === 'none' ? 'flex' : 'none';
});

document.getElementById('submitTermBtn').addEventListener('click', async () => {
    const original = document.getElementById('originalTerm').value.trim();
    const corrected = document.getElementById('correctedTerm').value.trim();
    const context = document.getElementById('termContext').value.trim();
    
    if (!original || !corrected) {
        alert('请输入原词和正确词！');
        return;
    }
    
    try {
        const response = await fetch('/add_correction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                original: original,
                corrected: corrected,
                context: context
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('术语添加成功！');
            document.getElementById('originalTerm').value = '';
            document.getElementById('correctedTerm').value = '';
            document.getElementById('termContext').value = '';
            addTermForm.style.display = 'none';
            
            // 刷新术语列表
            if (termsList.style.display !== 'none') {
                viewTermsBtn.click();
                viewTermsBtn.click();
            }
        } else {
            alert('添加失败: ' + data.error);
        }
    } catch (error) {
        alert('网络错误: ' + error.message);
    }
});

document.getElementById('cancelTermBtn').addEventListener('click', () => {
    addTermForm.style.display = 'none';
});