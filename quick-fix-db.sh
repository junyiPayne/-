#!/bin/bash

# 快速修复数据库脚本

echo "🔧 快速修复数据库..."
echo ""

cd backend

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv"
    exit 1
fi

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt --quiet

# 删除旧的数据库文件
echo "🗑️  清理旧数据库..."
rm -f instance/bs_system.db

# 确保目录存在
mkdir -p instance
chmod 755 instance

# 直接使用Python创建数据库并初始化
echo "🔄 初始化数据库..."
python3 << 'PYEOF'
import os
import sys
import sqlite3

# 设置路径
sys.path.insert(0, os.getcwd())

# 先创建数据库文件
db_path = os.path.abspath('instance/bs_system.db')
print(f"数据库路径: {db_path}")

# 创建空数据库文件
conn = sqlite3.connect(db_path)
conn.close()
print("✅ 数据库文件创建成功")

# 使用环境变量设置数据库路径（这样create_app会使用正确的路径）
abs_db_uri = f'sqlite:///{db_path}'
os.environ['DATABASE_URL'] = abs_db_uri
print(f"设置DATABASE_URL环境变量: {abs_db_uri}")

# 现在初始化
from app import create_app, db
from app.models import User, Role

app = create_app()

# 验证路径
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
print(f"最终数据库URI: {db_uri}")

with app.app_context():
    # 创建表
    db.create_all()
    print("✅ 数据库表创建完成")
    
    # 创建角色
    roles_config = [
        {'code': 'admin', 'name': '管理员', 'description': '系统管理员'},
        {'code': 'teacher', 'name': '教师', 'description': '教师'},
        {'code': 'student', 'name': '学生', 'description': '学生'},
        {'code': 'user', 'name': '普通用户', 'description': '普通用户'}
    ]
    
    roles = {}
    for r_cfg in roles_config:
        role = Role.query.filter_by(code=r_cfg['code']).first()
        if not role:
            role = Role(name=r_cfg['name'], code=r_cfg['code'], description=r_cfg['description'])
            db.session.add(role)
            print(f"✅ 创建{r_cfg['name']}角色")
        roles[r_cfg['code']] = role
    
    db.session.commit()
    
    # 创建管理员
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', real_name='管理员')
        admin.set_password('admin123')
        admin.role_id = roles['admin'].id
        db.session.add(admin)
        db.session.commit()
        print("✅ 创建管理员账户: admin / admin123")
    
    print("\n✅ 数据库初始化完成！")
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 数据库修复成功！"
    echo "现在可以运行: cd .. && ./start-local.sh"
else
    echo ""
    echo "❌ 数据库修复失败，请检查错误信息"
    exit 1
fi
