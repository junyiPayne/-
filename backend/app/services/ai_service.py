"""AI服务模块 - 集成通义千问和DeepSeek API"""
import os
import requests
import json
import time
from datetime import datetime

class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.qianwen_api_key = os.environ.get('QWEN_API_KEY', '')
        self.provider = os.environ.get('AI_PROVIDER', 'deepseek')  # deepseek 或 qwen
        
    def generate_health_assessment(self, profile_data, log_data, weeks=4):
        """
        生成健康风险评估和建议
        """
        # 检查API Key配置，如果没有配置则使用模拟模式
        if not self.deepseek_api_key and not self.qianwen_api_key:
            print("⚠️ 未检测到API Key，使用本地模拟模式")
            return self._generate_simulation_response(profile_data, log_data, weeks)

        # 打印API Key状态（仅显示前8个字符，保护隐私）
        api_key_preview = (self.deepseek_api_key[:8] + "..." if self.deepseek_api_key else "未配置")
        print(f"✅ 使用 {self.provider} API，Key: {api_key_preview}")

        prompt = self._build_assessment_prompt(profile_data, log_data, weeks)
        
        try:
            if self.provider == 'deepseek':
                response = self._call_deepseek_api(prompt)
            else:
                response = self._call_qianwen_api(prompt)
            
            print(f"✅ AI API调用成功，响应长度: {len(response)} 字符")
            parsed_response = self._parse_ai_response(response)
            print(f"✅ 解析后建议数量: {len(parsed_response.get('suggestions', []))} 条")
            return parsed_response
        except Exception as e:
            print(f"❌ AI API调用失败: {str(e)}，切换至模拟模式")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return self._generate_simulation_response(profile_data, log_data, weeks)

    def analyze_daily_log(self, profile_data, log_data):
        """
        分析每日日志，生成风险评估和建议
        """
        # 检查API Key配置，如果没有配置则使用模拟模式
        if not self.deepseek_api_key and not self.qianwen_api_key:
            return self._generate_daily_simulation_response(profile_data, log_data)

        prompt = self._build_daily_analysis_prompt(profile_data, log_data)
        
        try:
            if self.provider == 'deepseek':
                response = self._call_deepseek_api(prompt)
            else:
                response = self._call_qianwen_api(prompt)
            
            return self._parse_daily_ai_response(response)
        except Exception as e:
            print(f"AI API调用失败: {str(e)}，切换至模拟模式")
            return self._generate_daily_simulation_response(profile_data, log_data)

    def _generate_daily_simulation_response(self, profile_data, log_data):
        """生成模拟的每日日志分析响应"""
        intake = float(log_data.get('calorie_intake', 0) or 0)
        expenditure = float(log_data.get('calorie_expenditure', 0) or 0)
        bmr = float(profile_data.get('bmr', 1500) or 1500)
        
        # 估算总消耗 (BMR / 0.7 + 运动消耗) - 保持与 calculations.py 一致
        # BMR 约占总消耗的 70%
        base_expenditure = bmr / 0.7
        total_expenditure = base_expenditure + expenditure
        
        risks = []
        suggestions = []
        
        # 饮食分析
        if intake > total_expenditure + 500:
            risks.append("今日热量摄入严重超标")
            suggestions.append("建议晚餐清淡，或增加运动量")
        elif intake < bmr:
            # 只有当摄入量真的非常低（低于BMR）时才提示
            # 并且要明确告知用户这是低于基础代谢，而不是低于运动消耗
            risks.append(f"热量摄入({intake}kcal)低于基础代谢({bmr}kcal)")
            suggestions.append("长期摄入过低会降低代谢，建议适当增加")
        elif intake < total_expenditure:
            # 处于热量缺口状态，这是正常的减脂状态
            suggestions.append("今日处于热量缺口状态，有助于减脂")
        else:
            # 摄入 > 消耗，但没超过500
            suggestions.append("今日热量略有盈余，请注意控制")
            
        carb_pct = float(log_data.get('carb_percent', 0) or 0)
            
        carb_pct = float(log_data.get('carb_percent', 0) or 0)
        protein_pct = float(log_data.get('protein_percent', 0) or 0)
        fat_pct = float(log_data.get('fat_percent', 0) or 0)
        
        if carb_pct > 65:
            risks.append("碳水化合物比例过高")
            suggestions.append("减少精制碳水，增加蔬菜摄入")
        if protein_pct < 15:
            suggestions.append("蛋白质摄入不足，建议补充蛋奶肉类")
        if fat_pct > 35:
            risks.append("脂肪摄入比例偏高")
            suggestions.append("注意控制油脂摄入，选择健康脂肪")
            
        # 运动分析
        exercise_duration = float(log_data.get('exercise_duration', 0) or 0)
        if exercise_duration < 30:
            suggestions.append("今日运动量不足，建议增加30分钟中等强度运动")
        elif exercise_duration > 120:
            risks.append("运动时间过长，注意防止过度训练")
            
        if not risks:
            risks.append("今日饮食运动状况良好")
        if not suggestions:
            suggestions.append("继续保持良好的生活习惯")
            
        return {
            "risks": risks[:3],
            "suggestions": suggestions[:3]
        }

    def _build_daily_analysis_prompt(self, profile_data, log_data):
        """构建每日分析提示词"""
        bmr = profile_data.get('bmr', 1500)
        return f"""【角色】营养师。
【任务】分析今日数据，给出风险和建议。
【数据】用户{profile_data.get('age')}岁，目标{profile_data.get('goal')}，BMR={bmr}。
今日摄入{log_data.get('calorie_intake')}kcal，运动消耗{log_data.get('calorie_expenditure')}kcal。
碳水{log_data.get('carb_percent')}%, 蛋白{log_data.get('protein_percent')}%, 脂肪{log_data.get('fat_percent')}%。
运动{log_data.get('exercise_duration')}分钟。
注意：如果摄入量低于BMR({bmr})，请务必警告风险。
【输出JSON】{{ "risks": ["风险1"], "suggestions": ["建议1"] }}"""

    def _parse_daily_ai_response(self, response_text):
        """解析每日分析响应"""
        try:
            # 简单清理和解析JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            return self._generate_daily_simulation_response({}, {})
        except:
            return self._generate_daily_simulation_response({}, {})

    def _generate_simulation_response(self, profile_data, log_data, weeks):
        """生成模拟的AI响应（基于规则）"""
        intake = float(log_data.get('avg_daily_intake', 2000))
        expenditure = float(log_data.get('avg_daily_expenditure', 2000))
        balance = intake - expenditure
        
        # 预测体重变化 (7700kcal = 1kg)
        total_calorie_diff = balance * 7 * weeks
        weight_change = total_calorie_diff / 7700
        
        # 预测体脂变化 (假设70%的体重变化来自脂肪)
        current_weight = float(profile_data.get('weight_kg', 60))
        fat_mass_change = weight_change * 0.7
        # 粗略估算体脂率变化
        fat_percent_change = (fat_mass_change / current_weight) * 100 if current_weight > 0 else 0
        
        # 生成建议
        suggestions = []
        risks = []
        
        # 1. 热量平衡分析
        if balance > 500:
            risks.append("热量盈余过多，有肥胖风险")
            suggestions.append("建议减少高热量食物摄入")
            suggestions.append("增加有氧运动时长")
        elif balance < -1000:
            risks.append("热量缺口过大，可能导致代谢损伤")
            suggestions.append("适当增加摄入，避免过度节食")
        elif balance < -500:
            suggestions.append("当前热量缺口适宜，继续保持")
        else:
            suggestions.append("热量收支基本平衡")
            
        # 2. 营养素分析
        carb_pct = float(log_data.get('carb_percent', 0) or 0)
        protein_pct = float(log_data.get('protein_percent', 0) or 0)
        fat_pct = float(log_data.get('fat_percent', 0) or 0)
        
        if carb_pct > 65:
            risks.append("碳水化合物比例过高，易引起血糖波动")
            suggestions.append("减少精制碳水，增加全谷物")
        elif carb_pct < 40:
            risks.append("碳水过低可能影响运动表现")
            suggestions.append("运动前后适当补充碳水")
            
        if protein_pct < 15:
            risks.append("蛋白质摄入不足，肌肉流失风险")
            suggestions.append("增加瘦肉、蛋奶或豆制品摄入")
        elif protein_pct > 35:
            suggestions.append("高蛋白饮食需注意多喝水")
            
        if fat_pct > 35:
            risks.append("脂肪摄入比例偏高")
            suggestions.append("减少油炸食品和肥肉摄入")
            
        # 3. 运动分析
        exercise_duration = float(log_data.get('exercise_duration', 0) or 0)
        
        if exercise_duration < 30:
            suggestions.append("运动量不足，建议每周至少150分钟中等强度运动")
        elif exercise_duration > 120:
            risks.append("单次运动时间过长，注意防止过度训练")
            
        # 补充建议
        if len(suggestions) < 3:
            suggestions.append("定期监测身体指标变化")
            suggestions.append("保持充足睡眠")
            
        return {
            "weight": f"{weight_change:+.1f} kg",
            "fat": f"{fat_percent_change:+.1f} %",
            "risks": risks or ["暂无明显风险"],
            "suggestions": suggestions[:4]  # 返回前4条建议
        }

    
    def _build_assessment_prompt(self, profile_data, log_data, weeks):
        """构建AI提示词"""
        prompt = f"""【角色】你是一位资深的运动生理学家兼注册营养师，拥有10年以上临床经验。

【任务】根据以下干预方案数据，预测{weeks}周后的体重和体脂变化，并给出专业、详细、可操作的健康建议。

【用户基本信息】
- 年龄: {profile_data.get('age', '未知')}岁
- 性别: {profile_data.get('gender', '未知')}
- 当前BMI: {profile_data.get('bmi', '未知')}
- 当前体重: {profile_data.get('weight_kg', '未知')}kg
- 基础代谢率(BMR): {profile_data.get('bmr', '未知')}kcal
- 健康目标: {profile_data.get('goal', '未设定')}

【干预方案参数】
- 每日热量摄入: {log_data.get('avg_daily_intake', log_data.get('calorie_intake', 0))}kcal
- 每日热量消耗: {log_data.get('avg_daily_expenditure', log_data.get('calorie_expenditure', 0))}kcal
- 热量平衡: {log_data.get('avg_daily_intake', log_data.get('calorie_intake', 0)) - log_data.get('avg_daily_expenditure', log_data.get('calorie_expenditure', 0))}kcal/天
- 营养素比例: 碳水化合物 {log_data.get('carb_percent', 0)}%, 蛋白质 {log_data.get('protein_percent', 0)}%, 脂肪 {log_data.get('fat_percent', 0)}%
- 膳食纤维: {log_data.get('fiber_grams', 0)}g/天
- 酒精摄入: {log_data.get('alcohol_grams', 0)}g/天
- 运动频率: {log_data.get('aerobic_freq', log_data.get('exercise_frequency', 0))}次/周
- 运动强度: {log_data.get('aerobic_intensity', '中等')}
- 运动时长: {log_data.get('exercise_duration', 0)}分钟/次
- 日常步数: {log_data.get('steps', 0)}步/天

【要求】
1. 基于能量平衡原理（7700kcal = 1kg体重），计算{weeks}周后的体重变化
2. 考虑代谢适应、肌肉保留等因素，给出体脂率变化预测
3. 识别至少3-5个潜在健康风险（如热量不足、营养素失衡、运动过度等）
4. 提供5-8条详细、可操作的专业建议，每条建议30-80字，涵盖：
   - 饮食调整建议（具体食物推荐、进餐时间等）
   - 运动优化建议（运动类型、强度、频率等）
   - 生活方式建议（睡眠、压力管理、恢复等）
   - 监测指标建议（需要关注的健康指标）

【输出格式】严格使用JSON格式：
{{
  "weight": "±x.x kg",
  "fat": "±x.x %",
  "risks": ["风险1（详细描述）", "风险2", "风险3", ...],
  "suggestions": ["建议1（具体可操作）", "建议2", "建议3", "建议4", "建议5", ...]
}}"""
        return prompt
    
    def _call_deepseek_api(self, prompt):
        """调用DeepSeek API"""
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API Key未配置")
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        print(f"📤 正在调用 DeepSeek API，提示词长度: {len(prompt)} 字符")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # 检查HTTP状态码
        if response.status_code != 200:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            print(f"❌ API调用失败: {error_msg}")
            response.raise_for_status()
        
        result = response.json()
        
        # 检查API返回的错误
        if 'error' in result:
            error_msg = result['error'].get('message', '未知错误')
            raise ValueError(f"DeepSeek API错误: {error_msg}")
        
        content = result['choices'][0]['message']['content']
        print(f"✅ DeepSeek API调用成功，返回内容长度: {len(content)} 字符")
        return content
    
    def _call_qianwen_api(self, prompt):
        """调用通义千问API"""
        if not self.qianwen_api_key:
            raise ValueError("通义千问API Key未配置")
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.qianwen_api_key}"
        }
        data = {
            "model": "qwen-turbo",
            "input": {"messages": [{"role": "user", "content": prompt}]},
            "parameters": {"temperature": 0.7}
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        return result['output']['choices'][0]['message']['content']
    
    def _parse_ai_response(self, response_text):
        """解析AI响应"""
        try:
            # 尝试提取JSON
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # 尝试找到JSON部分
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            result = json.loads(response_text)
            
            # 兼容不同的key
            weight = result.get("weight") or result.get("weight_change") or "0 kg"
            fat = result.get("fat") or result.get("fat_change") or "0 %"
            
            # 确保建议数量足够（至少5条）
            suggestions = result.get("suggestions", [])
            if isinstance(suggestions, list):
                # 如果建议少于5条，补充通用建议
                if len(suggestions) < 5:
                    print(f"⚠️ AI返回的建议只有 {len(suggestions)} 条，补充通用建议")
                    default_suggestions = [
                        "保持均衡饮食，控制热量摄入",
                        "适量运动，提高基础代谢率",
                        "定期监测体重和身体指标变化",
                        "保证充足睡眠，有助于代谢恢复",
                        "保持良好心态，避免过度焦虑"
                    ]
                    suggestions.extend(default_suggestions[:5 - len(suggestions)])
                # 限制最多8条，避免过多
                suggestions = suggestions[:8]
            else:
                suggestions = [str(suggestions)]
            
            # 确保风险数量合理（至少2条，最多6条）
            risks = result.get("risks", [])
            if isinstance(risks, list):
                if len(risks) < 2:
                    risks.append("请定期监测身体指标变化")
                risks = risks[:6]
            else:
                risks = [str(risks)] if risks else ["暂无明显风险"]
            
            return {
                "weight": weight,
                "fat": fat,
                "risks": risks,
                "suggestions": suggestions
            }
        except json.JSONDecodeError as e:
            # JSON解析失败，打印详细信息
            print(f"❌ JSON解析失败: {str(e)}")
            print(f"响应内容前500字符: {response_text[:500]}")
            return self._get_default_response()
        except Exception as e:
            # 其他解析错误
            print(f"❌ 解析AI响应时出错: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return self._get_default_response()
    
    def _get_default_response(self):
        """获取默认响应（API调用失败时）"""
        return {
            "weight": "0 kg",
            "fat": "0 %",
            "risks": ["无法获取AI分析，请检查API配置"],
            "suggestions": [
                "保持均衡饮食，控制热量摄入",
                "适量运动，提高基础代谢率",
                "定期监测体重和身体指标变化"
            ]
        }

# 全局AI服务实例
ai_service = AIService()

