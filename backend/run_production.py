#!/usr/bin/env python3
"""
生产环境启动脚本
注意：生产环境应该使用 Gunicorn，此脚本仅用于测试
"""
from app import create_app
import os

# 设置生产环境
os.environ['FLASK_ENV'] = 'production'

app = create_app('production')

if __name__ == '__main__':
    # 生产环境不应该使用 Flask 开发服务器
    # 应该使用 Gunicorn: gunicorn -c gunicorn.conf.py "app:create_app()"
    print("警告: 生产环境应该使用 Gunicorn 启动!")
    print("使用命令: gunicorn -c gunicorn.conf.py 'app:create_app()'")
    app.run(host='0.0.0.0', port=5001, debug=False)
