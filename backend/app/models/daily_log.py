"""每日日志模型 - 运动和饮食记录"""
from datetime import datetime, date
from app import db

class DailyLog(db.Model):
    """每日日志模型 - 记录运动和饮食情况"""
    __tablename__ = 'daily_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, index=True)
    
    # 饮食记录
    calorie_intake = db.Column(db.Float, default=0)  # 每日摄入热量(kcal)
    carb_percent = db.Column(db.Float)  # 碳水百分比
    protein_percent = db.Column(db.Float)  # 蛋白质百分比
    fat_percent = db.Column(db.Float)  # 脂肪百分比
    fiber_grams = db.Column(db.Float)  # 膳食纤维(克)
    alcohol_grams = db.Column(db.Float, default=0)  # 酒精(克)
    food_images = db.Column(db.Text)  # 食物图片URL（JSON格式存储）
    food_description = db.Column(db.Text)  # 食物描述
    
    # 运动记录
    exercise_type = db.Column(db.String(100))  # 运动类型
    exercise_duration = db.Column(db.Integer)  # 运动时长(分钟)
    exercise_intensity = db.Column(db.String(50))  # 运动强度
    exercise_frequency = db.Column(db.Integer)  # 运动频率(次/周)
    calorie_expenditure = db.Column(db.Float, default=0)  # 运动消耗热量(kcal)
    
    # 身体指标记录（每日测量）
    daily_weight = db.Column(db.Float)  # 当日体重(kg)
    daily_waist = db.Column(db.Float)  # 当日腰围(cm)
    daily_hip = db.Column(db.Float)  # 当日臀围(cm)
    
    # 计算指标
    net_calorie = db.Column(db.Float)  # 净热量(摄入-消耗)
    predicted_weight_change = db.Column(db.Float)  # 预测体重变化(kg)
    
    # AI分析
    ai_risk_assessment = db.Column(db.Text)  # AI健康风险评估
    ai_suggestions = db.Column(db.Text)  # AI建议（JSON格式）
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = db.relationship('User', backref='daily_logs', lazy=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'log_date': self.log_date.isoformat() if self.log_date else None,
            'calorie_intake': self.calorie_intake,
            'carb_percent': self.carb_percent,
            'protein_percent': self.protein_percent,
            'fat_percent': self.fat_percent,
            'fiber_grams': self.fiber_grams,
            'alcohol_grams': self.alcohol_grams,
            'food_images': self.food_images,
            'food_description': self.food_description,
            'exercise_type': self.exercise_type,
            'exercise_duration': self.exercise_duration,
            'exercise_intensity': self.exercise_intensity,
            'exercise_frequency': self.exercise_frequency,
            'calorie_expenditure': self.calorie_expenditure,
            'daily_weight': self.daily_weight,
            'daily_waist': self.daily_waist,
            'daily_hip': self.daily_hip,
            'net_calorie': self.net_calorie,
            'predicted_weight_change': self.predicted_weight_change,
            'ai_risk_assessment': self.ai_risk_assessment,
            'ai_suggestions': self.ai_suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DailyLog user_id={self.user_id} date={self.log_date}>'

