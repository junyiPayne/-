#!/usr/bin/env python3
"""
GPU 版本启动脚本
使用 8000 端口，支持 GPU
"""
import os
import sys

# 数据库配置：使用 SQLite（本地部署）
db_type = os.environ.get('DB_TYPE', 'sqlite')
if os.environ.get('FLASK_ENV') != 'production':
    print(f"[DEBUG] 数据库类型: {db_type}")
    
    # 如果使用 SQLite 且没有设置 DATABASE_URL，自动设置绝对路径
    if db_type == 'sqlite' and not os.environ.get('DATABASE_URL'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, 'instance', 'bs_system.db'))
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        print(f"[DEBUG] 设置DATABASE_URL: {os.environ['DATABASE_URL']}")

from app import create_app

app = create_app()

# 检查 GPU 支持
try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU 可用: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA 版本: {torch.version.cuda}")
    else:
        print("⚠️ GPU 不可用，将使用 CPU")
except ImportError:
    print("⚠️ PyTorch 未安装，GPU 功能不可用")
    print("💡 提示: 如需 GPU 支持，请安装 PyTorch CUDA 版本:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117")

if __name__ == '__main__':
    # 使用 8000 端口（GPU 版本）
    port = int(os.environ.get('PORT', 8000))
    print(f"\n🚀 启动后端服务器 (端口 {port})...")
    print(f"📱 API 地址: http://localhost:{port}/api")
    print(f"🔍 健康检查: http://localhost:{port}/api/health")
    print(f"🎮 GPU 状态: http://localhost:{port}/api/gpu/status")
    print("\n按 Ctrl+C 停止服务\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
