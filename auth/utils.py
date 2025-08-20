# -*- coding: utf-8 -*-
"""
认证工具模块
包含认证相关的辅助函数
"""

from flask import request


def get_client_ip():
    """获取客户端真实IP地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr