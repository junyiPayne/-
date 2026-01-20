#!/bin/bash
# 不设置 set -e，允许脚本在非关键错误时继续执行
# set -e
echo "=========================================="
echo "运动健康系统 - 容器启动"
echo "=========================================="

# 首先测试代码导入，避免在等待数据库时才发现导入错误
echo "🔍 测试代码导入..."
IMPORT_TEST=$(python -c "
import sys
try:
    print('测试导入 app.models.user_settings...')
    from app.models.user_settings import UserSettings
    print('✅ UserSettings 模型导入成功')
    
    print('测试导入 app.routes.settings...')
    from app.routes.settings import bp
    print('✅ settings 路由导入成功')
    
    print('测试导入 app...')
    from app import create_app
    print('✅ create_app 导入成功')
    
    sys.exit(0)
except Exception as e:
    print(f'❌ 导入失败: {type(e).__name__}: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
" 2>&1)

IMPORT_EXIT=$?
if [ $IMPORT_EXIT -ne 0 ]; then
    echo "❌ 代码导入失败，无法启动服务"
    echo ""
    echo "错误详情:"
    echo "$IMPORT_TEST"
    echo ""
    echo "请检查:"
    echo "1. UserSettings 模型文件是否存在: backend/app/models/user_settings.py"
    echo "2. settings 路由文件是否存在: backend/app/routes/settings.py"
    echo "3. 模型导入是否正确: backend/app/models/__init__.py"
    exit 1
fi

echo "✅ 代码导入测试通过"
echo ""

echo "📦 等待 MySQL 数据库就绪（最多 90 秒）..."
echo "   数据库配置:"
echo "   DB_HOST=${DB_HOST:-未设置}"
echo "   DB_PORT=${DB_PORT:-3306}"
echo "   DB_USER=${DB_USER:-未设置}"
echo "   DB_NAME=${DB_NAME:-未设置}"
DB_READY=false
for i in {1..90}; do
    # 尝试连接 MySQL（捕获所有错误，包括导入错误）
    ERROR_OUTPUT=$(python -c "
import sys
import os
try:
    print(f'环境变量检查: DB_HOST={os.environ.get(\"DB_HOST\", \"未设置\")}, DB_TYPE={os.environ.get(\"DB_TYPE\", \"未设置\")}')
    # 先测试导入，避免在 create_app 时出错
    try:
        from app.models.user_settings import UserSettings
        print('✅ UserSettings 模型导入成功')
    except Exception as import_err:
        print(f'❌ UserSettings 模型导入失败: {import_err}', file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    from app import create_app, db
    from sqlalchemy import text
    app = create_app()
    print(f'数据库URI: {app.config.get(\"SQLALCHEMY_DATABASE_URI\", \"未设置\")[:50]}...')
    with app.app_context():
        db.session.execute(text('SELECT 1'))
        print('✅ 数据库连接测试成功')
except Exception as e:
    print(f'❌ 错误: {type(e).__name__}: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
" 2>&1)
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ MySQL 数据库已就绪 (耗时 ${i} 秒)"
        DB_READY=true
        break
    fi
    # 每 5 秒显示一次进度和错误信息（更频繁地显示）
    if [ $((i % 5)) -eq 0 ]; then
        echo "   等待中... ($i/90 秒)"
        # 显示错误信息（显示更多行以便诊断）
        echo "$ERROR_OUTPUT" | tail -10 | sed 's/^/   /'
    fi
    sleep 1
done
if [ "$DB_READY" = false ]; then
    echo "⚠️  MySQL 数据库连接超时（90 秒）"
    echo ""
    echo "诊断信息:"
    echo "=========="
    # 显示环境变量
    echo "环境变量:"
    echo "  DB_TYPE=${DB_TYPE:-未设置}"
    echo "  DB_HOST=${DB_HOST:-未设置}"
    echo "  DB_PORT=${DB_PORT:-未设置}"
    echo "  DB_USER=${DB_USER:-未设置}"
    echo "  DB_NAME=${DB_NAME:-未设置}"
    # 显示最后一次完整的错误信息
    python -c "
import os
print(f'环境变量: DB_HOST={os.environ.get(\"DB_HOST\")}, DB_TYPE={os.environ.get(\"DB_TYPE\")}')
from app import create_app, db
from sqlalchemy import text
app = create_app()
print(f'数据库URI: {app.config.get(\"SQLALCHEMY_DATABASE_URI\", \"未设置\")}')
try:
    db.session.execute(text('SELECT 1'))
    print('连接测试成功')
except Exception as e:
    print(f'连接测试失败: {e}')
" 2>&1 || true
    echo ""
    echo "⚠️  继续尝试初始化数据库（可能会失败）..."
    echo "   如果初始化失败，请检查:"
    echo "   1. MySQL 容器是否正常运行: docker ps | grep bs-system-db"
    echo "   2. MySQL 日志: docker logs bs-system-db"
    echo "   3. 数据库连接配置（DB_HOST, DB_USER, DB_PASSWORD, DB_NAME）"
    # 不退出，继续尝试初始化
fi
echo "📦 检查并初始化数据库..."
echo "   策略: 优先使用已有数据库，如果不存在则创建新数据库"
echo "   将自动创建所有必需的表（包括 user_settings 等新表）"

# 运行数据库初始化，捕获输出和错误
INIT_OUTPUT=$(python init_database.py 2>&1)
INIT_EXIT_CODE=$?

# 显示初始化输出
echo "$INIT_OUTPUT"

if [ $INIT_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ 数据库初始化失败（退出码: $INIT_EXIT_CODE）"
    echo ""
    echo "详细错误信息:"
    echo "$INIT_OUTPUT" | tail -50
    echo ""
    echo "⚠️  尝试验证数据库连接..."
    # 再次尝试连接数据库，确认是否是临时错误
    python -c "
from app import create_app, db
from sqlalchemy import text
app = create_app()
try:
    with app.app_context():
        db.session.execute(text('SELECT 1'))
        print('✅ 数据库连接正常')
        # 检查关键表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'📊 当前数据库表: {len(tables)} 个')
        required = ['users', 'roles', 'system_settings', 'user_settings']
        missing = [t for t in required if t not in tables]
        if missing:
            print(f'⚠️  缺少表: {missing}')
        else:
            print('✅ 所有关键表都存在')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
" 2>&1
    
    DB_CHECK_EXIT=$?
    if [ $DB_CHECK_EXIT -ne 0 ]; then
        echo ""
        echo "❌ 数据库连接验证失败，无法启动服务"
        echo "请检查:"
        echo "1. MySQL 容器是否正常运行: docker ps | grep bs-system-db"
        echo "2. MySQL 日志: docker logs bs-system-db"
        echo "3. 数据库连接配置（DB_HOST, DB_USER, DB_PASSWORD, DB_NAME）"
        exit 1
    else
        echo ""
        echo "⚠️  数据库连接正常，但初始化过程有错误"
        echo "   继续启动服务（数据库可能已经部分初始化）"
    fi
else
    # 验证初始化是否成功
    echo ""
    echo "🔍 验证数据库初始化结果..."
    python -c "
from app import create_app, db
from sqlalchemy import inspect
app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    required = ['users', 'roles', 'system_settings', 'user_settings']
    missing = [t for t in required if t not in tables]
    if missing:
        print(f'⚠️  警告: 缺少关键表: {missing}')
        print('   尝试创建缺失的表...')
        db.create_all()
        print('✅ 表创建完成')
    else:
        print('✅ 所有关键表已存在')
" 2>&1
fi

echo ""
echo "✅ 数据库初始化检查完成"
echo "🚀 启动 Gunicorn 服务器..."
exec "$@"
