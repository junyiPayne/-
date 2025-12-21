from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity,
    jwt_required
)
from app import db
from app.models.user import User
from app.models.role import Role
from app.models.system import SystemSetting
from app.utils.errors import ValidationError, AuthenticationError
from app.utils.response import success_response

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'email', 'password', 'role']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"{field}不能为空")
    
    # 验证角色是否合法
    allowed_roles = ['student', 'teacher']
    if data['role'] not in allowed_roles:
        raise ValidationError("无效的角色类型")

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        raise ValidationError("用户名已存在")
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        raise ValidationError("邮箱已被注册")
    
    # 创建用户
    user = User(
        username=data['username'],
        email=data['email'],
        real_name=data.get('real_name')
    )
    user.set_password(data['password'])
    
    # 分配角色
    role = Role.query.filter_by(code=data['role']).first()
    if not role:
        raise ValidationError(f"系统未找到角色: {data['role']}")
    user.role_id = role.id
    
    db.session.add(user)
    db.session.commit()
    
    return success_response({
        'user_id': user.id,
        'username': user.username
    }, "注册成功")

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        raise ValidationError("用户名和密码不能为空")
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        raise AuthenticationError("用户名或密码错误")
    
    if not user.is_active:
        raise AuthenticationError("账号已被禁用")
    
    # 检查维护模式
    maintenance_setting = SystemSetting.query.filter_by(key='maintenance_mode').first()
    if maintenance_setting and maintenance_setting.value == 'true':
        # 如果是维护模式，仅允许管理员登录
        # 确保role已加载
        if not user.role or user.role.code != 'admin':
             raise AuthenticationError("系统维护中，请等待系统维护完成")

    # 生成Token
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return success_response({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 86400,
        'user': user.to_dict()
    }, "登录成功")

@bp.route('/refresh', methods=['POST'])
def refresh():
    """刷新Token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        raise AuthenticationError("用户不存在或已被禁用")
    
    access_token = create_access_token(identity=current_user_id)
    
    return success_response({
        'access_token': access_token,
        'expires_in': 86400
    })

@bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    # JWT是无状态的，客户端删除token即可
    # 这里可以记录登出日志或加入黑名单
    return success_response(message="登出成功")

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    from flask_jwt_extended import get_jwt_identity
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        raise AuthenticationError("用户不存在")
    
    return success_response(data=user.to_dict())

