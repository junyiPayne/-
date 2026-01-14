#!/bin/bash

# 健康检查诊断脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 后端健康检查诊断..."
echo ""

# 检查后端是否运行
if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ 后端服务未运行（端口5001未监听）${NC}"
    echo ""
    echo "启动后端:"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  python run.py"
    exit 1
fi

echo -e "${GREEN}✅ 后端服务正在运行${NC}"
echo ""

# 检查健康接口
if command -v curl &> /dev/null; then
    echo "📡 检查健康接口..."
    RESPONSE=$(curl -s http://localhost:5001/api/health)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/health)
    
    echo "HTTP状态码: $HTTP_CODE"
    echo ""
    echo "响应内容:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    
    if [ "$HTTP_CODE" = "200" ]; then
        if echo "$RESPONSE" | grep -q '"status":"healthy"'; then
            echo -e "${GREEN}✅ 后端健康检查通过${NC}"
        else
            echo -e "${YELLOW}⚠️  后端返回200但状态不是healthy${NC}"
            echo ""
            echo "可能的问题:"
            echo "  1. 数据库连接失败"
            echo "  2. 数据库文件权限问题"
            echo ""
            echo "检查数据库:"
            echo "  ls -la backend/instance/bs_system.db"
            echo "  cd backend && python -c 'from app import create_app, db; app = create_app(); app.app_context().push(); db.session.execute(\"SELECT 1\")'"
        fi
    elif [ "$HTTP_CODE" = "503" ]; then
        echo -e "${RED}❌ 后端返回503（服务不可用）${NC}"
        echo ""
        echo "可能的原因:"
        echo "  1. 数据库连接失败"
        echo "  2. 数据库文件不存在或损坏"
        echo ""
        echo "解决方案:"
        echo "  1. 检查数据库文件: ls -la backend/instance/bs_system.db"
        echo "  2. 重新初始化数据库: cd backend && python init_database.py"
        echo "  3. 查看后端日志: tail -f backend.log"
    else
        echo -e "${RED}❌ 后端返回异常状态码: $HTTP_CODE${NC}"
        echo ""
        echo "查看后端日志: tail -f backend.log"
    fi
else
    echo -e "${YELLOW}⚠️  未找到curl，无法检查健康接口${NC}"
    echo "请安装curl或手动访问: http://localhost:5001/api/health"
fi

echo ""
echo "📋 查看后端日志:"
echo "  tail -f backend.log"
echo ""
echo "🔄 重启后端:"
echo "  ./stop-local.sh"
echo "  ./start-local.sh"
