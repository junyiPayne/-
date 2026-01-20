@echo off
chcp 65001 >nul
echo 🛑 停止 GPU 版本服务...
echo.

cd /d %~dp0

docker-compose -f docker-compose.gpu.yml down

echo.
echo ✅ 服务已停止！
echo.

pause
