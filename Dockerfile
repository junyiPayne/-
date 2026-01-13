# BS系统 - Dockerfile
# 多阶段构建，优化镜像大小

# ============================================
# 阶段 1: 构建前端
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制前端源代码
COPY frontend/ .

# 构建生产版本
RUN npm run build

# ============================================
# 阶段 2: Python 后端
# ============================================
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源代码
COPY backend/ .

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/frontend/dist ./static/frontend

# 创建必要的目录
RUN mkdir -p logs instance app/static/uploads app/static/avatars app/static/reports

# 设置环境变量
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/api/health')" || exit 1

# 启动命令
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
