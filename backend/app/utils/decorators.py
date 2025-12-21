from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app.utils.errors import AuthenticationError, PermissionDeniedError

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if not user_id:
                raise AuthenticationError("未登录")
        except Exception as e:
            if isinstance(e, (AuthenticationError, PermissionDeniedError)):
                raise
            # 只捕获JWT相关的错误，其他错误抛出以便调试
            from flask_jwt_extended.exceptions import JWTExtendedException
            if isinstance(e, JWTExtendedException):
                raise AuthenticationError("认证失败: " + str(e))
            # 如果是其他异常（如代码错误），不要捕获，让它抛出500
            raise e
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.role or user.role.code != 'admin':
            raise PermissionDeniedError("需要管理员权限")
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_code):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.role:
                raise PermissionDeniedError("权限不足")
            
            # 检查用户是否有该权限
            has_permission = any(
                perm.code == permission_code 
                for perm in user.role.permissions
            )
            
            if not has_permission:
                raise PermissionDeniedError("权限不足")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

