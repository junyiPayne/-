@echo off
chcp 65001 >nul
echo 🛑 停止本地开发服务...
echo.

REM 停止占用5001端口的进程
echo 停止后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001') do (
    taskkill /PID %%a /F >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 后端服务已停止
    )
)

REM 停止占用8080端口的进程
echo 停止前端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    taskkill /PID %%a /F >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 前端服务已停止
    )
)

echo.
echo ✅ 所有服务已停止
pause
