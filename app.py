# -*- coding: utf-8 -*-
"""
文件服务器主应用
重构后的Flask应用入口文件
"""

from flask import Flask
from werkzeug.exceptions import RequestEntityTooLarge
from config import SECRET_KEY, MAX_FILE_SIZE, DEBUG, HOST, PORT, APP_NAME
from security import setup_logging
from routes import auth_bp, file_bp, admin_bp

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 设置日志
setup_logging()

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(file_bp)
app.register_blueprint(admin_bp)

# 错误处理
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """处理文件过大错误"""
    return {'error': '文件太大'}, 413

if __name__ == '__main__':
    print(f"{APP_NAME}启动中...")
    print(f"访问地址: http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)