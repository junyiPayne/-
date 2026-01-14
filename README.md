# BS系统 - 运动生理健康管理系统

## 项目概述

BS系统是一个基于Browser/Server架构的运动生理健康管理系统，采用前后端分离的设计模式。系统集成了运动生理基础数据管理、AI健康评估、报告生成等核心功能，为教师和学生提供完整的健康数据管理和分析服务。

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
- **SQLite** - 默认数据库（单文件，便于部署）
- 支持迁移到 **PostgreSQL** / **MySQL**

### AI服务
- **DeepSeek API** - AI健康评估
- **通义千问 API** - AI预测分析

### 部署
- **Nginx** - 反向代理和静态文件服务
- **Docker** - 容器化部署（可选）
- **Gunicorn** - 生产环境WSGI服务器

## 项目结构

```
BS系统/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── role.py        # 角色权限模型
│   │   │   ├── profile.py     # 用户档案模型
│   │   │   ├── daily_log.py   # 每日日志模型
│   │   │   ├── report.py      # 报告模型
│   │   │   └── business.py    # 业务数据模型
│   │   ├── routes/            # API路由
│   │   │   ├── auth.py        # 认证路由
│   │   │   ├── users.py       # 用户管理路由
│   │   │   ├── profile.py     # 档案管理路由
│   │   │   ├── daily_log.py   # 日志管理路由
│   │   │   ├── report.py      # 报告管理路由
│   │   │   ├── ai.py          # AI服务路由
│   │   │   ├── health.py      # 健康检查路由
│   │   │   └── roles.py       # 角色管理路由
│   │   ├── services/          # 业务服务层
│   │   │   └── ai_service.py  # AI服务封装
│   │   ├── utils/             # 工具函数
│   │   │   ├── calculations.py # 计算公式模块
│   │   │   ├── decorators.py  # 装饰器
│   │   │   ├── errors.py       # 异常处理
│   │   │   └── response.py    # 响应格式化
│   │   └── static/            # 静态文件
│   │       ├── avatars/       # 头像文件
│   │       ├── uploads/       # 上传文件
│   │       └── reports/       # 报告文件
│   ├── config.py              # 配置文件
│   ├── run.py                 # 开发环境运行入口
│   ├── run_production.py      # 生产环境运行入口（测试用）
│   ├── start.sh               # 生产环境启动脚本
│   ├── stop.sh                # 生产环境停止脚本
│   ├── gunicorn.conf.py       # Gunicorn配置文件
│   ├── logging.conf           # 日志配置文件
│   ├── init_database.py       # 数据库初始化
│   └── requirements.txt      # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   │   ├── auth/          # 认证页面
│   │   │   ├── users/         # 用户管理
│   │   │   ├── profile/       # 用户档案
│   │   │   ├── daily-log/      # 每日日志
│   │   │   ├── statistics/     # 统计分析
│   │   │   └── business/       # 业务数据
│   │   ├── api/               # API调用
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # 状态管理
│   │   └── layouts/           # 布局组件
│   └── package.json           # 前端依赖
├── docs/                      # 文档目录
│   ├── 01-AI编程实验环境配置.md
│   ├── 02-概要设计文档.md
│   ├── 03-详细设计文档.md
│   ├── 04-用例测试文档.md
│   ├── 05-使用安装开发说明.md
│   └── 06-后期展望.md
├── database/                  # 数据库脚本
│   └── init.sql
├── nginx.conf                  # Nginx配置文件
├── Dockerfile                  # Docker镜像配置
├── docker-compose.yml         # Docker Compose配置
├── deploy.md                   # 部署文档
├── 快速启动.md                 # 快速启动指南
└── README.md                   # 项目说明
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

### 方式一：快速启动（开发环境）

详细步骤请参考 [`快速启动.md`](./快速启动.md)

**三步启动：**
1. 初始化数据库：`cd backend && python init_database.py`
2. 启动后端：`python run.py`
3. 启动前端：`cd frontend && npm install && npm run serve`

### 方式二：生产环境部署

详细步骤请参考 [`deploy.md`](./deploy.md)

**快速部署：**
1. 配置环境变量：`cp backend/.env.example backend/.env` 并修改配置
2. 初始化数据库：`cd backend && python init_database.py`
3. 启动后端：`cd backend && ./start.sh`
4. 构建前端：`cd frontend && npm install && npm run build`
5. 配置Nginx：参考 `nginx.conf` 和 `deploy.md`

### 方式三：Docker部署（推荐）

```bash
# 使用 Docker Compose 一键部署
docker-compose up -d
```

详细说明请参考 [`deploy.md`](./deploy.md)

## 默认账户

- **用户名**：`admin`
- **密码**：`admin123`
- **角色**：管理员

⚠️ **生产环境部署后请立即修改默认密码！**

## 系统要求

### 开发环境
- Python 3.9+
- Node.js 18+
- SQLite（默认，无需额外安装）

### 生产环境
- Python 3.9+
- Node.js 18+
- Nginx 1.18+（用于反向代理）
- SQLite（默认）或 MySQL 8.0+ / PostgreSQL 13+（推荐）
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

# 数据库配置（如果使用MySQL）
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=bs_user
DB_PASSWORD=your_password
DB_NAME=bs_system

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
VUE_APP_TITLE=BS系统 - 学生健康管理系统
VUE_APP_DEBUG=false
```

## 文档说明

- **项目结构图**：`项目结构图.md` - 详细的系统架构图和数据流向图（包含Mermaid图表）
- **快速启动指南**：`快速启动.md` - 开发环境快速启动
- **部署文档**：`deploy.md` - 生产环境部署详细指南
- **安装开发说明**：`docs/05-使用安装开发说明.md` - 详细的安装和开发指南
- **概要设计文档**：`docs/02-概要设计文档.md` - 系统架构和设计概览
- **详细设计文档**：`docs/03-详细设计文档.md` - 详细的实现设计
- **用例测试文档**：`docs/04-用例测试文档.md` - 测试用例和测试说明
- **后期展望**：`docs/06-后期展望.md` - 系统未来发展规划

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