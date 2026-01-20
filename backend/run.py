#!/usr/bin/env python3
import os
import sys

# 数据库配置：使用环境变量（由启动脚本设置）
# 本地开发：start-local.sh 会设置 MySQL 配置
# Docker：docker-compose.yml 会设置 MySQL 配置
# 必须在导入app之前设置，因为config.py会在导入时读取环境变量

db_type = os.environ.get('DB_TYPE', 'mysql')
if os.environ.get('FLASK_ENV') != 'production':
    print(f"[DEBUG] 数据库类型: {db_type}")
    print(f"[DEBUG] 数据库主机: {os.environ.get('DB_HOST', 'localhost')}")
    print(f"[DEBUG] 数据库名称: {os.environ.get('DB_NAME', 'bs_system')}")
    
    # 如果使用 SQLite 且没有设置 DATABASE_URL，自动设置绝对路径
    if db_type == 'sqlite' and not os.environ.get('DATABASE_URL'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, 'instance', 'bs_system.db'))
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        print(f"[DEBUG] 设置DATABASE_URL: {os.environ['DATABASE_URL']}")

from app import create_app

app = create_app()

if __name__ == '__main__':
    # 使用5001端口，避免与macOS AirPlay Receiver冲突
    # 生产环境关闭debug模式
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)

