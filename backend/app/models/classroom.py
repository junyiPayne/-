"""班级模型"""
from datetime import datetime
from app import db

class Classroom(db.Model):
    """班级模型"""
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='班级名称')
    description = db.Column(db.Text, comment='班级描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系 - User模型通过class_id外键关联，backref='classroom'在User模型中定义
    
    def to_dict(self, include_users=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_users:
            # 统计班级中的学生和教师数量
            from app.models.user import User
            from app.models.role import Role
            
            student_role = Role.query.filter_by(code='student').first()
            teacher_role = Role.query.filter_by(code='teacher').first()
            
            student_count = User.query.filter_by(class_id=self.id, role_id=student_role.id if student_role else None).count()
            teacher_count = User.query.filter_by(class_id=self.id, role_id=teacher_role.id if teacher_role else None).count()
            
            data['student_count'] = student_count
            data['teacher_count'] = teacher_count
        
        return data
    
    def __repr__(self):
        return f'<Classroom {self.name}>'
