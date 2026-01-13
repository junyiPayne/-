#!/bin/bash
# BS系统 - Docker 一键测试部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📋 $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 标题
clear
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║         BS系统 - Docker 一键测试部署                  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查 Docker
print_step "检查 Docker 环境"
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装，请先安装 Docker Desktop"
    exit 1
fi
print_success "Docker 已安装: $(docker --version)"

if ! docker ps &> /dev/null; then
    print_error "Docker daemon 未运行，请启动 Docker Desktop"
    exit 1
fi
print_success "Docker daemon 正在运行"

# 检查 docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "docker-compose 未安装"
    exit 1
fi
print_success "docker-compose 可用"

# 步骤 1: 清理旧的 dist 目录
print_step "步骤 1: 清理前端构建目录"
if [ -d "frontend/dist" ]; then
    print_info "删除旧的 dist 目录..."
    rm -rf frontend/dist 2>/dev/null || {
        print_warning "无法删除 dist 目录，尝试使用 sudo..."
        sudo rm -rf frontend/dist 2>/dev/null || {
            print_warning "请手动删除 frontend/dist 目录后重试"
            exit 1
        }
    }
    print_success "旧的 dist 目录已删除"
else
    print_info "dist 目录不存在，跳过清理"
fi

# 步骤 2: 构建前端
print_step "步骤 2: 构建前端"
cd frontend

if [ ! -d "node_modules" ]; then
    print_info "安装前端依赖..."
    npm install
    print_success "依赖安装完成"
else
    print_info "依赖已存在，跳过安装"
fi

print_info "开始构建前端（这可能需要几分钟）..."
if npm run build; then
    print_success "前端构建完成"
else
    print_error "前端构建失败"
    cd ..
    exit 1
fi

cd ..
print_success "前端准备就绪"

# 步骤 3: 停止旧容器
print_step "步骤 3: 停止旧容器（如果存在）"
docker-compose -f docker-compose.test.yml down 2>/dev/null || true
print_success "旧容器已清理"

# 步骤 4: 构建并启动 Docker 服务
print_step "步骤 4: 构建并启动 Docker 服务"
print_info "这可能需要 5-10 分钟（首次构建）..."
print_info "正在构建镜像并启动容器..."

if docker-compose -f docker-compose.test.yml up --build -d; then
    print_success "Docker 服务启动中..."
else
    print_error "Docker 服务启动失败"
    exit 1
fi

# 步骤 5: 等待服务就绪
print_step "步骤 5: 等待服务就绪"
print_info "等待后端服务启动（约 30-60 秒）..."

for i in {1..30}; do
    if docker exec bs-system-backend-test python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/api/health')" &>/dev/null 2>&1; then
        print_success "后端服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "等待超时，但服务可能仍在启动中..."
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# 步骤 6: 检查服务状态
print_step "步骤 6: 检查服务状态"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "bs-system|NAMES" || true
echo ""

# 步骤 7: 显示访问信息
print_step "部署完成！"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌐 访问地址:${NC}"
echo -e "   ${BLUE}前端页面:${NC}    http://localhost:80"
echo -e "   ${BLUE}后端 API:${NC}    http://localhost:5001/api"
echo -e "   ${BLUE}健康检查:${NC}    http://localhost:5001/api/health"
echo ""
echo -e "${GREEN}👤 默认账户:${NC}"
echo -e "   ${BLUE}用户名:${NC}     admin"
echo -e "   ${BLUE}密码:${NC}       admin123"
echo ""
echo -e "${GREEN}📝 常用命令:${NC}"
echo -e "   ${BLUE}查看后端日志:${NC}  docker logs -f bs-system-backend-test"
echo -e "   ${BLUE}查看 Nginx 日志:${NC} docker logs -f bs-system-nginx-test"
echo -e "   ${BLUE}停止服务:${NC}      docker-compose -f docker-compose.test.yml down"
echo -e "   ${BLUE}重启服务:${NC}      docker-compose -f docker-compose.test.yml restart"
echo -e "   ${BLUE}查看容器状态:${NC}  docker ps | grep bs-system"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 测试健康检查
print_info "测试健康检查接口..."
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    print_success "健康检查通过！"
else
    print_warning "健康检查未响应，服务可能仍在启动中，请稍后访问"
fi

echo ""
print_success "部署脚本执行完成！"
print_info "如果遇到问题，请查看日志: docker logs bs-system-backend-test"
