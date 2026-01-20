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
from app.models.classroom import Classroom
from app.utils.errors import ValidationError, AuthenticationError
from app.utils.response import success_response

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    import re
    data = request.get_json()
    
    # 检查维护模式：维护模式下禁止注册
    maintenance_setting = SystemSetting.query.filter_by(key='maintenance_mode').first()
    if maintenance_setting and maintenance_setting.value == 'true':
        raise AuthenticationError("系统维护中，请耐心等候")
    
    # 验证必填字段
    required_fields = ['username', 'email', 'password', 'role', 'real_name']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"{field}不能为空")
    
    # 验证用户名格式：只能包含字母和数字
    username = data['username'].strip()
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        raise ValidationError("账号（学号）只能输入字母和数字")
    
    # 验证真实姓名格式：只能包含中文字符
    real_name = data['real_name'].strip()
    if not re.match(r'^[\u4e00-\u9fa5]+$', real_name):
        raise ValidationError("真实姓名只能输入中文字符")
    
    # 验证密码不能为空
    if not data['password'] or not data['password'].strip():
        raise ValidationError("密码不能为空")
    
    # 验证角色是否合法
    allowed_roles = ['student', 'teacher']
    if data['role'] not in allowed_roles:
        raise ValidationError("无效的角色类型")
    
    # 验证班级字段（必填）
    if not data.get('class_id') and not data.get('class_name'):
        raise ValidationError("班级不能为空")
    
    # 处理班级
    classroom = None
    role_code = data['role']
    
    if role_code == 'teacher':
        # 教师：需要输入班级名称（创建新班级或使用已存在的班级）
        class_name = data.get('class_name', '').strip()
        if not class_name:
            raise ValidationError("教师注册时必须输入班级名称")
        
        # 检查班级是否已存在
        classroom = Classroom.query.filter_by(name=class_name).first()
        if not classroom:
            # 创建新班级
            classroom = Classroom(name=class_name, description=f"由教师 {real_name} 创建")
            db.session.add(classroom)
            db.session.flush()  # 获取班级ID
    
    elif role_code == 'student':
        # 学生：必须选择已存在的班级
        class_id = data.get('class_id')
        if not class_id:
            raise ValidationError("学生注册时必须选择班级")
        
        classroom = Classroom.query.get(class_id)
        if not classroom:
            raise ValidationError("选择的班级不存在")

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        raise ValidationError("账号（学号）已存在")
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        raise ValidationError("邮箱已被注册")
    
    # 创建用户
    user = User(
        username=username,
        email=data['email'],
        real_name=real_name,
        class_id=classroom.id
    )
    user.set_password(data['password'])
    
    # 分配角色
    role = Role.query.filter_by(code=role_code).first()
    if not role:
        raise ValidationError(f"系统未找到角色: {role_code}")
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
    import re
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username:
        raise ValidationError("账号（学号）不能为空")
    if not password:
        raise ValidationError("密码不能为空")
    
    # 验证用户名格式：只能包含字母和数字
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        raise ValidationError("账号（学号）只能输入字母和数字")
    
    # 先检查维护模式（在验证账号密码之前）
    maintenance_setting = SystemSetting.query.filter_by(key='maintenance_mode').first()
    is_maintenance = maintenance_setting and maintenance_setting.value == 'true'
    
    # 查找用户（需要先查找用户以判断是否是管理员）
    user = User.query.filter_by(username=username).first()
    
    # 如果是维护模式，且不是管理员账号，直接返回维护提示
    if is_maintenance:
        # 如果用户不存在，直接返回维护提示
        if not user:
            raise AuthenticationError("系统维护中，请耐心等候")
        
        # 如果用户存在，检查是否是管理员
        # 如果是管理员，继续验证密码；如果不是管理员，直接返回维护提示
        if not user.role or user.role.code != 'admin':
            raise AuthenticationError("系统维护中，请耐心等候")
    
    # 区分账号不存在和密码错误（仅在非维护模式或管理员时执行）
    if not user:
        raise AuthenticationError("账号不存在，请注册")
    
    if not user.check_password(password):
        raise AuthenticationError("密码错误")
    
    if not user.is_active:
        raise AuthenticationError("账号已被禁用")

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
        'user': user.to_dict(include_role=True, include_classroom=True)
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
    
    return success_response(data=user.to_dict(include_role=True, include_classroom=True))

