const fileInput = document.getElementById('file');
const selectedFileName = document.getElementById('selectedFileName');
const selectedFileInfo = document.getElementById('selectedFileInfo');
const uploadBtn = document.getElementById('uploadBtn');
const uploadForm = document.getElementById('uploadForm');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const uploadStatus = document.getElementById('uploadStatus');
const largeFileNotice = document.getElementById('largeFileNotice');

const CHUNK_SIZE = 1024 * 1024; // 1MB per chunk
const LARGE_FILE_THRESHOLD = 50 * 1024 * 1024; // 50MB

fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        const fileName = this.files[0].name;
        const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2);
        selectedFileName.textContent = `${fileName} (${fileSize} MB)`;
        selectedFileInfo.style.display = 'flex';
        uploadBtn.disabled = false;
        
        // 显示大文件提示
        if (this.files[0].size > LARGE_FILE_THRESHOLD) {
            largeFileNotice.style.display = 'flex';
        } else {
            largeFileNotice.style.display = 'none';
        }
    } else {
        selectedFileName.textContent = '未选择文件';
        selectedFileInfo.style.display = 'none';
        uploadBtn.disabled = true;
        largeFileNotice.style.display = 'none';
    }
});

// 处理表单提交
uploadForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) return;

    // 大文件使用分块上传
    if (file.size > LARGE_FILE_THRESHOLD) {
        uploadLargeFile(file);
    } else {
        uploadSmallFile(file);
    }
});

function uploadSmallFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // 获取target_path值并添加到FormData
    const targetPathInput = document.querySelector('input[name="target_path"]');
    if (targetPathInput) {
        formData.append('target_path', targetPathInput.value);
    }

    showProgress();
    updateStatus('正在上传...');

    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            updateProgress(percentComplete);
        }
    });

    xhr.addEventListener('load', function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (response.success) {
                updateStatus('上传成功！');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                updateStatus('上传失败：' + response.error);
                hideProgress();
            }
        } else {
            updateStatus('上传失败，请重试');
            hideProgress();
        }
    });

    xhr.addEventListener('error', function() {
        updateStatus('网络错误，请重试');
        hideProgress();
    });

    xhr.open('POST', '/upload');
    xhr.send(formData);
}

function uploadLargeFile(file) {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    const uploadId = generateUploadId();
    
    showProgress();
    updateStatus('准备分块上传...');

    function uploadChunk(chunkIndex) {
        const start = chunkIndex * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('chunk_index', chunkIndex);
        formData.append('total_chunks', totalChunks);
        formData.append('upload_id', uploadId);
        formData.append('filename', file.name);
        
        // 获取target_path值并添加到FormData
        const targetPathInput = document.querySelector('input[name="target_path"]');
        if (targetPathInput) {
            formData.append('target_path', targetPathInput.value);
        }

        const xhr = new XMLHttpRequest();
        
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    const progress = ((chunkIndex + 1) / totalChunks) * 100;
                    updateProgress(progress);
                    updateStatus(`上传进度: ${chunkIndex + 1}/${totalChunks} 块`);
                    
                    if (chunkIndex + 1 < totalChunks) {
                        uploadChunk(chunkIndex + 1);
                    } else {
                        updateStatus('上传完成！');
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    }
                } else {
                    updateStatus('上传失败：' + response.error);
                    hideProgress();
                }
            } else {
                updateStatus('上传失败，请重试');
                hideProgress();
            }
        });
        
        xhr.addEventListener('error', function() {
            updateStatus('网络错误，请重试');
            hideProgress();
        });
        
        xhr.open('POST', '/upload_chunk');
        xhr.send(formData);
    }
    
    uploadChunk(0);
}

function generateUploadId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function showProgress() {
    progressContainer.style.display = 'block';
    uploadStatus.style.display = 'block';
    uploadBtn.disabled = true;
}

function hideProgress() {
    progressContainer.style.display = 'none';
    uploadStatus.style.display = 'none';
    uploadBtn.disabled = false;
}

function updateProgress(percent) {
    const roundedPercent = Math.round(percent);
    progressBar.style.width = roundedPercent + '%';
    progressBar.textContent = roundedPercent + '%';
}

function updateStatus(message) {
    uploadStatus.textContent = message;
}

// 拖拽上传功能
const uploadSection = document.querySelector('.upload-section');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadSection.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    uploadSection.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadSection.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    uploadSection.style.background = '#e3f2fd';
}

function unhighlight(e) {
    uploadSection.style.background = '#f8f9fa';
}

uploadSection.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        fileInput.files = files;
        fileInput.dispatchEvent(new Event('change'));
    }
}

// 文件夹创建功能 - 弹出对话框版本
const createFolderBtn = document.getElementById('createFolderBtn');
const folderModal = document.getElementById('folderModal');
const modalFolderName = document.getElementById('modalFolderName');
const modalCreateBtn = document.getElementById('modalCreateBtn');
const modalCancelBtn = document.getElementById('modalCancelBtn');

// 显示创建文件夹对话框
createFolderBtn.addEventListener('click', function() {
    folderModal.style.display = 'block';
    modalFolderName.value = '';
    modalFolderName.focus();
});

// 取消按钮
modalCancelBtn.addEventListener('click', function() {
    folderModal.style.display = 'none';
});

// 点击对话框外部关闭
folderModal.addEventListener('click', function(e) {
    if (e.target === folderModal) {
        folderModal.style.display = 'none';
    }
});

// ESC键关闭对话框
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && folderModal.style.display === 'block') {
        folderModal.style.display = 'none';
    }
});

// 回车键创建文件夹
modalFolderName.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        modalCreateBtn.click();
    }
});

// 创建文件夹
modalCreateBtn.addEventListener('click', function() {
    const folderName = modalFolderName.value.trim();
    if (!folderName) {
        alert('请输入文件夹名称');
        modalFolderName.focus();
        return;
    }

    // 验证文件夹名称
    if (!/^[^<>:"/\\|?*]+$/.test(folderName)) {
        alert('文件夹名称包含非法字符');
        modalFolderName.focus();
        return;
    }

    modalCreateBtn.disabled = true;
    modalCreateBtn.textContent = '创建中...';

    const formData = new FormData();
    formData.append('folder_name', folderName);
    
    // 获取当前路径
    const targetPathInput = document.querySelector('input[name="target_path"]');
    if (targetPathInput) {
        formData.append('target_path', targetPathInput.value);
    }

    fetch('/create_folder', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            folderModal.style.display = 'none';
            location.reload(); // 刷新页面显示新文件夹
        } else {
            alert('创建失败：' + data.error);
            modalFolderName.focus();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('创建失败，请重试');
        modalFolderName.focus();
    })
    .finally(() => {
        modalCreateBtn.disabled = false;
        modalCreateBtn.textContent = '创建';
    });
});

// 保留原有的文件夹创建功能作为备用（隐藏状态）
const folderForm = document.getElementById('folderForm');
const folderInput = document.getElementById('folderName');
const folderBtn = document.getElementById('folderBtn');

folderForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const folderName = folderInput.value.trim();
    if (!folderName) {
        alert('请输入文件夹名称');
        return;
    }

    folderBtn.disabled = true;
    folderBtn.textContent = '创建中...';

    const formData = new FormData();
    formData.append('folder_name', folderName);

    fetch('/create_folder', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            folderInput.value = '';
            location.reload(); // 刷新页面显示新文件夹
        } else {
            alert('创建失败：' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('创建失败，请重试');
    })
    .finally(() => {
        folderBtn.disabled = false;
        folderBtn.textContent = '📁 创建文件夹';
    });
});

// 处理删除确认和拖拽功能
document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const filename = this.dataset.filename;
            const type = this.dataset.type;
            
            if (confirm(`确定要删除${type} ${filename} 吗？`)) {
                this.submit();
            }
        });
    });

    // 简化的拖拽功能实现
    let draggedElement = null;

    // 初始化拖拽功能
    function initDragAndDrop() {
        // 为所有可拖拽文件添加事件
         document.querySelectorAll('.draggable').forEach(element => {
             element.ondragstart = function(e) {
                 draggedElement = this;
                 this.style.opacity = '0.5';
                 e.dataTransfer.setData('text/plain', this.dataset.filepath);
                 e.dataTransfer.effectAllowed = 'move';
             };
             
             element.ondragend = function(e) {
                 this.style.opacity = '1';
                 draggedElement = null;
                 // 清除所有高亮
                 document.querySelectorAll('.drop-zone').forEach(zone => {
                     zone.classList.remove('drag-over');
                 });
             };
         });

        // 为所有文件夹添加拖放事件
         document.querySelectorAll('.drop-zone').forEach(zone => {
             zone.ondragover = function(e) {
                 e.preventDefault();
                 e.dataTransfer.dropEffect = 'move';
                 return false;
             };
             
             zone.ondragenter = function(e) {
                 e.preventDefault();
                 if (this.dataset.isFolder === 'true') {
                     this.classList.add('drag-over');
                 }
                 return false;
             };
             
             zone.ondragleave = function(e) {
                 // 检查是否真的离开了元素
                 if (!this.contains(e.relatedTarget)) {
                     this.classList.remove('drag-over');
                 }
             };
             
             zone.ondrop = function(e) {
                 e.preventDefault();
                 this.classList.remove('drag-over');
                 
                 if (draggedElement && this.dataset.isFolder === 'true') {
                     const sourceFile = draggedElement.dataset.filepath;
                     const targetFolder = this.dataset.filepath;
                     
                     // 发送移动请求
                     fetch('/move_file', {
                         method: 'POST',
                         headers: {
                             'Content-Type': 'application/json',
                         },
                         body: JSON.stringify({
                             source_path: sourceFile,
                             target_path: targetFolder
                         })
                     })
                     .then(response => response.json())
                     .then(data => {
                         if (data.success) {
                             location.reload();
                         } else {
                             alert('文件移动失败：' + data.error);
                         }
                     })
                     .catch(error => {
                         console.error('移动文件时出错:', error);
                         alert('文件移动失败');
                     });
                 }
                 return false;
             };
         });
    }

    // 页面加载完成后初始化
    initDragAndDrop();

    // 添加文件夹点击事件处理
    document.querySelectorAll('.folder-content').forEach(folderContent => {
        folderContent.addEventListener('click', function(e) {
            // 如果正在拖拽，不执行跳转
            if (e.target.closest('.file-card').classList.contains('dragging')) {
                return;
            }
            
            const folderUrl = this.dataset.folderUrl;
            if (folderUrl) {
                window.location.href = folderUrl;
            }
        });
    });
});