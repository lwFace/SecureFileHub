# -*- coding: utf-8 -*-
"""
管理员路由模块
处理安全管理等管理员功能路由
"""

from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from auth import login_required, is_admin_user
from security import (
    get_banned_ips_info,
    get_login_attempts_info,
    unban_ip_address,
    clear_ip_attempts
)
from config import MAX_LOGIN_ATTEMPTS, BAN_DURATION, ATTEMPT_WINDOW

admin_bp = Blueprint('admin_routes', __name__, url_prefix='/admin')


def admin_required(f):
    """管理员权限验证装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_user(session.get('username')):
            flash('权限不足，只有管理员可以访问此页面', 'error')
            return redirect(url_for('file_routes.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/security')
@login_required
@admin_required
def security_admin():
    """安全管理页面"""
    # 获取封禁IP信息
    banned_info = get_banned_ips_info()
    
    # 获取登录失败信息
    attempt_info = get_login_attempts_info()
    
    return render_template('security_admin.html', 
                         banned_ips=banned_info, 
                         login_attempts=attempt_info,
                         config={
                             'max_attempts': MAX_LOGIN_ATTEMPTS,
                             'ban_duration': BAN_DURATION // 60,  # 转换为分钟
                             'attempt_window': ATTEMPT_WINDOW // 60  # 转换为分钟
                         })


@admin_bp.route('/unban/<ip>', methods=['POST'])
@login_required
@admin_required
def unban_ip(ip):
    """手动解封IP"""
    admin_user = session.get('username')
    
    if unban_ip_address(ip, admin_user):
        flash(f'IP {ip} 已成功解封', 'success')
        return jsonify({'success': True, 'message': f'IP {ip} 已解封'})
    else:
        return jsonify({'success': False, 'message': 'IP未在封禁列表中'})


@admin_bp.route('/clear_attempts/<ip>', methods=['POST'])
@login_required
@admin_required
def clear_attempts(ip):
    """清除IP的失败记录"""
    admin_user = session.get('username')
    
    if clear_ip_attempts(ip, admin_user):
        flash(f'IP {ip} 的失败记录已清除', 'success')
        return jsonify({'success': True, 'message': f'IP {ip} 失败记录已清除'})
    else:
        return jsonify({'success': False, 'message': 'IP无失败记录'})