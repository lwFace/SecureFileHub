# -*- coding: utf-8 -*-
"""
配置模块
集中管理应用的所有配置参数
"""

import os
from werkzeug.security import generate_password_hash

# Flask应用配置
SECRET_KEY = 'your-secret-key-change-this-in-production'
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# 用户认证配置
# 密码已使用Werkzeug的密码哈希功能加密
USERS = {
    'root': 'pbkdf2:sha256:260000$ysc7IdhVfLKRaFO5$6942b1dad1c14005d3c31b5fe290535b407f428dff618233e6c8c53e7146e25b',  # 用户名: 密码哈希
}

# 登录安全配置
MAX_LOGIN_ATTEMPTS = 3  # 最大登录失败次数
BAN_DURATION = 600  # 封禁时长（秒），10分钟
ATTEMPT_WINDOW = 900  # 失败次数统计时间窗口（秒），15分钟

# 文件上传配置
UPLOAD_FOLDER = 'D:/upload'
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'security.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 管理员用户列表
ADMIN_USERS = ['root']

# 应用信息
APP_NAME = '文件服务器'
APP_VERSION = '1.0.0'