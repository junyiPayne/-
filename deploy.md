# BS系统 - 部署文档

## 📋 目录

1. [部署前准备](#部署前准备)
2. [服务器要求](#服务器要求)
3. [后端部署](#后端部署)
4. [前端部署](#前端部署)
5. [Nginx 配置](#nginx-配置)
6. [数据库配置](#数据库配置)
7. [环境变量配置](#环境变量配置)
8. [启动和停止服务](#启动和停止服务)
9. [监控和维护](#监控和维护)
10. [故障排除](#故障排除)

---

## 部署前准备

### 1. 检查清单

- [ ] 服务器已准备好（Linux/macOS/Windows）
- [ ] Python 3.9+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] Nginx 已安装（用于反向代理）
- [ ] 域名已配置（可选，建议）
- [ ] SSL 证书已准备（可选，推荐）

### 2. 获取代码

```bash
# 从 Git 仓库克隆
git clone <your-repository-url>
cd 学生健康管理系统

# 或解压源代码压缩包
unzip 学生健康管理系统_源代码.zip
cd 学生健康管理系统
```

---

## 服务器要求

### 最低配置

- **CPU**: 2 核
- **内存**: 4GB RAM
- **硬盘**: 20GB 可用空间
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 7+), macOS, Windows Server

### 推荐配置

- **CPU**: 4 核或更多
- **内存**: 8GB RAM 或更多
- **硬盘**: 50GB+ SSD
- **操作系统**: Linux (Ubuntu 22.04 LTS)

### 软件要求

- Python 3.9+
- Node.js 18+
- Nginx 1.18+
- MySQL 8.0+ 或 PostgreSQL 13+（生产环境推荐，可选）
- SQLite（默认，无需额外安装）

---

## 后端部署

### 步骤 1: 安装依赖

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用其他编辑器
```

**重要配置项：**

```env
# 生产环境必须修改！
FLASK_ENV=production
FLASK_DEBUG=False

# 生成安全密钥（在 Python 中执行）:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-generated-jwt-secret-key-here

# 数据库配置（如果使用 MySQL）
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=bs_user
DB_PASSWORD=your_secure_password
DB_NAME=bs_system

# CORS 配置（修改为你的前端域名）
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# AI 服务配置（可选）
DEEPSEEK_API_KEY=your-deepseek-api-key
QWEN_API_KEY=your-qwen-api-key
AI_PROVIDER=deepseek
```

### 步骤 3: 初始化数据库

```bash
# 初始化数据库（创建表和管理员账户）
python init_database.py
```

**默认管理员账户：**
- 用户名: `admin`
- 密码: `admin123`

**⚠️ 生产环境请立即修改默认密码！**

### 步骤 4: 创建日志目录

```bash
mkdir -p logs
```

### 步骤 5: 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
# 给脚本添加执行权限（如果还没有）
chmod +x start.sh

# 启动服务
./start.sh
```

#### 方式二：手动启动 Gunicorn

```bash
# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_ENV=production

# 启动 Gunicorn
gunicorn -c gunicorn.conf.py "app:create_app()"
```

#### 方式三：使用 systemd（Linux，推荐生产环境）

创建 `/etc/systemd/system/bs-system.service`:

```ini
[Unit]
Description=BS System Backend Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/path/to/backend/venv/bin/gunicorn -c gunicorn.conf.py "app:create_app()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable bs-system
sudo systemctl start bs-system
sudo systemctl status bs-system
```

### 步骤 6: 验证后端服务

```bash
# 检查健康状态
curl http://localhost:5001/api/health

# 应该返回 JSON 响应，status 为 "healthy"
```

---

## 前端部署

### 步骤 1: 安装依赖

```bash
cd frontend

# 安装 Node.js 依赖
npm install
```

### 步骤 2: 配置生产环境变量

```bash
# 编辑生产环境配置
nano .env.production  # 或使用其他编辑器
```

修改 `VUE_APP_API_BASE_URL` 为你的后端地址：

```env
# 如果使用 Nginx 反向代理，保持为 /api
VUE_APP_API_BASE_URL=/api

# 如果直接访问后端，修改为完整地址
# VUE_APP_API_BASE_URL=https://api.yourdomain.com/api
```

### 步骤 3: 构建生产版本

```bash
# 构建生产版本
npm run build

# 构建完成后，dist 目录包含所有静态文件
```

### 步骤 4: 部署静态文件

将 `dist` 目录中的文件部署到 Web 服务器：

```bash
# 方式一：使用 Nginx（推荐）
# 将 dist 目录内容复制到 Nginx 配置的 root 目录
sudo cp -r dist/* /var/www/bs-system/

# 方式二：使用其他 Web 服务器
# 将 dist 目录内容复制到服务器相应目录
```

---

## Nginx 配置

### 步骤 1: 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 步骤 2: 配置 Nginx

```bash
# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/bs-system

# 修改配置文件中的路径和域名
sudo nano /etc/nginx/sites-available/bs-system

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/bs-system /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载 Nginx
sudo systemctl reload nginx
```

### 步骤 3: 配置 SSL（推荐）

使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期（已自动配置）
```

---

## 数据库配置

### 使用 SQLite（默认，简单）

无需额外配置，数据库文件自动创建在 `backend/instance/bs_system.db`

### 使用 MySQL（生产环境推荐）

#### 1. 安装 MySQL

```bash
# Ubuntu/Debian
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
```

#### 2. 创建数据库和用户

```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE bs_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'bs_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- 授权
GRANT ALL PRIVILEGES ON bs_system.* TO 'bs_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 配置环境变量

在 `backend/.env` 中设置：

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=bs_user
DB_PASSWORD=your_secure_password
DB_NAME=bs_system
```

#### 4. 初始化数据库

```bash
cd backend
python init_database.py
```

---

## 环境变量配置

### 后端环境变量（backend/.env）

参考 `backend/.env.example`，必须配置的项：

- `FLASK_ENV=production`
- `SECRET_KEY`（必须修改！）
- `JWT_SECRET_KEY`（必须修改！）
- `CORS_ORIGINS`（修改为你的前端域名）
- 数据库配置（如果使用 MySQL）

### 前端环境变量（frontend/.env.production）

- `VUE_APP_API_BASE_URL`（API 地址）

---

## 启动和停止服务

### 启动服务

```bash
# 后端
cd backend
./start.sh

# 或使用 systemd
sudo systemctl start bs-system

# 前端（如果使用 Nginx，无需单独启动）
# Nginx 会自动服务静态文件
```

### 停止服务

```bash
# 后端
cd backend
./stop.sh

# 或使用 systemd
sudo systemctl stop bs-system
```

### 查看服务状态

```bash
# 检查后端进程
ps aux | grep gunicorn

# 检查 Nginx 状态
sudo systemctl status nginx

# 检查后端服务（如果使用 systemd）
sudo systemctl status bs-system
```

### 查看日志

```bash
# 后端日志
tail -f backend/logs/app.log
tail -f backend/logs/error.log
tail -f backend/logs/access.log

# Nginx 日志
sudo tail -f /var/log/nginx/bs-system-access.log
sudo tail -f /var/log/nginx/bs-system-error.log
```

---

## 监控和维护

### 健康检查

```bash
# 检查后端健康状态
curl http://localhost:5001/api/health

# 检查前端（通过 Nginx）
curl http://yourdomain.com/api/health
```

### 定期备份

```bash
# 备份数据库（SQLite）
cp backend/instance/bs_system.db backups/bs_system_$(date +%Y%m%d_%H%M%S).db

# 备份数据库（MySQL）
mysqldump -u bs_user -p bs_system > backups/bs_system_$(date +%Y%m%d_%H%M%S).sql

# 备份上传的文件
tar -czf backups/uploads_$(date +%Y%m%d_%H%M%S).tar.gz backend/app/static/
```

### 日志轮转

日志文件会自动轮转（通过 Gunicorn 和 Nginx 配置），但建议定期清理旧日志。

---

## 故障排除

### 问题 1: 后端无法启动

**检查：**
1. 虚拟环境是否激活
2. 依赖是否安装完整：`pip install -r requirements.txt`
3. 端口是否被占用：`lsof -i :5001`
4. 环境变量是否正确配置
5. 日志文件：`tail -f logs/error.log`

### 问题 2: 前端无法访问后端 API

**检查：**
1. 后端服务是否运行：`curl http://localhost:5001/api/health`
2. CORS 配置是否正确
3. Nginx 配置是否正确
4. 防火墙是否开放端口

### 问题 3: 数据库连接失败

**检查：**
1. 数据库服务是否运行
2. 数据库用户和密码是否正确
3. 数据库是否存在
4. 网络连接是否正常

### 问题 4: 文件上传失败

**检查：**
1. 文件大小是否超过限制（默认 16MB）
2. 上传目录权限是否正确
3. 磁盘空间是否充足

### 问题 5: 性能问题

**优化建议：**
1. 增加 Gunicorn 工作进程数
2. 启用 Nginx 缓存
3. 使用 CDN 加速静态资源
4. 数据库查询优化
5. 启用数据库连接池

---

## 安全建议

1. **修改默认密码**：部署后立即修改管理员密码
2. **使用 HTTPS**：配置 SSL 证书
3. **定期更新**：保持系统和依赖包更新
4. **防火墙配置**：只开放必要端口
5. **备份策略**：定期备份数据库和文件
6. **监控日志**：定期检查错误日志
7. **限制访问**：使用防火墙限制管理接口访问

---

## 联系和支持

如有问题，请查看：
- 项目 README.md
- 快速启动.md
- 使用安装开发说明.md

---

**部署完成后，请访问你的域名测试系统功能！**
