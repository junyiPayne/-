from app import db
from datetime import datetime

class UserSettings(db.Model):
    """用户个性化设置模型"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
    
    # 字体设置
    fontSize = db.Column(db.Integer, default=14, comment='字体大小（px）')
    fontFamily = db.Column(db.String(100), default='Arial, sans-serif', comment='字体样式')
    fontColor = db.Column(db.String(20), default='#303133', comment='字体颜色')
    customFontName = db.Column(db.String(100), nullable=True, comment='自定义字体名称')
    customFontUrl = db.Column(db.String(500), nullable=True, comment='自定义字体文件URL')
    
    # 导航栏设置
    headerColor = db.Column(db.String(20), default='#304156', comment='导航栏背景色（单色模式）')
    headerUseGradient = db.Column(db.Boolean, default=False, comment='是否使用渐变')
    headerGradientType = db.Column(db.String(20), default='linear', comment='渐变类型：linear/radial')
    headerGradientColor1 = db.Column(db.String(20), default='#304156', comment='渐变颜色1')
    headerGradientColor2 = db.Column(db.String(20), default='#409EFF', comment='渐变颜色2')
    headerGradientDirection = db.Column(db.String(50), default='to right', comment='渐变方向')
    
    # 侧边栏设置
    sidebarColor = db.Column(db.String(20), default='#fff', comment='侧边栏背景色（单色模式）')
    sidebarUseGradient = db.Column(db.Boolean, default=False, comment='侧边栏是否使用渐变')
    sidebarGradientType = db.Column(db.String(20), default='linear', comment='侧边栏渐变类型')
    sidebarGradientColor1 = db.Column(db.String(20), default='#fff', comment='侧边栏渐变颜色1')
    sidebarGradientColor2 = db.Column(db.String(20), default='#f0f2f5', comment='侧边栏渐变颜色2')
    sidebarGradientDirection = db.Column(db.String(50), default='to bottom', comment='侧边栏渐变方向')
    
    # 内容区域设置
    contentBackgroundColor = db.Column(db.String(20), default='#f0f2f5', comment='内容区域背景色')
    backgroundImageUrl = db.Column(db.String(500), nullable=True, comment='背景图片URL')
    backgroundImageOpacity = db.Column(db.Float, default=1.0, comment='背景图片不透明度（0-1）')
    
    # Logo设置
    logoSize = db.Column(db.Integer, default=40, comment='Logo大小（px）')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = db.relationship('User', backref='settings', uselist=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'fontSize': self.fontSize,
            'fontFamily': self.fontFamily,
            'fontColor': self.fontColor,
            'customFontName': self.customFontName,
            'customFontUrl': self.customFontUrl,
            'headerColor': self.headerColor,
            'headerUseGradient': self.headerUseGradient,
            'headerGradientType': self.headerGradientType,
            'headerGradientColor1': self.headerGradientColor1,
            'headerGradientColor2': self.headerGradientColor2,
            'headerGradientDirection': self.headerGradientDirection,
            'sidebarColor': self.sidebarColor,
            'sidebarUseGradient': self.sidebarUseGradient,
            'sidebarGradientType': self.sidebarGradientType,
            'sidebarGradientColor1': self.sidebarGradientColor1,
            'sidebarGradientColor2': self.sidebarGradientColor2,
            'sidebarGradientDirection': self.sidebarGradientDirection,
            'contentBackgroundColor': self.contentBackgroundColor,
            'backgroundImageUrl': self.backgroundImageUrl,
            'backgroundImageOpacity': self.backgroundImageOpacity,
            'logoSize': self.logoSize,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
