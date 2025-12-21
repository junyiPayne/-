from datetime import datetime
from app import db

class Report(db.Model):
    """学生报告模型 - 每个用户只有一个报告"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)  # 唯一约束，确保每个用户只有一个报告
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)  # 保留字段，兼容旧数据
    pdf_content = db.Column(db.LargeBinary, nullable=True)  # PDF二进制内容
    data_hash = db.Column(db.String(64), nullable=True)  # 报告数据内容的哈希值，用于判断是否有变化
    status = db.Column(db.String(20), default='submitted')  # submitted, reviewed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    user = db.relationship('User', backref=db.backref('report', uselist=False, lazy=True))  # 一对一关系
    history = db.relationship('ReportHistory', backref='report', lazy=True, order_by='ReportHistory.created_at.desc()')
    
    def to_dict(self, include_history=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'student_name': self.user.real_name or self.user.username,
            'title': self.title,
            'file_path': self.file_path,
            'has_pdf': self.pdf_content is not None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_history:
            data['history'] = [h.to_dict() for h in self.history]
        return data


class ReportHistory(db.Model):
    """报告修改日志"""
    __tablename__ = 'report_history'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    modified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 修改者ID
    action = db.Column(db.String(50), nullable=False)  # 'created', 'updated', 'edited'
    description = db.Column(db.String(500))  # 修改描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    modified_by = db.relationship('User', foreign_keys=[modified_by_id], lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'modified_by': self.modified_by.real_name or self.modified_by.username if self.modified_by else '未知',
            'action': self.action,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
