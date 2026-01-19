# 学生运动健康管理系统

## 项目概述

系统是一个基于Browser/Server架构的学生运动生理健康管理系统，采用前后端分离的设计模式。系统集成了运动生理基础数据管理、AI健康评估、报告生成等核心功能，为教师和学生提供完整的健康数据管理和分析服务。

### 核心功能

- **用户管理**：支持管理员、教师、学生三种角色，完善的权限控制
- **用户档案管理**：记录和管理用户的基础生理数据（性别、年龄、身高、体重、腰围、臀围、体脂率等）
- **每日日志记录**：记录饮食、运动、身体指标等日常数据
- **自动计算**：BMI、BMR、腰臀比、腰高比等指标自动计算
- **健康评估**：基于多维度指标的健康状态评估
- **AI健康分析**：集成DeepSeek和通义千问API，提供智能健康风险评估和建议
- **报告生成**：自动生成PDF格式的健康报告，支持预览、提交和历史记录
- **统计分析**：数据统计、趋势分析、预测报告

## 技术栈

### 后端
- **Python** 3.9+
- **Flask** 2.3+ - Web框架
- **SQLAlchemy** - ORM数据库操作
- **Flask-JWT-Extended** - JWT身份认证
- **Flask-CORS** - 跨域支持
- **Gunicorn** - 生产环境WSGI服务器
- **fpdf2** 2.7.6 - PDF生成
- **requests** - HTTP请求（AI API调用）
- **bcrypt** - 密码加密

### 前端
- **Vue.js** 3.3+ - 前端框架（Composition API）
- **Element Plus** 2.4+ - UI组件库
- **Vue Router** 4.2+ - 路由管理
- **Pinia** 2.1+ - 状态管理
- **Axios** 1.6+ - HTTP客户端
- **ECharts** 6.0+ - 数据可视化

### 数据库
- **SQLite** - 本地开发环境（简单易用，无需安装数据库服务）
- **MySQL 8.0+** - Docker 部署环境（适合生产环境，支持高并发）

**数据库初始化说明：**
- **本地开发（SQLite）**：
  - 如果数据库不存在：自动创建 `backend/instance/bs_system.db` 并初始化表结构
  - 如果数据库已存在：直接使用现有数据库，只创建缺失的表和初始化默认数据
- **Docker 部署（MySQL）**：
  - 如果数据库不存在：MySQL 容器自动创建数据库，后端容器初始化表结构和默认数据
  - 如果数据库已存在：直接使用现有数据库（数据存储在 Docker volume `db_data` 中），只创建缺失的表和初始化默认数据

### AI服务
- **DeepSeek API** - AI健康评估
- **通义千问 API** - AI预测分析

### 部署
- **Nginx** - 反向代理和静态文件服务
- **Docker** - 容器化部署（可选）
- **Gunicorn** - 生产环境WSGI服务器

## 项目结构（已按启动方式和职责重新梳理）

```
学生健康管理系统/
├── backend/                        # 后端（Flask）
│   ├── app/
│   │   ├── models/                # 数据模型（user、role、profile、daily_log、report、business 等）
│   │   ├── routes/                # API 路由（auth、users、profile、daily_log、report、ai、health 等）
│   │   ├── services/              # 服务层（ai_service 等）
│   │   ├── utils/                 # 工具模块（calculations、decorators、errors、response）
│   │   └── static/                # 静态资源（avatars、uploads、reports）
│   ├── config.py                  # 配置中心（加载 .env / 环境变量，配置数据库、JWT、CORS 等）
│   ├── run.py                     # 开发环境入口（本地 5001 端口）
│   ├── gunicorn.conf.py           # Gunicorn 配置
│   ├── logging.conf               # 日志配置
│   ├── init_database.py           # 数据库初始化与备份恢复逻辑
│   ├── requirements.txt           # 后端依赖
│   └── check_api_config.py        # AI API Key 状态检查与连通性测试工具
│
├── frontend/                      # 前端（Vue 3 + Element Plus）
│   ├── src/
│   │   ├── views/                 # 页面组件（登录、DashBoard、AI体重助手、统计、报告等）
│   │   ├── api/                   # Axios 封装的 API 调用
│   │   ├── router/                # 路由配置
│   │   ├── stores/                # Pinia 状态管理
│   │   └── layouts/               # 布局组件
│   ├── public/
│   ├── package.json
│   └── vue.config.js             # 本地开发代理配置（转发到后端 5001）
│
├── scripts & 工具脚本（位于项目根目录）           # 启动/诊断/修复脚本
│   ├── start-local.sh / stop-local.sh         # 本地开发一键启动/停止（Python + Node 开发服务器）
│   ├── start-local.bat / stop-local.bat       # Windows 下本地启动/停止
│   ├── start-docker.sh                        # Docker 开发/演示一键启动（支持 --rebuild）
│   ├── Dockerfile                             # 后端 + 前端打包的基础镜像（Debian bookworm）
│   └── docker-compose.yml                     # Docker Compose 编排（backend + db + nginx）
│
├── docs/                         # 文档
│   ├── 01-AI编程实验环境配置.md
│   ├── 02-概要设计文档.md
│   ├── 03-详细设计文档.md
│   ├── 04-用例测试文档.md
│   ├── 05-使用安装开发说明.md
│   └── 06-后期展望.md
│
├── database/
│   └── init.sql                  # MySQL 初始化脚本
├── nginx.conf                    # Nginx 反向代理与静态资源配置
├── 生产环境部署指南.md           # 生产环境正式部署详细指南
├── 快速启动.md                   # 本地开发快速启动指南
├── 项目结构图.md                 # Mermaid 项目结构与数据流图
└── README.md                     # 项目总览（当前文档）
```

## 核心功能模块

### 1. 用户认证与权限管理
- 用户注册、登录、登出
- JWT Token认证
- 基于角色的访问控制（RBAC）
- 角色：管理员、教师、学生

### 2. 用户档案管理
- 基础数据录入（性别、年龄、身高、体重、腰围、臀围、体脂率）
- 自动计算BMI、BMR、腰臀比、腰高比
- 健康状态评估（体重等级、体脂等级、肥胖评估）
- 头像上传和管理

### 3. 每日日志记录
- 饮食记录（热量、营养素比例、膳食纤维、酒精）
- 运动记录（类型、时长、强度、消耗）
- 身体指标记录（体重、腰围、臀围）
- 图片上传（食物照片）
- 自动计算净热量和预测体重变化

### 4. AI健康分析
- 健康风险评估（基于档案和日志数据）
- AI生成修正建议（三段式输出）
- 体重/体脂变化预测
- 支持DeepSeek和通义千问双API

### 5. 报告生成与管理
- PDF格式健康报告生成
- 报告预览功能
- 报告提交和历史记录
- 数据哈希对比，避免重复提交
- 角色权限控制（管理员查看全部，教师查看学生，学生查看自己）

### 6. 统计分析
- 数据统计（平均摄入、平均消耗、预测体重变化）
- 时间范围筛选（4周/8周/12周）
- 报告预览和提交（集成在统计页面）

### 7. 健康检查
- `/api/health` - 健康检查接口
- `/api/ready` - 就绪检查接口（Kubernetes）
- `/api/live` - 存活检查接口（Kubernetes）

## 快速开始

### 方式一：一键启动（推荐，最简单）

详细步骤请参考 [`快速启动.md`](./快速启动.md)

**本地开发模式：**
- macOS/Linux: `./start-local.sh`
- Windows: `start-local.bat`

**Docker开发模式：**
- 所有平台: `./start-docker.sh`

就这么简单！脚本会自动检查环境、安装依赖、初始化数据库并启动服务。

### 方式二：手动启动（高级用户）

如果一键启动脚本无法使用，可以手动启动：

**后端：**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python init_database.py
python run.py
```

**前端（新终端）：**
```bash
cd frontend
npm install
npm run serve
```

### 方式三：生产环境部署

详细步骤请参考 [`生产环境部署指南.md`](./生产环境部署指南.md)

**快速部署（Docker，推荐）：**
```bash
./start-docker.sh --rebuild
```

**传统部署：**
1. 配置环境变量：创建 `.env` 文件（本地开发用 SQLite，无需配置数据库）
2. 初始化数据库：`cd backend && python init_database.py`（自动创建 SQLite）
3. 启动后端：`cd backend && python run.py`（开发环境）或使用 Gunicorn（生产环境）
4. 构建前端：`cd frontend && npm install && npm run build`
5. 配置Nginx：参考 `nginx.conf` 和 `生产环境部署指南.md`

### 方式四：Docker 部署（推荐，本机模拟生产环境）

```bash
# 使用 Docker Compose 一键部署
./start-docker.sh --rebuild
```

**特点：**
- ✅ 自动启动 MySQL 数据库容器
- ✅ 自动配置 Nginx 反向代理
- ✅ 数据持久化存储（Docker volume）
- ✅ 完全模拟生产环境（MySQL + Nginx + Gunicorn）
- ✅ 本地开发用 SQLite，Docker 用 MySQL，数据独立

**访问地址：**
- 前端：http://localhost
- 后端 API：http://localhost:5001/api/health

**详细说明：**
- 快速启动：参考 [`快速启动.md`](./快速启动.md) 的"方式二：Docker开发模式"
- 完整部署指南：参考 [`生产环境部署指南.md`](./生产环境部署指南.md)

## 默认账户

- **用户名**：`admin`
- **密码**：`admin123`
- **角色**：管理员

⚠️ **生产环境部署后请立即修改默认密码！**

## 系统要求

### 开发环境
- Python 3.9+
- Node.js 18+
- SQLite（自动创建，无需安装）

### 生产环境（Docker 部署）
- Docker & Docker Compose
- MySQL 8.0+（Docker 自动启动）
- Nginx（Docker 自动启动）
- Gunicorn（已包含在 requirements.txt）

## 环境变量配置

### 后端环境变量（backend/.env）

生产环境必须配置以下变量：

```env
# 安全密钥（必须修改！）
SECRET_KEY=your-generated-secret-key
JWT_SECRET_KEY=your-generated-jwt-secret-key

# 运行环境
FLASK_ENV=production
FLASK_DEBUG=False

# CORS配置（修改为你的前端域名）
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 数据库配置
# 本地开发：使用 SQLite（默认，无需配置）
DB_TYPE=sqlite

# Docker 部署：自动使用 MySQL（docker-compose.yml 中已配置）
# 如需修改 MySQL 配置，编辑 docker-compose.yml

# AI服务配置（可选）
DEEPSEEK_API_KEY=your-deepseek-api-key
QWEN_API_KEY=your-qwen-api-key
AI_PROVIDER=deepseek
```

> 提示：如果 DeepSeek 返回 “Insufficient Balance” 会自动降级为本地模拟。请在 DeepSeek 控制台充值，或改用 Qwen：  
> ```
> QWEN_API_KEY=your-qwen-api-key
> AI_PROVIDER=qwen
> ```

生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 前端环境变量（frontend/.env.production）

```env
VUE_APP_API_BASE_URL=/api
VUE_APP_TITLE=运动健康系统 - 学生健康管理系统
VUE_APP_DEBUG=false
```

## 📚 文档说明

### 快速开始文档（推荐先看）

- **`快速启动.md`** - 🚀 **本地开发快速启动指南**
  - 用途：本地开发环境一键启动
  - 适用：开发、测试、学习
  - 内容：本地开发模式和 Docker 开发模式的快速启动方法
  - 数据库：本地使用 SQLite，Docker 使用 MySQL

- **`README.md`** - 📖 **项目总览文档（当前文档）**
  - 用途：项目概述、技术栈、快速开始
  - 适用：了解项目整体情况
  - 内容：项目介绍、核心功能、技术栈、快速开始

### 部署文档

- **`生产环境部署指南.md`** - 🚀 **完整部署文档（推荐）**
  - 用途：包含所有部署方式（Docker、传统部署、网络部署）
  - 适用：生产环境、正式上线、网络部署
  - 内容：
    - Docker 一键部署（推荐）
    - 网络部署（让其他学校学生访问）
    - 传统手动部署
    - Nginx 配置、MySQL 配置
    - 环境变量配置
    - 监控维护、故障排除
  - **这是最完整的部署文档，包含所有部署场景**

### 设计文档

- **`项目结构图.md`** - 📊 **系统架构图和数据流图**
  - 用途：了解系统架构和数据流向
  - 适用：理解系统设计
  - 内容：Mermaid 图表展示项目结构和数据流

- **`docs/02-概要设计文档.md`** - 📋 **系统架构和设计概览**
  - 用途：了解系统整体设计
  - 适用：理解系统架构

- **`docs/03-详细设计文档.md`** - 📝 **详细的实现设计**
  - 用途：了解具体实现细节
  - 适用：深入理解实现

- **`docs/04-用例测试文档.md`** - ✅ **测试用例和测试说明**
  - 用途：了解测试用例
  - 适用：测试和验证

- **`docs/05-使用安装开发说明.md`** - 🔧 **详细的安装和开发指南**
  - 用途：详细的安装和开发步骤
  - 适用：深入开发

- **`docs/06-后期展望.md`** - 🔮 **系统未来发展规划**
  - 用途：了解未来发展方向
  - 适用：规划扩展

### 📋 文档使用建议

**如果你是开发者：**
1. 先看 `README.md` 了解项目
2. 看 `快速启动.md` 开始开发
3. 需要了解架构时看 `项目结构图.md`

**如果你要部署到服务器：**
1. **快速启动**（本地测试）：看 `快速启动.md` 的"方式二：Docker开发模式"
2. **完整部署指南**（生产环境）：看 `生产环境部署指南.md`
   - 包含 Docker 一键部署、网络部署、传统手动部署

**如果你想深入了解：**
- 看 `docs/` 目录下的设计文档

## API接口

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/refresh` - 刷新Token

### 健康检查
- `GET /api/health` - 健康检查
- `GET /api/ready` - 就绪检查
- `GET /api/live` - 存活检查

### 用户管理
- `GET /api/users` - 获取用户列表
- `GET /api/users/:id` - 获取用户详情
- `PUT /api/users/:id` - 更新用户信息

### 用户档案
- `GET /api/profile` - 获取用户档案
- `POST /api/profile` - 创建用户档案
- `PUT /api/profile` - 更新用户档案

### 每日日志
- `GET /api/daily-log` - 获取日志列表
- `POST /api/daily-log` - 创建/更新日志
- `GET /api/daily-log/statistics` - 获取统计数据

### AI服务
- `POST /api/ai/health-assessment` - 获取AI健康评估
- `POST /api/ai/prediction` - 获取AI预测

### 报告管理
- `GET /api/reports/preview` - 预览报告
- `POST /api/reports/submit` - 提交报告
- `GET /api/reports/list` - 获取报告列表

## 开发规范

- **后端**：遵循PEP 8规范
- **前端**：使用ESLint和Prettier
- **API**：RESTful风格
- **响应格式**：统一的JSON格式

## 安全特性

- ✅ JWT Token认证
- ✅ 密码bcrypt加密
- ✅ 生产环境错误信息保护
- ✅ CORS跨域安全配置
- ✅ 文件上传大小限制（16MB）
- ✅ SQL注入防护（SQLAlchemy ORM）
- ✅ XSS防护（前端自动转义）

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请查看文档或提交Issue。

---

**项目状态**: ✅ 已完成，支持生产环境部署