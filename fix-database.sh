#!/bin/bash

# 数据库修复脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔧 数据库修复工具..."
echo ""

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo -e "${YELLOW}📥 检查并安装依赖...${NC}"
pip install -r requirements.txt --quiet

# 检查数据库文件
echo ""
echo -e "${YELLOW}🔍 检查数据库文件...${NC}"
if [ -f "instance/bs_system.db" ]; then
    echo -e "${GREEN}✅ 数据库文件存在: instance/bs_system.db${NC}"
    ls -lh instance/bs_system.db
else
    echo -e "${YELLOW}⚠️  数据库文件不存在${NC}"
fi

# 确保instance目录存在
if [ ! -d "instance" ]; then
    echo -e "${YELLOW}创建instance目录...${NC}"
    mkdir -p instance
fi

# 测试数据库连接
echo ""
echo -e "${YELLOW}🔍 测试数据库连接...${NC}"
python3 << EOF
from app import create_app, db
from sqlalchemy import text
import sys

try:
    app = create_app()
    with app.app_context():
        print("数据库URI:", app.config['SQLALCHEMY_DATABASE_URI'])
        print("Instance路径:", app.instance_path)
        
        # 测试连接
        result = db.session.execute(text('SELECT 1'))
        db.session.commit()
        print("✅ 数据库连接成功")
        sys.exit(0)
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

DB_TEST_RESULT=$?

if [ $DB_TEST_RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 数据库连接正常${NC}"
else
    echo ""
    echo -e "${RED}❌ 数据库连接失败，尝试重新初始化...${NC}"
    echo ""
    
    # 备份现有数据库
    if [ -f "instance/bs_system.db" ]; then
        BACKUP_FILE="instance/bs_system.db.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}备份现有数据库到: $BACKUP_FILE${NC}"
        cp instance/bs_system.db "$BACKUP_FILE"
    fi
    
    # 重新初始化数据库
    echo -e "${YELLOW}🔄 重新初始化数据库...${NC}"
    if python init_database.py; then
        echo -e "${GREEN}✅ 数据库初始化成功${NC}"
    else
        echo -e "${RED}❌ 数据库初始化失败${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 数据库修复完成${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "现在可以重新启动后端服务:"
echo "  ./start-local.sh"
echo ""
