from datetime import datetime
from app import db

class BusinessData(db.Model):
    """业务数据模型"""
    __tablename__ = 'business_data'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(50), index=True)
    status = db.Column(db.String(20), default='active', index=True)
    priority = db.Column(db.Integer, default=0)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    creator = db.relationship('User', backref='business_data', lazy=True)
    
    def to_dict(self, include_creator=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_creator and self.creator:
            data['creator_name'] = self.creator.username
        return data
    
    def __repr__(self):
        return f'<BusinessData {self.title}>'

