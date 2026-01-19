# ⚡ 本地 GPU 部署快速参考（无 Docker）

## 🚀 快速启动

### 1. 安装环境
- Python 3.9+：https://www.python.org/downloads/
- Node.js 18+：https://nodejs.org/
- NVIDIA 驱动：https://www.nvidia.com/Download/index.aspx

### 2. 一键启动
```batch
双击 start-local-gpu.bat
```

### 3. 访问系统
- 前端：http://localhost:8080
- 后端：http://localhost:8000/api/health
- GPU状态：http://localhost:8000/api/gpu/status

---

## 🌐 外网访问（Cpolar）

### 1. 下载 Cpolar
https://www.cpolar.com/

### 2. 创建隧道
- 协议：HTTP
- 本地地址：`localhost:8080`
- 域名类型：随机域名（免费）

### 3. 获取公网地址
例如：`https://abc123.cpolar.io`

### 4. 访问测试
访问 Cpolar 提供的地址，前端会自动适配 API 地址。

---

## 📋 文件说明

### 启动脚本
- `start-local-gpu.bat` - 一键启动
- `stop-local-gpu.bat` - 停止服务

### 配置文件
- `backend/run_gpu.py` - 后端启动（端口 8000）
- `frontend/vue.config.gpu.js` - 前端配置（代理到 8000）

### GPU 相关
- `backend/app/utils/gpu_utils.py` - GPU 工具
- `backend/app/routes/gpu_test.py` - GPU 测试路由

---

## 🔍 常见问题

### GPU 不可用？
```powershell
# 检查驱动
nvidia-smi

# 安装 PyTorch CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

### 端口被占用？
修改 `run_gpu.py` 和 `vue.config.gpu.js` 中的端口

### 前端无法访问后端？
前端会自动检测：
- `localhost` → `http://localhost:8000/api`
- Cpolar 域名 → `https://你的域名:8000/api`

---

## 📝 端口说明

- **8080** - 前端（Vue）
- **8000** - 后端 API（Flask）

---

**详细文档请查看：`Windows本地GPU部署指南.md`**
