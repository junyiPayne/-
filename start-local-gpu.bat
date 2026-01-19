@echo off
chcp 65001 >nul
echo 🚀 启动本地 GPU 版本服务...
echo.

cd /d %~dp0

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.9+
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js 18+
    echo 📥 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

REM 检查 GPU 支持
echo 🔍 检查 GPU 支持...
python -c "import torch; print('✅ GPU 可用' if torch.cuda.is_available() else '⚠️ GPU 不可用，将使用 CPU')" 2>nul
if errorlevel 1 (
    echo ⚠️ PyTorch 未安装，将跳过 GPU 检测
    echo 💡 提示: 如需 GPU 支持，请安装 PyTorch CUDA 版本
    echo    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
)

echo.

REM 启动后端
echo 📦 启动后端服务（端口 8000）...
cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo 📥 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖
if not exist "venv\Lib\site-packages\flask" (
    echo 📥 安装后端依赖（requirements.txt）...
    pip install -r requirements.txt
    echo.
    echo 💡 如需 GPU 支持，请安装 PyTorch CUDA 版本:
    echo    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
    echo    或使用: pip install -r requirements-gpu.txt
)

REM 检查数据库
if not exist "instance\bs_system.db" (
    echo 📦 初始化数据库...
    python init_database.py
)

REM 设置环境变量
set FLASK_ENV=development
set FLASK_APP=run.py
set PORT=8000

REM 启动后端（后台运行）
echo 🚀 启动后端服务...
start "后端服务" cmd /k "venv\Scripts\activate.bat && set PORT=8000 && python run_gpu.py"

cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 📦 启动前端服务（端口 8080）...
cd frontend

REM 检查依赖
if not exist "node_modules" (
    echo 📥 安装前端依赖（这可能需要几分钟）...
    call npm install
)

REM 启动前端（后台运行，使用 GPU 配置）
echo 🚀 启动前端服务...
REM 临时备份原配置文件（如果存在）
if exist "vue.config.js" (
    copy vue.config.js vue.config.js.bak >nul 2>&1
)
REM 使用 GPU 配置文件
copy vue.config.gpu.js vue.config.js >nul 2>&1
start "前端服务" cmd /k "npm run serve"
REM 注意：启动后 vue.config.js 会被替换为 GPU 版本，如需恢复请手动恢复备份

cd ..

echo.
echo ✅ 服务已启动！
echo.
echo 📱 访问地址：
echo    前端: http://localhost:8080
echo    后端API: http://localhost:8000/api/health
echo    GPU状态: http://localhost:8000/api/gpu/status
echo.
echo 💡 提示：
echo    - 前端会自动检测访问地址，如果通过 Cpolar 域名访问，API 会自动适配
echo    - 如需外网访问，请配置 Cpolar 内网穿透（映射端口 8080）
echo    - 停止服务：关闭命令行窗口，或运行 stop-local-gpu.bat
echo.
echo 🌐 Cpolar 配置：
echo    1. 下载 Cpolar: https://www.cpolar.com/
echo    2. 创建 HTTP 隧道，本地地址: localhost:8080
echo    3. 获取公网地址后访问即可
echo.

pause
