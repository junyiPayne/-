"""AI服务路由"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.daily_log import DailyLog
from app.utils.decorators import login_required
from app.utils.errors import NotFoundError, ValidationError
from app.utils.response import success_response
from app.services.ai_service import ai_service
from datetime import datetime, timedelta, date

bp = Blueprint('ai', __name__)

@bp.route('/health-assessment', methods=['POST'])
@login_required
def get_health_assessment():
    """获取AI健康风险评估"""
    user_id = get_jwt_identity()
    data = request.get_json()
    weeks = data.get('weeks', 4)
    
    # 获取用户档案
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        raise NotFoundError("请先创建用户档案")
    
    # 获取最近N周的数据
    end_date = date.today()
    start_date = end_date - timedelta(weeks=weeks)
    
    logs = DailyLog.query.filter(
        DailyLog.user_id == user_id,
        DailyLog.log_date >= start_date,
        DailyLog.log_date <= end_date
    ).all()
    
    # 统计数据
    if logs:
        total_intake = sum(log.calorie_intake or 0 for log in logs)
        total_expenditure = sum(log.calorie_expenditure or 0 for log in logs)
        avg_intake = total_intake / len(logs)
        avg_expenditure = total_expenditure / len(logs)
        
        # 统计宏量营养素平均值
        avg_carb = sum(log.carb_percent or 0 for log in logs) / len(logs)
        avg_protein = sum(log.protein_percent or 0 for log in logs) / len(logs)
        avg_fat = sum(log.fat_percent or 0 for log in logs) / len(logs)
        
        # 统计运动平均值
        avg_exercise_duration = sum(log.exercise_duration or 0 for log in logs) / len(logs)
    else:
        avg_intake = profile.bmr or 2000
        avg_expenditure = profile.bmr or 2000
        avg_carb = 50
        avg_protein = 20
        avg_fat = 30
        avg_exercise_duration = 0
    
    log_data = {
        'avg_daily_intake': avg_intake,
        'avg_daily_expenditure': avg_expenditure,
        'carb_percent': avg_carb,
        'protein_percent': avg_protein,
        'fat_percent': avg_fat,
        'exercise_duration': avg_exercise_duration,
        'predicted_weight_change_kg': data.get('predicted_weight_change', 0)
    }
    
    # 调用AI服务
    assessment = ai_service.generate_health_assessment(
        profile.to_dict(),
        log_data,
        weeks
    )
    
    return success_response(data=assessment, message="AI分析完成")

@bp.route('/prediction', methods=['POST'])
@login_required
def get_prediction():
    """获取AI预测（用于干预工坊）"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔵 收到AI预测请求")
        user_id = get_jwt_identity()
        logger.info(f"🔵 用户ID: {user_id}")
        
        data = request.get_json()
        logger.info(f"🔵 请求参数: {data}")
        
        # 获取用户档案
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            logger.error("❌ 用户档案不存在")
            raise NotFoundError("请先创建用户档案")
        
        logger.info(f"🔵 用户档案获取成功: {profile.name if hasattr(profile, 'name') else '未知'}")
        
        # 获取预测参数（支持干预工坊的详细参数）
        calorie_intake = data.get('calorie_intake', profile.bmr or 2000)
        calorie_expenditure = data.get('calorie_expenditure', profile.bmr or 2000)
        weeks = data.get('weeks', 4)
        
        # 调用AI生成预测
        profile_data = profile.to_dict()
        log_data = {
            'avg_daily_intake': calorie_intake,
            'avg_daily_expenditure': calorie_expenditure,
            'calorie_intake': calorie_intake,  # 兼容字段
            'calorie_expenditure': calorie_expenditure,  # 兼容字段
            'carb_percent': data.get('carb_percent', 50),
            'protein_percent': data.get('protein_percent', 20),
            'fat_percent': data.get('fat_percent', 30),
            'fiber_grams': data.get('fiber_grams', 25),
            'alcohol_grams': data.get('alcohol_grams', 0),
            'exercise_duration': data.get('exercise_duration', 0),
            'aerobic_freq': data.get('aerobic_freq', 3),
            'aerobic_intensity': data.get('aerobic_intensity', 5),
            'steps': data.get('steps', 6000),
            'predicted_weight_change_kg': 0
        }
        
        logger.info(f"🔵 准备调用AI服务，预测周数: {weeks}")
        assessment = ai_service.generate_health_assessment(
            profile_data,
            log_data,
            weeks
        )
        
        logger.info(f"✅ AI预测完成，建议数量: {len(assessment.get('suggestions', []))}")
        
        return success_response(data={
            'assessment': assessment,
            'prediction_period': f"{weeks}周",
            'current_weight': profile.weight_kg,
            'predicted_weight_change': assessment.get('weight', '0 kg')
        }, message="AI预测完成")
    except Exception as e:
        logger.error(f"❌ AI预测请求处理失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        raise

