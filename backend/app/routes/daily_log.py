"""每日日志路由"""
from flask import Blueprint, request, current_app, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.models.profile import UserProfile
from app.models.daily_log import DailyLog
from app.utils.decorators import login_required
from app.utils.errors import NotFoundError, ValidationError
from app.utils.response import success_response
from app.utils.calculations import (
    calculate_weight_change, calculate_calorie_expenditure,
    predict_future_weight, calculate_recommended_calories, calculate_bmi
)
from app.services.ai_service import ai_service
import json

bp = Blueprint('daily_log', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    """上传图片（临时存储，不存入数据库）"""
    if 'file' not in request.files:
        raise ValidationError("没有文件部分")
    file = request.files['file']
    if file.filename == '':
        raise ValidationError("没有选择文件")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 生成唯一文件名
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 使用临时目录存储，不存入数据库
        temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
            
        file_path = os.path.join(temp_folder, unique_filename)
        file.save(file_path)
        
        # 返回文件URL和文件路径（用于后续识别和删除）
        file_url = f"/api/daily-log/image/{unique_filename}"
        return success_response(data={
            'url': file_url,
            'filename': unique_filename,
            'path': file_path
        }, message="上传成功（临时存储，保存记录后将自动删除）")
    else:
        raise ValidationError("不支持的文件类型")

@bp.route('/image/<filename>')
def get_image(filename):
    """获取图片（从临时目录或正式目录）"""
    # 先尝试临时目录
    temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
    temp_path = os.path.join(temp_folder, filename)
    if os.path.exists(temp_path):
        return send_from_directory(temp_folder, filename)
    
    # 如果临时目录没有，尝试正式目录（兼容旧数据）
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    upload_path = os.path.join(upload_folder, filename)
    if os.path.exists(upload_path):
        return send_from_directory(upload_folder, filename)
    
    raise NotFoundError("图片不存在")

@bp.route('/recognize-food', methods=['POST'])
@login_required
def recognize_food():
    """AI识别食物"""
    data = request.get_json()
    image_path = data.get('image_path')
    
    if not image_path:
        raise ValidationError("请提供图片路径")
    
    # 检查文件是否存在（支持绝对路径和相对路径）
    if not os.path.exists(image_path):
        # 尝试从临时目录查找
        temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
        filename = os.path.basename(image_path)
        temp_path = os.path.join(temp_folder, filename)
        if os.path.exists(temp_path):
            image_path = temp_path
        else:
            raise NotFoundError("图片文件不存在")
    
    # 调用AI识别
    import sys
    print("=" * 80, file=sys.stderr)
    print(f"🍽️ 开始AI识别食物，图片路径: {image_path}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    try:
        result = ai_service.recognize_food_from_image(image_path)
        print("=" * 80, file=sys.stderr)
        print(f"✅ AI识别完成，结果: {result}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        return success_response(data=result, message="识别成功")
    except Exception as e:
        import traceback
        print("=" * 80, file=sys.stderr)
        print(f"❌ 识别失败: {str(e)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        raise ValidationError(f"识别失败: {str(e)}")

@bp.route('/delete-temp-image', methods=['POST'])
@login_required
def delete_temp_image():
    """删除临时图片"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        raise ValidationError("请提供文件名")
    
    # 删除临时文件
    temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
    file_path = os.path.join(temp_folder, filename)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return success_response(message="临时图片已删除")
        except Exception as e:
            print(f"删除临时图片失败: {str(e)}")
            return success_response(message="删除失败，但不影响保存")
    
    return success_response(message="文件不存在或已删除")

@bp.route('', methods=['GET'])
@login_required
def get_logs():
    """获取日志列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = DailyLog.query.filter_by(user_id=user_id)
    
    # 日期筛选
    if start_date:
        query = query.filter(DailyLog.log_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(DailyLog.log_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # 排序：最新的在前
    query = query.order_by(DailyLog.log_date.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return success_response({
        'items': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """获取统计信息"""
    user_id = get_jwt_identity()
    weeks = request.args.get('weeks', 4, type=int)
    month = request.args.get('month') # 格式: YYYY-MM
    
    query = DailyLog.query.filter(DailyLog.user_id == user_id)
    
    if month:
        try:
            # 解析月份
            year, month_val = map(int, month.split('-'))
            # 计算该月的起始和结束日期
            import calendar
            _, last_day = calendar.monthrange(year, month_val)
            start_date = date(year, month_val, 1)
            end_date = date(year, month_val, last_day)
            
            query = query.filter(
                DailyLog.log_date >= start_date,
                DailyLog.log_date <= end_date
            )
        except ValueError:
            raise ValidationError("月份格式错误，请使用YYYY-MM格式")
    else:
        # 默认获取最近N周的数据
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        query = query.filter(
            DailyLog.log_date >= start_date,
            DailyLog.log_date <= end_date
        )
    
    logs = query.order_by(DailyLog.log_date.asc()).all()
    
    # 统计数据
    total_calorie_intake = sum(log.calorie_intake or 0 for log in logs)
    total_calorie_expenditure = sum(log.calorie_expenditure or 0 for log in logs)
    avg_daily_intake = total_calorie_intake / len(logs) if logs else 0
    avg_daily_expenditure = total_calorie_expenditure / len(logs) if logs else 0
    
    # 获取用户档案
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    # 预测体重变化
    predicted_weight_change = None
    
    # 处理日志列表，添加推荐值
    processed_logs = []
    
    # 预处理 Profile 数据
    profile_data = {}
    if profile:
        goal_map = {'减脂': 'lose', '增肌': 'gain', '保持': 'maintain'}
        activity_map = {
            '久坐': 'sedentary', '轻度活动': 'light', '中度活动': 'moderate',
            '重度活动': 'active', '极重度活动': 'very_active'
        }
        profile_data = {
            'gender': profile.gender,
            'height_cm': profile.height_cm,
            'goal': goal_map.get(getattr(profile, 'goal', '保持'), 'maintain'),
            'activity': activity_map.get(getattr(profile, 'activity_level', '中度活动'), 'moderate'),
            'weight_kg': profile.weight_kg
        }

    for log in logs:
        log_dict = log.to_dict()
        
        if profile:
            # 优先使用当天的体重，否则使用 Profile 体重
            current_weight = log.daily_weight or profile_data['weight_kg']
            
            # 计算当天的 BMI
            current_bmi = calculate_bmi(current_weight, profile_data['height_cm'])
            
            # 计算推荐值
            rec_intake, rec_expenditure = calculate_recommended_calories(
                weight_kg=current_weight,
                gender=profile_data['gender'],
                activity_level=profile_data['activity'],
                goal=profile_data['goal'],
                bmi=current_bmi
            )
            
            log_dict['recommended_intake'] = rec_intake
            log_dict['recommended_expenditure'] = rec_expenditure
        else:
            log_dict['recommended_intake'] = None
            log_dict['recommended_expenditure'] = None
            
        processed_logs.append(log_dict)

    if profile and logs:
        avg_intake = avg_daily_intake
        # 这里的avg_daily_expenditure是日志中记录的运动消耗
        # 总消耗 = BMR/0.7 (估算基础消耗) + 运动消耗
        # 参见 calculations.py 中的 calculate_calorie_expenditure 说明
        
        base_expenditure = 0
        if profile.bmr:
            base_expenditure = profile.bmr / 0.7
            
        total_avg_expenditure = base_expenditure + avg_daily_expenditure
        
        predicted_weight_change = calculate_weight_change(
            avg_intake, total_avg_expenditure, (end_date - start_date).days + 1
        )
    
    return success_response(data={
        'weeks': weeks,
        'month': month,
        'total_logs': len(logs),
        'avg_daily_intake': round(avg_daily_intake, 2),
        'avg_daily_expenditure': round(avg_daily_expenditure, 2), # 仅显示运动消耗
        'total_estimated_expenditure': round(total_avg_expenditure if 'total_avg_expenditure' in locals() else 0, 2), # 显示估算的总消耗
        'predicted_weight_change_kg': predicted_weight_change,
        'logs': processed_logs
    })

@bp.route('/<string:log_date>', methods=['GET'])
@login_required
def get_log(log_date):
    """获取指定日期的日志"""
    user_id = get_jwt_identity()
    try:
        log_date_obj = datetime.strptime(log_date, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError("日期格式错误，请使用YYYY-MM-DD格式")
    
    log = DailyLog.query.filter_by(user_id=user_id, log_date=log_date_obj).first()
    
    # 获取用户档案以计算推荐值
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    recommended_intake = None
    recommended_expenditure = None
    
    if profile:
        # 映射目标到计算函数需要的格式
        goal_map = {
            '减脂': 'lose',
            '增肌': 'gain',
            '保持': 'maintain'
        }
        # 使用 getattr 防止 AttributeError，默认维持
        user_goal = getattr(profile, 'goal', '保持')
        goal = goal_map.get(user_goal, 'maintain')
        
        # 映射活动水平
        activity_map = {
            '久坐': 'sedentary',
            '轻度活动': 'light',
            '中度活动': 'moderate',
            '重度活动': 'active',
            '极重度活动': 'very_active'
        }
        # 使用 getattr 防止 AttributeError，默认中度活动
        user_activity = getattr(profile, 'activity_level', '中度活动')
        activity = activity_map.get(user_activity, 'moderate')
        
        # 使用新的 Schofield 公式计算，传入体重、性别、BMI
        recommended_intake, recommended_expenditure = calculate_recommended_calories(
            weight_kg=profile.weight_kg,
            gender=profile.gender,
            activity_level=activity,
            goal=goal,
            bmi=profile.bmi
        )
    
    data = log.to_dict() if log else {}
    data['recommended_intake'] = recommended_intake
    data['recommended_expenditure'] = recommended_expenditure
    
    if not log:
        return success_response(data=data, message="该日期没有日志记录")
    
    return success_response(data=data)

@bp.route('', methods=['POST'])
@login_required
def create_log():
    """创建或更新日志"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('log_date'):
        raise ValidationError("日期不能为空")
    
    try:
        log_date_obj = datetime.strptime(data['log_date'], '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError("日期格式错误，请使用YYYY-MM-DD格式")
    
    # 查找是否已存在该日期的日志
    log = DailyLog.query.filter_by(user_id=user_id, log_date=log_date_obj).first()
    
    if log:
        # 更新现有日志
        return _update_log(log, data, user_id)
    else:
        # 创建新日志
        log = DailyLog(
            user_id=user_id,
            log_date=log_date_obj
        )
        db.session.add(log)
        return _update_log(log, data, user_id)

def _update_log(log, data, user_id):
    """更新日志内容并计算指标"""
    # 更新饮食记录
    if 'calorie_intake' in data:
        log.calorie_intake = data.get('calorie_intake', 0)
    if 'carb_percent' in data:
        log.carb_percent = data.get('carb_percent')
    if 'protein_percent' in data:
        log.protein_percent = data.get('protein_percent')
    if 'fat_percent' in data:
        log.fat_percent = data.get('fat_percent')
    if 'fiber_grams' in data:
        log.fiber_grams = data.get('fiber_grams')
    if 'alcohol_grams' in data:
        log.alcohol_grams = data.get('alcohol_grams', 0)
    if 'food_images' in data:
        import json
        log.food_images = json.dumps(data['food_images']) if data['food_images'] else None
    if 'food_description' in data:
        log.food_description = data.get('food_description')
    
    # 更新运动记录
    if 'exercise_type' in data:
        log.exercise_type = data.get('exercise_type')
    if 'exercise_duration' in data:
        log.exercise_duration = data.get('exercise_duration')
    if 'exercise_intensity' in data:
        log.exercise_intensity = data.get('exercise_intensity')
    if 'exercise_frequency' in data:
        log.exercise_frequency = data.get('exercise_frequency')
    if 'calorie_expenditure' in data:
        log.calorie_expenditure = data.get('calorie_expenditure', 0)
    
    # 更新身体指标
    if 'daily_weight' in data:
        log.daily_weight = data.get('daily_weight')
    if 'daily_waist' in data:
        log.daily_waist = data.get('daily_waist')
    if 'daily_hip' in data:
        log.daily_hip = data.get('daily_hip')
    
    # 获取用户档案用于计算
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    # 计算净热量和预测体重变化
    if log.calorie_intake is not None and profile and profile.bmr:
        # 计算总消耗 = BMR + 运动消耗
        total_expenditure = calculate_calorie_expenditure(
            profile.bmr, 
            log.calorie_expenditure or 0
        )
        log.net_calorie = log.calorie_intake - (total_expenditure or 0)
        
        # 预测1天的体重变化
        if log.net_calorie is not None:
            log.predicted_weight_change = calculate_weight_change(
                log.calorie_intake or 0,
                total_expenditure or 0,
                1
            )
            
    # AI 分析
    if profile:
        try:
            profile_data = profile.to_dict()
            # 构造当前日志数据字典，因为 log.to_dict() 可能包含旧数据或者格式问题，
            # 这里直接使用 log 对象属性更准确
            log_data = {
                'calorie_intake': log.calorie_intake,
                'calorie_expenditure': log.calorie_expenditure,
                'carb_percent': log.carb_percent,
                'protein_percent': log.protein_percent,
                'fat_percent': log.fat_percent,
                'exercise_duration': log.exercise_duration
            }
            
            ai_result = ai_service.analyze_daily_log(profile_data, log_data)
            
            if ai_result:
                # ai_risk_assessment 存储为文本
                log.ai_risk_assessment = "; ".join(ai_result.get('risks', []))
                # ai_suggestions 存储为 JSON
                log.ai_suggestions = json.dumps(ai_result.get('suggestions', []))
        except Exception as e:
            print(f"AI分析失败: {e}")
            # 不中断保存流程
            pass
    
    db.session.commit()
    
    return success_response(data=log.to_dict(), message="日志保存成功")


