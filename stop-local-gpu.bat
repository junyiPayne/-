@echo off
chcp 65001 >nul
echo 🛑 停止本地 GPU 版本服务...
echo.

REM 停止 Python 进程（后端）
echo 📦 停止后端服务...
taskkill /FI "WINDOWTITLE eq 后端服务*" /F >nul 2>&1
for /f "tokens=2" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM 停止 Node.js 进程（前端）
echo 📦 停止前端服务...
taskkill /FI "WINDOWTITLE eq 前端服务*" /F >nul 2>&1
for /f "tokens=2" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo ✅ 服务已停止！
echo.

pause
