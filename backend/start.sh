#!/bin/bash
# BS系统 - 生产环境启动脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BS系统 - 生产环境启动${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否在正确的目录
if [ ! -f "run.py" ]; then
    echo -e "${RED}错误: 请在 backend 目录下运行此脚本${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}警告: 未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${GREEN}激活虚拟环境...${NC}"
source venv/bin/activate

# 检查依赖
if [ ! -f "venv/bin/gunicorn" ]; then
    echo -e "${YELLOW}安装依赖...${NC}"
    pip install -r requirements.txt
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到 .env 文件${NC}"
    echo -e "${YELLOW}请从 .env.example 复制并配置 .env 文件${NC}"
    if [ -f ".env.example" ]; then
        read -p "是否从 .env.example 创建 .env 文件? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo -e "${GREEN}已创建 .env 文件，请编辑配置后重新运行${NC}"
            exit 0
        fi
    fi
fi

# 检查日志目录
if [ ! -d "logs" ]; then
    echo -e "${GREEN}创建日志目录...${NC}"
    mkdir -p logs
fi

# 设置环境变量
export FLASK_ENV=production

# 启动 Gunicorn
echo -e "${GREEN}启动 Gunicorn 服务器...${NC}"
echo -e "${GREEN}服务器将在 http://0.0.0.0:5001 启动${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo ""

gunicorn -c gunicorn.conf.py "app:create_app()"
