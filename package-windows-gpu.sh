#!/bin/bash

# 学生健康管理系统 - Windows 本地 GPU 部署打包脚本
# 用于打包本地 GPU 部署所需的文件，方便在 Windows 电脑上部署

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📦 开始打包 Windows 本地 GPU 部署文件...${NC}"
echo ""

# 项目名称
PROJECT_NAME="学生健康管理系统"
PACKAGE_NAME="学生健康管理系统_Windows本地GPU部署包"
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
cp backend/run_gpu.py "${PACKAGE_DIR}/backend/"  # GPU 版本启动脚本
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
cp frontend/vue.config.gpu.js "${PACKAGE_DIR}/frontend/"  # GPU 版本配置
cp frontend/.eslintrc.js "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/.prettierrc "${PACKAGE_DIR}/frontend/" 2>/dev/null || true
cp frontend/README.md "${PACKAGE_DIR}/frontend/" 2>/dev/null || true

# 3. 数据库初始化文件
echo "  ✅ 复制数据库初始化文件..."
mkdir -p "${PACKAGE_DIR}/database"
cp database/init.sql "${PACKAGE_DIR}/database/" 2>/dev/null || true

# 4. Windows 启动脚本（GPU 版本）
echo "  ✅ 复制 Windows 启动脚本..."
cp start-local-gpu.bat "${PACKAGE_DIR}/"
cp stop-local-gpu.bat "${PACKAGE_DIR}/"

# 5. 配置文件
echo "  ✅ 复制配置文件..."
cp env.example "${PACKAGE_DIR}/"
cp .gitignore "${PACKAGE_DIR}/"

# 6. 文档文件
echo "  ✅ 复制文档文件..."
cp README.md "${PACKAGE_DIR}/"
cp 快速启动.md "${PACKAGE_DIR}/"
cp Windows本地GPU部署指南.md "${PACKAGE_DIR}/"
cp 本地GPU部署快速参考.md "${PACKAGE_DIR}/"

# 7. 创建 Windows 部署说明文件
echo "  ✅ 创建 Windows 部署说明文件..."
cat > "${PACKAGE_DIR}/Windows本地GPU部署说明.txt" << 'EOF'
学生健康管理系统 - Windows 本地 GPU 部署说明
==========================================

一、系统要求
-----------
1. Windows 10/11
2. Python 3.9+ 
3. Node.js 18+
4. NVIDIA 显卡（RTX 3050Ti 或其他支持 CUDA 的显卡）
5. NVIDIA 驱动程序（最新版本）

二、快速启动（推荐）
------------------
1. 双击运行 start-local-gpu.bat

脚本会自动：
  ✅ 检查 Python 和 Node.js 环境
  ✅ 创建虚拟环境
  ✅ 安装依赖
  ✅ 初始化 SQLite 数据库
  ✅ 检测 GPU 支持
  ✅ 启动后端服务（端口 8000）
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

3. 安装 NVIDIA 驱动
   - 访问：https://www.nvidia.com/Download/index.aspx
   - 下载并安装最新的驱动程序

4. 验证安装
   打开命令提示符（CMD）或 PowerShell：
   python --version  # 应显示 Python 3.9.x 或更高
   node --version    # 应显示 v18.x.x 或更高
   nvidia-smi        # 应显示 GPU 信息

5. 后端启动
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
   # 安装 PyTorch CUDA 版本（GPU 支持）
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
   
   python init_database.py
   python run_gpu.py

6. 前端启动（新开一个命令行窗口）
   cd frontend
   npm install
   # 临时使用 GPU 配置
   copy vue.config.gpu.js vue.config.js
   npm run serve

四、访问地址
-----------
- 前端：http://localhost:8080
- 后端API：http://localhost:8000/api/health
- GPU状态：http://localhost:8000/api/gpu/status

五、默认账户
-----------
用户名：admin
密码：admin123

⚠️ 首次登录后请立即修改密码！

六、停止服务
-----------
- 双击运行 stop-local-gpu.bat
- 或直接关闭命令行窗口

七、外网访问（Cpolar 内网穿透）
------------------------------

1. 下载 Cpolar
   - 访问：https://www.cpolar.com/
   - 下载并安装 Cpolar 客户端

2. 注册账号
   - 注册 Cpolar 账号（免费版支持）

3. 创建隧道
   - 打开 Cpolar Web 界面：http://localhost:9200
   - 登录账号
   - 点击 "隧道管理" → "创建隧道"
   - 配置：
     * 隧道名称：学生健康管理系统
     * 协议：HTTP
     * 本地地址：localhost:8080
     * 域名类型：随机域名（免费）
   - 点击 "创建"

4. 获取公网地址
   - 创建成功后，Cpolar 会提供一个公网地址
   - 例如：https://abc123.cpolar.io

5. 访问测试
   - 在浏览器中访问 Cpolar 提供的公网地址
   - 前端会自动检测访问地址，API 会自动适配

八、常见问题
-----------

1. GPU 不可用
   - 检查 NVIDIA 驱动：nvidia-smi
   - 安装 PyTorch CUDA 版本：
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

2. 端口被占用
   - 关闭占用端口的程序
   - 或修改 run_gpu.py 和 vue.config.gpu.js 中的端口

3. 依赖安装失败
   - 使用国内镜像源：
     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
     npm config set registry https://registry.npmmirror.com

4. 前端无法访问后端
   - 前端会自动检测访问地址
   - localhost → http://localhost:8000/api
   - Cpolar 域名 → https://你的域名:8000/api

九、数据库说明
-------------
- 本地部署使用 SQLite 数据库
- 数据库文件位置：backend/instance/bs_system.db
- 数据库会自动创建，无需手动配置
- 数据会持久化保存，重启不会丢失

十、更新代码
-----------
如果需要更新代码：
1. 停止服务（运行 stop-local-gpu.bat）
2. 替换代码文件
3. 重新启动（运行 start-local-gpu.bat）

十一、技术支持
------------
详细文档请查看：
- Windows本地GPU部署指南.md - 详细部署指南
- 本地GPU部署快速参考.md - 快速参考
- README.md - 项目总览

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
    -x "*Dockerfile*" \
    -x "*docker-compose*" \
    -x "*docker-entrypoint*" \
    -x "*start-docker*" \
    -x "*stop-docker*" \
    -x "*nginx.conf*" \
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
echo "  ✅ Windows 启动脚本（start-local-gpu.bat, stop-local-gpu.bat）"
echo "  ✅ GPU 版本配置文件（run_gpu.py, vue.config.gpu.js）"
echo "  ✅ GPU 工具模块（gpu_utils.py, gpu_test.py）"
echo "  ✅ 依赖文件（requirements.txt, package.json）"
echo "  ✅ 数据库初始化脚本（init_database.py）"
echo "  ✅ 配置文件（env.example）"
echo "  ✅ 文档文件（Windows本地GPU部署指南.md 等）"
echo ""
echo "❌ 已排除："
echo "  ❌ Docker 相关文件（Dockerfile, docker-compose.yml）"
echo "  ❌ Linux 脚本（start-docker.sh, docker-entrypoint.sh）"
echo "  ❌ node_modules（需要 npm install）"
echo "  ❌ venv（需要 python -m venv）"
echo ""
echo "🚀 Windows 使用方法："
echo "  1. 解压压缩包到任意目录"
echo "  2. 双击 start-local-gpu.bat 启动"
echo "  3. 访问 http://localhost:8080"
echo "  4. 配置 Cpolar 内网穿透（可选，用于外网访问）"
echo ""
