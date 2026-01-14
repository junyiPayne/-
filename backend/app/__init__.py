from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__, instance_relative_config=True)
    
    # 确保instance目录存在（用于存储SQLite数据库等）
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # 加载配置
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 数据库初始化检查（仅对SQLite）
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            if app.config.get('DEBUG'):
                print(f"[DEBUG] 数据库文件已存在: {db_path} (大小: {file_size} 字节)")
        else:
            if app.config.get('DEBUG'):
                print(f"[DEBUG] 数据库文件不存在，将在首次使用时创建: {db_path}")
    
    # 如果使用SQLite且路径是相对路径，确保使用instance目录并转换为绝对路径
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///') and not os.environ.get('DATABASE_URL'):
        db_path = db_uri.replace('sqlite:///', '')
        
        # 确保instance目录存在
        os.makedirs(app.instance_path, exist_ok=True)
        
        # 检查路径是否是绝对路径
        if not os.path.isabs(db_path):
            # 相对路径，使用instance目录
            # 如果db_path只是文件名（如bs_system.db），直接拼接
            # 如果db_path包含路径（如instance/bs_system.db），需要处理
            if '/' in db_path or '\\' in db_path:
                # 包含路径分隔符，提取文件名
                db_filename = os.path.basename(db_path)
            else:
                # 只是文件名
                db_filename = db_path
            
            # 使用instance目录和文件名构建绝对路径
            db_file = os.path.abspath(os.path.join(app.instance_path, db_filename))
        else:
            # 已经是绝对路径，直接使用
            db_file = os.path.abspath(db_path)
        
        # SQLite URI格式：sqlite:///绝对路径（注意是3个斜杠）
        # 确保路径是绝对路径
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
        
        # 调试信息（开发环境）
        if app.config.get('DEBUG'):
            print(f"[DEBUG] 原始数据库URI: {db_uri}")
            print(f"[DEBUG] Instance路径: {app.instance_path}")
            print(f"[DEBUG] 最终数据库文件路径: {db_file}")
            print(f"[DEBUG] 最终数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # 生产环境初始化
    if config_name == 'production' and hasattr(config[config_name], 'init_app'):
        config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # 注册蓝图
    from app.routes.health import bp as health_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.users import bp as users_bp
    from app.routes.roles import bp as roles_bp
    from app.routes.business import bp as business_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.daily_log import bp as daily_log_bp
    from app.routes.ai import bp as ai_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.report import report_bp
    
    # 健康检查路由（不需要认证）
    app.register_blueprint(health_bp, url_prefix='/api')
    # 其他业务路由
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(roles_bp, url_prefix='/api/roles')
    app.register_blueprint(business_bp, url_prefix='/api/business')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(daily_log_bp, url_prefix='/api/daily-log')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    
    # 错误处理
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    return app

