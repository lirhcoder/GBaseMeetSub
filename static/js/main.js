// 全局变量
let selectedFile = null;
let currentTaskId = null;
let statusInterval = null;
let uploadedSubtitle = null;

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

async function handleFileSelect(file) {
    const allowedTypes = ['audio/mp4', 'audio/mpeg', 'audio/wav', 'audio/x-m4a', 'video/mp4', 'video/webm'];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp4|mp3|wav|m4a|webm)$/i)) {
        alert('请选择支持的音频格式文件！');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'block';
    processBtn.disabled = false;
    
    // 分析音频文件获取分片信息
    analyzeAudioFile(file);
}

// 分析音频文件，获取分片信息
async function analyzeAudioFile(file) {
    const formData = new FormData();
    formData.append('audio', file);
    
    try {
        const response = await fetch('/analyze_audio', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            updateChunkSelector(data.chunks);
            
            // 显示音频总时长信息
            const minutes = Math.floor(data.duration / 60);
            const seconds = Math.floor(data.duration % 60);
            document.getElementById('chunkInfo').textContent = 
                `音频总时长: ${minutes}分${seconds}秒，共${data.chunks.length}个片段`;
            document.getElementById('chunkInfo').style.display = 'block';
        }
    } catch (error) {
        console.error('分析音频失败:', error);
    }
}

// 更新分片选择器
function updateChunkSelector(chunks) {
    const selector = document.getElementById('startChunk');
    selector.disabled = false;
    selector.innerHTML = '<option value="0">从头开始处理</option>';
    
    chunks.forEach((chunk, index) => {
        if (index > 0) {  // 跳过第一个片段，因为"从头开始"已经包含了
            const option = document.createElement('option');
            option.value = chunk.start;
            option.textContent = chunk.label;
            selector.appendChild(option);
        }
    });
}

// 处理按钮
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('audio', selectedFile);
    formData.append('model_size', document.getElementById('modelSize').value);
    formData.append('subtitle_format', document.getElementById('subtitleFormat').value);
    formData.append('start_time', document.getElementById('startChunk').value || '0');
    
    // 如果有上传的字幕，也添加到表单
    if (uploadedSubtitle) {
        // 创建一个Blob对象来传递字幕内容
        const subtitleBlob = new Blob([uploadedSubtitle], { type: 'text/plain' });
        formData.append('existing_subtitle', subtitleBlob, 'subtitle.srt');
    }
    
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
        initAudioPlayer(); // 初始化音频播放器事件
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
    
    // 保持音频播放器显示
    if (!document.getElementById('audioPlayer').src && currentTaskId) {
        document.getElementById('audioPlayer').src = `/preview/${currentTaskId}`;
        initAudioPlayer();
    }
    
    // 在结果区域显示完整字幕列表
    if (data.segments && data.segments.length > 0) {
        const resultSubtitleContent = document.getElementById('resultSubtitleContent');
        
        // 生成完整的字幕HTML
        resultSubtitleContent.innerHTML = data.segments.map((segment, index) => `
            <div class="subtitle-item" 
                 data-start="${segment.start}" 
                 data-end="${segment.end}"
                 data-index="${index}">
                <div class="subtitle-time" onclick="seekToTime(${segment.start})">${formatTime(segment.start)} - ${formatTime(segment.end)}</div>
                <div class="subtitle-text" 
                     contenteditable="true"
                     data-original-text="${segment.text}"
                     onblur="handleSubtitleEdit(this, ${index})"
                     onclick="event.stopPropagation()"
                     onkeydown="handleSubtitleKeydown(event)">${segment.text}</div>
            </div>
        `).join('');
    }
}

// 新任务按钮
newTaskBtn.addEventListener('click', () => {
    resetUI();
});

// 字幕预览
let lastSegmentCount = 0; // 记录上次的字幕数量

function startSubtitlePreview() {
    // 重置计数器
    lastSegmentCount = 0;
    
    window.subtitleInterval = setInterval(async () => {
        try {
            const response = await fetch(`/preview_subtitles/${currentTaskId}`);
            const data = await response.json();
            
            if (data.segments && data.segments.length > 0) {
                // 检查是否有新的字幕片段
                if (data.segments.length > lastSegmentCount) {
                    // 只添加新的片段
                    const newSegments = data.segments.slice(lastSegmentCount);
                    updateSubtitleDisplay(newSegments, true); // append模式
                    lastSegmentCount = data.segments.length;
                }
            }
            
            // 如果任务完成，停止轮询
            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(window.subtitleInterval);
                window.subtitleInterval = null;
                
                // 如果是完成状态，确保显示所有字幕
                if (data.status === 'completed' && data.segments) {
                    updateSubtitleDisplay(data.segments, false); // 完整替换，确保顺序正确
                }
            }
        } catch (error) {
            console.error('字幕预览错误:', error);
        }
    }, 2000); // 每2秒更新一次
}

// 更新字幕显示
function updateSubtitleDisplay(segments, append = false) {
    const container = document.getElementById('subtitleContent');
    
    // 获取现有的字幕数量，用于计算新的索引
    const existingItems = container.querySelectorAll('.subtitle-item').length;
    
    // 生成新的字幕HTML
    const newSubtitlesHtml = segments.map((segment, index) => {
        const actualIndex = append ? existingItems + index : index;
        return `
        <div class="subtitle-item" 
             data-start="${segment.start}" 
             data-end="${segment.end}"
             data-index="${actualIndex}">
            <div class="subtitle-time" onclick="seekToTime(${segment.start})">${formatTime(segment.start)} - ${formatTime(segment.end)}</div>
            <div class="subtitle-text" 
                 contenteditable="true"
                 data-original-text="${segment.text}"
                 onblur="handleSubtitleEdit(this, ${actualIndex})"
                 onclick="event.stopPropagation()"
                 onkeydown="handleSubtitleKeydown(event)">${segment.text}</div>
        </div>
    `;
    }).join('');
    
    if (append) {
        // 追加模式：保留现有内容，添加新内容
        container.innerHTML += newSubtitlesHtml;
    } else {
        // 覆盖模式：替换所有内容
        container.innerHTML = newSubtitlesHtml;
    }
    
    // 不自动滚动，保持当前位置
    // container.scrollTop = container.scrollHeight;
}

// 跳转到指定时间
function seekToTime(seconds) {
    const audioPlayer = document.getElementById('audioPlayer');
    if (audioPlayer && audioPlayer.src) {
        audioPlayer.currentTime = seconds;
        audioPlayer.play();
        
        // 高亮当前播放的字幕
        highlightCurrentSubtitle(seconds);
    }
}

// 高亮当前播放的字幕
function highlightCurrentSubtitle(currentTime) {
    // 同时处理进度中的字幕和结果中的字幕
    const items = document.querySelectorAll('.subtitle-item');
    items.forEach(item => {
        const start = parseFloat(item.dataset.start);
        const end = parseFloat(item.dataset.end);
        
        if (currentTime >= start && currentTime <= end) {
            item.classList.add('playing');
            // 不自动滚动，让用户自己控制滚动位置
        } else {
            item.classList.remove('playing');
        }
    });
}

// 音频播放器最小化/展开
function toggleAudioPlayer(event) {
    if (event) {
        event.stopPropagation(); // 阻止事件冒泡
    }
    
    const audioPreview = document.getElementById('audioPreview');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (audioPreview.classList.contains('minimized')) {
        audioPreview.classList.remove('minimized');
        toggleIcon.textContent = '－';
    } else {
        audioPreview.classList.add('minimized');
        toggleIcon.textContent = '＋';
    }
}

// 处理音频播放器的点击事件
function handleAudioPlayerClick(event) {
    const audioPreview = document.getElementById('audioPreview');
    
    // 如果是最小化状态，点击整个区域都可以展开
    if (audioPreview.classList.contains('minimized')) {
        // 确保不是点击了其他控件
        if (event.target === audioPreview || event.target.className === 'audio-header') {
            toggleAudioPlayer();
        }
    }
}

// 监听音频播放进度
function initAudioPlayer() {
    const audioPlayer = document.getElementById('audioPlayer');
    
    if (audioPlayer) {
        // 监听时间更新
        audioPlayer.addEventListener('timeupdate', function() {
            highlightCurrentSubtitle(audioPlayer.currentTime);
        });
        
        // 监听播放/暂停
        audioPlayer.addEventListener('play', function() {
            console.log('音频开始播放');
        });
        
        audioPlayer.addEventListener('pause', function() {
            console.log('音频暂停');
        });
    }
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
    uploadedSubtitle = null;
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
    document.getElementById('resultSubtitleContent').innerHTML = '';
    document.getElementById('chunkInfo').textContent = '';
    
    // 重置字幕计数器
    lastSegmentCount = 0;
    
    // 重置高级选项
    document.getElementById('subtitleFile').value = '';
    document.getElementById('uploadedSubtitleInfo').style.display = 'none';
    document.getElementById('startChunk').innerHTML = '<option value="0">请先上传音频文件</option>';
    document.getElementById('startChunk').disabled = true;
    document.getElementById('chunkInfo').style.display = 'none';
    
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

// 字幕编辑功能
let editedSubtitles = {};  // 存储编辑过的字幕

function handleSubtitleEdit(element, index) {
    const originalText = element.getAttribute('data-original-text');
    const currentText = element.textContent.trim();
    
    // 如果文本没有改变，不做任何处理
    if (originalText === currentText) {
        return;
    }
    
    // 记录编辑
    editedSubtitles[index] = {
        original: originalText,
        edited: currentText,
        timestamp: new Date().toISOString()
    };
    
    // 标记已编辑
    element.parentElement.classList.add('edited');
    
    // 显示保存提示
    showEditNotification();
}

function handleSubtitleKeydown(event) {
    // 按Enter键保存并移到下一个字幕
    if (event.key === 'Enter') {
        event.preventDefault();
        event.target.blur();
        
        // 找到下一个字幕
        const nextItem = event.target.closest('.subtitle-item').nextElementSibling;
        if (nextItem) {
            const nextText = nextItem.querySelector('.subtitle-text');
            if (nextText) {
                nextText.focus();
                // 选中全部文本
                const range = document.createRange();
                range.selectNodeContents(nextText);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }
    }
    // 按Escape键取消编辑
    else if (event.key === 'Escape') {
        event.preventDefault();
        const originalText = event.target.getAttribute('data-original-text');
        event.target.textContent = originalText;
        event.target.blur();
    }
}

// 显示编辑提示
function showEditNotification() {
    // 检查是否已有提示
    let notification = document.getElementById('editNotification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'editNotification';
        notification.className = 'edit-notification';
        notification.innerHTML = `
            <p>已编辑 ${Object.keys(editedSubtitles).length} 处字幕</p>
            <button onclick="saveEditedSubtitles()" class="save-edits-btn">保存编辑并提取术语</button>
            <button onclick="cancelEdits()" class="cancel-edits-btn">取消</button>
        `;
        document.body.appendChild(notification);
    } else {
        notification.querySelector('p').textContent = `已编辑 ${Object.keys(editedSubtitles).length} 处字幕`;
    }
}

// 查找字符串差异，提取修改的部分
function findDifferences(original, edited) {
    // 简单的差异检测算法
    const terms = [];
    
    // 按空格分词
    const originalWords = original.split(/\s+/);
    const editedWords = edited.split(/\s+/);
    
    // 使用动态规划找出差异
    let i = 0, j = 0;
    while (i < originalWords.length || j < editedWords.length) {
        if (i >= originalWords.length) {
            // 原文已结束，剩余都是新增
            j++;
        } else if (j >= editedWords.length) {
            // 编辑后已结束，剩余都是删除
            i++;
        } else if (originalWords[i] === editedWords[j]) {
            // 相同，继续
            i++;
            j++;
        } else {
            // 不同，查找最近的匹配
            let found = false;
            
            // 查找是否是替换
            for (let k = 1; k <= 3 && i + k <= originalWords.length && j + k <= editedWords.length; k++) {
                if (originalWords[i + k] === editedWords[j + k]) {
                    // 找到匹配，这是一个替换
                    const originalTerm = originalWords.slice(i, i + k).join(' ');
                    const editedTerm = editedWords.slice(j, j + k).join(' ');
                    if (originalTerm !== editedTerm) {
                        terms.push({
                            original: originalTerm,
                            corrected: editedTerm
                        });
                    }
                    i += k;
                    j += k;
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                // 单词替换
                if (i < originalWords.length && j < editedWords.length) {
                    terms.push({
                        original: originalWords[i],
                        corrected: editedWords[j]
                    });
                }
                i++;
                j++;
            }
        }
    }
    
    return terms;
}

// 保存编辑的字幕并提取术语
async function saveEditedSubtitles() {
    if (Object.keys(editedSubtitles).length === 0) {
        return;
    }
    
    // 提取所有差异术语
    const allTerms = [];
    Object.values(editedSubtitles).forEach(edit => {
        const diffs = findDifferences(edit.original, edit.edited);
        diffs.forEach(diff => {
            // 避免重复
            const exists = allTerms.some(t => 
                t.original === diff.original && t.corrected === diff.corrected
            );
            if (!exists) {
                allTerms.push(diff);
            }
        });
    });
    
    // 显示确认对话框
    const confirmDialog = document.createElement('div');
    confirmDialog.className = 'confirm-dialog';
    confirmDialog.innerHTML = `
        <div class="confirm-content">
            <h3>提取专用术语</h3>
            <p>系统从 ${Object.keys(editedSubtitles).length} 处修改中提取了以下术语：</p>
            <div class="term-preview">
                ${allTerms.length > 0 ? allTerms.map(term => `
                    <div class="term-item">
                        <input type="checkbox" checked value="${term.original}|${term.corrected}">
                        <span class="original">${term.original}</span> → 
                        <span class="corrected">${term.corrected}</span>
                    </div>
                `).join('') : '<p style="text-align: center; color: #999;">未检测到具体的术语差异</p>'}
            </div>
            <div class="edited-examples">
                <details>
                    <summary>查看完整的编辑内容</summary>
                    <div class="full-edits">
                        ${Object.values(editedSubtitles).map(edit => `
                            <div class="full-edit-item">
                                <div class="original-full">${edit.original}</div>
                                <div class="edited-full">${edit.edited}</div>
                            </div>
                        `).join('')}
                    </div>
                </details>
            </div>
            <div class="dialog-actions">
                <button onclick="confirmSaveTerms()" class="confirm-btn">确认保存</button>
                <button onclick="closeConfirmDialog()" class="cancel-btn">取消</button>
            </div>
        </div>
    `;
    document.body.appendChild(confirmDialog);
}

// 确认保存术语
async function confirmSaveTerms() {
    const checkboxes = document.querySelectorAll('.term-preview input[type="checkbox"]:checked');
    const termsToSave = [];
    
    checkboxes.forEach(checkbox => {
        const [original, corrected] = checkbox.value.split('|');
        termsToSave.push({ original, corrected });
    });
    
    if (termsToSave.length === 0) {
        closeConfirmDialog();
        return;
    }
    
    // 批量保存术语
    for (const term of termsToSave) {
        try {
            const response = await fetch('/add_correction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    original: term.original,
                    corrected: term.corrected,
                    context: '字幕编辑'
                })
            });
            
            if (!response.ok) {
                console.error('保存术语失败:', term);
            }
        } catch (error) {
            console.error('保存术语出错:', error);
        }
    }
    
    // 清除编辑记录
    editedSubtitles = {};
    
    // 移除编辑标记
    document.querySelectorAll('.subtitle-item.edited').forEach(item => {
        item.classList.remove('edited');
    });
    
    // 关闭对话框和通知
    closeConfirmDialog();
    const notification = document.getElementById('editNotification');
    if (notification) {
        notification.remove();
    }
    
    alert(`成功保存 ${termsToSave.length} 个术语！`);
}

// 关闭确认对话框
function closeConfirmDialog() {
    const dialog = document.querySelector('.confirm-dialog');
    if (dialog) {
        dialog.remove();
    }
}

// 取消所有编辑
function cancelEdits() {
    // 恢复所有编辑的原始文本
    Object.entries(editedSubtitles).forEach(([index, edit]) => {
        const items = document.querySelectorAll(`.subtitle-item[data-index="${index}"] .subtitle-text`);
        items.forEach(item => {
            item.textContent = edit.original;
            item.parentElement.classList.remove('edited');
        });
    });
    
    // 清除编辑记录
    editedSubtitles = {};
    
    // 移除通知
    const notification = document.getElementById('editNotification');
    if (notification) {
        notification.remove();
    }
}

// 处理字幕文件上传
function handleSubtitleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        uploadedSubtitle = e.target.result;
        document.getElementById('uploadedSubtitleInfo').style.display = 'block';
        document.getElementById('uploadedSubtitleName').textContent = file.name;
        
        // 如果是SRT或VTT格式，解析并显示预览
        if (file.name.endsWith('.srt') || file.name.endsWith('.vtt')) {
            const segments = parseSubtitle(e.target.result, file.name.endsWith('.srt') ? 'srt' : 'vtt');
            if (segments.length > 0) {
                // 立即在结果区域显示上传的字幕
                displayUploadedSubtitles(segments);
                alert(`成功加载 ${segments.length} 条字幕`);
            }
        }
    };
    reader.readAsText(file);
}

// 显示上传的字幕
function displayUploadedSubtitles(segments) {
    // 显示字幕预览区域
    document.getElementById('subtitlePreview').style.display = 'block';
    document.getElementById('subtitleContent').innerHTML = '';
    
    // 重置计数器
    lastSegmentCount = segments.length;
    
    // 显示所有上传的字幕
    updateSubtitleDisplay(segments, false);
    
    // 如果有结果区域，也更新那里
    const resultSection = document.getElementById('resultSection');
    if (resultSection.style.display !== 'none') {
        const resultSubtitleContent = document.getElementById('resultSubtitleContent');
        resultSubtitleContent.innerHTML = segments.map((segment, index) => `
            <div class="subtitle-item" 
                 data-start="${segment.start}" 
                 data-end="${segment.end}"
                 data-index="${index}">
                <div class="subtitle-time" onclick="seekToTime(${segment.start})">${formatTime(segment.start)} - ${formatTime(segment.end)}</div>
                <div class="subtitle-text" 
                     contenteditable="true"
                     data-original-text="${segment.text}"
                     onblur="handleSubtitleEdit(this, ${index})"
                     onclick="event.stopPropagation()"
                     onkeydown="handleSubtitleKeydown(event)">${segment.text}</div>
            </div>
        `).join('');
    }
}

// 解析字幕文件
function parseSubtitle(content, format) {
    const segments = [];
    
    if (format === 'srt') {
        // 解析SRT格式
        const blocks = content.trim().split(/\n\s*\n/);
        blocks.forEach(block => {
            const lines = block.trim().split('\n');
            if (lines.length >= 3) {
                const timeMatch = lines[1].match(/(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})/);
                if (timeMatch) {
                    const start = srtTimeToSeconds(timeMatch[1]);
                    const end = srtTimeToSeconds(timeMatch[2]);
                    const text = lines.slice(2).join(' ');
                    segments.push({ start, end, text });
                }
            }
        });
    } else if (format === 'vtt') {
        // 解析VTT格式
        const lines = content.split('\n');
        let i = 0;
        
        // 跳过WEBVTT头
        while (i < lines.length && !lines[i].includes('-->')) {
            i++;
        }
        
        while (i < lines.length) {
            const line = lines[i];
            if (line.includes('-->')) {
                const timeMatch = line.match(/(\d{2}:\d{2}:\d{2}.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}.\d{3})/);
                if (timeMatch) {
                    const start = vttTimeToSeconds(timeMatch[1]);
                    const end = vttTimeToSeconds(timeMatch[2]);
                    let text = '';
                    i++;
                    while (i < lines.length && lines[i].trim() !== '' && !lines[i].includes('-->')) {
                        text += lines[i] + ' ';
                        i++;
                    }
                    segments.push({ start, end, text: text.trim() });
                }
            }
            i++;
        }
    }
    
    return segments;
}

// SRT时间转换为秒
function srtTimeToSeconds(timeStr) {
    const match = timeStr.match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})/);
    if (match) {
        return parseInt(match[1]) * 3600 + parseInt(match[2]) * 60 + parseInt(match[3]) + parseInt(match[4]) / 1000;
    }
    return 0;
}

// VTT时间转换为秒
function vttTimeToSeconds(timeStr) {
    const match = timeStr.match(/(\d{2}):(\d{2}):(\d{2}).(\d{3})/);
    if (match) {
        return parseInt(match[1]) * 3600 + parseInt(match[2]) * 60 + parseInt(match[3]) + parseInt(match[4]) / 1000;
    }
    return 0;
}

// 下载当前编辑的字幕
function downloadEditedSubtitles() {
    // 收集所有字幕
    const subtitleItems = document.querySelectorAll('.subtitle-item');
    const segments = [];
    
    subtitleItems.forEach(item => {
        const start = parseFloat(item.dataset.start);
        const end = parseFloat(item.dataset.end);
        const text = item.querySelector('.subtitle-text').textContent.trim();
        segments.push({ start, end, text });
    });
    
    if (segments.length === 0) {
        alert('没有字幕可下载');
        return;
    }
    
    // 生成SRT格式
    let srtContent = '';
    segments.forEach((segment, index) => {
        srtContent += `${index + 1}\n`;
        srtContent += `${secondsToSrtTime(segment.start)} --> ${secondsToSrtTime(segment.end)}\n`;
        srtContent += `${segment.text}\n\n`;
    });
    
    // 创建下载
    const blob = new Blob([srtContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `edited_subtitle_${new Date().getTime()}.srt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 秒转换为SRT时间格式
function secondsToSrtTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')},${String(ms).padStart(3, '0')}`;
}