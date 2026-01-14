@echo off
chcp 65001 >nul
echo 🚀 启动本地开发模式...
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

REM 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 npm，请先安装 npm
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

REM 检查端口占用
netstat -ano | findstr :5001 >nul
if not errorlevel 1 (
    echo ⚠️  端口 5001 已被占用，正在释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 1 >nul
)

netstat -ano | findstr :8080 >nul
if not errorlevel 1 (
    echo ⚠️  端口 8080 已被占用，正在释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 1 >nul
)

REM 启动后端
echo 📦 启动后端服务...
cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo ⚠️  未找到虚拟环境，正在创建...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖
if not exist "venv\.installed" (
    echo 📥 安装后端依赖...
    pip install -r requirements.txt >nul 2>&1
    type nul > venv\.installed
)

REM 检查数据库
if not exist "instance\bs_system.db" (
    echo 🗄️  初始化数据库...
    python init_database.py
)

REM 启动后端
echo 🚀 启动后端服务器 (端口 5001)...
start "后端服务" /min cmd /c "python run.py > ..\backend.log 2>&1"

REM 等待后端启动
echo ⏳ 等待后端启动...
timeout /t 5 >nul

cd ..

REM 启动前端
echo.
echo 📦 启动前端服务...
cd frontend

REM 检查node_modules
if not exist "node_modules" (
    echo 📥 安装前端依赖（这可能需要几分钟）...
    npm install
)

REM 启动前端
echo 🚀 启动前端开发服务器 (端口 8080)...
start "前端服务" /min cmd /c "npm run serve > ..\frontend.log 2>&1"

REM 等待前端启动
echo ⏳ 等待前端启动...
timeout /t 8 >nul

cd ..

echo.
echo ════════════════════════════════════════
echo ✅ 系统启动成功！
echo ════════════════════════════════════════
echo.
echo 📱 访问地址:
echo    前端: http://localhost:8080
echo    后端API: http://localhost:5001/api/health
echo.
echo 👤 默认账户:
echo    用户名: admin
echo    密码: admin123
echo.
echo 📋 日志文件:
echo    后端日志: backend.log
echo    前端日志: frontend.log
echo.
echo 🛑 停止服务:
echo    关闭后端服务和前端服务的命令行窗口
echo    或运行: stop-local.bat
echo.
echo 📊 查看实时日志:
echo    后端: type backend.log
echo    前端: type frontend.log
echo.
echo 💡 提示: 如果遇到问题，请查看快速启动.md中的故障排查章节
echo.
pause
