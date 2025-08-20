# -*- coding: utf-8 -*-
"""
认证路由模块
处理登录、登出等认证相关路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import verify_user_password, get_client_ip
from security import is_ip_banned, record_login_attempt, get_remaining_attempts, get_ban_remaining_time

auth_bp = Blueprint('auth_routes', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    client_ip = get_client_ip()
    
    # 检查IP是否被封禁
    if is_ip_banned(client_ip):
        remaining_time = get_ban_remaining_time(client_ip)
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        if minutes > 0:
            time_str = f"{minutes}分{seconds}秒"
        else:
            time_str = f"{seconds}秒"
        flash(f'您的IP已被临时封禁，请在 {time_str} 后重试', 'error')
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verify_user_password(username, password):
            # 登录成功
            record_login_attempt(client_ip, success=True)
            session['logged_in'] = True
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('file_routes.index'))
        else:
            # 登录失败
            is_banned = record_login_attempt(client_ip, success=False)
            
            if is_banned:
                flash('登录失败次数过多，您的IP已被临时封禁10分钟', 'error')
            else:
                remaining = get_remaining_attempts(client_ip)
                if remaining > 0:
                    flash(f'用户名或密码错误，剩余尝试次数: {remaining}', 'error')
                else:
                    flash('用户名或密码错误', 'error')
    
    # GET请求或登录失败时，显示剩余尝试次数
    remaining = get_remaining_attempts(client_ip)
    return render_template('login.html', remaining_attempts=remaining)


@auth_bp.route('/logout')
def logout():
    """登出"""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('已成功登出', 'success')
    return redirect(url_for('auth_routes.login'))