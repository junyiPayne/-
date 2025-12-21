from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.business import BusinessData
from sqlalchemy import or_
from app.utils.decorators import login_required
from app.utils.errors import NotFoundError, ValidationError
from app.utils.response import success_response

bp = Blueprint('business', __name__)

@bp.route('/data', methods=['GET'])
@login_required
def get_business_data():
    """获取业务数据列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search', '')
    
    query = BusinessData.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                BusinessData.title.like(f'%{search}%'),
                BusinessData.content.like(f'%{search}%')
            )
        )
    
    # 分类过滤
    if category:
        query = query.filter_by(category=category)
    
    # 状态过滤
    if status:
        query = query.filter_by(status=status)
    
    # 排序
    query = query.order_by(BusinessData.created_at.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return success_response({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@bp.route('/data/<int:data_id>', methods=['GET'])
@login_required
def get_business_data_detail(data_id):
    """获取业务数据详情"""
    data = BusinessData.query.get_or_404(data_id)
    return success_response(data=data.to_dict())

@bp.route('/data', methods=['POST'])
@login_required
def create_business_data():
    """创建业务数据"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('title'):
        raise ValidationError("标题不能为空")
    
    business_data = BusinessData(
        title=data['title'],
        content=data.get('content'),
        category=data.get('category'),
        status=data.get('status', 'active'),
        priority=data.get('priority', 0),
        creator_id=user_id
    )
    
    db.session.add(business_data)
    db.session.commit()
    
    return success_response(data=business_data.to_dict(), message="创建成功")

@bp.route('/data/<int:data_id>', methods=['PUT'])
@login_required
def update_business_data(data_id):
    """更新业务数据"""
    user_id = get_jwt_identity()
    business_data = BusinessData.query.get_or_404(data_id)
    
    # 只能修改自己创建的数据，除非是管理员
    from app.models.user import User
    current_user = User.query.get(user_id)
    if business_data.creator_id != user_id:
        if not current_user.role or current_user.role.code != 'admin':
            from app.utils.errors import PermissionDeniedError
            raise PermissionDeniedError("只能修改自己创建的数据")
    
    data = request.get_json()
    
    if 'title' in data:
        business_data.title = data['title']
    if 'content' in data:
        business_data.content = data['content']
    if 'category' in data:
        business_data.category = data['category']
    if 'status' in data:
        business_data.status = data['status']
    if 'priority' in data:
        business_data.priority = data['priority']
    
    db.session.commit()
    
    return success_response(data=business_data.to_dict(), message="更新成功")

@bp.route('/data/<int:data_id>', methods=['DELETE'])
@login_required
def delete_business_data(data_id):
    """删除业务数据"""
    user_id = get_jwt_identity()
    business_data = BusinessData.query.get_or_404(data_id)
    
    # 只能删除自己创建的数据，除非是管理员
    from app.models.user import User
    current_user = User.query.get(user_id)
    if business_data.creator_id != user_id:
        if not current_user.role or current_user.role.code != 'admin':
            from app.utils.errors import PermissionDeniedError
            raise PermissionDeniedError("只能删除自己创建的数据")
    
    db.session.delete(business_data)
    db.session.commit()
    
    return success_response(message="删除成功")

@bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """获取系统统计数据"""
    from app.models.user import User
    from app.models.role import Role
    
    # 业务数据统计
    total_business = BusinessData.query.count()
    active_business = BusinessData.query.filter_by(status='active').count()
    
    # 用户统计
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # 角色统计
    total_roles = Role.query.count()
    
    return success_response(data={
        'business_count': total_business,
        'active_business_count': active_business,
        'user_count': total_users,
        'active_user_count': active_users,
        'role_count': total_roles
    })

