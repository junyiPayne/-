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
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.Timeout:
            raise ValueError("DeepSeek API调用超时（30秒）")
        except requests.exceptions.ConnectionError:
            raise ValueError("无法连接到DeepSeek API，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"DeepSeek API请求失败: {str(e)}")
        
        # 检查HTTP状态码
        if response.status_code != 200:
            error_text = response.text[:500] if response.text else "无响应内容"
            error_msg = f"HTTP {response.status_code}: {error_text}"
            print(f"❌ API调用失败: {error_msg}")
            
            # 尝试解析错误信息
            try:
                error_json = response.json()
                if 'error' in error_json:
                    api_error = error_json['error']
                    error_detail = api_error.get('message', '未知错误')
                    error_type = api_error.get('type', '')
                    print(f"   API错误类型: {error_type}")
                    print(f"   API错误信息: {error_detail}")
                    raise ValueError(f"DeepSeek API错误 ({error_type}): {error_detail}")
            except (ValueError, KeyError, json.JSONDecodeError):
                pass
            
            response.raise_for_status()
        
        result = response.json()
        
        # 检查API返回的错误
        if 'error' in result:
            error_info = result['error']
            error_msg = error_info.get('message', '未知错误')
            error_type = error_info.get('type', 'unknown')
            error_code = error_info.get('code', '')
            
            # 常见错误提示
            if 'insufficient_quota' in error_msg.lower() or 'quota' in error_msg.lower() or error_code == 'insufficient_quota':
                raise ValueError("API余额不足，请充值后使用。系统将自动切换到模拟模式。")
            elif 'invalid_api_key' in error_msg.lower() or error_code == 'invalid_api_key':
                raise ValueError("API Key无效，请检查配置。系统将自动切换到模拟模式。")
            else:
                raise ValueError(f"DeepSeek API错误 ({error_type}): {error_msg}")
        
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

    def generate_daily_plan(self, profile_data, target_weight_gain_kg, weeks=4, log_data=None):
        """
        根据目标增重生成每日饮食和运动建议
        
        Args:
            profile_data: 用户档案数据
            target_weight_gain_kg: 目标增重（公斤）
            weeks: 计划周期（周）
            log_data: 用户近30天的饮食记录统计（可选）
        
        Returns:
            dict: 包含每日饮食建议和运动建议，以及is_ai_generated标识
        """
        # 检查API Key配置，如果没有配置则使用模拟模式
        if not self.deepseek_api_key and not self.qianwen_api_key:
            print("=" * 60)
            print("⚠️ 【模拟模式】未检测到API Key，使用本地模拟模式生成每日计划")
            print("=" * 60)
            result = self._generate_simulation_daily_plan(profile_data, target_weight_gain_kg, weeks, log_data)
            result['_is_ai_generated'] = False
            result['_mode'] = 'simulation'
            result['_reason'] = 'no_api_key'
            return result

        prompt = self._build_daily_plan_prompt(profile_data, target_weight_gain_kg, weeks, log_data)
        
        try:
            print("=" * 60)
            print(f"🤖 【真实AI模式】正在调用AI API生成每日计划")
            print(f"   目标增重: {target_weight_gain_kg}kg")
            print(f"   计划周期: {weeks}周")
            print(f"   使用服务: {self.provider.upper()}")
            print(f"   提示词长度: {len(prompt)} 字符")
            print("=" * 60)
            
            if self.provider == 'deepseek':
                response = self._call_deepseek_api(prompt)
            else:
                response = self._call_qianwen_api(prompt)
            
            print(f"✅ AI API调用成功，响应长度: {len(response)} 字符")
            parsed_response = self._parse_daily_plan_response(response)
            
            # 验证返回的数据结构
            if not parsed_response or 'daily_diet' not in parsed_response:
                print("⚠️ AI返回的数据格式不正确，降级到模拟模式")
                result = self._generate_simulation_daily_plan(profile_data, target_weight_gain_kg, weeks, log_data)
                result['_is_ai_generated'] = False
                result['_mode'] = 'simulation'
                result['_reason'] = 'invalid_ai_response'
                return result
            
            # 标记为AI生成
            parsed_response['_is_ai_generated'] = True
            parsed_response['_mode'] = 'ai'
            parsed_response['_provider'] = self.provider
            print("=" * 60)
            print("✅ 【真实AI模式】每日计划生成完成（由AI生成）")
            print("=" * 60)
            return parsed_response
        except Exception as e:
            print("=" * 60)
            print(f"❌ 【降级到模拟模式】AI API调用失败: {str(e)}")
            print("=" * 60)
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            # 确保即使API失败也返回模拟数据
            result = self._generate_simulation_daily_plan(profile_data, target_weight_gain_kg, weeks, log_data)
            result['_is_ai_generated'] = False
            result['_mode'] = 'simulation'
            result['_reason'] = f'api_error: {str(e)[:100]}'
            return result

    def _build_daily_plan_prompt(self, profile_data, target_weight_gain_kg, weeks, log_data=None):
        """构建每日计划提示词"""
        current_weight = profile_data.get('weight_kg', 60)
        bmr = profile_data.get('bmr', 1500)
        age = profile_data.get('age', 25)
        gender = profile_data.get('gender', '未知')
        height = profile_data.get('height_cm', 170)
        
        # 计算每日需要增加的热量
        # 7700kcal = 1kg，所以目标增重需要的总热量 = target_weight_gain_kg * 7700
        total_calories_needed = target_weight_gain_kg * 7700
        daily_calorie_surplus = total_calories_needed / (weeks * 7)
        
        # 构建当前饮食情况描述
        current_diet_info = ""
        if log_data and log_data.get('log_count', 0) > 0:
            avg_intake = log_data.get('avg_daily_intake', 0)
            avg_expenditure = log_data.get('avg_daily_expenditure', 0)
            carb_pct = log_data.get('carb_percent', 50)
            protein_pct = log_data.get('protein_percent', 20)
            fat_pct = log_data.get('fat_percent', 30)
            exercise_duration = log_data.get('exercise_duration', 0)
            steps = log_data.get('steps', 0)
            log_count = log_data.get('log_count', 0)
            
            current_diet_info = f"""
【用户当前饮食情况（近30天统计，共{log_count}条记录）】
- 平均每日热量摄入: {avg_intake:.0f}kcal
- 平均每日热量消耗: {avg_expenditure:.0f}kcal
- 平均热量平衡: {avg_intake - avg_expenditure:+.0f}kcal/天
- 营养素比例: 碳水化合物 {carb_pct:.1f}%, 蛋白质 {protein_pct:.1f}%, 脂肪 {fat_pct:.1f}%
- 平均运动时长: {exercise_duration:.0f}分钟/天
- 平均步数: {steps:.0f}步/天

【分析要求】
请基于用户当前的饮食和运动习惯，制定一个渐进式的增重计划。考虑：
1. 用户当前的热量摄入水平，建议在现有基础上逐步增加
2. 用户当前的营养素比例，适当调整以支持健康增重
3. 用户当前的运动习惯，建议增加力量训练以促进肌肉增长
4. 避免过快增重导致脂肪堆积过多
"""
        else:
            current_diet_info = """
【用户当前饮食情况】
- 用户暂无近30天的饮食记录
- 建议基于基础代谢率(BMR)制定初始计划
"""
        
        prompt = f"""【角色】你是一位资深的注册营养师和运动教练，拥有10年以上临床经验。

【任务】根据用户的目标增重需求，制定详细的每日饮食和运动计划。

【用户基本信息】
- 年龄: {age}岁
- 性别: {gender}
- 身高: {height}cm
- 当前体重: {current_weight}kg
- 基础代谢率(BMR): {bmr}kcal
- BMI: {profile_data.get('bmi', '未知')}

【目标设定】
- 目标增重: {target_weight_gain_kg}kg
- 计划周期: {weeks}周
- 平均每日需要热量盈余: 约{daily_calorie_surplus:.0f}kcal

{current_diet_info}

【要求】
1. 制定每日饮食建议（不需要具体到每一餐，只需要每日总量和主要食物类型）：
   - 每日总热量摄入建议（kcal）
   - 碳水化合物摄入量（g）和主要来源（如：米饭、面条、全麦面包等）
   - 蛋白质摄入量（g）和主要来源（如：鸡胸肉、鸡蛋、牛奶、豆类等）
   - 脂肪摄入量（g）和主要来源（如：坚果、橄榄油、鱼油等）
   - 膳食纤维建议（g）
   - 每日饮水量建议（L）

2. 制定每日运动建议：
   - 有氧运动类型、时长和强度
   - 力量训练建议（如果有）
   - 日常活动建议（步数等）
   - 休息和恢复建议

3. 注意事项和风险提示

【输出格式】严格使用JSON格式：
{{
  "daily_diet": {{
    "total_calories": 2500,
    "carbohydrates": {{
      "amount": 300,
      "unit": "g",
      "sources": ["米饭", "全麦面包", "燕麦", "红薯"]
    }},
    "protein": {{
      "amount": 120,
      "unit": "g",
      "sources": ["鸡胸肉", "鸡蛋", "牛奶", "豆类"]
    }},
    "fat": {{
      "amount": 80,
      "unit": "g",
      "sources": ["坚果", "橄榄油", "鱼油"]
    }},
    "fiber": {{
      "amount": 30,
      "unit": "g"
    }},
    "water": {{
      "amount": 2.5,
      "unit": "L"
    }},
    "notes": ["建议分3-4餐进食", "运动前后适当补充碳水"]
  }},
  "daily_exercise": {{
    "aerobic": {{
      "type": "快走或慢跑",
      "duration": 30,
      "unit": "分钟",
      "frequency": "每周3-4次",
      "intensity": "中等强度"
    }},
    "strength": {{
      "type": "力量训练",
      "duration": 45,
      "unit": "分钟",
      "frequency": "每周2-3次",
      "focus": "全身大肌群"
    }},
    "steps": {{
      "target": 8000,
      "unit": "步"
    }},
    "rest": "每周至少1-2天完全休息"
  }},
  "notes": ["注意事项1", "注意事项2"],
  "risks": ["潜在风险1", "潜在风险2"]
}}"""
        return prompt

    def _parse_daily_plan_response(self, response_text):
        """解析每日计划响应"""
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
            return result
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {str(e)}")
            print(f"响应内容前500字符: {response_text[:500]}")
            return self._generate_simulation_daily_plan({}, 0, 4, None)
        except Exception as e:
            print(f"❌ 解析AI响应时出错: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return self._generate_simulation_daily_plan({}, 0, 4, None)

    def _generate_simulation_daily_plan(self, profile_data, target_weight_gain_kg, weeks, log_data=None):
        """生成模拟的每日计划（基于规则）"""
        print(f"📝 【模拟模式】使用基于规则的算法生成每日计划")
        print(f"   目标增重: {target_weight_gain_kg}kg, 周期: {weeks}周")
        
        try:
            current_weight = float(profile_data.get('weight_kg', 60) or 60)
            bmr = float(profile_data.get('bmr', 1500) or 1500)
        except (ValueError, TypeError):
            current_weight = 60
            bmr = 1500
            print("⚠️ 用户档案数据不完整，使用默认值")
        
        # 如果有用户的历史记录，基于历史记录计算目标热量
        if log_data and log_data.get('log_count', 0) > 0:
            avg_intake = log_data.get('avg_daily_intake', bmr * 1.2)
            avg_expenditure = log_data.get('avg_daily_expenditure', bmr * 1.2)
            # 基于当前平均摄入量，增加所需的热量盈余
            total_calories_needed = target_weight_gain_kg * 7700
            daily_calorie_surplus = total_calories_needed / (weeks * 7)
            target_calories = avg_intake + daily_calorie_surplus
            
            # 使用历史营养素比例作为参考
            carb_pct = log_data.get('carb_percent', 50)
            protein_pct = log_data.get('protein_percent', 20)
            fat_pct = log_data.get('fat_percent', 30)
            
            print(f"📊 基于历史记录: 当前平均摄入{avg_intake:.0f}kcal，目标摄入{target_calories:.0f}kcal")
        else:
            # 没有历史记录，使用BMR计算
            total_calories_needed = target_weight_gain_kg * 7700
            daily_calorie_surplus = total_calories_needed / (weeks * 7)
            target_calories = bmr * 1.5 + daily_calorie_surplus  # BMR * 1.5 作为基础活动量
            
            # 使用标准比例
            carb_pct = 50
            protein_pct = 20
            fat_pct = 30
        
        # 计算营养素分配（增重期间适当增加蛋白质和碳水）
        protein_grams = current_weight * 1.8  # 每公斤体重1.8g蛋白质
        carb_grams = (target_calories * (carb_pct / 100)) / 4  # 基于历史比例或标准比例
        fat_grams = (target_calories * (fat_pct / 100)) / 9
        
        print(f"✅ 模拟计划计算完成: 目标热量={int(target_calories)}kcal, 蛋白质={int(protein_grams)}g")
        
        return {
            "daily_diet": {
                "total_calories": int(target_calories),
                "carbohydrates": {
                    "amount": int(carb_grams),
                    "unit": "g",
                    "sources": ["米饭", "全麦面包", "燕麦", "红薯", "香蕉"]
                },
                "protein": {
                    "amount": int(protein_grams),
                    "unit": "g",
                    "sources": ["鸡胸肉", "瘦牛肉", "鸡蛋", "牛奶", "豆类", "鱼"]
                },
                "fat": {
                    "amount": int(fat_grams),
                    "unit": "g",
                    "sources": ["坚果", "橄榄油", "牛油果", "鱼油"]
                },
                "fiber": {
                    "amount": 30,
                    "unit": "g"
                },
                "water": {
                    "amount": 2.5,
                    "unit": "L"
                },
                "notes": [
                    "建议分3-4餐进食，每餐间隔3-4小时",
                    "运动前后1小时内补充碳水",
                    "睡前可适量补充蛋白质"
                ]
            },
            "daily_exercise": {
                "aerobic": {
                    "type": "快走或慢跑",
                    "duration": 30,
                    "unit": "分钟",
                    "frequency": "每周3-4次",
                    "intensity": "中等强度（心率控制在最大心率的60-70%）"
                },
                "strength": {
                    "type": "力量训练",
                    "duration": 45,
                    "unit": "分钟",
                    "frequency": "每周2-3次",
                    "focus": "全身大肌群（深蹲、卧推、硬拉等）"
                },
                "steps": {
                    "target": 8000,
                    "unit": "步"
                },
                "rest": "每周至少1-2天完全休息，保证充足睡眠"
            },
            "notes": [
                "增重期间注意营养均衡，避免只增脂肪",
                "力量训练有助于增加肌肉量",
                "保证充足睡眠（7-9小时）有助于恢复和增重"
            ],
            "risks": [
                "过快增重可能导致脂肪增加过多",
                "热量摄入过高可能影响消化系统"
            ]
        }

# 全局AI服务实例
ai_service = AIService()

