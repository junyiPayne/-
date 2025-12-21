"""运动生理计算公式模块"""
from datetime import datetime, timedelta

def calculate_bmi(weight_kg, height_cm):
    """
    计算BMI
    BMI = weight_kg / (height_m ** 2)
    """
    if not height_cm or height_cm <= 0:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_bmr(gender, weight_kg, height_cm, age):
    """
    计算基础代谢率 (Harris-Benedict公式)
    男：BMR = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    女：BMR = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    """
    if not all([weight_kg, height_cm, age]):
        return None
    
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    elif gender == 'female':
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    else:
        return None
    
    return round(bmr, 2)


def calculate_whr(waist_cm, hip_cm):
    """计算腰臀比 WHR = waist_cm / hip_cm"""
    if not hip_cm or hip_cm <= 0:
        return None
    return round(waist_cm / hip_cm, 2)


def calculate_whtr(waist_cm, height_cm):
    """计算腰高比 WHtR = waist_cm / height_cm"""
    if not height_cm or height_cm <= 0:
        return None
    return round(waist_cm / height_cm, 2)


def assess_weight_category_by_bmi(bmi):
    """
    根据BMI评估体重等级
    <18.5: 偏瘦
    18.5~23.9: 正常
    24.0~27.9: 超重
    >=28.0: 肥胖
    """
    if not bmi:
        return None
    
    if bmi < 18.5:
        return '偏瘦'
    elif bmi < 24.0:
        return '正常'
    elif bmi < 28.0:
        return '超重'
    else:
        return '肥胖'


def assess_body_fat_category(gender, age, body_fat_percent):
    """
    根据体脂率评估身体成分等级 (基于附件3)
    """
    if not body_fat_percent or not gender or not age:
        return None
    
    bf = body_fat_percent
    
    if gender == 'male':
        if age <= 19:
            if bf < 3: return '体脂过少'
            if bf <= 12: return '非常好'
            if bf <= 17: return '很好'
            if bf <= 22: return '正常'
            if bf <= 27: return '体脂多'
            return '体脂过多'
        elif 20 <= age <= 29:
            if bf < 3: return '体脂过少'
            if bf <= 13: return '非常好'
            if bf <= 18: return '很好'
            if bf <= 23: return '正常'
            if bf <= 28: return '体脂多'
            return '体脂过多'
        elif 30 <= age <= 39:
            if bf < 3: return '体脂过少'
            if bf <= 14: return '非常好'
            if bf <= 19: return '很好'
            if bf <= 24: return '正常'
            if bf <= 29: return '体脂多'
            return '体脂过多'
        elif 40 <= age <= 49:
            if bf < 3: return '体脂过少'
            if bf <= 15: return '非常好'
            if bf <= 20: return '很好'
            if bf <= 25: return '正常'
            if bf <= 30: return '体脂多'
            return '体脂过多'
        else: # >= 50
            if bf < 3: return '体脂过少'
            if bf <= 16: return '非常好'
            if bf <= 21: return '很好'
            if bf <= 26: return '正常'
            if bf <= 31: return '体脂多'
            return '体脂过多'
            
    elif gender == 'female':
        if age <= 19:
            if bf < 12: return '体脂过少'
            if bf <= 17: return '非常好'
            if bf <= 22: return '很好'
            if bf <= 27: return '正常'
            if bf <= 32: return '体脂多'
            return '体脂过多'
        elif 20 <= age <= 29:
            if bf < 12: return '体脂过少'
            if bf <= 18: return '非常好'
            if bf <= 23: return '很好'
            if bf <= 28: return '正常'
            if bf <= 33: return '体脂多'
            return '体脂过多'
        elif 30 <= age <= 39:
            if bf < 12: return '体脂过少'
            if bf <= 19: return '非常好'
            if bf <= 24: return '很好'
            if bf <= 29: return '正常'
            if bf <= 34: return '体脂多'
            return '体脂过多'
        elif 40 <= age <= 49:
            if bf < 12: return '体脂过少'
            if bf <= 20: return '非常好'
            if bf <= 25: return '很好'
            if bf <= 30: return '正常'
            if bf <= 35: return '体脂多'
            return '体脂过多'
        else: # >= 50
            if bf < 12: return '体脂过少'
            if bf <= 21: return '非常好'
            if bf <= 26: return '很好'
            if bf <= 31: return '正常'
            if bf <= 36: return '体脂多'
            return '体脂过多'
    
    return None


def assess_central_obesity_by_whr(gender, whr):
    """
    根据腰臀比评估中心性肥胖
    男性 >= 0.90
    女性 >= 0.85
    """
    if not whr or not gender:
        return None
    
    if gender == 'male':
        return '中心性肥胖' if whr >= 0.90 else '正常'
    elif gender == 'female':
        return '中心性肥胖' if whr >= 0.85 else '正常'
    
    return None


def assess_visceral_fat_by_whtr(whtr):
    """
    根据腰高比评估内脏脂肪
    >= 0.5: 内脏脂肪超标
    """
    if not whtr:
        return None
    
    return '内脏脂肪超标' if whtr >= 0.5 else '正常'


def calculate_linear_weight_prediction(daily_intake, daily_expenditure, days):
    """
    线性体重预测公式
    体重变化(kg) = (摄入热量 - 消耗热量) * 天数 / 7700
    """
    if daily_intake is None or daily_expenditure is None:
        return 0
    
    calorie_balance = daily_intake - daily_expenditure
    weight_change = (calorie_balance * days) / 7700
    return round(weight_change, 2)

    if gender == 'male' and whr >= 0.90:          
        return '中心性肥胖'
    elif gender == 'female' and whr >= 0.85:
        return '中心性肥胖'
    
    return '正常'


def assess_visceral_fat_by_whtr(whtr):
    """根据腰高比评估内脏脂肪"""
    if not whtr:
        return None
    
    if whtr >= 0.5:
        return '内脏脂肪超标'
    
    return '正常'


def assess_obesity_by_waist(gender, waist_cm):
    """根据腰围评估肥胖"""
    if not waist_cm:
        return None
    
    if gender == 'male' and waist_cm >= 90:
        return '肥胖'
    elif gender == 'female' and waist_cm >= 85:
        return '肥胖'
    
    return '正常'


def calculate_weight_change(calorie_intake, calorie_expenditure, days):
    """
    基于能量平衡计算体重变化
    weight_change_kg = (calorie_intake - calorie_expenditure) * days / 7700
    7700 kcal = 1 kg 脂肪
    """
    if not all([calorie_intake is not None, calorie_expenditure is not None, days]):
        return None
    
    calorie_diff = calorie_intake - calorie_expenditure
    weight_change = (calorie_diff * days) / 7700
    return round(weight_change, 2)


def calculate_calorie_expenditure(bmr, exercise_calorie=0):
    """
    计算每日总能量消耗
    能量消耗 = 基础代谢率 (70%) + 运动产热 (20%) + 食物热效应 (10%)
    
    注意：这里的公式是基于能量消耗的构成比例。
    如果已知BMR（约占70%），则估算总消耗：
    Total = BMR / 0.7 + 运动消耗 (如果运动消耗是额外的)
    
    或者更简单的模型：
    Total = BMR * PAL (身体活动水平) + 运动消耗
    
    根据需求文档：
    能量消耗 = 基础代谢率（70%）+ 运动产热（20%）+ 食物热效应（10%）
    这意味着 BMR 只是其中的一部分。
    
    这里我们采用一个简化的估算模型，假设BMR占基础消耗的大部分，
    并加上明确记录的运动消耗。
    为了符合文档描述的比例，我们可以反推：
    如果 BMR = 70% Total_Base, 那么 Total_Base = BMR / 0.7
    Total = Total_Base + Extra_Exercise
    """
    if not bmr:
        return None
    
    # 估算静息状态下的总消耗（包含食物热效应和基础活动）
    # 假设 BMR 占 70%
    base_expenditure = bmr / 0.7
    
    total_expenditure = base_expenditure + exercise_calorie
    return round(total_expenditure, 2)


def predict_future_weight(current_weight, calorie_intake, calorie_expenditure, days):
    """
    预测未来体重
    """
    weight_change = calculate_weight_change(calorie_intake, calorie_expenditure, days)
    if weight_change is None or current_weight is None:
        return None
    
    predicted_weight = current_weight + weight_change
    return round(max(predicted_weight, 0), 2)  # 体重不能为负


def calculate_schofield_tdee(weight_kg, gender, activity_level='moderate'):
    """
    使用 Schofield 公式计算 TDEE (kJ -> kcal)
    Men: (63 * W + 2896) * MET
    Women: (62 * W + 2036) * MET
    1 kcal = 4.184 kJ
    """
    if not weight_kg or not gender:
        return None
    
    # MET values (Activity Factors)
    mets = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    met = mets.get(activity_level, 1.55)
    
    if gender == 'male':
        tdee_kj = (63 * weight_kg + 2896) * met
    elif gender == 'female':
        tdee_kj = (62 * weight_kg + 2036) * met
    else:
        return None
        
    # Convert kJ to kcal
    tdee_kcal = tdee_kj / 4.184
    return round(tdee_kcal, 0)


def calculate_recommended_calories(weight_kg, gender, activity_level='moderate', goal=None, bmi=None):
    """
    计算推荐热量
    
    1. 推荐消耗 (Expenditure) = TDEE (Schofield Equation)
    2. 推荐摄入 (Intake) = TDEE + Goal Adjustment
       - 如果未提供目标，根据BMI自动推断：
         - BMI >= 24 (超重/肥胖) -> 减脂 (-500 kcal)
         - BMI < 18.5 (偏瘦) -> 增肌 (+300 kcal)
         - 正常 -> 保持 (0)
    """
    tdee = calculate_schofield_tdee(weight_kg, gender, activity_level)
    
    if not tdee:
        return None, None
        
    # 如果没有明确目标，根据BMI推断
    if not goal or goal == 'maintain':
        if bmi:
            if bmi >= 24:
                goal = 'lose'
            elif bmi < 18.5:
                goal = 'gain'
            else:
                goal = 'maintain'
        else:
            goal = 'maintain'
    
    if goal == 'lose':
        recommended_intake = tdee - 500
    elif goal == 'gain':
        recommended_intake = tdee + 300
    else:
        recommended_intake = tdee
        
    # 确保摄入量不低于基础安全值 (例如 1200)
    recommended_intake = max(recommended_intake, 1200)
        
    return round(recommended_intake, 0), round(tdee, 0)

