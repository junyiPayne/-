import sys
import os

# Add the backend directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.calculations import (
    assess_weight_category_by_bmi,
    assess_body_fat_category,
    assess_central_obesity_by_whr,
    assess_visceral_fat_by_whtr,
    assess_obesity_by_waist
)

def run_tests():
    print("开始执行健康指标计算逻辑验证...\n")
    
    # 1. BMI 测试
    print("1. BMI (身体质量指数) 测试")
    bmi_cases = [
        (18.4, '偏瘦'),
        (18.5, '正常'),
        (23.9, '正常'),
        (24.0, '超重'),
        (27.9, '超重'),
        (28.0, '肥胖'),
        (30.0, '肥胖'),
        (None, None)
    ]
    for val, expected in bmi_cases:
        result = assess_weight_category_by_bmi(val)
        status = "✅ 通过" if result == expected else f"❌ 失败 (预期: {expected}, 实际: {result})"
        print(f"   BMI: {val} -> {result} | {status}")
    print("-" * 50)

    # 2. 体脂率测试
    print("2. 体脂率测试")
    # (gender, age, body_fat, expected)
    # 注意：当前代码逻辑简化了年龄判断，主要基于性别
    bf_cases = [
        # 男性
        ('male', 25, 9.0, '体脂偏低'),
        ('male', 25, 10.0, '正常'),
        ('male', 25, 20.0, '正常'),
        ('male', 25, 21.0, '体脂偏低'), # 代码逻辑漏洞检查: 10-20正常, >25肥胖, 21-25之间呢?
        ('male', 25, 26.0, '肥胖'),
        # 女性
        ('female', 25, 14.0, '体脂偏低'),
        ('female', 25, 15.0, '正常'),
        ('female', 25, 25.0, '正常'),
        ('female', 25, 26.0, '体脂偏低'), # 代码逻辑漏洞检查: 15-25正常, >30肥胖, 26-30之间呢?
        ('female', 25, 31.0, '肥胖'),
    ]
    for gender, age, bf, expected in bf_cases:
        result = assess_body_fat_category(gender, age, bf)
        # 这里的 expected 是基于我对代码的阅读，如果代码逻辑有漏洞，这里会显示出来
        print(f"   性别: {gender}, 年龄: {age}, 体脂: {bf}% -> {result}")
    print("-" * 50)

    # 2.1 体脂率-年龄影响测试 (附件3)
    print("2.1 体脂率-年龄影响测试 (验证是否区分年龄段)")
    # 选取一个在不同年龄段应该有不同评价的值
    # 例如男性 22% 体脂:
    # 20-29岁: 正常 (18.1~23)
    # >=50岁: 正常 (21.1~26)
    # 
    # 再看男性 15% 体脂:
    # 20-29岁: 很好 (13.1~18)
    # >=50岁: 非常好 (16) -> 实际上附件3表格比较复杂
    # 
    # 我们简单测试同一个体脂率在不同年龄是否返回相同结果
    age_cases = [
        ('male', 20, 15.0),
        ('male', 40, 15.0),
        ('male', 60, 15.0),
    ]
    print("   测试用例: 男性, 体脂率 15.0% (预期: 若实现了附件3逻辑，不同年龄评价可能不同)")
    results = []
    for gender, age, bf in age_cases:
        res = assess_body_fat_category(gender, age, bf)
        results.append(res)
        print(f"   年龄: {age} -> {res}")
    
    if len(set(results)) == 1:
        print("   ⚠️ 结论: 当前逻辑未区分年龄段 (所有年龄结果相同)")
    else:
        print("   ✅ 结论: 当前逻辑已区分年龄段")
    print("-" * 50)

    # 3. 腰臀比 (WHR) 测试
    print("3. 腰臀比 (WHR) 测试")
    whr_cases = [
        ('male', 0.89, '正常'),
        ('male', 0.90, '中心性肥胖'),
        ('female', 0.84, '正常'),
        ('female', 0.85, '中心性肥胖'),
    ]
    for gender, whr, expected in whr_cases:
        result = assess_central_obesity_by_whr(gender, whr)
        status = "✅ 通过" if result == expected else f"❌ 失败 (预期: {expected}, 实际: {result})"
        print(f"   性别: {gender}, WHR: {whr} -> {result} | {status}")
    print("-" * 50)

    # 4. 腰高比 (WHtR) 测试
    print("4. 腰高比 (WHtR) 测试")
    whtr_cases = [
        (0.49, '正常'),
        (0.50, '内脏脂肪超标'),
        (0.60, '内脏脂肪超标'),
    ]
    for whtr, expected in whtr_cases:
        result = assess_visceral_fat_by_whtr(whtr)
        status = "✅ 通过" if result == expected else f"❌ 失败 (预期: {expected}, 实际: {result})"
        print(f"   WHtR: {whtr} -> {result} | {status}")
    print("-" * 50)

    # 5. 腰围测试
    print("5. 腰围测试")
    waist_cases = [
        ('male', 89, '正常'),
        ('male', 90, '肥胖'),
        ('female', 84, '正常'),
        ('female', 85, '肥胖'),
    ]
    for gender, waist, expected in waist_cases:
        result = assess_obesity_by_waist(gender, waist)
        status = "✅ 通过" if result == expected else f"❌ 失败 (预期: {expected}, 实际: {result})"
        print(f"   性别: {gender}, 腰围: {waist}cm -> {result} | {status}")
    print("-" * 50)

    # 6. 异常值/边界值测试
    print("6. 异常值/边界值测试")
    # BMI 负数
    res = assess_weight_category_by_bmi(-1)
    print(f"   BMI: -1 -> {res} (注意: 当前逻辑 <18.5 均返回偏瘦)")
    
    # 体脂率 > 100%
    res = assess_body_fat_category('male', 25, 105)
    print(f"   体脂: 105% -> {res} (注意: 当前逻辑 >25 均返回肥胖)")
    print("-" * 50)

if __name__ == "__main__":
    run_tests()
