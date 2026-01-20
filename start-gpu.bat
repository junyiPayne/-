@echo off
chcp 65001 >nul
echo 🚀 启动 GPU 版本服务...
echo.

cd /d %~dp0

echo 📋 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过
echo.

echo 🐳 启动容器（GPU 版本）...
docker-compose -f docker-compose.gpu.yml up -d --build

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请查看错误信息
    echo 📋 查看日志: docker-compose -f docker-compose.gpu.yml logs
    pause
    exit /b 1
)

echo.
echo ✅ 服务已启动！
echo.
echo 📱 访问地址：
echo    前端: http://localhost
echo    后端API: http://localhost:8000/api/health
echo    GPU状态: http://localhost:8000/api/gpu/status
echo.
echo 📋 常用命令：
echo    查看日志: docker-compose -f docker-compose.gpu.yml logs -f
echo    查看状态: docker-compose -f docker-compose.gpu.yml ps
echo    停止服务: docker-compose -f docker-compose.gpu.yml down
echo.
echo 💡 提示: 首次启动需要下载镜像，可能需要 15-20 分钟
echo.

pause
