#!/usr/bin/env python3
import os
import sys

# 如果没有设置DATABASE_URL，自动设置绝对路径
# 必须在导入app之前设置，因为config.py会在导入时读取环境变量
if not os.environ.get('DATABASE_URL'):
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_dir, 'instance', 'bs_system.db'))
    # SQLite URI格式：sqlite:///绝对路径
    # 对于绝对路径，SQLite接受 sqlite:/// 或 sqlite://// 格式
    # 我们使用标准格式 sqlite:///（3个斜杠）
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    # 调试输出
    if os.environ.get('FLASK_ENV') != 'production':
        print(f"[DEBUG] 设置DATABASE_URL: {os.environ['DATABASE_URL']}")

from app import create_app

app = create_app()

if __name__ == '__main__':
    # 使用5001端口，避免与macOS AirPlay Receiver冲突
    app.run(host='0.0.0.0', port=5001, debug=True)

