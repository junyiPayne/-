"""用户档案模型 - 运动生理基础数据"""
from datetime import datetime
from app import db

class UserProfile(db.Model):
    """用户档案模型 - 存储基础生理数据"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
    
    # 基础数据
    gender = db.Column(db.String(10))  # 性别: male/female
    birthday = db.Column(db.Date)  # 出生日期
    age = db.Column(db.Integer)  # 年龄
    height_cm = db.Column(db.Float)  # 身高(cm)
    weight_kg = db.Column(db.Float)  # 体重(kg)
    waist_cm = db.Column(db.Float)  # 腰围(cm)
    hip_cm = db.Column(db.Float)  # 臀围(cm)
    body_fat_percent = db.Column(db.Float)  # 体脂百分比
    
    # 计算指标
    bmi = db.Column(db.Float)  # BMI
    bmr = db.Column(db.Float)  # 基础代谢率(kcal/天)
    whr = db.Column(db.Float)  # 腰臀比
    whtr = db.Column(db.Float)  # 腰高比
    
    # 评估结果
    weight_category = db.Column(db.String(50))  # 体重等级
    body_fat_category = db.Column(db.String(50))  # 体脂等级
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = db.relationship('User', backref='profile', uselist=False)
    
    def to_dict(self):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'gender': self.gender,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'age': self.age,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'waist_cm': self.waist_cm,
            'hip_cm': self.hip_cm,
            'body_fat_percent': self.body_fat_percent,
            'bmi': self.bmi,
            'bmr': self.bmr,
            'whr': self.whr,
            'whtr': self.whtr,
            'weight_category': self.weight_category,
            'body_fat_category': self.body_fat_category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if self.user:
            if self.user.avatar:
                data['avatar'] = self.user.avatar
            if self.user.real_name:
                data['real_name'] = self.user.real_name
        return data
    
    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'

