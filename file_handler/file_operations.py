# -*- coding: utf-8 -*-
"""
文件操作核心模块
处理文件上传、下载、删除等功能
"""

import os
import tempfile
import shutil
import mimetypes
from werkzeug.utils import secure_filename
from flask import send_file
from config import UPLOAD_FOLDER


def get_file_size(filepath):
    """获取文件大小的可读格式"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_files_list():
    """获取文件列表"""
    files = []
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': get_file_size(filepath),
                    'type': mimetypes.guess_type(filename)[0] or 'unknown'
                })
    except Exception as e:
        raise Exception(f'读取文件夹时出错: {str(e)}')
    
    return files


def upload_single_file(file):
    """处理单文件上传"""
    if not file or file.filename == '':
        raise ValueError('没有选择文件')
    
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError('文件名无效')
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # 检查文件是否已存在
    if os.path.exists(filepath):
        raise FileExistsError(f'文件 {filename} 已存在')
    
    file.save(filepath)
    return f'文件 {filename} 上传成功'


def upload_chunk_file(chunk, chunk_number, total_chunks, filename, upload_id):
    """处理分块上传"""
    filename = secure_filename(filename)
    
    # 创建临时目录存储分块
    temp_dir = os.path.join(tempfile.gettempdir(), 'file_upload', upload_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 保存分块
    chunk_path = os.path.join(temp_dir, f'chunk_{chunk_number}')
    chunk.save(chunk_path)
    
    # 检查是否所有分块都已上传
    uploaded_chunks = len([f for f in os.listdir(temp_dir) if f.startswith('chunk_')])
    
    if uploaded_chunks == total_chunks:
        # 合并所有分块
        final_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 检查文件是否已存在
        if os.path.exists(final_path):
            # 清理临时文件
            shutil.rmtree(temp_dir)
            raise FileExistsError(f'文件 {filename} 已存在')
        
        with open(final_path, 'wb') as final_file:
            for i in range(total_chunks):
                chunk_path = os.path.join(temp_dir, f'chunk_{i}')
                with open(chunk_path, 'rb') as chunk_file:
                    final_file.write(chunk_file.read())
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        
        return {'success': True, 'message': f'文件 {filename} 上传成功'}
    else:
        return {'success': True, 'progress': (uploaded_chunks / total_chunks) * 100}


def download_file_handler(filename):
    """处理文件下载"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError('文件不存在')
    
    return send_file(filepath, as_attachment=True, download_name=filename)


def delete_file_handler(filename):
    """删除文件"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError('文件不存在')
    
    os.remove(filepath)
    return f'文件 {filename} 删除成功'