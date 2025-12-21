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
    app = Flask(__name__)
    
    # 加载配置
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # 注册蓝图
    from app.routes.auth import bp as auth_bp
    from app.routes.users import bp as users_bp
    from app.routes.roles import bp as roles_bp
    from app.routes.business import bp as business_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.daily_log import bp as daily_log_bp
    from app.routes.ai import bp as ai_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.report import report_bp
    
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

