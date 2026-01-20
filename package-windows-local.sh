#!/bin/bash

# 学生健康管理系统 - Windows 本地部署打包脚本
# 专门用于 Windows 本地部署，不包含 Docker 相关文件

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📦 开始打包 Windows 本地部署文件...${NC}"
echo ""

# 项目名称
PROJECT_NAME="学生健康管理系统"
PACKAGE_NAME="学生健康管理系统_Windows本地部署包"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_FILE="${PACKAGE_NAME}_${TIMESTAMP}.zip"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="${TEMP_DIR}/${PROJECT_NAME}"
mkdir -p "${PACKAGE_DIR}"

echo -e "${YELLOW}📋 复制文件到临时目录...${NC}"

# 1. 后端文件
echo "  ✅ 复制后端源代码..."
mkdir -p "${PACKAGE_DIR}/backend/app"
cp -r backend/app/* "${PACKAGE_DIR}/backend/app/" 2>/dev/null || true
cp backend/config.py "${PACKAGE_DIR}/backend/"
cp backend/run.py "${PACKAGE_DIR}/backend/"
cp backend/wsgi.py "${PACKAGE_DIR}/backend/"
cp backend/init_database.py "${PACKAGE_DIR}/backend/"
cp backend/requirements.txt "${PACKAGE_DIR}/backend/"
cp backend/gunicorn.conf.py "${PACKAGE_DIR}/backend/" 2>/dev/null || true
cp backend/logging.conf "${PACKAGE_DIR}/backend/" 2>/dev/null || true
cp backend/check_api_config.py "${PACKAGE_DIR}/backend/" 2>/dev/null || true

# 创建必要的目录结构
mkdir -p "${PACKAGE_DIR}/backend/instance"
mkdir -p "${PACKAGE_DIR}/backend/logs"
mkdir -p "${PACKAGE_DIR}/backend/app/static/uploads"
mkdir -p "${PACKAGE_DIR}/backend/app/static/avatars"
mkdir -p "${PACKAGE_DIR}/backend/app/static/reports"

# 2. 前端文件
echo "  ✅ 复制前端源代码..."
mkdir -p "${PACKAGE_DIR}/frontend"
cp -r frontend/src "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp -r frontend/public "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/package.json "${PACKAGE_DIR}/frontend/"
cp frontend/package-lock.json "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/vue.config.js "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/.eslintrc.js "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/.prettierrc "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/README.md "${PACKAGE_DIR}/frontend/" 2>/dev/null || true

# 3. 数据库初始化文件
echo "  ✅ 复制数据库初始化文件..."
mkdir -p "${PACKAGE_DIR}/database"
cp database/init.sql "${PACKAGE_DIR}/database/" 2>/dev/null || true

# 4. Windows 启动脚本（重要！）
echo "  ✅ 复制 Windows 启动脚本..."
cp start-local.bat "${PACKAGE_DIR}/"
cp stop-local.bat "${PACKAGE_DIR}/" 2>/dev/null || true
cp start-local.sh "${PACKAGE_DIR}/" 2>/dev/null || true
cp stop-local.sh "${PACKAGE_DIR}/" 2>/dev/null || true

# 5. 配置文件（本地部署需要）
echo "  ✅ 复制配置文件..."
cp env.example "${PACKAGE_DIR}/"
cp .gitignore "${PACKAGE_DIR}/"

# 6. 文档文件
echo "  ✅ 复制文档文件..."
cp README.md "${PACKAGE_DIR}/"
cp 快速启动.md "${PACKAGE_DIR}/"

# 7. 创建 Windows 部署说明文件
echo "  ✅ 创建 Windows 部署说明文件..."
cat > "${PACKAGE_DIR}/Windows本地部署说明.txt" << 'EOF'
学生健康管理系统 - Windows 本地部署说明
==========================================

一、系统要求
-----------
1. Windows 10/11
2. Python 3.9+ 
3. Node.js 18+

二、快速启动（推荐）
------------------
1. 双击运行 start-local.bat

脚本会自动：
  ✅ 检查 Python 和 Node.js 环境
  ✅ 创建虚拟环境
  ✅ 安装依赖
  ✅ 初始化 SQLite 数据库
  ✅ 启动后端服务（端口 5001）
  ✅ 启动前端服务（端口 8080）

三、手动安装步骤（如果一键启动失败）
-----------------------------------

1. 安装 Python
   - 访问：https://www.python.org/downloads/
   - 下载并安装 Python 3.9+
   - ⚠️ 重要：安装时勾选 "Add Python to PATH"

2. 安装 Node.js
   - 访问：https://nodejs.org/
   - 下载并安装 Node.js 18+ LTS 版本

3. 验证安装
   打开命令提示符（CMD）或 PowerShell：
   python --version  # 应显示 Python 3.9.x 或更高
   node --version    # 应显示 v18.x.x 或更高
   npm --version     # 应显示版本号

4. 后端启动
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python init_database.py
   python run.py

5. 前端启动（新开一个命令行窗口）
   cd frontend
   npm install
   npm run serve

四、访问地址
-----------
- 前端：http://localhost:8080
- 后端API：http://localhost:5001/api/health

五、默认账户
-----------
用户名：admin
密码：admin123

⚠️ 首次登录后请立即修改密码！

六、停止服务
-----------
- 双击运行 stop-local.bat
- 或直接关闭命令行窗口

七、常见问题
-----------

1. 提示"未找到 Python"
   - 检查是否安装了 Python
   - 检查是否勾选了 "Add Python to PATH"
   - 重启命令行窗口

2. 提示"未找到 Node.js"
   - 检查是否安装了 Node.js
   - 重启命令行窗口

3. 端口被占用
   - 关闭占用端口的程序
   - 或修改 backend/run.py 和 frontend/vue.config.js 中的端口

4. 依赖安装失败
   - 检查网络连接
   - 尝试使用国内镜像源：
     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

5. npm install 很慢
   - 使用淘宝镜像：
     npm config set registry https://registry.npmmirror.com
     npm install

八、数据库说明
-------------
- 本地部署使用 SQLite 数据库
- 数据库文件位置：backend/instance/bs_system.db
- 数据库会自动创建，无需手动配置
- 数据会持久化保存，重启不会丢失

九、更新代码
-----------
如果需要更新代码：
1. 停止服务（运行 stop-local.bat）
2. 替换代码文件
3. 重新启动（运行 start-local.bat）

十、技术支持
-----------
详细文档请查看：
- README.md - 项目总览
- 快速启动.md - 详细启动指南

==========================================
祝使用愉快！
EOF

echo ""
echo -e "${GREEN}📦 创建压缩包...${NC}"
cd "${TEMP_DIR}"
zip -r "${ZIP_FILE}" "${PROJECT_NAME}" \
    -x "*.DS_Store" \
    -x "*/__pycache__/*" \
    -x "*/node_modules/*" \
    -x "*/venv/*" \
    -x "*/frontend/dist/*" \
    -x "*/backend/instance/*.db" \
    -x "*.log" \
    -x "*.pid" \
    -x "*/backups/*" \
    > /dev/null 2>&1

# 移动到项目根目录
mv "${ZIP_FILE}" "${OLDPWD}/"

# 清理临时目录
rm -rf "${TEMP_DIR}"

echo ""
echo -e "${GREEN}✅ 打包完成！${NC}"
echo ""
echo "📦 压缩包文件：${ZIP_FILE}"
echo "📁 文件大小：$(du -h "${OLDPWD}/${ZIP_FILE}" | cut -f1)"
echo ""
echo "📋 打包内容："
echo "  ✅ 后端源代码（backend/app/）"
echo "  ✅ 前端源代码（frontend/src/）"
echo "  ✅ Windows 启动脚本（start-local.bat, stop-local.bat）"
echo "  ✅ 依赖文件（requirements.txt, package.json）"
echo "  ✅ 数据库初始化脚本（init_database.py）"
echo "  ✅ 配置文件（env.example）"
echo "  ✅ 文档文件（README.md, 快速启动.md）"
echo "  ✅ Windows 部署说明（Windows本地部署说明.txt）"
echo ""
echo "❌ 已排除："
echo "  ❌ Docker 相关文件（Dockerfile, docker-compose.yml）"
echo "  ❌ Linux 脚本（start-docker.sh, docker-entrypoint.sh）"
echo "  ❌ node_modules（需要 npm install）"
echo "  ❌ venv（需要 python -m venv）"
echo ""
echo "🚀 Windows 使用方法："
echo "  1. 解压压缩包到任意目录"
echo "  2. 双击 start-local.bat 启动"
echo "  3. 访问 http://localhost:8080"
echo ""
