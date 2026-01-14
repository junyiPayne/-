#!/bin/bash

# 数据库恢复脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔄 数据库恢复工具..."
echo ""

cd backend

# 检查备份文件
BACKUP_FILES=$(ls -t backups/bs_system_backup_*.db 2>/dev/null | head -1)

if [ -z "$BACKUP_FILES" ]; then
    echo -e "${RED}❌ 未找到备份文件${NC}"
    exit 1
fi

echo -e "${YELLOW}找到备份文件:${NC}"
ls -lh backups/bs_system_backup_*.db
echo ""

# 使用最新的备份
LATEST_BACKUP=$(ls -t backups/bs_system_backup_*.db | head -1)
echo -e "${YELLOW}使用最新备份: ${LATEST_BACKUP}${NC}"
echo ""

# 备份当前数据库（如果存在）
if [ -f "instance/bs_system.db" ]; then
    CURRENT_BACKUP="instance/bs_system.db.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}备份当前数据库到: ${CURRENT_BACKUP}${NC}"
    cp instance/bs_system.db "$CURRENT_BACKUP"
fi

# 恢复备份
echo -e "${YELLOW}正在恢复数据库...${NC}"
cp "$LATEST_BACKUP" instance/bs_system.db

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库恢复成功！${NC}"
    echo ""
    echo "恢复的数据库文件: instance/bs_system.db"
    echo "备份来源: $LATEST_BACKUP"
    echo ""
    echo "现在可以重新启动服务:"
    echo "  cd .."
    echo "  ./start-local.sh"
else
    echo -e "${RED}❌ 数据库恢复失败${NC}"
    exit 1
fi
