from flask import Blueprint, request
from app import db
from app.models.role import Role, Permission
from app.utils.decorators import login_required, admin_required
from app.utils.errors import NotFoundError, ValidationError
from app.utils.response import success_response

bp = Blueprint('roles', __name__)

@bp.route('', methods=['GET'])
@login_required
def get_roles():
    """获取角色列表"""
    roles = Role.query.all()
    return success_response(data=[role.to_dict() for role in roles])

@bp.route('/<int:role_id>', methods=['GET'])
@login_required
def get_role(role_id):
    """获取角色详情"""
    role = Role.query.get_or_404(role_id)
    return success_response(data=role.to_dict())

@bp.route('', methods=['POST'])
@admin_required
def create_role():
    """创建角色"""
    data = request.get_json()
    
    if not data.get('name') or not data.get('code'):
        raise ValidationError("角色名称和代码不能为空")
    
    # 检查代码是否已存在
    if Role.query.filter_by(code=data['code']).first():
        raise ValidationError("角色代码已存在")
    
    role = Role(
        name=data['name'],
        code=data['code'],
        description=data.get('description')
    )
    
    # 分配权限
    if data.get('permission_ids'):
        permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
        role.permissions = permissions
    
    db.session.add(role)
    db.session.commit()
    
    return success_response(data=role.to_dict(), message="创建成功")

@bp.route('/<int:role_id>', methods=['PUT'])
@admin_required
def update_role(role_id):
    """更新角色"""
    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    
    if 'name' in data:
        role.name = data['name']
    if 'description' in data:
        role.description = data['description']
    
    # 更新权限
    if 'permission_ids' in data:
        permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
        role.permissions = permissions
    
    db.session.commit()
    
    return success_response(data=role.to_dict(), message="更新成功")

@bp.route('/<int:role_id>', methods=['DELETE'])
@admin_required
def delete_role(role_id):
    """删除角色"""
    role = Role.query.get_or_404(role_id)
    
    # 检查是否有用户使用该角色
    if role.users:
        raise ValidationError("该角色下还有用户，无法删除")
    
    db.session.delete(role)
    db.session.commit()
    
    return success_response(message="删除成功")

@bp.route('/permissions', methods=['GET'])
@login_required
def get_permissions():
    """获取权限列表"""
    permissions = Permission.query.all()
    return success_response(data=[p.to_dict() for p in permissions])

