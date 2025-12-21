from datetime import datetime
from app import db

# 角色权限关联表
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 多对多关系
    permissions = db.relationship('Permission', secondary=role_permissions, lazy='subquery',
                                  backref=db.backref('roles', lazy=True))
    
    def to_dict(self, include_permissions=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
        if include_permissions:
            data['permissions'] = [p.to_dict() for p in self.permissions]
        return data
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    resource = db.Column(db.String(50))  # 资源类型: user, role, business等
    action = db.Column(db.String(50))    # 操作: create, read, update, delete
    description = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'resource': self.resource,
            'action': self.action,
            'description': self.description
        }
    
    def __repr__(self):
        return f'<Permission {self.code}>'

