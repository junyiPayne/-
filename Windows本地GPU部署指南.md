# 🚀 Windows 本地 GPU 部署指南（无 Docker）

> **快速参考：** 安装环境 → 解压项目 → 双击 `start-local-gpu.bat` → 访问 http://localhost:8080

## 📋 前置要求

### 硬件要求
- ✅ Windows 10/11
- ✅ NVIDIA RTX 3050Ti 显卡（或其他支持 CUDA 的 NVIDIA 显卡）
- ✅ 至少 8GB 内存（推荐 16GB+）

### 软件要求
- ✅ Python 3.9+
- ✅ Node.js 18+
- ✅ NVIDIA 驱动程序（最新版本）
- ✅ Cpolar（用于内网穿透，可选）

---

## 🔧 第一步：安装基础环境

### 1. 安装 Python

1. 访问：https://www.python.org/downloads/
2. 下载并安装 Python 3.9+
3. ⚠️ **重要**：安装时勾选 **"Add Python to PATH"**

验证安装：
```powershell
python --version
```

### 2. 安装 Node.js

1. 访问：https://nodejs.org/
2. 下载并安装 Node.js 18+ LTS 版本

验证安装：
```powershell
node --version
npm --version
```

### 3. 安装 NVIDIA 驱动和 CUDA

1. 访问：https://www.nvidia.com/Download/index.aspx
2. 下载并安装最新的 NVIDIA 驱动程序
3. 验证安装：
```powershell
nvidia-smi
```

---

## 📦 第二步：准备项目文件

### 1. 解压项目

将项目文件解压到任意目录，例如：
```
D:\学生健康管理系统
```

### 2. 检查文件结构

确保以下文件存在：
- ✅ `start-local-gpu.bat` - GPU 版本启动脚本
- ✅ `stop-local-gpu.bat` - GPU 版本停止脚本
- ✅ `backend/run_gpu.py` - GPU 版本后端启动脚本
- ✅ `frontend/vue.config.gpu.js` - GPU 版本前端配置
- ✅ `backend/app/utils/gpu_utils.py` - GPU 工具模块
- ✅ `backend/app/routes/gpu_test.py` - GPU 测试路由

---

## 🚀 第三步：一键启动

### 方法一：使用启动脚本（推荐）

1. **双击 `start-local-gpu.bat`**

脚本会自动：
- ✅ 检查 Python 和 Node.js 环境
- ✅ 创建虚拟环境（如果不存在）
- ✅ 安装依赖（如果未安装）
- ✅ 初始化数据库（如果不存在）
- ✅ 检测 GPU 支持
- ✅ 启动后端服务（端口 8000）
- ✅ 启动前端服务（端口 8080）

### 方法二：手动启动

#### 启动后端

```powershell
cd backend

# 创建虚拟环境（如果不存在）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 PyTorch CUDA 版本（GPU 支持）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# 初始化数据库（如果不存在）
python init_database.py

# 启动后端（端口 8000）
python run_gpu.py
```

#### 启动前端（新开一个命令行窗口）

```powershell
cd frontend

# 安装依赖（如果未安装）
npm install

# 启动前端（使用 GPU 配置）
set VUE_CLI_SERVICE_CONFIG_PATH=vue.config.gpu.js
npm run serve
```

---

## ✅ 第四步：验证部署

### 1. 检查服务状态

打开浏览器访问：
- **前端：** http://localhost:8080
- **后端API：** http://localhost:8000/api/health
- **GPU状态：** http://localhost:8000/api/gpu/status

### 2. 测试 GPU

访问 GPU 状态接口：
```
http://localhost:8000/api/gpu/status
```

应该返回：
```json
{
  "code": 200,
  "data": {
    "gpu_available": true,
    "device": "cuda:0",
    "device_name": "NVIDIA GeForce RTX 3050 Ti Laptop GPU",
    "cuda_version": "11.7",
    "gpu_count": 1
  }
}
```

### 3. 登录系统

- 用户名：`admin`
- 密码：`admin123`

---

## 🌐 第五步：配置 Cpolar 内网穿透（外网访问）

### 1. 下载 Cpolar

访问：https://www.cpolar.com/

下载并安装 Cpolar 客户端

### 2. 注册账号

注册 Cpolar 账号（免费版支持）

### 3. 配置内网穿透

#### 方式一：Web 界面配置（推荐）

1. 打开 Cpolar Web 界面：http://localhost:9200
2. 登录账号
3. 点击 **"隧道管理"** → **"创建隧道"**
4. 配置隧道：
   - **隧道名称**：学生健康管理系统
   - **协议**：HTTP
   - **本地地址**：`localhost:8080`（前端端口）
   - **域名类型**：选择"随机域名"（免费）或"固定域名"（付费）
   - **地区**：选择最近的地区
5. 点击 **"创建"**

#### 方式二：命令行配置

```powershell
# 安装 Cpolar（如果使用命令行）
# 下载后解压，添加到 PATH

# 创建 HTTP 隧道（映射本地 8080 端口）
cpolar http 8080
```

### 4. 获取公网地址

创建成功后，Cpolar 会提供一个公网地址，例如：
```
https://abc123.cpolar.io
```

### 5. 测试访问

在浏览器中访问 Cpolar 提供的公网地址，应该能看到前端页面。

**前端会自动检测访问地址：**
- 如果通过 `localhost` 访问 → API 自动指向 `http://localhost:8000/api`
- 如果通过 Cpolar 域名访问 → API 自动指向 `https://你的域名:8000/api`

**无需手动配置！**

---

## 🔍 常见问题排查

### 1. GPU 不可用

**检查：**
```powershell
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 PyTorch 是否安装
python -c "import torch; print(torch.cuda.is_available())"
```

**解决：**
- 更新 NVIDIA 驱动程序到最新版本
- 安装 PyTorch CUDA 版本：
  ```powershell
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
  ```

### 2. 端口被占用

**检查：**
```powershell
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8080
```

**解决：**
- 关闭占用端口的程序
- 或修改 `run_gpu.py` 和 `vue.config.gpu.js` 中的端口

### 3. 前端无法访问后端 API

**检查：**
- 打开浏览器开发者工具（F12）
- 查看 Network 标签
- 检查 API 请求的 URL 是否正确

**前端会自动检测：**
- `localhost` → `http://localhost:8000/api`
- Cpolar 域名 → `https://你的域名:8000/api`

如果仍有问题，检查：
- 后端服务是否正常运行
- `vue.config.gpu.js` 中的代理配置是否正确
- CORS 配置是否正确

### 4. Cpolar 配置后无法访问

**检查：**
1. Cpolar 隧道是否运行
2. 本地服务是否正常运行（http://localhost:8080）
3. 防火墙设置
4. Cpolar 隧道状态（在 Web 界面查看）

**解决：**
- 确保本地服务正常运行
- 检查防火墙是否阻止了 Cpolar
- 重启 Cpolar 服务

### 5. 依赖安装失败

**解决：**
```powershell
# 使用国内镜像源（Python）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用国内镜像源（Node.js）
npm config set registry https://registry.npmmirror.com
npm install
```

---

## 📊 常用管理命令

### 查看服务状态

```powershell
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# 查看进程
tasklist | findstr python
tasklist | findstr node
```

### 停止服务

**方法一：使用停止脚本**
```powershell
双击 stop-local-gpu.bat
```

**方法二：手动停止**
```powershell
# 停止 Python 进程（后端）
taskkill /FI "WINDOWTITLE eq 后端服务*" /F

# 停止 Node.js 进程（前端）
taskkill /FI "WINDOWTITLE eq 前端服务*" /F
```

### 查看日志

后端日志会在命令行窗口显示，前端日志也会在命令行窗口显示。

---

## 💻 代码使用示例

### 在代码中使用 GPU

```python
from app.utils.gpu_utils import get_device, load_convnext_model

# 获取设备（自动检测 GPU）
device = get_device()

# 加载 ConvNeXt 模型
model, device = load_convnext_model()

# 使用模型进行预测
import torch
input_tensor = torch.randn(1, 3, 224, 224).to(device)
output = model(input_tensor)
```

---

## 📝 端口说明

- **8080** - 前端（Vue 开发服务器）
- **8000** - 后端 API（Flask）
- **9200** - Cpolar Web 管理界面（如果安装）

---

## 📦 依赖说明

### 基础依赖（requirements.txt）

已包含所有必需依赖（19个）：
- Flask 相关：Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-CORS, Flask-Marshmallow
- 工具库：python-dotenv, bcrypt, PyMySQL, cryptography, Werkzeug, requests
- AI 服务：dashscope
- 图像处理：Pillow, fpdf2, matplotlib

### GPU 依赖（可选，requirements-gpu.txt）

仅在需要 GPU 功能时安装：
- torch, torchvision, torchaudio

**安装 GPU 依赖：**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
# 或
pip install -r requirements-gpu.txt
```

---

## 🎯 快速启动流程

1. ✅ 安装 Python 3.9+ 和 Node.js 18+
2. ✅ 安装 NVIDIA 驱动
3. ✅ 解压项目文件（或 Git 克隆）
4. ✅ 双击 `start-local-gpu.bat`
5. ✅ 访问 http://localhost:8080
6. ✅ 配置 Cpolar 内网穿透（可选）
7. ✅ 通过公网地址访问

---

## 📋 关键文件

- `start-local-gpu.bat` - 一键启动脚本
- `stop-local-gpu.bat` - 停止脚本
- `backend/run_gpu.py` - GPU 版本后端启动脚本（端口 8000）
- `frontend/vue.config.gpu.js` - GPU 版本前端配置
- `backend/app/utils/gpu_utils.py` - GPU 工具模块
- `backend/app/routes/gpu_test.py` - GPU 测试路由
- `frontend/src/api/request.js` - 智能 API 地址检测（自动适配 localhost 和 Cpolar）

---

## ✅ 总结

**关键特性：**
- GPU 自动检测（可用时使用 GPU，否则使用 CPU）
- 智能 API 地址（前端自动检测访问地址）
- Cpolar 支持（自动适配公网访问）
- 一键启动（双击 start-local-gpu.bat）

**🎉 部署完成！现在你的系统已经可以在本地运行，并且可以通过 Cpolar 外网访问了！**
