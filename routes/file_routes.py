# -*- coding: utf-8 -*-
"""
文件路由模块
处理文件上传、下载、删除等路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from auth import login_required
from file_handler import (
    get_files_list,
    upload_single_file,
    upload_chunk_file,
    download_file_handler,
    delete_file_handler,
    create_folder_handler
)

file_bp = Blueprint('file_routes', __name__)


@file_bp.route('/')
@login_required
def index():
    """主页面，显示文件列表"""
    try:
        files = get_files_list()
    except Exception as e:
        flash(str(e), 'error')
        files = []
    
    return render_template('index.html', files=files, username=session.get('username'))


@file_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """处理文件上传"""
    try:
        if 'file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(url_for('file_routes.index'))
        
        file = request.files['file']
        message = upload_single_file(file)
        flash(message, 'success')
        
    except RequestEntityTooLarge:
        flash('文件太大，最大支持1GB', 'error')
    except ValueError as e:
        flash(str(e), 'error')
    except FileExistsError as e:
        flash(str(e), 'warning')
    except Exception as e:
        flash(f'上传失败: {str(e)}', 'error')
    
    return redirect(url_for('file_routes.index'))


@file_bp.route('/upload_chunk', methods=['POST'])
@login_required
def upload_chunk():
    """处理分块上传"""
    try:
        chunk = request.files['chunk']
        chunk_number = int(request.form['chunkNumber'])
        total_chunks = int(request.form['totalChunks'])
        filename = request.form['filename']
        upload_id = request.form['uploadId']
        
        result = upload_chunk_file(chunk, chunk_number, total_chunks, filename, upload_id)
        return jsonify(result)
        
    except FileExistsError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})


@file_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    """处理文件下载"""
    try:
        return download_file_handler(filename)
    except FileNotFoundError:
        flash('文件不存在', 'error')
        return redirect(url_for('file_routes.index'))
    except Exception as e:
        flash(f'下载失败: {str(e)}', 'error')
        return redirect(url_for('file_routes.index'))


@file_bp.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    """删除文件或文件夹"""
    try:
        message = delete_file_handler(filename)
        flash(message, 'success')
    except FileNotFoundError:
        flash('文件或文件夹不存在', 'error')
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('file_routes.index'))


@file_bp.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    """创建文件夹"""
    try:
        folder_name = request.form.get('folder_name', '').strip()
        if not folder_name:
            return jsonify({'success': False, 'error': '文件夹名称不能为空'})
        
        message = create_folder_handler(folder_name)
        return jsonify({'success': True, 'message': message})
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)})
    except FileExistsError as e:
        return jsonify({'success': False, 'error': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'error': f'创建文件夹失败: {str(e)}'})