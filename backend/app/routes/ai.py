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
    """获取AI预测（用于AI体重助手）"""
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
        
        # 获取预测参数（支持AI体重助手的详细参数）
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

@bp.route('/daily-plan', methods=['POST'])
@login_required
def get_daily_plan():
    """根据体重管理目标生成每日饮食和运动建议"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 添加详细的请求日志
        logger.info("=" * 50)
        logger.info("🔵 收到每日计划生成请求")
        logger.info(f"🔵 请求方法: {request.method}")
        logger.info(f"🔵 请求URL: {request.url}")
        logger.info(f"🔵 请求头: {dict(request.headers)}")
        
        user_id = get_jwt_identity()
        logger.info(f"🔵 用户ID: {user_id}")
        
        data = request.get_json()
        logger.info(f"🔵 请求数据: {data}")
        
        # 获取目标类型和目标体重变化（斤转公斤）
        goal_type = data.get('goal_type', 'gain')  # 'gain' 增重 或 'loss' 减重
        target_weight_change_jin = data.get('target_weight_change', data.get('target_weight_gain', 0))  # 兼容旧字段名
        
        # 确保 target_weight_change_jin 是数字
        try:
            target_weight_change_jin = float(target_weight_change_jin)
        except (ValueError, TypeError):
            raise ValidationError("目标体重变化必须是数字")
        
        target_weight_change_kg = target_weight_change_jin / 2  # 转换为公斤
        weeks = data.get('weeks', 4)
        
        # 确保 weeks 是数字
        try:
            weeks = int(weeks)
        except (ValueError, TypeError):
            weeks = 4
        
        if target_weight_change_kg <= 0:
            raise ValidationError(f"目标{'增重' if goal_type == 'gain' else '减重'}必须大于0")
        
        # 获取用户档案
        try:
            profile = UserProfile.query.filter_by(user_id=user_id).first()
        except Exception as db_error:
            logger.error(f"❌ 查询用户档案失败: {str(db_error)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            from app.utils.response import error_response
            return error_response(message=f"数据库查询失败: {str(db_error)}", code=500)
        
        if not profile:
            raise NotFoundError("请先完善个人档案")
        
        # 获取用户近30天的饮食记录
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            logs = DailyLog.query.filter(
                DailyLog.user_id == user_id,
                DailyLog.log_date >= start_date,
                DailyLog.log_date <= end_date
            ).order_by(DailyLog.log_date.desc()).all()
        except Exception as db_error:
            logger.error(f"❌ 查询饮食记录失败: {str(db_error)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            # 如果查询失败，使用空列表，不影响后续处理
            logs = []
        
        # 统计近30天的平均数据
        log_data = {}
        if logs:
            total_intake = sum(log.calorie_intake or 0 for log in logs)
            total_expenditure = sum(log.calorie_expenditure or 0 for log in logs)
            avg_intake = total_intake / len(logs)
            avg_expenditure = total_expenditure / len(logs)
            
            # 统计宏量营养素平均值
            avg_carb = sum(log.carb_percent or 0 for log in logs) / len(logs)
            avg_protein = sum(log.protein_percent or 0 for log in logs) / len(logs)
            avg_fat = sum(log.fat_percent or 0 for log in logs) / len(logs)
            
            # 统计其他营养素
            avg_fiber = sum(log.fiber_grams or 0 for log in logs) / len(logs)
            avg_alcohol = sum(log.alcohol_grams or 0 for log in logs) / len(logs)
            
            # 统计运动数据
            avg_exercise_duration = sum(log.exercise_duration or 0 for log in logs) / len(logs)
            avg_steps = sum(log.steps or 0 for log in logs) / len(logs) if hasattr(logs[0], 'steps') else 0
            
            log_data = {
                'avg_daily_intake': avg_intake,
                'avg_daily_expenditure': avg_expenditure,
                'carb_percent': avg_carb,
                'protein_percent': avg_protein,
                'fat_percent': avg_fat,
                'fiber_grams': avg_fiber,
                'alcohol_grams': avg_alcohol,
                'exercise_duration': avg_exercise_duration,
                'steps': avg_steps,
                'log_count': len(logs),
                'days_covered': (end_date - start_date).days + 1
            }
            logger.info(f"📊 统计了近30天的数据: {len(logs)}条记录，平均摄入{avg_intake:.0f}kcal，平均消耗{avg_expenditure:.0f}kcal")
        else:
            # 如果没有记录，使用用户档案的BMR作为基础
            bmr = profile.bmr or 1500
            log_data = {
                'avg_daily_intake': bmr * 1.2,  # 假设轻度活动
                'avg_daily_expenditure': bmr * 1.2,
                'carb_percent': 50,
                'protein_percent': 20,
                'fat_percent': 30,
                'fiber_grams': 25,
                'alcohol_grams': 0,
                'exercise_duration': 0,
                'steps': 6000,
                'log_count': 0,
                'days_covered': 30
            }
            logger.info(f"⚠️ 用户没有近30天的记录，使用默认值（基于BMR: {bmr}kcal）")
        
        goal_text = '增重' if goal_type == 'gain' else '减重'
        logger.info(f"🔵 用户目标{goal_text}: {target_weight_change_kg}kg，计划周期: {weeks}周")
        
        # 调用AI服务生成每日计划（传入用户档案和饮食记录数据）
        try:
            profile_data = profile.to_dict()
        except Exception as e:
            logger.error(f"❌ 转换用户档案失败: {str(e)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            from app.utils.response import error_response
            return error_response(message=f"处理用户档案失败: {str(e)}", code=500)
        
        try:
            daily_plan = ai_service.generate_daily_plan(
                profile_data,
                target_weight_change_kg,
                weeks,
                log_data,  # 传入近30天的饮食记录统计
                goal_type=goal_type  # 传入目标类型
            )
        except Exception as ai_error:
            logger.error(f"❌ AI服务调用失败: {str(ai_error)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            # 不直接返回错误，让降级方案处理
            raise ai_error
        
        # 检查是否使用AI生成
        is_ai_generated = daily_plan.get('_is_ai_generated', False)
        mode = daily_plan.get('_mode', 'unknown')
        provider = daily_plan.get('_provider', '')
        
        if is_ai_generated:
            logger.info(f"✅ 每日计划生成成功（使用真实AI: {provider}）")
            message = f"每日计划生成成功（AI生成）"
        else:
            reason = daily_plan.get('_reason', 'unknown')
            logger.info(f"✅ 每日计划生成成功（使用模拟模式，原因: {reason}）")
            message = f"每日计划生成成功（模拟模式）"
        
        # 移除内部标识字段（不返回给前端，避免混淆）
        daily_plan_clean = {k: v for k, v in daily_plan.items() if not k.startswith('_')}
        
        logger.info(f"📤 准备返回给前端的数据结构:")
        logger.info(f"   daily_plan 键: {list(daily_plan_clean.keys())}")
        logger.info(f"   daily_plan.daily_diet 存在: {'daily_diet' in daily_plan_clean}")
        logger.info(f"   daily_plan.daily_exercise 存在: {'daily_exercise' in daily_plan_clean}")
        
        # 计算目标体重
        if goal_type == 'gain':
            target_weight = profile.weight_kg + target_weight_change_kg
        else:
            target_weight = profile.weight_kg - target_weight_change_kg
        
        return success_response(data={
            'daily_plan': daily_plan_clean,
            'goal_type': goal_type,
            'target_weight_change_kg': target_weight_change_kg,
            'target_weight_change_jin': target_weight_change_jin,
            'weeks': weeks,
            'current_weight': profile.weight_kg,
            'target_weight': target_weight,
            'log_statistics': log_data,  # 返回统计信息供前端显示
            'is_ai_generated': is_ai_generated,  # 明确标识是否使用AI
            'mode': mode,  # 模式标识
            'provider': provider if is_ai_generated else None  # AI服务提供商
        }, message=message)
    except ValidationError as e:
        logger.error(f"❌ 参数验证失败: {str(e)}")
        from app.utils.response import error_response
        return error_response(message=str(e), code=400)
    except NotFoundError as e:
        logger.error(f"❌ 资源未找到: {str(e)}")
        from app.utils.response import error_response
        # 如果是用户档案未找到，返回友好的提示信息
        error_message = str(e)
        if "用户档案" in error_message or "个人档案" in error_message or "profile" in error_message.lower():
            error_message = "请先完善个人档案"
        return error_response(message=error_message, code=404)
    except Exception as e:
        logger.error(f"❌ 每日计划生成失败: {str(e)}")
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"详细错误: {error_detail}")
        
        # 即使出错，也尝试返回模拟数据，确保前端有响应
        try:
            # 安全地获取变量（如果它们已定义）
            local_vars = locals()
            profile_data = profile.to_dict() if 'profile' in local_vars and profile else {}
            target_weight_change_kg = local_vars.get('target_weight_change_kg', 1.0)  # 默认1kg
            target_weight_change_jin = local_vars.get('target_weight_change_jin', 2.0)  # 默认2斤
            weeks = local_vars.get('weeks', 4)
            goal_type = local_vars.get('goal_type', 'gain')
            
            fallback_plan = ai_service._generate_simulation_daily_plan(
                profile_data,
                target_weight_change_kg,
                weeks,
                log_data if 'log_data' in local_vars else None
            )
            logger.warning("⚠️ 使用降级方案返回模拟数据")
            
            # 计算目标体重
            current_weight = profile.weight_kg if 'profile' in local_vars and profile else 60
            if goal_type == 'gain':
                target_weight = current_weight + target_weight_change_kg
            else:
                target_weight = current_weight - target_weight_change_kg
            
            return success_response(data={
                'daily_plan': fallback_plan,
                'goal_type': goal_type,
                'target_weight_change_kg': target_weight_change_kg,
                'target_weight_change_jin': target_weight_change_jin,
                'weeks': weeks,
                'current_weight': current_weight,
                'target_weight': target_weight,
                'log_statistics': log_data if 'log_data' in local_vars else {},
                'is_fallback': True  # 标记这是降级数据
            }, message="每日计划生成成功（使用模拟模式）")
        except Exception as fallback_error:
            logger.error(f"❌ 降级方案也失败: {str(fallback_error)}")
            import traceback
            logger.error(f"降级方案详细错误: {traceback.format_exc()}")
            from app.utils.response import error_response
            return error_response(message=f"生成计划失败: {str(e)}", code=500)

