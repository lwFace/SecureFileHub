# -*- coding: utf-8 -*-
"""
认证核心模块
处理用户登录验证、密码哈希等功能
"""

from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import USERS


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function


def generate_user_password_hash(password):
    """生成用户密码哈希值的工具函数"""
    return generate_password_hash(password)


def verify_user_password(username, password):
    """验证用户密码的工具函数"""
    if username not in USERS:
        return False
    return check_password_hash(USERS[username], password)


def is_admin_user(username):
    """检查用户是否为管理员"""
    from config import ADMIN_USERS
    return username in ADMIN_USERS


def get_current_user():
    """获取当前登录用户"""
    return session.get('username')


def is_logged_in():
    """检查用户是否已登录"""
    return 'logged_in' in session and session['logged_in']