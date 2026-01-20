from datetime import datetime
from app import db
import bcrypt

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=True, index=True, comment='班级ID')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    role = db.relationship('Role', backref='users', lazy=True)
    classroom = db.relationship('Classroom', backref='users', lazy=True)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self, include_role=True, include_classroom=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'phone': self.phone,
            'avatar': self.avatar,
            'role_id': self.role_id,
            'class_id': self.class_id,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_role and self.role:
            data['role_name'] = self.role.name
            data['role_code'] = self.role.code
        if include_classroom and self.classroom:
            data['classroom_name'] = self.classroom.name
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'

