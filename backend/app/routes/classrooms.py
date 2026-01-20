"""班级管理路由"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.classroom import Classroom
from app.models.user import User
from app.models.role import Role
from app.utils.decorators import login_required, admin_required
from app.utils.errors import ValidationError, NotFoundError
from app.utils.response import success_response

bp = Blueprint('classrooms', __name__)

@bp.route('', methods=['GET'])
@login_required
def get_classrooms():
    """获取班级列表"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.role:
        raise ValidationError("无权访问")
    
    # 管理员可以看到所有班级，教师和学生只能看到自己的班级
    if current_user.role.code == 'admin':
        classrooms = Classroom.query.all()
    else:
        # 教师和学生只能看到自己所在的班级
        if current_user.class_id:
            classrooms = Classroom.query.filter_by(id=current_user.class_id).all()
        else:
            classrooms = []
    
    return success_response(data=[c.to_dict(include_users=True) for c in classrooms])

@bp.route('', methods=['POST'])
@admin_required
def create_classroom():
    """创建班级（仅管理员）"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    if not name:
        raise ValidationError("班级名称不能为空")
    
    # 检查班级名称是否已存在
    if Classroom.query.filter_by(name=name).first():
        raise ValidationError("班级名称已存在")
    
    description = data.get('description', '').strip()
    
    classroom = Classroom(name=name, description=description)
    db.session.add(classroom)
    db.session.commit()
    
    return success_response(data=classroom.to_dict(), message="班级创建成功")

@bp.route('/<int:classroom_id>', methods=['PUT'])
@admin_required
def update_classroom(classroom_id):
    """更新班级信息（仅管理员）"""
    classroom = Classroom.query.get_or_404(classroom_id)
    data = request.get_json()
    
    name = data.get('name', '').strip()
    if name and name != classroom.name:
        # 检查新名称是否已存在
        if Classroom.query.filter_by(name=name).first():
            raise ValidationError("班级名称已存在")
        classroom.name = name
    
    if 'description' in data:
        classroom.description = data['description'].strip()
    
    db.session.commit()
    
    return success_response(data=classroom.to_dict(), message="班级更新成功")

@bp.route('/<int:classroom_id>', methods=['DELETE'])
@admin_required
def delete_classroom(classroom_id):
    """删除班级（仅管理员）"""
    classroom = Classroom.query.get_or_404(classroom_id)
    
    # 检查是否有用户关联到此班级
    user_count = User.query.filter_by(class_id=classroom_id).count()
    if user_count > 0:
        raise ValidationError(f"无法删除班级，该班级还有 {user_count} 个用户")
    
    db.session.delete(classroom)
    db.session.commit()
    
    return success_response(message="班级删除成功")

@bp.route('/<int:classroom_id>/users', methods=['GET'])
@login_required
def get_classroom_users(classroom_id):
    """获取班级用户列表"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.role:
        raise ValidationError("无权访问")
    
    classroom = Classroom.query.get_or_404(classroom_id)
    
    # 权限检查：管理员可以查看所有班级，教师只能查看自己班级的学生
    if current_user.role.code == 'admin':
        # 管理员可以查看所有班级
        pass
    elif current_user.role.code == 'teacher':
        # 教师只能查看自己班级的学生
        if current_user.class_id != classroom_id:
            raise ValidationError("无权查看该班级的学生")
    else:
        # 学生只能查看自己班级
        if current_user.class_id != classroom_id:
            raise ValidationError("无权查看该班级")
    
    # 获取班级中的用户
    users = User.query.filter_by(class_id=classroom_id).all()
    
    # 区分学生和教师
    student_role = Role.query.filter_by(code='student').first()
    teacher_role = Role.query.filter_by(code='teacher').first()
    
    students = [u.to_dict(include_classroom=True) for u in users if u.role_id == (student_role.id if student_role else None)]
    teachers = [u.to_dict(include_classroom=True) for u in users if u.role_id == (teacher_role.id if teacher_role else None)]
    
    return success_response(data={
        'classroom': classroom.to_dict(),
        'students': students,
        'teachers': teachers
    })

@bp.route('/available', methods=['GET'])
def get_available_classrooms():
    """获取可用的班级列表（用于注册时选择，无需登录）"""
    classrooms = Classroom.query.all()
    return success_response(data=[{'id': c.id, 'name': c.name} for c in classrooms])
