"""用户档案路由"""
from flask import Blueprint, request, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.profile import UserProfile
from app.utils.decorators import login_required
from app.utils.errors import NotFoundError, ValidationError
from app.utils.response import success_response
from app.utils.calculations import (
    calculate_bmi, calculate_bmr, calculate_whr, calculate_whtr,
    assess_weight_category_by_bmi, assess_body_fat_category,
    assess_central_obesity_by_whr, assess_visceral_fat_by_whtr,
    assess_obesity_by_waist
)
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from datetime import datetime, date

bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """上传头像"""
    if 'file' not in request.files:
        raise ValidationError("没有文件部分")
    file = request.files['file']
    if file.filename == '':
        raise ValidationError("没有选择文件")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 生成唯一文件名
        unique_filename = f"avatar_{uuid.uuid4().hex}.jpg"
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        filepath = os.path.join(upload_folder, unique_filename)
        
        try:
            # 处理图片
            image = Image.open(file)
            # 如果是RGBA模式（如PNG），转换为RGB
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
                
            # 调整大小为 400x400
            image = image.resize((400, 400), Image.Resampling.LANCZOS)
            
            # 保存
            image.save(filepath, 'JPEG', quality=85)
            
            # 更新用户头像
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            file_url = f"/api/profile/avatar/{unique_filename}"
            user.avatar = file_url
            db.session.commit()
            
            return success_response(data={'url': file_url}, message="头像上传成功")
        except Exception as e:
            raise ValidationError(f"图片处理失败: {str(e)}")
    else:
        raise ValidationError("不支持的文件类型")

@bp.route('/avatar/<filename>')
def get_avatar_image(filename):
    """获取头像图片"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
    return send_from_directory(upload_folder, filename)

@bp.route('', methods=['GET'])
@login_required
def get_profile():
    """获取用户档案"""
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return success_response(data=None, message="档案不存在，请先创建")
    
    return success_response(data=profile.to_dict())

@bp.route('', methods=['POST'])
@login_required
def create_profile():
    """创建用户档案"""
    user_id = get_jwt_identity()
    
    # 检查是否已存在档案
    existing_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if existing_profile:
        raise ValidationError("档案已存在，请使用更新接口")
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['gender', 'age', 'height_cm', 'weight_kg']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"{field}不能为空")
    
    # 创建档案
    profile = UserProfile(
        user_id=user_id,
        gender=data['gender'],
        age=data['age'],
        height_cm=data['height_cm'],
        weight_kg=data['weight_kg'],
        waist_cm=data.get('waist_cm'),
        hip_cm=data.get('hip_cm'),
        body_fat_percent=data.get('body_fat_percent')
    )
    
    if 'birthday' in data and data['birthday']:
        try:
            profile.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        except ValueError:
            pass # Ignore invalid date format
            
    # 更新真实姓名
    if 'real_name' in data:
        user = User.query.get(user_id)
        if user:
            user.real_name = data['real_name']

    # 计算各项指标
    try:
        _calculate_profile_indicators(profile)
    except Exception as e:
        # 记录错误但不中断流程，指标可能为空
        print(f"Error calculating profile indicators: {e}")
    
    db.session.add(profile)
    db.session.commit()
    
    return success_response(data=profile.to_dict(), message="档案创建成功")

@bp.route('', methods=['PUT'])
@login_required
def update_profile():
    """更新用户档案"""
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first_or_404()
    
    data = request.get_json()
    
    if 'birthday' in data and data['birthday']:
        try:
            profile.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        except ValueError:
            pass
            
    # 更新真实姓名
    if 'real_name' in data:
        user = User.query.get(user_id)
        if user:
            user.real_name = data['real_name']
            
    # 更新字段
    if 'gender' in data:
        profile.gender = data['gender']
    if 'age' in data:
        profile.age = data['age']
    if 'height_cm' in data:
        profile.height_cm = data['height_cm']
    if 'weight_kg' in data:
        profile.weight_kg = data['weight_kg']
    if 'waist_cm' in data:
        profile.waist_cm = data.get('waist_cm')
    if 'hip_cm' in data:
        profile.hip_cm = data.get('hip_cm')
    if 'body_fat_percent' in data:
        profile.body_fat_percent = data.get('body_fat_percent')
    
    # 重新计算指标
    try:
        _calculate_profile_indicators(profile)
    except Exception as e:
        print(f"Error calculating profile indicators: {e}")
    
    db.session.commit()
    
    return success_response(data=profile.to_dict(), message="档案更新成功")

def _calculate_profile_indicators(profile):
    """计算档案的各项指标"""
    # 计算BMI
    if profile.weight_kg and profile.height_cm:
        profile.bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
        profile.weight_category = assess_weight_category_by_bmi(profile.bmi)
    
    # 计算BMR
    if profile.gender and profile.weight_kg and profile.height_cm and profile.age:
        profile.bmr = calculate_bmr(profile.gender, profile.weight_kg, profile.height_cm, profile.age)
    
    # 计算腰臀比
    if profile.waist_cm and profile.hip_cm:
        profile.whr = calculate_whr(profile.waist_cm, profile.hip_cm)
    
    # 计算腰高比
    if profile.waist_cm and profile.height_cm:
        profile.whtr = calculate_whtr(profile.waist_cm, profile.height_cm)
    
    # 评估体脂等级
    if profile.body_fat_percent and profile.gender and profile.age:
        profile.body_fat_category = assess_body_fat_category(
            profile.gender, profile.age, profile.body_fat_percent
        )
    
    # 评估中心性肥胖和内脏脂肪
    if profile.whr and profile.gender:
        central_obesity = assess_central_obesity_by_whr(profile.gender, profile.whr)
        if central_obesity == '中心性肥胖':
            if profile.weight_category:
                if '中心性肥胖' not in profile.weight_category:
                    profile.weight_category = profile.weight_category + '（中心性肥胖）'
            else:
                profile.weight_category = '中心性肥胖'
    
    if profile.whtr:
        visceral_fat = assess_visceral_fat_by_whtr(profile.whtr)
        if visceral_fat == '内脏脂肪超标':
            if profile.weight_category:
                if '内脏脂肪超标' not in profile.weight_category:
                    profile.weight_category = profile.weight_category + '（内脏脂肪超标）'
            else:
                profile.weight_category = '内脏脂肪超标'
    
    # 评估腰围肥胖
    if profile.waist_cm and profile.gender:
        waist_obesity = assess_obesity_by_waist(profile.gender, profile.waist_cm)
        if waist_obesity == '肥胖':
             if profile.weight_category:
                if '腹型肥胖' not in profile.weight_category: # 使用腹型肥胖区别于BMI肥胖
                    profile.weight_category = profile.weight_category + '（腹型肥胖）'
             else:
                profile.weight_category = '腹型肥胖'

