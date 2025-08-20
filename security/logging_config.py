# -*- coding: utf-8 -*-
"""
日志配置模块
处理应用的日志配置
"""

import logging
from config import LOG_LEVEL, LOG_FILE, LOG_FORMAT


def setup_logging():
    """配置应用日志"""
    # 获取日志级别
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # 配置日志
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)