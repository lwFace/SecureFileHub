# -*- coding: utf-8 -*-
"""
路由模块
处理应用的所有路由
"""

from .auth_routes import auth_bp
from .file_routes import file_bp
from .admin_routes import admin_bp

__all__ = [
    'auth_bp',
    'file_bp', 
    'admin_bp'
]