#!/bin/bash

# 学生健康管理系统 - Docker开发模式一键启动脚本

set -e  # 遇到错误立即退出

echo "🐳 启动Docker开发模式..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 参数解析：默认不重建，需要时手动传 --rebuild
REBUILD=false
for arg in "$@"; do
    case "$arg" in
        --rebuild|--build)
            REBUILD=true
            ;;
        -h|--help)
            echo "用法: ./start-docker.sh [--rebuild]"
            echo ""
            echo "默认行为：只启动容器（不重建镜像）"
            echo "  --rebuild / --build  : 先构建镜像再启动（等价于 docker-compose up -d --build）"
            exit 0
            ;;
    esac
done

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Docker，请先安装 Docker${NC}"
    echo "   安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Docker Compose，请先安装 Docker Compose${NC}"
    echo "   安装指南: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误: Docker 服务未运行，请先启动 Docker${NC}"
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

check_port 80
check_port 5001
check_port 3306

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件，使用默认配置${NC}"
    echo "如需配置AI功能，请创建 .env 文件并添加:"
    echo "  DEEPSEEK_API_KEY=your-api-key"
    echo "  AI_PROVIDER=deepseek"
fi

# 停止已存在的容器
echo -e "${YELLOW}🛑 停止已存在的容器...${NC}"
docker-compose down 2>/dev/null || true

# 启动服务（默认不重建镜像）
if [ "$REBUILD" = true ]; then
    echo -e "${GREEN}🔨 构建并启动Docker容器（--rebuild）...${NC}"
    docker-compose up -d --build
else
    echo -e "${GREEN}🚀 启动Docker容器（默认不重建）...${NC}"
    docker-compose up -d
fi

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动（约30秒）...${NC}"
sleep 10

# 检查后端健康状态
echo -e "${YELLOW}🔍 检查后端服务...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务正常${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 后端服务启动超时，请查看日志: docker-compose logs backend${NC}"
        exit 1
    fi
    sleep 1
done

# 检查前端（Nginx）
echo -e "${YELLOW}🔍 检查前端服务...${NC}"
for i in {1..10}; do
    if curl -s http://localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务正常${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⚠️  前端服务可能还在启动中${NC}"
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Docker服务启动成功！${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "📱 访问地址:"
echo "   前端: http://localhost"
echo "   后端API: http://localhost:5001/api/health"
echo ""
echo "👤 默认账户:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📋 常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   查看后端日志: docker-compose logs -f backend"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
echo -e "${YELLOW}💡 提示: 如果前端代码有更新，需要重新构建:${NC}"
echo "   cd frontend && npm run build && cd .. && docker-compose restart nginx"
echo ""
