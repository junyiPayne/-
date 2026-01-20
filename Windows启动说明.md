# Windows 启动说明

> TL;DR：在项目根目录打开 PowerShell，执行 `./start-local.bat` 即可启动本地开发（前端 8080，后端 5001）。

## 1. 环境要求
- Windows 10/11
- 必装：Python 3.9+、Node.js 18+（安装时勾选 “Add to PATH”）
- 可选：Docker Desktop（GPU 版容器启动用）
- GPU 版可选：NVIDIA 驱动 + CUDA + PyTorch CUDA 版

## 2. 获取项目
- 解压或 `git clone` 到任意目录（示例：`D:\学生健康管理系统`）。
- 保证根目录下有 `start-local.bat`, `start-local-gpu.bat`, `start-gpu.bat` 等脚本。

## 3. 一键启动（本地 CPU 版，推荐）
1) 打开 PowerShell，切到项目根目录：
```powershell
cd D:\学生健康管理系统
```
2) 运行：
```powershell
./start-local.bat
```
脚本会自动检查 Python/Node、创建虚拟环境、安装依赖、初始化 SQLite，并启动：
- 前端：http://localhost:8080
- 后端：http://localhost:5001/api/health
- 默认账户：用户名 admin / 密码 admin123

停止：关闭启动时弹出的两个命令行窗口，或运行 `stop-local.bat`。
日志：`backend.log`、`frontend.log`。

## 4. 一键启动（本地 GPU 版，可选）
适合本机有 NVIDIA GPU 且已装 CUDA/PyTorch 的情况。
1) 打开 PowerShell，切到项目根目录。
2) 运行：
```powershell
./start-local-gpu.bat
```
脚本会检测 GPU，可用则后端启 8000 端口，前端启 8080 端口并自动使用 `vue.config.gpu.js`。
- 前端：http://localhost:8080
- 后端：http://localhost:8000/api/health
- GPU 状态：http://localhost:8000/api/gpu/status

停止：关闭窗口，或运行 `stop-local-gpu.bat`。

## 5. 一键启动（Docker GPU 版，可选）
需要 Docker Desktop + GPU 支持。
1) 打开 PowerShell，切到项目根目录。
2) 运行：
```powershell
./start-gpu.bat
```
脚本会使用 `docker-compose.gpu.yml` 启动前后端与数据库：
- 前端：http://localhost
- 后端：http://localhost:8000/api/health
- GPU 状态：http://localhost:8000/api/gpu/status

停止：
```powershell
docker-compose -f docker-compose.gpu.yml down
```
查看日志：
```powershell
docker-compose -f docker-compose.gpu.yml logs -f
```

## 6. 常见问题
- 端口占用：脚本已尝试释放 5001/8080（本地版）或按提示更换端口。
- 依赖安装慢：可临时切换镜像源（Python 用清华源，npm 用 `https://registry.npmmirror.com`）。
- GPU 不可用：确认 `nvidia-smi` 正常，并安装 PyTorch CUDA 版：`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117`。

## 7. 一键命令速查
- 本地 CPU 版：`./start-local.bat`
- 本地 GPU 版：`./start-local-gpu.bat`
- Docker GPU 版：`./start-gpu.bat`
- 停止本地版：`./stop-local.bat` 或 `./stop-local-gpu.bat`
- 停止 Docker 版：`docker-compose -f docker-compose.gpu.yml down`
