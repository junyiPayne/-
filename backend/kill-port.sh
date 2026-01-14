#!/bin/bash
# 快速释放5001端口的脚本

PORT=5001

echo "正在查找占用端口 $PORT 的进程..."

PIDS=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ 端口 $PORT 未被占用"
    exit 0
fi

echo "找到以下进程占用端口 $PORT:"
for PID in $PIDS; do
    echo "  - PID: $PID"
done

echo ""
read -p "是否终止这些进程? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null && echo "✅ 已终止进程 $PID" || echo "❌ 无法终止进程 $PID"
    done
    
    sleep 1
    
    # 再次检查
    REMAINING=$(lsof -ti:$PORT 2>/dev/null)
    if [ -z "$REMAINING" ]; then
        echo "✅ 端口 $PORT 已释放"
    else
        echo "⚠️  仍有进程占用端口: $REMAINING"
    fi
else
    echo "已取消操作"
fi
