import os
from datetime import timedelta
from dotenv import load_dotenv

# 查找项目根目录的 .env 文件
# 如果当前目录是 backend，向上查找一级；否则在当前目录查找
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_paths = [
    os.path.join(current_dir, '.env'),  # backend/.env
    os.path.join(parent_dir, '.env'),    # 项目根目录/.env
]

# 按优先级加载 .env 文件
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        if os.environ.get('FLASK_ENV') != 'production':
            print(f"[DEBUG] 加载环境变量文件: {env_path}")
        break
else:
    # 如果都没找到，使用默认行为（当前目录）
    load_dotenv()

class Config:
    """基础配置"""
    # 安全密钥配置 - 生产环境必须设置环境变量
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import warnings
        warnings.warn("SECRET_KEY 未设置，使用默认值（不安全！生产环境必须设置）")
        SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # 数据库配置
    # 优先使用环境变量指定的数据库，默认使用SQLite（本地开发）
    db_type = os.environ.get('DB_TYPE', 'sqlite')
    if db_type == 'mysql':
        # MySQL 连接字符串，添加连接池和超时参数
        db_user = os.environ.get('DB_USER', 'bs_user')
        db_password = os.environ.get('DB_PASSWORD', 'password')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '3306')
        db_name = os.environ.get('DB_NAME', 'bs_system')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{db_user}:{db_password}@"
            f"{db_host}:{db_port}/{db_name}"
            f"?charset=utf8mb4&connect_timeout=10&read_timeout=30&write_timeout=30"
        )
    else:
        # 使用SQLite（不需要MySQL服务）
        # Flask默认使用instance文件夹存储数据库文件
        # 如果设置了DATABASE_URL环境变量，使用它；否则使用instance目录下的数据库
        if os.environ.get('DATABASE_URL'):
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        else:
            # 使用instance目录下的数据库文件
            # 注意：这里使用相对路径，Flask会在create_app中转换为绝对路径
            # 这样可以避免路径中包含中文字符时的问题
            SQLALCHEMY_DATABASE_URI = 'sqlite:///bs_system.db'
    
    # SQLAlchemy 配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    # 数据库连接池配置（仅对 MySQL/PostgreSQL 有效）
    # SQLite 不支持连接池配置
    # 注意：connect_timeout 等参数已在连接字符串中设置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,  # 连接前检查连接是否有效（重要：自动重连断开的连接）
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20))
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800)))
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    # CORS配置 - 支持环境变量配置多个域名
    # 格式：多个域名用逗号分隔，如 "http://domain1.com,http://domain2.com"
    # 特殊值 "*" 表示允许所有域名（⚠️ 仅测试用，生产环境不推荐）
    cors_origins_str = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://localhost:3000')
    if cors_origins_str.strip() == '*':
        # 允许所有域名（仅测试环境）
        CORS_ORIGINS = ['*']
    else:
        # 解析多个域名
        CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 默认 16MB

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境安全检查
    @staticmethod
    def init_app(app):
        """初始化生产环境应用"""
        # 检查必要的环境变量（允许测试环境使用测试密钥）
        secret_key = app.config.get('SECRET_KEY', '')
        is_test_env = 'test' in secret_key.lower() or os.environ.get('TESTING', 'false').lower() == 'true'
        
        if not is_test_env:
            required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            if missing_vars:
                raise ValueError(f"生产环境缺少必要的环境变量: {', '.join(missing_vars)}")
            
            # 确保不使用默认密钥（测试环境除外）
            if secret_key == 'dev-secret-key-change-in-production':
                raise ValueError("生产环境必须设置 SECRET_KEY 环境变量，不能使用默认值！")
        
        # 配置日志
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            # 创建日志目录
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            # 配置文件日志
            file_handler = RotatingFileHandler(
                'logs/app.log', 
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('运动健康系统启动')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

