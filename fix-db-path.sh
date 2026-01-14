#!/bin/bash

# 数据库路径修复脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔧 修复数据库路径问题..."
echo ""

cd backend

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ 未找到虚拟环境，请先运行: python3 -m venv venv${NC}"
    exit 1
fi

# 确保instance目录存在且有写权限
echo -e "${YELLOW}📁 检查instance目录...${NC}"
if [ ! -d "instance" ]; then
    echo "创建instance目录..."
    mkdir -p instance
fi

# 检查权限
chmod 755 instance 2>/dev/null || true

# 删除可能损坏的数据库文件（先备份）
if [ -f "instance/bs_system.db" ]; then
    echo -e "${YELLOW}备份现有数据库...${NC}"
    cp instance/bs_system.db "instance/bs_system.db.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
    rm -f instance/bs_system.db
fi

# 使用Python直接创建数据库文件
echo -e "${YELLOW}🔄 使用Python创建数据库文件...${NC}"
python3 << 'PYEOF'
import os
import sqlite3

# 确保instance目录存在
instance_dir = os.path.join(os.getcwd(), 'instance')
os.makedirs(instance_dir, exist_ok=True)

# 创建数据库文件
db_path = os.path.join(instance_dir, 'bs_system.db')
print(f"数据库路径: {db_path}")

# 先创建一个空的数据库文件
try:
    conn = sqlite3.connect(db_path)
    conn.close()
    print("✅ 数据库文件创建成功")
except Exception as e:
    print(f"❌ 创建数据库文件失败: {e}")
    exit(1)

# 检查文件权限
if os.path.exists(db_path):
    print(f"✅ 文件存在，权限: {oct(os.stat(db_path).st_mode)}")
    os.chmod(db_path, 0o664)
    print("✅ 权限已设置")
else:
    print("❌ 文件不存在")
    exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 创建数据库文件失败${NC}"
    exit 1
fi

# 现在初始化数据库
echo ""
echo -e "${YELLOW}🔄 初始化数据库表...${NC}"
python3 << 'PYEOF'
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.getcwd())

try:
    from app import create_app, db
    
    app = create_app()
    with app.app_context():
        print(f"数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Instance路径: {app.instance_path}")
        
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功")
        
        # 导入模型并创建初始数据
        from app.models import User, Role
        
        # 创建角色
        roles_config = [
            {'code': 'admin', 'name': '管理员', 'description': '系统管理员'},
            {'code': 'teacher', 'name': '教师', 'description': '教师，管理课程和学生'},
            {'code': 'student', 'name': '学生', 'description': '学生，查看课程和提交作业'},
            {'code': 'user', 'name': '普通用户', 'description': '普通注册用户'}
        ]
        
        roles = {}
        for r_cfg in roles_config:
            role = Role.query.filter_by(code=r_cfg['code']).first()
            if not role:
                role = Role(
                    name=r_cfg['name'],
                    code=r_cfg['code'],
                    description=r_cfg['description']
                )
                db.session.add(role)
                print(f"✅ 创建{r_cfg['name']}角色")
            roles[r_cfg['code']] = role
        
        db.session.commit()
        
        # 创建管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员'
            )
            admin_user.set_password('admin123')
            admin_user.role_id = roles['admin'].id
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 创建管理员账户: admin / admin123")
        else:
            print("ℹ️  管理员账户已存在")
        
        print("\n✅ 数据库初始化完成！")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ 数据库修复成功！${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo "现在可以重新启动服务:"
    echo "  cd .."
    echo "  ./start-local.sh"
else
    echo ""
    echo -e "${RED}❌ 数据库修复失败${NC}"
    echo "请检查上面的错误信息"
    exit 1
fi
