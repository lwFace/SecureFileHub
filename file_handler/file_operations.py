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


def get_files_list(current_path=''):
    """获取文件列表（包括文件夹）
    
    Args:
        current_path (str): 当前浏览的相对路径，默认为根目录
    
    Returns:
        tuple: (files_list, current_path, parent_path)
    """
    files = []
    folders = []
    
    # 构建完整路径
    if current_path:
        # 安全检查：防止路径遍历攻击
        current_path = current_path.strip('/')
        if '..' in current_path or current_path.startswith('/'):
            raise ValueError('非法路径')
        full_path = os.path.join(UPLOAD_FOLDER, current_path)
    else:
        full_path = UPLOAD_FOLDER
        current_path = ''
    
    # 检查路径是否存在且为目录
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        raise FileNotFoundError('文件夹不存在')
    
    try:
        for filename in os.listdir(full_path):
            filepath = os.path.join(full_path, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': get_file_size(filepath),
                    'type': mimetypes.guess_type(filename)[0] or 'unknown',
                    'is_folder': False,
                    'path': os.path.join(current_path, filename).replace('\\', '/') if current_path else filename
                })
            elif os.path.isdir(filepath):
                folders.append({
                    'name': filename,
                    'size': '文件夹',
                    'type': 'folder',
                    'is_folder': True,
                    'path': os.path.join(current_path, filename).replace('\\', '/') if current_path else filename
                })
    except Exception as e:
        raise Exception(f'读取文件夹时出错: {str(e)}')
    
    # 计算父路径
    parent_path = ''
    if current_path:
        parent_parts = current_path.replace('\\', '/').split('/')
        if len(parent_parts) > 1:
            parent_path = '/'.join(parent_parts[:-1])
    
    # 文件夹排在前面，然后是文件
    return folders + files, current_path, parent_path


def upload_single_file(file, target_path=''):
    """
    上传单个文件到指定路径
    """
    try:
        # 安全检查：防止路径遍历攻击
        if target_path and ('..' in target_path or target_path.startswith('/')):
            return "无效的路径"
        
        # 构建完整的上传路径
        if target_path:
            upload_path = os.path.join(UPLOAD_FOLDER, target_path)
        else:
            upload_path = UPLOAD_FOLDER
        
        # 检查目标文件夹是否存在
        if not os.path.exists(upload_path):
            return f"目标文件夹不存在: {target_path}"
        
        if not file or file.filename == '':
            raise ValueError('没有选择文件')
        
        filename = secure_filename(file.filename)
        if not filename:
            raise ValueError('文件名无效')
        
        filepath = os.path.join(upload_path, filename)
        
        # 检查文件是否已存在
        if os.path.exists(filepath):
            raise FileExistsError(f'文件 {filename} 已存在')
        
        file.save(filepath)
        return f'文件 {filename} 上传成功'
    
    except Exception as e:
        return f'上传失败: {str(e)}'


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
    """删除文件或文件夹"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError('文件或文件夹不存在')
    
    if os.path.isfile(filepath):
        os.remove(filepath)
        return f'文件 {filename} 删除成功'
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)
        return f'文件夹 {filename} 删除成功'
    else:
        raise Exception(f'无法删除 {filename}：未知类型')


def create_folder_handler(folder_name):
    """创建文件夹"""
    if not folder_name or folder_name.strip() == '':
        raise ValueError('文件夹名称不能为空')
    
    # 使用secure_filename确保文件夹名称安全
    folder_name = secure_filename(folder_name.strip())
    if not folder_name:
        raise ValueError('文件夹名称无效')
    
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    
    # 检查文件夹是否已存在
    if os.path.exists(folder_path):
        raise FileExistsError(f'文件夹 {folder_name} 已存在')
    
    try:
        os.makedirs(folder_path)
        return f'文件夹 {folder_name} 创建成功'
    except Exception as e:
        raise Exception(f'创建文件夹时出错: {str(e)}')