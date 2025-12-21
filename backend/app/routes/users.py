from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.role import Role
from sqlalchemy import or_
from app.utils.decorators import login_required, admin_required
from app.utils.errors import NotFoundError, ValidationError, PermissionDeniedError
from app.utils.response import success_response
import os

bp = Blueprint('users', __name__)

@bp.route('', methods=['GET'])
@login_required
def get_users():
    """获取用户列表"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.role:
        raise PermissionDeniedError("无权访问")

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    role_id = request.args.get('role_id', type=int)
    
    query = User.query
    
    # 权限控制
    if current_user.role.code == 'teacher':
        # 教师只能看到学生
        query = query.join(Role).filter(Role.code == 'student')
    elif current_user.role.code == 'admin':
        # 管理员可以看到所有
        pass
    else:
        # 其他角色（如学生）只能看到自己，或者无权访问列表
        # 这里假设学生不能访问用户列表，或者只能看到自己
        # 根据需求"学生...数据范围：仅自己"，这里直接返回自己或者空
        query = query.filter(User.id == current_user_id)
    
    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                User.username.like(f'%{search}%'),
                User.email.like(f'%{search}%'),
                User.real_name.like(f'%{search}%')
            )
        )
    
    # 角色过滤 (如果传入了role_id)
    if role_id:
        query = query.filter(User.role_id == role_id)
    
    # 排序：按添加顺序（旧的在前）
    query = query.order_by(User.created_at.asc())

    # 分页
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return success_response({
        'items': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@bp.route('', methods=['POST'])
@admin_required
def create_user():
    """创建用户"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        raise ValidationError("用户名和密码不能为空")
    
    if User.query.filter_by(username=data['username']).first():
        raise ValidationError("用户名已存在")
        
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        raise ValidationError("邮箱已被使用")
    
    user = User(
        username=data['username'],
        email=data.get('email'),
        real_name=data.get('real_name'),
        role_id=data.get('role_id')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return success_response(data=user.to_dict(), message="创建成功")

@bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    return success_response(data=user.to_dict())

@bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """更新用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    current_user = User.query.get(current_user_id)
    
    # 权限检查
    is_admin = current_user.role and current_user.role.code == 'admin'
    is_teacher = current_user.role and current_user.role.code == 'teacher'
    is_target_student = user.role and user.role.code == 'student'
    
    # 允许修改的情况：
    # 1. 管理员
    # 2. 自己修改自己
    # 3. 教师修改学生
    if not (is_admin or user_id == current_user_id or (is_teacher and is_target_student)):
        raise PermissionDeniedError("权限不足")
    
    data = request.get_json()
    
    # 更新字段
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        # 检查邮箱是否已被使用
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            raise ValidationError("邮箱已被使用")
        user.email = data['email']
    
    # 只有管理员可以修改角色
    if 'role_id' in data and is_admin:
        user.role_id = data['role_id']
    
    db.session.commit()
    
    return success_response(data=user.to_dict(), message="更新成功")

@bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 权限检查
    is_admin = current_user.role and current_user.role.code == 'admin'
    is_teacher = current_user.role and current_user.role.code == 'teacher'
    is_target_student = user.role and user.role.code == 'student'
    
    # 允许删除的情况：
    # 1. 管理员
    # 2. 教师删除学生
    # 3. 学生删除自己 (根据需求"增删自己的档案与日志")
    if not (is_admin or (is_teacher and is_target_student) or user_id == current_user_id):
        raise PermissionDeniedError("权限不足")
    
    # 不能删除自己 (如果是管理员操作) - 但如果是学生注销自己是可以的
    # 这里保留原逻辑：如果是管理员操作，不能删除自己
    if is_admin and user_id == current_user_id:
        raise ValidationError("不能删除自己")
    
    db.session.delete(user)
    db.session.commit()
    
    return success_response(message="删除成功")

@bp.route('/<int:user_id>/password', methods=['PUT'])
@login_required
def change_password(user_id):
    """修改密码"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # 只能修改自己的密码
    if user_id != current_user_id:
        from app.utils.errors import PermissionDeniedError
        raise PermissionDeniedError("只能修改自己的密码")
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        raise ValidationError("旧密码和新密码不能为空")
    
    if not user.check_password(old_password):
        raise ValidationError("旧密码错误")
    
    if len(new_password) < 6:
        raise ValidationError("新密码长度至少6位")
    
    user.set_password(new_password)
    db.session.commit()
    
    return success_response(message="密码修改成功")

@bp.route('/<int:user_id>/reset', methods=['POST'])
@login_required
def reset_user(user_id):
    """重置学生数据：保留账号，重置密码为123，删除所有关联数据"""
    user = User.query.get_or_404(user_id)
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 权限检查
    is_admin = current_user.role and current_user.role.code == 'admin'
    is_teacher = current_user.role and current_user.role.code == 'teacher'
    is_target_student = user.role and user.role.code == 'student'
    
    # 仅允许管理员或教师重置学生数据
    if not (is_admin or (is_teacher and is_target_student)):
        raise PermissionDeniedError("权限不足，只能重置学生数据")
        
    try:
        # 1. 重置密码
        user.set_password('123')
        
        # 2. 清除用户基本信息
        user.real_name = None
        user.phone = None
        
        # 3. 删除头像文件
        if user.avatar:
            try:
                # 假设 avatar 存储的是 URL，如 /api/profile/avatar/filename.jpg
                if user.avatar.startswith('/api/profile/avatar/'):
                    filename = user.avatar.split('/')[-1]
                    avatar_path = os.path.join(current_app.root_path, 'static', 'avatars', filename)
                    if os.path.exists(avatar_path):
                        os.remove(avatar_path)
            except Exception as e:
                print(f"Error deleting avatar file: {e}")
            user.avatar = None
        
        # 4. 删除关联数据
        from app.models.profile import UserProfile
        from app.models.daily_log import DailyLog
        
        # 删除档案
        UserProfile.query.filter_by(user_id=user_id).delete()
        
        # 删除日志
        DailyLog.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        return success_response(message="重置成功：密码已重置为123，关联数据已清空")
        
    except Exception as e:
        db.session.rollback()
        raise e

