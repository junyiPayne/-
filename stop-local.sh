#!/bin/bash

# 学生健康管理系统 - 停止本地开发模式脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🛑 停止本地开发服务..."
echo ""

# 停止后端
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}停止后端服务 (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        rm backend.pid
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}后端服务未运行${NC}"
        rm backend.pid
    fi
else
    echo -e "${YELLOW}未找到后端PID文件${NC}"
    # 尝试通过端口查找并杀死进程
    if lsof -ti:5001 > /dev/null 2>&1; then
        echo -e "${YELLOW}发现端口5001被占用，正在释放...${NC}"
        lsof -ti:5001 | xargs kill -9 2>/dev/null || true
    fi
fi

# 停止前端
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}停止前端服务 (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        rm frontend.pid
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}前端服务未运行${NC}"
        rm frontend.pid
    fi
else
    echo -e "${YELLOW}未找到前端PID文件${NC}"
    # 尝试通过端口查找并杀死进程
    if lsof -ti:8080 > /dev/null 2>&1; then
        echo -e "${YELLOW}发现端口8080被占用，正在释放...${NC}"
        lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    fi
fi

echo ""
echo -e "${GREEN}✅ 所有服务已停止${NC}"
