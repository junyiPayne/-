#!/bin/bash
# BS系统 - 停止脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BS系统 - 停止服务${NC}"
echo -e "${GREEN}========================================${NC}"

# 查找 Gunicorn 进程
PID=$(ps aux | grep '[g]unicorn.*app:create_app' | awk '{print $2}')

if [ -z "$PID" ]; then
    echo -e "${YELLOW}未找到运行中的 Gunicorn 进程${NC}"
    exit 0
fi

echo -e "${GREEN}找到 Gunicorn 进程: $PID${NC}"
echo -e "${YELLOW}正在停止...${NC}"

# 发送 TERM 信号，优雅关闭
kill -TERM $PID

# 等待进程结束
sleep 2

# 检查进程是否还在运行
if ps -p $PID > /dev/null; then
    echo -e "${YELLOW}进程仍在运行，强制终止...${NC}"
    kill -KILL $PID
    sleep 1
fi

echo -e "${GREEN}服务已停止${NC}"
