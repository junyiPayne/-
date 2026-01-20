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
echo -e "${YELLOW}🔍 检查 Docker 服务状态...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误: Docker 服务未运行${NC}"
    echo ""
    echo -e "${YELLOW}解决方法:${NC}"
    echo "1. 打开 Docker Desktop 应用程序"
    echo "2. 等待 Docker Desktop 完全启动（状态栏显示 'Docker Desktop is running'）"
    echo "3. 如果 Docker Desktop 无法启动，请尝试："
    echo "   - 重启 Docker Desktop"
    echo "   - 检查系统权限设置（系统偏好设置 > 安全性与隐私 > 完全磁盘访问权限）"
    echo "   - 查看 Docker Desktop 日志"
    echo ""
    echo -e "${YELLOW}验证 Docker 是否运行:${NC}"
    echo "   docker ps"
    echo ""
    exit 1
fi

# 验证 Docker 是否真的可用（不仅仅是命令存在）
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误: Docker 命令无法连接到 Docker daemon${NC}"
    echo ""
    echo -e "${YELLOW}可能的原因:${NC}"
    echo "1. Docker Desktop 未完全启动"
    echo "2. Docker daemon 未运行"
    echo "3. 权限问题"
    echo ""
    echo -e "${YELLOW}请先启动 Docker Desktop，然后重试${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"

# 如果重建镜像，提示可能的网络问题
if [ "$REBUILD" = true ]; then
    echo -e "${YELLOW}💡 提示: 如果构建时遇到网络超时，可以配置 Docker 镜像加速器${NC}"
    echo "   编辑 ~/.docker/daemon.json，添加以下内容："
    echo '   "registry-mirrors": ['
    echo '     "https://docker.mirrors.ustc.edu.cn",'
    echo '     "https://hub-mirror.c.163.com"'
    echo '   ]'
    echo "   然后重启 Docker Desktop"
    echo ""
fi
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
    echo ""
    echo -e "${YELLOW}💡 网络部署提示:${NC}"
    echo "   如果需要在网络上部署（让其他学校学生访问），请创建 .env 文件："
    echo "   1. 复制配置示例: cp 部署配置示例.env .env"
    echo "   2. 编辑 .env 文件，配置 CORS_ORIGINS（允许访问的域名）"
    echo "   3. 修改数据库密码和安全密钥"
    echo ""
    echo "   详细说明请查看: 网络部署指南.md"
    echo ""
    echo "如需配置AI功能，请在 .env 文件中添加:"
    echo "  DEEPSEEK_API_KEY=your-api-key"
    echo "  AI_PROVIDER=deepseek"
fi

# 停止已存在的容器
echo -e "${YELLOW}🛑 停止已存在的容器...${NC}"
docker-compose down 2>/dev/null || true

# 如果重建，清理构建缓存（避免缓存问题）
if [ "$REBUILD" = true ]; then
    echo -e "${YELLOW}🧹 清理构建缓存...${NC}"
    docker builder prune -f > /dev/null 2>&1 || true
    echo -e "${GREEN}🔨 构建并启动Docker容器（--rebuild）...${NC}"
    docker-compose build --no-cache
    docker-compose up -d
else
    echo -e "${GREEN}🚀 启动Docker容器（默认不重建）...${NC}"
    docker-compose up -d
fi

# 等待 MySQL 和后端启动
echo -e "${YELLOW}⏳ 等待 MySQL 数据库就绪（最多 60 秒）...${NC}"
MYSQL_READY=false
for i in {1..60}; do
    # 检查容器是否存在且运行中
    if ! docker ps --format '{{.Names}}' | grep -q '^bs-system-db$'; then
        echo -e "${YELLOW}⚠️  MySQL 容器尚未启动，等待中... ($i/60)${NC}"
        sleep 1
        continue
    fi
    
    # 检查 MySQL 是否就绪
    if docker exec bs-system-db mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo -e "${GREEN}✅ MySQL 数据库已就绪 (耗时 ${i} 秒)${NC}"
        MYSQL_READY=true
        break
    fi
    
    # 每 10 秒显示一次进度
    if [ $((i % 10)) -eq 0 ]; then
        echo -e "${YELLOW}   等待中... ($i/60 秒)${NC}"
    fi
    
    sleep 1
done

if [ "$MYSQL_READY" = false ]; then
    echo -e "${RED}❌ MySQL 启动超时（60 秒）${NC}"
    echo -e "${YELLOW}检查 MySQL 容器状态:${NC}"
    docker ps -a | grep bs-system-db || echo "   MySQL 容器不存在"
    echo ""
    echo -e "${YELLOW}查看 MySQL 日志:${NC}"
    docker-compose logs db | tail -30
    echo ""
    echo -e "${YELLOW}可能的原因:${NC}"
    echo "1. Docker Desktop 未完全启动"
    echo "2. 端口 3306 被占用"
    echo "3. MySQL 容器启动失败"
    echo ""
    echo -e "${YELLOW}尝试手动启动:${NC}"
    echo "   docker-compose up db -d"
    echo "   docker-compose logs -f db"
    exit 1
fi

# 确保 MySQL 用户存在（修复权限问题）
echo -e "${YELLOW}🔧 检查并修复 MySQL 用户权限...${NC}"
DB_USER=${DB_USER:-bs_user}
DB_PASSWORD=${DB_PASSWORD:-password}
DB_NAME=${DB_NAME:-bs_system}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-rootpassword}

# MySQL 8.0 官方镜像会自动创建用户（如果 volume 是新的）
# 但如果 volume 已存在，需要手动修复
# 尝试使用 root 连接（使用环境变量方式，避免密码泄露）

# 首先尝试使用配置的 root 密码
MYSQL_CONNECTED=false
ROOT_PASSWORD_USED=""

# 尝试多种可能的 root 密码
for root_pwd in "$MYSQL_ROOT_PASSWORD" "rootpassword" ""; do
    if [ -z "$root_pwd" ]; then
        # 尝试无密码连接
        if docker exec bs-system-db mysql -u root -e "SELECT 1" >/dev/null 2>&1; then
            MYSQL_CONNECTED=true
            ROOT_PASSWORD_USED=""
            break
        fi
    else
        # 使用环境变量方式传递密码
        if docker exec -e MYSQL_PWD="$root_pwd" bs-system-db mysql -u root -e "SELECT 1" >/dev/null 2>&1; then
            MYSQL_CONNECTED=true
            ROOT_PASSWORD_USED="$root_pwd"
            break
        fi
    fi
done

if [ "$MYSQL_CONNECTED" = false ]; then
    echo -e "${YELLOW}   ⚠️  无法连接到 MySQL root，跳过用户修复${NC}"
    echo -e "${YELLOW}   提示：MySQL 官方镜像应该已自动创建用户 $DB_USER${NC}"
    echo -e "${YELLOW}   如果仍有问题，可以手动修复：${NC}"
    echo -e "${YELLOW}   docker exec -it bs-system-db mysql -u root -p${NC}"
    echo -e "${YELLOW}   然后执行：CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';${NC}"
    echo -e "${YELLOW}   GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%'; FLUSH PRIVILEGES;${NC}"
else
    # 检查用户是否存在
    if [ -n "$ROOT_PASSWORD_USED" ]; then
        USER_CHECK=$(docker exec -e MYSQL_PWD="$ROOT_PASSWORD_USED" bs-system-db mysql -u root -sN -e "SELECT COUNT(*) FROM mysql.user WHERE User='$DB_USER' AND Host='%';" 2>/dev/null || echo "ERROR")
    else
        USER_CHECK=$(docker exec bs-system-db mysql -u root -sN -e "SELECT COUNT(*) FROM mysql.user WHERE User='$DB_USER' AND Host='%';" 2>/dev/null || echo "ERROR")
    fi
    
    if [ "$USER_CHECK" = "0" ] || [ "$USER_CHECK" = "ERROR" ] || [ -z "$USER_CHECK" ]; then
        echo -e "${YELLOW}   ⚠️  用户 $DB_USER 不存在，正在创建...${NC}"
        if [ -n "$ROOT_PASSWORD_USED" ]; then
            docker exec -e MYSQL_PWD="$ROOT_PASSWORD_USED" bs-system-db mysql -u root <<EOF 2>/dev/null
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
EOF
        else
            docker exec bs-system-db mysql -u root <<EOF 2>/dev/null
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
EOF
        fi
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}   ✅ 用户创建成功${NC}"
        else
            echo -e "${YELLOW}   ⚠️  用户创建可能失败，但继续执行${NC}"
        fi
    else
        echo -e "${GREEN}   ✅ 用户已存在，更新权限...${NC}"
        if [ -n "$ROOT_PASSWORD_USED" ]; then
            docker exec -e MYSQL_PWD="$ROOT_PASSWORD_USED" bs-system-db mysql -u root <<EOF 2>/dev/null
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
EOF
        else
            docker exec bs-system-db mysql -u root <<EOF 2>/dev/null
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
EOF
        fi
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}   ✅ 权限更新完成${NC}"
        else
            echo -e "${YELLOW}   ⚠️  权限更新可能失败，但继续执行${NC}"
        fi
    fi
fi

# 等待后端启动（docker-entrypoint.sh 会自动初始化数据库）
echo -e "${YELLOW}⏳ 等待后端服务启动（最多 60 秒）...${NC}"
echo -e "${YELLOW}   提示：后端启动时会自动运行数据库初始化脚本${NC}"
BACKEND_STARTED=false
for i in {1..60}; do
    # 检查后端容器是否在运行
    if ! docker ps --format '{{.Names}}' | grep -q '^bs-system-backend$'; then
        echo -e "${YELLOW}⚠️  后端容器尚未启动，等待中... ($i/60)${NC}"
        sleep 1
        continue
    fi
    
    # 检查后端容器状态
    CONTAINER_STATUS=$(docker ps -a --format '{{.Status}}' --filter "name=bs-system-backend" 2>/dev/null || echo "未找到")
    
    # 如果容器在重启循环中，显示错误
    if echo "$CONTAINER_STATUS" | grep -q "Restarting"; then
        echo -e "${RED}⚠️  后端容器正在重启循环中，可能启动失败${NC}"
        echo -e "${YELLOW}   查看错误日志:${NC}"
        docker logs bs-system-backend 2>&1 | tail -50 | sed 's/^/   /'
        echo ""
        echo -e "${YELLOW}   可能的原因:${NC}"
        echo "   1. 数据库连接失败"
        echo "   2. 代码导入错误"
        echo "   3. 数据库初始化失败"
        echo "   4. Gunicorn 配置错误"
        echo ""
        BACKEND_STARTED=false
        break
    fi
    
    # 检查后端是否已启动（Gunicorn 启动成功，数据库初始化完成）
    BACKEND_LOGS=$(docker logs bs-system-backend 2>&1 | tail -50)
    if echo "$BACKEND_LOGS" | grep -qE "✅ 数据库初始化检查完成|🚀 启动 Gunicorn|Listening at:|Booting worker|运动健康系统已就绪"; then
        echo -e "${GREEN}✅ 后端服务已启动 (耗时 ${i} 秒)${NC}"
        # 检查数据库初始化是否成功
        if echo "$BACKEND_LOGS" | grep -qE "✅ 所有关键表已存在|✅ 数据库表创建完成"; then
            echo -e "${GREEN}✅ 数据库初始化成功${NC}"
        elif echo "$BACKEND_LOGS" | grep -qE "⚠️.*缺少关键表"; then
            echo -e "${YELLOW}⚠️  数据库表可能不完整，但服务已启动${NC}"
        fi
        BACKEND_STARTED=true
        break
    fi
    
    # 检查数据库初始化是否正在进行中
    if echo "$BACKEND_LOGS" | grep -qE "📦 检查并初始化数据库|正在创建新数据库|数据库初始化"; then
        # 数据库初始化正在进行，继续等待
        if [ $((i % 10)) -eq 0 ]; then
            echo -e "${YELLOW}   数据库初始化进行中... ($i/60 秒)${NC}"
        fi
    fi
    
    # 检查是否有错误（容器可能启动失败）
    if echo "$BACKEND_LOGS" | grep -qE "❌.*错误|Error|Exception|Traceback|failed to start"; then
        echo -e "${RED}⚠️  检测到后端启动错误${NC}"
        echo "$BACKEND_LOGS" | grep -E "❌|Error|error|Exception|Traceback|failed" | tail -5 | sed 's/^/   /'
        # 不立即退出，继续等待，可能只是警告
    fi
    
    # 每 5 秒显示一次进度
    if [ $((i % 5)) -eq 0 ]; then
        echo -e "${YELLOW}   等待后端启动... ($i/60 秒)${NC}"
        echo -e "${YELLOW}   容器状态: ${CONTAINER_STATUS}${NC}"
        # 显示最近的日志（如果有）
        RECENT_LOG=$(echo "$BACKEND_LOGS" | tail -3 | grep -v "^$" | head -1)
        if [ -n "$RECENT_LOG" ]; then
            echo -e "${YELLOW}   最新日志: ${RECENT_LOG:0:80}...${NC}"
        fi
    fi
    
    sleep 1
done

if [ "$BACKEND_STARTED" = false ]; then
    echo -e "${RED}❌ 后端服务启动失败或超时${NC}"
    echo -e "${YELLOW}查看完整日志:${NC}"
    docker logs bs-system-backend 2>&1 | tail -100 | sed 's/^/   /'
    echo ""
    echo -e "${YELLOW}可能的原因:${NC}"
    echo "   1. 数据库连接失败"
    echo "   2. 数据库初始化失败（表未创建）"
    echo "   3. 代码导入错误"
    echo "   4. Gunicorn 配置错误"
    echo ""
    echo -e "${YELLOW}手动检查数据库初始化:${NC}"
    echo "   docker exec bs-system-backend python init_database.py"
    echo ""
    echo -e "${YELLOW}手动验证数据库表:${NC}"
    echo "   docker exec bs-system-backend python -c \""
    echo "   from app import create_app, db"
    echo "   from sqlalchemy import inspect"
    echo "   app = create_app()"
    echo "   with app.app_context():"
    echo "       inspector = inspect(db.engine)"
    echo "       tables = inspector.get_table_names()"
    echo "       required = ['users', 'roles', 'system_settings', 'user_settings', 'user_profiles', 'daily_logs']"
    echo "       missing = [t for t in required if t not in tables]"
    echo "       if missing:"
    echo "           print(f'缺少表: {missing}')"
    echo "       else:"
    echo "           print('所有关键表都存在')"
    echo "   \""
fi

# 验证数据库表是否已创建
if [ "$BACKEND_STARTED" = true ]; then
    echo -e "${YELLOW}🔍 验证数据库表是否完整...${NC}"
    DB_TABLES_CHECK=$(docker exec bs-system-backend python -c "
from app import create_app, db
from sqlalchemy import inspect
app = create_app()
try:
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        required = ['users', 'roles', 'system_settings', 'user_settings', 'user_profiles', 'daily_logs']
        missing = [t for t in required if t not in tables]
        if missing:
            print(f'MISSING:{missing}')
        else:
            print('OK')
except Exception as e:
    print(f'ERROR:{str(e)}')
" 2>&1)
    
    if echo "$DB_TABLES_CHECK" | grep -q "^OK$"; then
        echo -e "${GREEN}✅ 所有关键数据库表已存在${NC}"
    elif echo "$DB_TABLES_CHECK" | grep -q "^MISSING:"; then
        MISSING_TABLES=$(echo "$DB_TABLES_CHECK" | grep "^MISSING:" | cut -d: -f2-)
        echo -e "${YELLOW}⚠️  缺少数据库表: ${MISSING_TABLES}${NC}"
        echo -e "${YELLOW}   尝试手动创建缺失的表...${NC}"
        docker exec bs-system-backend python init_database.py 2>&1 | tail -20 | sed 's/^/   /'
    elif echo "$DB_TABLES_CHECK" | grep -q "^ERROR:"; then
        ERROR_MSG=$(echo "$DB_TABLES_CHECK" | grep "^ERROR:" | cut -d: -f2-)
        echo -e "${RED}❌ 验证数据库表时出错: ${ERROR_MSG}${NC}"
    else
        echo -e "${YELLOW}⚠️  无法验证数据库表状态${NC}"
    fi
fi

# 检查后端健康状态
echo -e "${YELLOW}🔍 检查后端服务健康状态（最多 30 秒）...${NC}"
BACKEND_READY=false
for i in {1..30}; do
    # 检查容器是否存在且运行中
    if ! docker ps --format '{{.Names}}' | grep -q '^bs-system-backend$'; then
        echo -e "${YELLOW}⚠️  后端容器尚未启动，等待中... ($i/30)${NC}"
        sleep 1
        continue
    fi
    
    HEALTH_RESPONSE=$(curl -s http://localhost:5001/api/health 2>/dev/null)
    if [ -n "$HEALTH_RESPONSE" ]; then
        if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
            echo -e "${GREEN}✅ 后端服务健康检查通过 (耗时 ${i} 秒)${NC}"
            BACKEND_READY=true
            break
        fi
    fi
    
    # 每 5 秒显示一次进度
    if [ $((i % 5)) -eq 0 ]; then
        echo -e "${YELLOW}   等待后端健康检查... ($i/30 秒)${NC}"
    fi
    
    sleep 1
done

if [ "$BACKEND_READY" = false ]; then
    echo -e "${YELLOW}⚠️  后端健康检查超时，但服务可能仍在运行${NC}"
    echo -e "${YELLOW}检查后端容器状态:${NC}"
    docker ps -a | grep bs-system-backend || echo "   后端容器不存在"
    echo ""
    echo -e "${YELLOW}查看后端日志:${NC}"
    docker-compose logs backend | tail -30
    echo ""
    echo -e "${YELLOW}手动测试:${NC}"
    echo "   curl http://localhost:5001/api/health"
fi

# 检查前端（Nginx）
echo -e "${YELLOW}🔍 检查前端服务（最多 30 秒）...${NC}"
FRONTEND_READY=false
for i in {1..30}; do
    # 检查 Nginx 容器是否存在且运行中
    if ! docker ps --format '{{.Names}}' | grep -q '^bs-system-nginx$'; then
        echo -e "${YELLOW}⚠️  Nginx 容器尚未启动，等待中... ($i/30)${NC}"
        sleep 1
        continue
    fi
    
    # 检查前端文件是否存在
    if docker exec bs-system-nginx ls /usr/share/nginx/html/index.html > /dev/null 2>&1; then
        # 检查 HTTP 响应
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "304" ]; then
            echo -e "${GREEN}✅ 前端服务正常 (耗时 ${i} 秒)${NC}"
            echo -e "${GREEN}   HTTP状态码: ${HTTP_CODE}${NC}"
            FRONTEND_READY=true
            break
        fi
    fi
    
    # 每 5 秒显示一次进度
    if [ $((i % 5)) -eq 0 ]; then
        echo -e "${YELLOW}   等待前端启动... ($i/30 秒)${NC}"
        # 显示 Nginx 容器状态
        NGINX_STATUS=$(docker ps --format '{{.Status}}' --filter "name=bs-system-nginx" 2>/dev/null || echo "未运行")
        echo -e "${YELLOW}   Nginx 状态: ${NGINX_STATUS}${NC}"
    fi
    
    sleep 1
done

if [ "$FRONTEND_READY" = false ]; then
    echo -e "${YELLOW}⚠️  前端服务检查超时或未完全就绪${NC}"
    echo -e "${YELLOW}检查 Nginx 容器状态:${NC}"
    docker ps -a | grep bs-system-nginx || echo "   Nginx 容器不存在"
    echo ""
    echo -e "${YELLOW}查看 Nginx 日志:${NC}"
    docker-compose logs nginx | tail -20
    echo ""
    echo -e "${YELLOW}可能的原因:${NC}"
    echo "1. 前端文件未构建（需要运行: cd frontend && npm run build）"
    echo "2. 端口 80 被占用"
    echo "3. Nginx 配置错误"
    echo ""
    echo -e "${YELLOW}检查前端文件是否存在:${NC}"
    if [ -d "frontend/dist" ] && [ -f "frontend/dist/index.html" ]; then
        echo -e "${GREEN}   ✅ 前端文件存在: frontend/dist/index.html${NC}"
    else
        echo -e "${RED}   ❌ 前端文件不存在，需要构建前端:${NC}"
        echo "      cd frontend && npm run build"
    fi
    echo ""
    echo -e "${YELLOW}尝试手动检查:${NC}"
    echo "   docker-compose logs -f nginx"
    echo "   curl http://localhost"
    echo ""
    echo -e "${YELLOW}⚠️  继续启动流程（前端可能稍后可用）...${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Docker服务启动完成！${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "📊 服务状态报告:"
echo "   ┌─────────────────────────────────────────┐"
echo "   │ 服务名称        │ 状态      │ 访问地址  │"
echo "   ├─────────────────────────────────────────┤"
if [ "$MYSQL_READY" = true ]; then
    echo -e "   │ MySQL 数据库    │ ${GREEN}✅ 正常${NC}    │ localhost:3306 │"
else
    echo -e "   │ MySQL 数据库    │ ${YELLOW}⚠️  未知${NC}    │ localhost:3306 │"
fi
if [ "$BACKEND_STARTED" = true ] && [ "$BACKEND_READY" = true ]; then
    echo -e "   │ 后端服务        │ ${GREEN}✅ 正常${NC}    │ localhost:5001 │"
elif [ "$BACKEND_STARTED" = true ]; then
    echo -e "   │ 后端服务        │ ${YELLOW}⚠️  运行中${NC}  │ localhost:5001 │"
else
    echo -e "   │ 后端服务        │ ${RED}❌ 异常${NC}    │ localhost:5001 │"
fi
if [ "$FRONTEND_READY" = true ]; then
    echo -e "   │ 前端服务 (Nginx)│ ${GREEN}✅ 正常${NC}    │ http://localhost │"
else
    echo -e "   │ 前端服务 (Nginx)│ ${YELLOW}⚠️  检查中${NC}  │ http://localhost │"
fi
echo "   └─────────────────────────────────────────┘"
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
echo "   查看所有日志: docker-compose logs -f"
echo "   查看后端日志: docker-compose logs -f backend"
echo "   查看前端日志: docker-compose logs -f nginx"
echo "   查看数据库日志: docker-compose logs -f db"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
echo "🔧 数据库维护命令:"
echo "   手动初始化数据库: docker exec bs-system-backend python init_database.py"
echo "   验证数据库表: docker exec bs-system-backend python -c \""
echo "     from app import create_app, db"
echo "     from sqlalchemy import inspect"
echo "     app = create_app()"
echo "     with app.app_context():"
echo "         inspector = inspect(db.engine)"
echo "         print('数据库表:', inspector.get_table_names())\""
echo ""
if [ "$FRONTEND_READY" = false ]; then
    echo -e "${YELLOW}⚠️  前端服务状态异常，请检查:${NC}"
    echo "   1. 前端文件是否已构建: ls frontend/dist/index.html"
    echo "   2. 如果文件不存在，运行: cd frontend && npm run build"
    echo "   3. 然后重启 Nginx: docker-compose restart nginx"
    echo ""
fi
echo -e "${YELLOW}💡 提示: 如果前端代码有更新，需要重新构建:${NC}"
echo "   cd frontend && npm run build && cd .. && docker-compose restart nginx"
echo ""
