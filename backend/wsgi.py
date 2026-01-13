"""
WSGI 入口文件
用于 Gunicorn 等 WSGI 服务器
"""
from app import create_app
import os

# 创建应用实例
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()
