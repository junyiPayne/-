# BS系统 - Dockerfile
# 多阶段构建，优化镜像大小

# ============================================
# 阶段 1: 构建前端
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖（包括开发依赖，因为需要构建）
RUN npm ci

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
    fonts-noto-cjk \
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

# 创建初始化脚本（自动初始化数据库）
RUN echo '#!/bin/bash\n\
set -e\n\
echo "=========================================="\n\
echo "BS系统 - 容器启动"\n\
echo "=========================================="\n\
if [ ! -f instance/bs_system.db ]; then\n\
    echo "📦 初始化数据库..."\n\
    python init_database.py || {\n\
        echo "❌ 数据库初始化失败"\n\
        exit 1\n\
    }\n\
    echo "✅ 数据库初始化完成"\n\
else\n\
    echo "✅ 数据库已存在，跳过初始化"\n\
fi\n\
echo "🚀 启动 Gunicorn 服务器..."\n\
exec "$@"' > /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# 设置环境变量
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 5001

# 健康检查（使用 urllib，更可靠）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/api/health')" || exit 1

# 入口点（自动初始化数据库）
ENTRYPOINT ["/docker-entrypoint.sh"]

# 启动命令（使用 wsgi.py 中的 app 实例）
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
