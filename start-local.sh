#!/bin/bash

# 学生健康管理系统 - 本地开发模式一键启动脚本

set -e  # 遇到错误立即退出

echo "🚀 启动本地开发模式..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Python3，请先安装 Python 3.9+${NC}"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Node.js，请先安装 Node.js 18+${NC}"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 npm，请先安装 npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"
echo ""

# 检查端口占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  端口 $port 已被占用${NC}"
        echo "正在尝试释放端口 $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

check_port 5001
check_port 8080

# 启动后端
echo -e "${GREEN}📦 启动后端服务...${NC}"
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖是否安装
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}📥 安装后端依赖...${NC}"
    pip install -r requirements.txt > /dev/null 2>&1
    touch venv/.installed
fi

# 检查数据库目录是否存在
if [ ! -d "instance" ]; then
    mkdir -p instance
fi

# 确保instance目录存在且有正确权限
if [ ! -d "instance" ]; then
    mkdir -p instance
fi
chmod 755 instance 2>/dev/null || true

# 检查数据库是否初始化
if [ ! -f "instance/bs_system.db" ]; then
    echo -e "${YELLOW}🗄️  初始化数据库...${NC}"
    # 先测试数据库路径配置
    echo -e "${YELLOW}检查数据库路径配置...${NC}"
    python3 << 'PYEOF'
import os
import sys
sys.path.insert(0, os.getcwd())
from app import create_app

app = create_app()
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
instance_path = app.instance_path

print(f"Instance路径: {instance_path}")
print(f"数据库URI: {db_uri}")

# 解析数据库文件路径
if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
    print(f"数据库文件路径: {db_path}")
    print(f"目录是否存在: {os.path.exists(os.path.dirname(db_path))}")
    print(f"目录可写: {os.access(os.path.dirname(db_path), os.W_OK) if os.path.exists(os.path.dirname(db_path)) else 'N/A'}")
PYEOF
    
    if ! python init_database.py; then
        echo -e "${RED}❌ 数据库初始化失败${NC}"
        echo -e "${YELLOW}检查错误信息:${NC}"
        python init_database.py 2>&1 | tail -30
        echo ""
        echo -e "${YELLOW}尝试手动修复:${NC}"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  rm -f instance/bs_system.db"
        echo "  python init_database.py"
        exit 1
    fi
    echo -e "${GREEN}✅ 数据库初始化完成${NC}"
fi

# 启动后端（后台运行）
# run.py会自动设置DATABASE_URL环境变量，使用绝对路径
echo -e "${GREEN}🚀 启动后端服务器 (端口 5001)...${NC}"
python run.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# 等待后端启动（最多等待15秒）
echo -e "${YELLOW}⏳ 等待后端启动...${NC}"
BACKEND_HEALTHY=false

# 检查curl是否可用
if command -v curl &> /dev/null; then
    for i in {1..15}; do
        # 检查HTTP状态码和响应内容
        HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" http://localhost:5001/api/health 2>/dev/null || echo "000")
        
        if [ "$HTTP_CODE" = "200" ]; then
            # 检查响应内容是否包含healthy
            # 优先检查checks.database字段（更准确），也检查status字段
            # JSON格式化后可能有空格，使用更宽松的匹配（支持带空格和不带空格）
            if grep -qE '"database"\s*:\s*"healthy"' /tmp/health_response.json 2>/dev/null || \
               grep -qE '"status"\s*:\s*"healthy"' /tmp/health_response.json 2>/dev/null || \
               grep -q '"database":"healthy"' /tmp/health_response.json 2>/dev/null || \
               grep -q '"status":"healthy"' /tmp/health_response.json 2>/dev/null; then
                echo -e "${GREEN}✅ 后端启动成功 (PID: $BACKEND_PID)${NC}"
                BACKEND_HEALTHY=true
                break
            else
                # 如果返回200但状态不是healthy，显示详细信息
                echo -e "${YELLOW}⚠️  后端已启动但健康检查未通过，查看详情...${NC}"
                cat /tmp/health_response.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -10 || cat /tmp/health_response.json 2>/dev/null | head -5
            fi
        elif [ "$HTTP_CODE" != "000" ] && [ "$HTTP_CODE" != "" ]; then
            # 如果返回了HTTP状态码但不是200，说明服务已启动但有问题
            echo -e "${YELLOW}⚠️  后端已启动但返回状态码: $HTTP_CODE${NC}"
            if [ -f /tmp/health_response.json ]; then
                cat /tmp/health_response.json 2>/dev/null
            fi
        fi
        
        if [ $i -eq 15 ]; then
            echo -e "${RED}❌ 后端启动超时或健康检查失败${NC}"
            echo -e "${YELLOW}检查后端日志:${NC}"
            tail -n 20 ../backend.log
            echo ""
            echo -e "${YELLOW}尝试手动访问: curl http://localhost:5001/api/health${NC}"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        
        sleep 1
    done
else
    # 如果没有curl，使用简单的端口检查
    echo -e "${YELLOW}⚠️  未找到curl，使用端口检查...${NC}"
    for i in {1..15}; do
        if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端端口已监听 (PID: $BACKEND_PID)${NC}"
            echo -e "${YELLOW}💡 建议安装curl以进行完整的健康检查${NC}"
            BACKEND_HEALTHY=true
            break
        fi
        if [ $i -eq 15 ]; then
            echo -e "${RED}❌ 后端启动超时${NC}"
            echo -e "${YELLOW}检查后端日志:${NC}"
            tail -n 20 ../backend.log
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
fi

# 如果健康检查失败，提供诊断信息
if [ "$BACKEND_HEALTHY" = false ]; then
    echo ""
    echo -e "${RED}════════════════════════════════════════${NC}"
    echo -e "${RED}❌ 后端健康检查失败${NC}"
    echo -e "${RED}════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}可能的原因和解决方法:${NC}"
    echo ""
    echo "1. 数据库连接失败"
    echo "   检查数据库文件: ls -la backend/instance/bs_system.db"
    echo "   重新初始化: cd backend && source venv/bin/activate && python init_database.py"
    echo ""
    echo "2. 依赖包缺失"
    echo "   重新安装: cd backend && source venv/bin/activate && pip install -r requirements.txt"
    echo ""
    echo "3. 端口被占用"
    echo "   检查端口: lsof -i :5001"
    echo ""
    echo -e "${YELLOW}查看详细日志:${NC}"
    echo "   tail -f backend.log"
    echo ""
    echo -e "${YELLOW}运行诊断脚本:${NC}"
    echo "   ./check-health.sh"
    echo ""
    echo -e "${YELLOW}手动检查健康状态:${NC}"
    echo "   curl http://localhost:5001/api/health"
    echo ""
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

cd ..

# 启动前端
echo ""
echo -e "${GREEN}📦 启动前端服务...${NC}"
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📥 安装前端依赖（这可能需要几分钟）...${NC}"
    npm install
fi

# 启动前端（后台运行）
echo -e "${GREEN}🚀 启动前端开发服务器 (端口 8080)...${NC}"
npm run serve > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

# 等待前端启动
sleep 5

# 检查前端是否启动成功
if ! curl -s http://localhost:8080 > /dev/null; then
    echo -e "${YELLOW}⚠️  前端可能还在启动中，请稍候...${NC}"
    sleep 5
fi

cd ..

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 系统启动成功！${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "📱 访问地址:"
echo "   前端: http://localhost:8080"
echo "   后端API: http://localhost:5001/api/health"
echo ""
echo "👤 默认账户:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📋 日志文件:"
echo "   后端日志: backend.log"
echo "   前端日志: frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: ./stop-local.sh"
echo ""
echo "📊 查看实时日志:"
echo "   后端: tail -f backend.log"
echo "   前端: tail -f frontend.log"
echo ""
echo -e "${YELLOW}💡 提示: 如果遇到问题，请查看故障排查章节${NC}"
echo ""
echo -e "${YELLOW}🔍 验证后端健康状态:${NC}"
echo "   ./check-health.sh"
echo "   或: curl http://localhost:5001/api/health"
echo ""
