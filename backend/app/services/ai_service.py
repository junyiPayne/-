"""AI服务模块 - 集成通义千问和DeepSeek API"""
import os
import requests
import json
import time
import ssl
from datetime import datetime

# 尝试导入 DashScope SDK（用于通义千问视觉API）
try:
    import dashscope  # type: ignore[import-untyped]
    from dashscope import MultiModalConversation  # type: ignore[import-untyped]
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    dashscope = None  # type: ignore[assignment]
    MultiModalConversation = None  # type: ignore[assignment]

class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY', '').strip()
        self.provider = os.environ.get('AI_PROVIDER', 'deepseek')  # deepseek 或 qwen
        
        # 通义千问支持两种配置方式：
        # 1. QWEN_API_KEY: 直接配置完整的 API Key（格式：AccessKeyID:AccessKeySecret）
        # 2. QWEN_ACCESS_KEY_ID + QWEN_ACCESS_KEY_SECRET: 分别配置，自动拼接
        qwen_api_key = os.environ.get('QWEN_API_KEY', '').strip()
        qwen_access_key_id = os.environ.get('QWEN_ACCESS_KEY_ID', '').strip()
        qwen_access_key_secret = os.environ.get('QWEN_ACCESS_KEY_SECRET', '').strip()
        
        # 优先使用 QWEN_API_KEY，如果没有则尝试拼接 AccessKey ID 和 Secret
        if qwen_api_key:
            self.qianwen_api_key = qwen_api_key
        elif qwen_access_key_id and qwen_access_key_secret:
            # 拼接格式：AccessKeyID:AccessKeySecret
            self.qianwen_api_key = f"{qwen_access_key_id}:{qwen_access_key_secret}"
            import sys
            if os.environ.get('FLASK_ENV') != 'production':
                print(f"[AI Service Init] 使用 AccessKey ID + Secret 拼接方式", file=sys.stderr)
        else:
            self.qianwen_api_key = ''
        
        # 验证通义千问 API Key 格式
        if self.qianwen_api_key:
            self._validate_qianwen_api_key()
        
        # 如果 DashScope SDK 可用，设置 API Key
        if DASHSCOPE_AVAILABLE and self.qianwen_api_key:
            dashscope.api_key = self.qianwen_api_key
        
        # 调试输出（仅在开发环境）
        if os.environ.get('FLASK_ENV') != 'production':
            import sys
            print(f"[AI Service Init] DeepSeek Key: {'已配置' if self.deepseek_api_key else '未配置'}", file=sys.stderr)
            print(f"[AI Service Init] 通义千问 Key: {'已配置' if self.qianwen_api_key else '未配置'}", file=sys.stderr)
            print(f"[AI Service Init] DashScope SDK: {'可用' if DASHSCOPE_AVAILABLE else '不可用（需要安装: pip install dashscope）'}", file=sys.stderr)
            if self.qianwen_api_key:
                print(f"[AI Service Init] 通义千问 Key长度: {len(self.qianwen_api_key)}", file=sys.stderr)
                print(f"[AI Service Init] 通义千问 Key预览: {self.qianwen_api_key[:10]}...{self.qianwen_api_key[-5:] if len(self.qianwen_api_key) > 15 else '***'}", file=sys.stderr)
    
    def _validate_qianwen_api_key(self):
        """验证通义千问 API Key 格式"""
        import sys
        
        key = self.qianwen_api_key.strip()
        
        # 检查是否包含冒号（AccessKeyID:AccessKeySecret 格式）
        if ':' in key:
            parts = key.split(':', 1)
            if len(parts) == 2:
                access_key_id, access_key_secret = parts
                print(f"✅ 检测到 AccessKey ID + Secret 格式", file=sys.stderr)
                print(f"   AccessKey ID 长度: {len(access_key_id)} 字符", file=sys.stderr)
                print(f"   AccessKey Secret 长度: {len(access_key_secret)} 字符", file=sys.stderr)
                
                if len(access_key_id) < 10 or len(access_key_secret) < 10:
                    print(f"⚠️  警告：AccessKey ID 或 Secret 长度可能不正确", file=sys.stderr)
            else:
                print(f"⚠️  警告：API Key 格式可能不正确（应包含一个冒号分隔 ID 和 Secret）", file=sys.stderr)
        else:
            # 单一 API Key 格式（sk- 开头）
            if len(key) < 20:
                print(f"⚠️  警告：通义千问 API Key 长度可能不正确 ({len(key)} 字符)", file=sys.stderr)
                print("   通义千问 API Key 通常较长，请检查是否正确复制", file=sys.stderr)
            
            # 检查是否包含占位符
            if 'your' in key.lower() or 'placeholder' in key.lower() or 'example' in key.lower():
                print("⚠️  警告：检测到可能是占位符的 API Key", file=sys.stderr)
                print("   请确保使用真实的 API Key，而不是示例值", file=sys.stderr)
            
            # 通义千问 API Key 可能以 sk- 开头，或者使用 AccessKeyID:AccessKeySecret 格式
            if not key.startswith('sk-') and ':' not in key and len(key) > 20:
                print("ℹ️  提示：通义千问 API Key 格式应为：", file=sys.stderr)
                print("   1. sk-开头的单一 Key", file=sys.stderr)
                print("   2. AccessKeyID:AccessKeySecret（用冒号拼接）", file=sys.stderr)
                print("   如果您的 Key 格式不同，请确认这是正确的格式", file=sys.stderr)
        
    def generate_health_assessment(self, profile_data, log_data, weeks=4):
        """
        生成健康风险评估和建议（体重助手）
        强制使用 DEEPSEEK API
        """
        import sys
        # 检查DEEPSEEK API Key配置
        if not self.deepseek_api_key:
            print("⚠️ 未检测到DEEPSEEK API Key，使用本地模拟模式", file=sys.stderr)
            return self._generate_simulation_response(profile_data, log_data, weeks)

        # 打印API Key状态（仅显示前8个字符，保护隐私）
        api_key_preview = (self.deepseek_api_key[:8] + "..." if self.deepseek_api_key else "未配置")
        print(f"✅ 体重助手使用 DEEPSEEK API，Key: {api_key_preview}", file=sys.stderr)

        prompt = self._build_assessment_prompt(profile_data, log_data, weeks)
        
        try:
            # 体重助手强制使用 DEEPSEEK API
            import sys
            response = self._call_deepseek_api(prompt)
            print(f"✅ DEEPSEEK API调用成功，响应长度: {len(response)} 字符", file=sys.stderr)
            parsed_response = self._parse_ai_response(response)
            print(f"✅ 解析后建议数量: {len(parsed_response.get('suggestions', []))} 条", file=sys.stderr)
            return parsed_response
        except Exception as e:
            import sys
            print(f"❌ DEEPSEEK API调用失败: {str(e)}，切换至模拟模式", file=sys.stderr)
            import traceback
            print(f"详细错误: {traceback.format_exc()}", file=sys.stderr)
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
            "model": "deepseek-chat",  # 文本对话使用 deepseek-chat（已升级为 DeepSeek-V3.2）
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        print(f"📤 正在调用 DeepSeek API，提示词长度: {len(prompt)} 字符")
        # AI生成可能需要较长时间，设置更长的超时（连接10秒，读取120秒）
        # 对于长内容生成，DeepSeek可能需要更长时间
        try:
            print(f"⏳ 等待AI响应（最长120秒）...")
            response = requests.post(url, headers=headers, json=data, timeout=(10, 120))
            print(f"✅ 收到HTTP响应，状态码: {response.status_code}")
        except requests.exceptions.Timeout as e:
            print(f"❌ 超时错误详情: {type(e).__name__}: {str(e)}")
            raise ValueError("DeepSeek API调用超时（120秒），AI生成可能需要更长时间，请稍后重试")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误详情: {type(e).__name__}: {str(e)}")
            raise ValueError(f"无法连接到DeepSeek API，请检查网络连接: {str(e)}")
        except requests.exceptions.ReadTimeout as e:
            print(f"❌ 读取超时错误详情: {type(e).__name__}: {str(e)}")
            raise ValueError(f"读取DeepSeek API响应超时，响应可能过长: {str(e)}")
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常详情: {type(e).__name__}: {str(e)}")
            raise ValueError(f"DeepSeek API请求失败: {str(e)}")
        
        # 检查HTTP状态码
        print(f"📥 HTTP响应状态: {response.status_code}")
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
        
        # 解析JSON响应
        print(f"📦 开始解析JSON响应...")
        try:
            result = response.json()
            print(f"✅ JSON解析成功，响应键: {list(result.keys())}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {str(e)}")
            print(f"   响应内容前500字符: {response.text[:500]}")
            raise ValueError(f"DeepSeek API返回的JSON格式无效: {str(e)}")
        
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
        """调用通义千问API（使用兼容模式）"""
        if not self.qianwen_api_key:
            raise ValueError("通义千问API Key未配置")
        
        # 兼容模式 URL（根据文档推荐）
        # 支持不同地域：
        # - 北京（默认）：https://dashscope.aliyuncs.com/compatible-mode/v1
        # - 新加坡：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
        # - 美国：https://dashscope-us.aliyuncs.com/compatible-mode/v1
        qwen_region = os.environ.get('QWEN_REGION', 'beijing').lower()
        if qwen_region == 'singapore' or qwen_region == 'intl':
            base_url = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'
        elif qwen_region == 'us' or qwen_region == 'virginia':
            base_url = 'https://dashscope-us.aliyuncs.com/compatible-mode/v1'
        else:
            # 默认使用北京地域
            base_url = os.environ.get('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        
        url = f"{base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.qianwen_api_key.strip()}"
        }
        
        # 兼容模式使用 OpenAI 格式
        data = {
            "model": "qwen-plus",  # 或 qwen-turbo, qwen-max
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # AI生成可能需要较长时间，设置更长的超时（连接10秒，读取90秒）
        try:
            response = requests.post(url, headers=headers, json=data, timeout=(10, 90))
            response.raise_for_status()
            result = response.json()
            
            # 兼容模式返回格式：result['choices'][0]['message']['content']
            return result['choices'][0]['message']['content']
        except requests.exceptions.SSLError as ssl_err:
            # SSL 错误，重新抛出以便上层处理
            raise
        except Exception as e:
            # 如果兼容模式失败，尝试回退到原始 API
            import sys
            print(f"⚠️ 兼容模式调用失败，尝试原始 API: {str(e)[:100]}...", file=sys.stderr)
            
            # 回退到原始 API
            url_original = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            data_original = {
                "model": "qwen-turbo",
                "input": {"messages": [{"role": "user", "content": prompt}]},
                "parameters": {"temperature": 0.7}
            }
            
            response = requests.post(url_original, headers=headers, json=data_original, timeout=(10, 90))
            response.raise_for_status()
            result = response.json()
            
            return result['output']['choices'][0]['message']['content']
    
    def recognize_food_from_image(self, image_path):
        """
        从图片识别食物并返回名称和预估热量
        使用通义千问 Qwen-VL 视觉API（DashScope SDK）
        """
        import base64
        import sys
        
        # 检查通义千问 API Key 和 DashScope SDK 配置
        print("=" * 80, file=sys.stderr)
        print(f"🔍 拍照识别功能 - 检查通义千问 API配置...", file=sys.stderr)
        print(f"   通义千问 API Key: {'已配置' if self.qianwen_api_key else '未配置'}", file=sys.stderr)
        print(f"   DashScope SDK: {'可用' if DASHSCOPE_AVAILABLE else '不可用（需要安装: pip install dashscope）'}", file=sys.stderr)
        if self.qianwen_api_key:
            print(f"   通义千问 Key值: {self.qianwen_api_key[:20]}...{self.qianwen_api_key[-5:] if len(self.qianwen_api_key) > 25 else '***'}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        
        if not self.qianwen_api_key:
            print("⚠️ 未检测到通义千问 API Key，使用模拟模式", file=sys.stderr)
            print("   提示：拍照识别功能需要使用通义千问 API Key（QWEN_API_KEY）", file=sys.stderr)
            return self._generate_simulation_food_recognition()
        
        if not DASHSCOPE_AVAILABLE:
            print("⚠️ DashScope SDK 未安装，使用模拟模式", file=sys.stderr)
            print("   提示：请运行 'pip install dashscope' 安装 DashScope SDK", file=sys.stderr)
            return self._generate_simulation_food_recognition()
        
        # 读取图片并转换为base64
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"无法读取图片文件: {str(e)}")
        
        # 构建提示词 - 直接询问食物名称和热量
        prompt = """请仔细观察图片中的食物，告诉我：
1. 图中的食物叫什么名字？（用中文回答）
2. 大概蕴含多少热量？（单位：kcal，基于常见分量估算）

请用JSON格式返回，格式如下：
{
  "foods": [
    {
      "name": "食物名称（中文）",
      "calories": 热量数字（单位：kcal）
    }
  ]
}

要求：
- 仔细识别图片中的食物，尽量给出具体的食物名称
- 如果图片中有多种食物，识别主要的一种或几种
- 热量估算要合理（例如：一碗米饭约200kcal，一个苹果约80kcal）
- 只有在完全无法识别任何食物时才返回"无法识别"
- 即使不确定，也请给出最可能的食物名称和估算热量"""
        
        try:
            # 检查通义千问 API Key是否配置（排除占位符和空值）
            qianwen_key_valid = (
                self.qianwen_api_key and 
                self.qianwen_api_key != 'your-api-key-here' and
                len(self.qianwen_api_key.strip()) > 10  # 确保不是占位符
            )
            
            import sys
            print(f"🔍 通义千问 API Key检查:", file=sys.stderr)
            print(f"   Key存在: {bool(self.qianwen_api_key)}", file=sys.stderr)
            print(f"   Key值: {self.qianwen_api_key[:20] if self.qianwen_api_key else 'None'}...", file=sys.stderr)
            print(f"   是否有效: {qianwen_key_valid}", file=sys.stderr)
            
            if not qianwen_key_valid:
                raise ValueError("未配置通义千问 API Key。请配置通义千问 API Key（QWEN_API_KEY）")
            
            # 使用 DashScope SDK 调用 Qwen-VL 视觉API
            import sys
            print("=" * 80, file=sys.stderr)
            print("📷 拍照识别 - 使用通义千问 Qwen-VL 视觉API（DashScope SDK）...", file=sys.stderr)
            print(f"   图片大小: {len(image_base64)} 字符 (base64)", file=sys.stderr)
            print(f"   API Key: {self.qianwen_api_key[:15]}...{self.qianwen_api_key[-5:] if len(self.qianwen_api_key) > 20 else '***'}", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            
            # 优先使用兼容模式 API（根据文档推荐）
            # 兼容模式 URL: https://dashscope.aliyuncs.com/compatible-mode/v1
            print("   🔄 尝试使用兼容模式 API...", file=sys.stderr)
            try:
                result = self._call_qianwen_vision_compatible_mode(image_base64, prompt)
                print("   ✅ 兼容模式 API 调用成功", file=sys.stderr)
                return result
            except Exception as compatible_error:
                error_msg = str(compatible_error)
                print(f"   ⚠️ 兼容模式 API 失败: {error_msg[:150]}...", file=sys.stderr)
                print("   🔄 回退到 DashScope SDK...", file=sys.stderr)
                # 如果兼容模式失败，回退到 SDK 方式
            
            # 设置 API Key
            dashscope.api_key = self.qianwen_api_key
            
            # 调用 Qwen-VL API（添加重试机制）
            max_retries = 3
            retry_delay = 2  # 秒
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        print(f"   🔄 SDK 重试第 {attempt} 次...", file=sys.stderr)
                        time.sleep(retry_delay * attempt)  # 指数退避
                    
                    response = MultiModalConversation.call(
                        model='qwen-vl-plus',  # 可选: qwen-vl-max, qwen-vl-plus
                        messages=[
                            {
                                'role': 'user',
                                'content': [
                                    {'image': f'data:image/jpeg;base64,{image_base64}'},
                                    {'text': prompt}
                                ]
                            }
                        ]
                    )
                    last_error = None
                    break  # 成功，退出重试循环
                except (requests.exceptions.SSLError, ssl.SSLError) as ssl_err:
                    last_error = ssl_err
                    error_msg = str(ssl_err)
                    if 'EOF occurred in violation of protocol' in error_msg:
                        print(f"   ⚠️ SSL连接错误（尝试 {attempt + 1}/{max_retries}）: {error_msg[:100]}...", file=sys.stderr)
                        if attempt < max_retries - 1:
                            continue  # 继续重试
                        else:
                            # 最后一次尝试失败，尝试使用直接 HTTP 方式
                            print("   🔄 SSL错误持续，尝试使用直接 HTTP 方式...", file=sys.stderr)
                            try:
                                return self._call_qianwen_vision_api(image_base64, prompt)
                            except Exception as http_error:
                                raise ValueError(
                                    "SSL连接失败：这通常是网络环境或SSL/TLS协议兼容性问题，不是API账户问题。\n"
                                    "可能的解决方案：\n"
                                    "1. 检查网络连接和代理设置\n"
                                    "2. 更新 Python、requests、urllib3 到最新版本\n"
                                    "3. 如果问题持续，可以尝试使用 DeepSeek API 作为替代"
                                ) from ssl_err
                    else:
                        raise  # 其他 SSL 错误直接抛出
                except Exception as e:
                    last_error = e
                    # 检查是否是账户相关错误
                    error_str = str(e).lower()
                    if any(keyword in error_str for keyword in ['401', '403', 'unauthorized', 'forbidden', 'invalid api key', '余额', 'quota']):
                        print(f"   ❌ API账户/权限错误: {str(e)}", file=sys.stderr)
                        raise ValueError(
                            f"API调用失败，可能是账户问题：{str(e)}\n"
                            "请检查：\n"
                            "1. API Key 是否正确\n"
                            "2. 账户是否有余额\n"
                            "3. API 服务是否已开通"
                        ) from e
                    elif attempt < max_retries - 1:
                        print(f"   ⚠️ 调用失败（尝试 {attempt + 1}/{max_retries}）: {str(e)[:100]}...", file=sys.stderr)
                        continue  # 继续重试
                    else:
                        raise  # 最后一次尝试失败，抛出原始异常
            
            if last_error:
                raise last_error
            
            # 检查响应状态
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                print(f"   ✅ 通义千问 Qwen-VL API调用成功，响应长度: {len(content)} 字符", file=sys.stderr)
                print(f"   响应内容预览: {content[:300]}...", file=sys.stderr)
            else:
                error_msg = f"API调用失败，状态码: {response.status_code}"
                if hasattr(response, 'message'):
                    error_msg += f", 错误信息: {response.message}"
                if hasattr(response, 'code'):
                    error_msg += f", 错误代码: {response.code}"
                print(f"   ❌ {error_msg}", file=sys.stderr)
                raise ValueError(error_msg)
            
            # 解析响应
            print(f"📦 开始解析AI响应...", file=sys.stderr)
            result = self._parse_food_recognition_response(content)
            print(f"✅ 识别成功，找到 {len(result.get('foods', []))} 种食物", file=sys.stderr)
            for idx, food in enumerate(result.get('foods', []), 1):
                print(f"   {idx}. {food.get('name', '未知')} - {food.get('calories', 0)} kcal", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            return result
        except Exception as e:
            import sys
            import traceback
            from requests.exceptions import SSLError as RequestsSSLError
            
            print("=" * 80, file=sys.stderr)
            
            # 区分不同类型的错误
            error_type = type(e).__name__
            error_msg = str(e)
            
            # SSL 错误特殊处理
            if isinstance(e, (RequestsSSLError, ssl.SSLError)) or 'SSL' in error_type or 'EOF occurred in violation of protocol' in error_msg:
                print("🔒 SSL/TLS 连接错误", file=sys.stderr)
                print(f"   错误类型: {error_type}", file=sys.stderr)
                print(f"   错误信息: {error_msg[:200]}...", file=sys.stderr)
                print("", file=sys.stderr)
                print("💡 这不是账户或余额问题！这是网络连接问题。", file=sys.stderr)
                print("   可能的原因：", file=sys.stderr)
                print("   1. SSL/TLS 协议版本不兼容", file=sys.stderr)
                print("   2. 网络环境限制（防火墙/代理）", file=sys.stderr)
                print("   3. Python/OpenSSL 版本问题", file=sys.stderr)
                print("   4. 服务器端 SSL 配置问题", file=sys.stderr)
                print("", file=sys.stderr)
                print("   建议解决方案：", file=sys.stderr)
                print("   1. 更新 Python、requests、urllib3: pip install --upgrade requests urllib3", file=sys.stderr)
                print("   2. 检查网络连接和代理设置", file=sys.stderr)
                print("   3. 尝试使用 DeepSeek API（如果已配置）", file=sys.stderr)
            # 账户/权限错误
            elif any(keyword in error_msg.lower() for keyword in ['401', '403', 'unauthorized', 'forbidden', 'invalid api key', '余额', 'quota', '账户']):
                print("💰 API 账户/权限问题", file=sys.stderr)
                print(f"   错误类型: {error_type}", file=sys.stderr)
                print(f"   错误信息: {error_msg}", file=sys.stderr)
                print("", file=sys.stderr)
                print("💡 这可能是账户问题，请检查：", file=sys.stderr)
                print("   1. API Key 是否正确", file=sys.stderr)
                print("   2. 账户是否有余额", file=sys.stderr)
                print("   3. API 服务是否已开通", file=sys.stderr)
            # 其他错误
            else:
                print(f"❌ AI识别失败: {error_type}: {error_msg}", file=sys.stderr)
            
            # 如果是 DashScope SDK 的异常，显示详细信息
            if DASHSCOPE_AVAILABLE and hasattr(e, 'response'):
                print("", file=sys.stderr)
                print("📋 DashScope SDK 响应详情：", file=sys.stderr)
                if hasattr(e.response, 'status_code'):
                    print(f"   HTTP状态码: {e.response.status_code}", file=sys.stderr)
                if hasattr(e.response, 'message'):
                    print(f"   错误消息: {e.response.message}", file=sys.stderr)
                if hasattr(e.response, 'code'):
                    print(f"   错误代码: {e.response.code}", file=sys.stderr)
            
            # 仅在开发环境显示完整堆栈跟踪
            if os.environ.get('FLASK_ENV') != 'production':
                print("", file=sys.stderr)
                print("📚 完整错误堆栈：", file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
            
            print("=" * 80, file=sys.stderr)
            print("⚠️ 切换至模拟模式（返回示例数据）", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            return self._generate_simulation_food_recognition()
    
    def _call_deepseek_vision_api(self, image_base64, prompt):
        """调用DeepSeek视觉API（优先使用DeepSeek-VL2视觉模型）"""
        import sys
        
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API Key未配置")
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }
        
        # 使用 deepseek-chat（DeepSeek-V3.2）
        # DeepSeek-V3.2 支持视觉功能，需要使用 DeepSeek 原生格式：
        # content 中使用 <image> 占位符，images 字段包含 base64 图片
        model_name = "deepseek-chat"
        
        # 优先使用 DeepSeek 原生格式（已验证可用）
        formats_to_try = [
            {
                "name": "DeepSeek原生格式(<image>+images)",
                "data": {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{prompt}\n<image>",
                            "images": [f"data:image/jpeg;base64,{image_base64}"]
                        }
                    ],
                    "temperature": 0.7
                }
            },
            {
                "name": "OpenAI格式(image_url)",
                "data": {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.7
                }
            }
        ]
        
        for format_info in formats_to_try:
            format_name = format_info["name"]
            data = format_info["data"]
            
            try:
                print(f"📤 正在调用 DeepSeek API识别食物...", file=sys.stderr)
                print(f"   URL: {url}", file=sys.stderr)
                print(f"   Model: {model_name}", file=sys.stderr)
                print(f"   格式: {format_name}", file=sys.stderr)
                print(f"   API Key: {self.deepseek_api_key[:10]}...{self.deepseek_api_key[-5:] if len(self.deepseek_api_key) > 15 else '***'}", file=sys.stderr)
                print(f"   图片大小: {len(image_base64)} 字符 (base64)", file=sys.stderr)
                
                response = requests.post(url, headers=headers, json=data, timeout=(10, 60))
                
                print(f"📥 HTTP响应状态码: {response.status_code}", file=sys.stderr)
                
                if response.status_code != 200:
                    error_text = response.text[:2000] if response.text else "无响应内容"
                    print(f"❌ DeepSeek API调用失败 (格式: {format_name}): HTTP {response.status_code}", file=sys.stderr)
                    print(f"   错误详情: {error_text}", file=sys.stderr)
                    
                    # 尝试解析错误JSON
                    try:
                        error_json = response.json()
                        error_info = error_json.get('error', {})
                        error_msg = error_info.get('message', '未知错误')
                        error_type = error_info.get('type', '')
                        print(f"   错误类型: {error_type}", file=sys.stderr)
                        print(f"   错误消息: {error_msg}", file=sys.stderr)
                    except:
                        pass
                    
                    # 如果不是最后一个格式，尝试下一个
                    if format_info != formats_to_try[-1]:
                        print(f"   尝试下一个格式...", file=sys.stderr)
                        continue
                    
                    response.raise_for_status()
                
                result = response.json()
                print(f"📦 响应JSON键: {list(result.keys())}", file=sys.stderr)
                
                # 检查API返回的错误
                if 'error' in result:
                    error_info = result['error']
                    error_msg = error_info.get('message', '未知错误')
                    error_type = error_info.get('type', '')
                    print(f"❌ DeepSeek API返回错误: {error_type} - {error_msg}", file=sys.stderr)
                    
                    # 如果不是最后一个格式，尝试下一个
                    if format_info != formats_to_try[-1]:
                        print(f"   尝试下一个格式...", file=sys.stderr)
                        continue
                    
                    raise ValueError(f"DeepSeek API错误: {error_msg}")
                
                if 'choices' not in result:
                    print(f"❌ DeepSeek API响应格式错误", file=sys.stderr)
                    if format_info != formats_to_try[-1]:
                        print(f"   尝试下一个格式...", file=sys.stderr)
                        continue
                    raise ValueError("DeepSeek API响应格式错误")
                
                content = result['choices'][0]['message']['content']
                print(f"✅ DeepSeek API调用成功！(使用格式: {format_name})", file=sys.stderr)
                print(f"   返回内容长度: {len(content)} 字符", file=sys.stderr)
                print(f"   响应内容预览: {content[:300]}...", file=sys.stderr)
                return content
                
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求异常 (格式: {format_name}): {str(e)}", file=sys.stderr)
                if format_info == formats_to_try[-1]:
                    raise
                print(f"   尝试下一个格式...", file=sys.stderr)
                continue
        
        # 如果所有格式都失败
        raise ValueError("deepseek-chat 不支持图片输入。请检查 DeepSeek API 文档确认是否支持视觉功能。")
    
    def _call_qianwen_vision_compatible_mode(self, image_base64, prompt):
        """
        使用兼容模式 API 调用通义千问视觉模型
        根据文档：https://dashscope.aliyuncs.com/compatible-mode/v1
        """
        import sys
        
        if not self.qianwen_api_key:
            raise ValueError("通义千问API Key未配置")
        
        # 兼容模式 URL（根据文档推荐）
        base_url = os.environ.get('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        url = f"{base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.qianwen_api_key.strip()}"
        }
        
        # 兼容模式使用 OpenAI 格式
        # 注意：根据官方文档，content 数组顺序可以是 text 在前或 image_url 在前
        # 这里使用 text 在前，image_url 在后的格式（更符合常见用法）
        data = {
            "model": "qwen-vl-plus",  # 或 qwen-vl-max
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.7
        }
        
        print(f"   📡 兼容模式 API URL: {url}", file=sys.stderr)
        print(f"   📡 Model: qwen-vl-plus", file=sys.stderr)
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=(10, 90))
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"   ✅ 兼容模式 API 调用成功，响应长度: {len(content)} 字符", file=sys.stderr)
                return self._parse_food_recognition_response(content)
            else:
                # 详细错误诊断
                error_text = response.text[:1000] if response.text else "无响应内容"
                print(f"   ❌ HTTP 状态码: {response.status_code}", file=sys.stderr)
                print(f"   📋 响应头: {dict(response.headers)}", file=sys.stderr)
                print(f"   📋 响应内容: {error_text}", file=sys.stderr)
                
                error_msg = f"HTTP {response.status_code}"
                error_detail = {}
                
                # 尝试解析错误 JSON
                try:
                    error_json = response.json()
                    if 'error' in error_json:
                        error_detail = error_json['error']
                        error_msg = error_detail.get('message', error_msg)
                        error_code = error_detail.get('code', '')
                        error_type = error_detail.get('type', '')
                        
                        print(f"   🔍 错误类型: {error_type}", file=sys.stderr)
                        print(f"   🔍 错误代码: {error_code}", file=sys.stderr)
                        print(f"   🔍 错误消息: {error_msg}", file=sys.stderr)
                        
                        # 常见错误诊断
                        if response.status_code == 401:
                            print("", file=sys.stderr)
                            print("   💡 诊断：API Key 认证失败", file=sys.stderr)
                            print("   可能原因：", file=sys.stderr)
                            print("   1. API Key 不正确或已过期", file=sys.stderr)
                            print("   2. API Key 格式错误（应该以 sk- 开头）", file=sys.stderr)
                            print("   3. API Key 未正确配置到环境变量 QWEN_API_KEY", file=sys.stderr)
                            print(f"   4. 当前使用的 Key 前10字符: {self.qianwen_api_key[:10] if self.qianwen_api_key else 'None'}...", file=sys.stderr)
                        elif response.status_code == 403:
                            print("", file=sys.stderr)
                            print("   💡 诊断：API 权限不足", file=sys.stderr)
                            print("   可能原因：", file=sys.stderr)
                            print("   1. 账户未开通该服务", file=sys.stderr)
                            print("   2. 服务权限未激活", file=sys.stderr)
                            print("   3. API Key 权限不足", file=sys.stderr)
                        elif response.status_code == 400:
                            print("", file=sys.stderr)
                            print("   💡 诊断：请求参数错误", file=sys.stderr)
                            print("   可能原因：", file=sys.stderr)
                            print("   1. 模型名称不正确（当前使用: qwen-vl-plus）", file=sys.stderr)
                            print("   2. 请求格式不符合 API 要求", file=sys.stderr)
                            print("   3. 图片格式或大小不符合要求", file=sys.stderr)
                        elif response.status_code == 429:
                            print("", file=sys.stderr)
                            print("   💡 诊断：请求频率限制", file=sys.stderr)
                            print("   建议：稍后重试", file=sys.stderr)
                        elif 'quota' in error_text.lower() or '余额' in error_text or 'insufficient' in error_text.lower():
                            print("", file=sys.stderr)
                            print("   💡 诊断：账户余额不足", file=sys.stderr)
                            print("   建议：检查账户余额，即使刚充值也可能需要几分钟生效", file=sys.stderr)
                    else:
                        print(f"   📋 完整错误响应: {error_json}", file=sys.stderr)
                except Exception as parse_error:
                    print(f"   ⚠️ 无法解析错误响应: {parse_error}", file=sys.stderr)
                
                raise ValueError(f"兼容模式 API 调用失败 ({response.status_code}): {error_msg}")
                
        except requests.exceptions.SSLError as ssl_err:
            # SSL 错误，让上层处理
            raise
        except Exception as e:
            raise ValueError(f"兼容模式 API 调用异常: {str(e)}") from e
    
    def _call_qianwen_vision_api(self, image_base64, prompt):
        """调用通义千问视觉API（直接HTTP方式，备用方案）"""
        if not self.qianwen_api_key:
            raise ValueError("通义千问API Key未配置")
        
        # 验证API Key格式（通义千问API Key格式可能不同，不强制检查）
        import sys
        if len(self.qianwen_api_key) < 10:
            print(f"⚠️  警告：通义千问API Key长度可能不正确: {len(self.qianwen_api_key)} 字符", file=sys.stderr)
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        
        # 清理API Key（去除前后空格和换行符）
        api_key_clean = self.qianwen_api_key.strip() if self.qianwen_api_key else ""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key_clean}"
        }
        
        import sys
        print(f"🔑 API Key清理后长度: {len(api_key_clean)}", file=sys.stderr)
        print(f"🔑 API Key前10字符: {api_key_clean[:10] if api_key_clean else 'None'}...", file=sys.stderr)
        
        data = {
            "model": "qwen-vl-max",  # 通义千问视觉模型
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": f"data:image/jpeg;base64,{image_base64}"
                            },
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "temperature": 0.7
            }
        }
        
        import sys
        print(f"📤 正在调用通义千问视觉API...", file=sys.stderr)
        print(f"   URL: {url}", file=sys.stderr)
        print(f"   Model: qwen-vl-max", file=sys.stderr)
        print(f"   API Key: {self.qianwen_api_key[:10]}...{self.qianwen_api_key[-5:] if len(self.qianwen_api_key) > 15 else '***'}", file=sys.stderr)
        print(f"   图片大小: {len(image_base64)} 字符 (base64)", file=sys.stderr)
        print(f"   提示词长度: {len(prompt)} 字符", file=sys.stderr)
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=(10, 60))
            
            import sys
            print(f"📥 HTTP响应状态码: {response.status_code}", file=sys.stderr)
            
            if response.status_code != 200:
                error_text = response.text[:2000] if response.text else "无响应内容"
                print(f"❌ 通义千问API调用失败: HTTP {response.status_code}", file=sys.stderr)
                print(f"   错误详情: {error_text}", file=sys.stderr)
                
                # 尝试解析错误JSON
                try:
                    error_json = response.json()
                    error_msg = error_json.get('message', error_json.get('Message', '未知错误'))
                    error_code = error_json.get('code', error_json.get('Code', ''))
                    request_id = error_json.get('RequestId', '')
                    print(f"   错误代码: {error_code}", file=sys.stderr)
                    print(f"   错误消息: {error_msg}", file=sys.stderr)
                    if request_id:
                        print(f"   请求ID: {request_id}", file=sys.stderr)
                    print(f"   完整错误响应: {error_json}", file=sys.stderr)
                    
                    # 检查是否是余额不足
                    if '余额' in error_msg or 'quota' in error_msg.lower() or 'insufficient' in error_msg.lower():
                        print("=" * 80, file=sys.stderr)
                        print("💰 检测到可能是余额不足的错误！", file=sys.stderr)
                        print("   请检查您的通义千问账户余额", file=sys.stderr)
                        print("=" * 80, file=sys.stderr)
                except Exception as parse_error:
                    print(f"   无法解析错误JSON: {parse_error}", file=sys.stderr)
                
                response.raise_for_status()
            
            result = response.json()
            import sys
            print(f"📦 响应JSON键: {list(result.keys())}", file=sys.stderr)
            
            # 检查API返回的错误
            if 'output' not in result:
                error_msg = result.get('message', result.get('Message', '未知错误'))
                error_code = result.get('code', result.get('Code', ''))
                request_id = result.get('RequestId', '')
                print(f"❌ 通义千问API返回错误: {error_msg} (code: {error_code})", file=sys.stderr)
                if request_id:
                    print(f"   请求ID: {request_id}", file=sys.stderr)
                print(f"   完整响应: {result}", file=sys.stderr)
                
                # 检查是否是余额不足
                if '余额' in error_msg or 'quota' in error_msg.lower() or 'insufficient' in error_msg.lower():
                    print("=" * 80, file=sys.stderr)
                    print("💰 检测到可能是余额不足的错误！", file=sys.stderr)
                    print("   请检查您的通义千问账户余额", file=sys.stderr)
                    print("=" * 80, file=sys.stderr)
                
                raise ValueError(f"通义千问API错误: {error_msg}")
            
            if 'choices' not in result['output']:
                error_msg = result.get('message', '未知错误')
                print(f"❌ 通义千问API响应格式错误: {error_msg}", file=sys.stderr)
                print(f"   output内容: {result.get('output', {})}", file=sys.stderr)
                raise ValueError(f"通义千问API响应格式错误: {error_msg}")
            
            content = result['output']['choices'][0]['message']['content']
            print(f"✅ 通义千问视觉API调用成功！", file=sys.stderr)
            print(f"   返回内容长度: {len(content)} 字符", file=sys.stderr)
            print(f"   响应内容预览: {content[:300]}...", file=sys.stderr)
            return content
        except requests.exceptions.RequestException as e:
            print(f"❌ 通义千问API请求异常: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def _parse_food_recognition_response(self, response_text):
        """解析食物识别响应（通义千问）"""
        import sys
        try:
            # 打印原始响应，便于调试
            print(f"📥 通义千问原始响应:", file=sys.stderr)
            print(f"   {response_text[:500]}...", file=sys.stderr)
            
            # 尝试提取JSON
            response_text = response_text.strip()
            
            # 移除 markdown 代码块标记
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            
            # 尝试找到JSON部分（从第一个 { 到最后一个 }）
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            print(f"📦 提取的JSON文本:", file=sys.stderr)
            print(f"   {response_text}", file=sys.stderr)
            
            result = json.loads(response_text)
            
            # 验证格式
            if 'foods' in result and isinstance(result['foods'], list):
                # 检查是否有"无法识别"的情况
                for food in result['foods']:
                    if food.get('name') == '无法识别':
                        print(f"⚠️ 通义千问返回'无法识别'，可能是图片识别失败", file=sys.stderr)
                return result
            else:
                # 尝试其他格式
                if 'name' in result and 'calories' in result:
                    return {"foods": [result]}
                raise ValueError("响应格式不正确：缺少 'foods' 字段")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            import sys
            print(f"❌ JSON解析失败: {str(e)}", file=sys.stderr)
            print(f"   原始响应: {response_text[:500]}", file=sys.stderr)
            print(f"⚠️ 使用模拟数据", file=sys.stderr)
            return self._generate_simulation_food_recognition()
    
    def _generate_simulation_food_recognition(self):
        """生成模拟的食物识别响应"""
        return {
            "foods": [
                {
                    "name": "示例食物（模拟模式）",
                    "calories": 200
                }
            ]
        }
    
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

    def generate_daily_plan(self, profile_data, target_weight_change_kg, weeks=4, log_data=None, goal_type='gain'):
        """
        根据体重管理目标生成每日饮食和运动建议

        Args:
            profile_data: 用户档案数据
            target_weight_change_kg: 目标体重变化（公斤，正数为增重，负数为减重）
            weeks: 计划周期（周）
            log_data: 用户近30天的饮食记录统计（可选）
            goal_type: 目标类型，'gain' 增重 或 'loss' 减重

        Returns:
            dict: 包含每日饮食建议和运动建议，以及is_ai_generated标识
        """
        goal_text = '增重' if goal_type == 'gain' else '减重'
        
        # 检查API Key配置，如果没有配置则使用模拟模式
        if not self.deepseek_api_key and not self.qianwen_api_key:
            print("=" * 60)
            print(f"⚠️ 【模拟模式】未检测到API Key，使用本地模拟模式生成每日{goal_text}计划")
            print("=" * 60)
            result = self._generate_simulation_daily_plan(profile_data, target_weight_change_kg, weeks, log_data, goal_type)
            result['_is_ai_generated'] = False
            result['_mode'] = 'simulation'
            result['_reason'] = 'no_api_key'
            return result

        prompt = self._build_daily_plan_prompt(profile_data, target_weight_change_kg, weeks, log_data, goal_type)
        
        try:
            print("=" * 60)
            print(f"🤖 【真实AI模式】正在调用AI API生成每日{goal_text}计划")
            print(f"   目标{goal_text}: {target_weight_change_kg}kg")
            print(f"   计划周期: {weeks}周")
            print(f"   使用服务: {self.provider.upper()}")
            print(f"   提示词长度: {len(prompt)} 字符")
            print("=" * 60)
            
            if self.provider == 'deepseek':
                response = self._call_deepseek_api(prompt)
            else:
                response = self._call_qianwen_api(prompt)
            
            print(f"✅ AI API调用成功，响应长度: {len(response)} 字符")
            print(f"📝 AI原始响应前500字符: {response[:500]}")
            parsed_response = self._parse_daily_plan_response(response)
            
            print(f"📦 解析后的响应类型: {type(parsed_response)}")
            print(f"📦 解析后的响应键: {list(parsed_response.keys()) if isinstance(parsed_response, dict) else '不是字典'}")
            if isinstance(parsed_response, dict):
                print(f"📦 是否有 daily_diet: {'daily_diet' in parsed_response}")
                if 'daily_diet' in parsed_response:
                    print(f"📦 daily_diet 内容: {parsed_response.get('daily_diet')}")
                print(f"📦 是否有 daily_exercise: {'daily_exercise' in parsed_response}")
            
            # 验证返回的数据结构
            if not parsed_response or 'daily_diet' not in parsed_response:
                print("⚠️ AI返回的数据格式不正确，降级到模拟模式")
                print(f"⚠️ parsed_response 内容: {parsed_response}")
                result = self._generate_simulation_daily_plan(profile_data, target_weight_change_kg, weeks, log_data, goal_type)
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
            print(f"📊 返回数据结构: daily_diet={parsed_response.get('daily_diet') is not None}, daily_exercise={parsed_response.get('daily_exercise') is not None}")
            print(f"📊 daily_diet 键: {list(parsed_response.get('daily_diet', {}).keys()) if isinstance(parsed_response.get('daily_diet'), dict) else 'N/A'}")
            print("=" * 60)
            return parsed_response
        except Exception as e:
            print("=" * 60)
            print(f"❌ 【降级到模拟模式】AI API调用失败: {str(e)}")
            print("=" * 60)
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            # 确保即使API失败也返回模拟数据
            result = self._generate_simulation_daily_plan(profile_data, target_weight_change_kg, weeks, log_data, goal_type)
            result['_is_ai_generated'] = False
            result['_mode'] = 'simulation'
            result['_reason'] = f'api_error: {str(e)[:100]}'
            return result

    def _build_daily_plan_prompt(self, profile_data, target_weight_change_kg, weeks, log_data=None, goal_type='gain'):
        """构建每日计划提示词"""
        current_weight = profile_data.get('weight_kg', 60)
        bmr = profile_data.get('bmr', 1500)
        age = profile_data.get('age', 25)
        gender = profile_data.get('gender', '未知')
        height = profile_data.get('height_cm', 170)
        
        goal_text = '增重' if goal_type == 'gain' else '减重'
        
        # 计算每日需要增加或减少的热量
        # 7700kcal = 1kg，所以目标体重变化需要的总热量 = target_weight_change_kg * 7700
        total_calories_needed = abs(target_weight_change_kg) * 7700
        if goal_type == 'gain':
            daily_calorie_change = total_calories_needed / (weeks * 7)  # 需要增加的热量
        else:
            daily_calorie_change = -total_calories_needed / (weeks * 7)  # 需要减少的热量（负数）
        
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
请基于用户当前的饮食和运动习惯，制定一个渐进式的{goal_text}计划。考虑：
1. 用户当前的热量摄入水平，建议在现有基础上逐步{'增加' if goal_type == 'gain' else '减少'}
2. 用户当前的营养素比例，适当调整以支持健康{goal_text}
3. 用户当前的运动习惯，{'建议增加力量训练以促进肌肉增长' if goal_type == 'gain' else '建议增加有氧运动以促进脂肪燃烧，同时保留力量训练以维持肌肉量'}
4. {'避免过快增重导致脂肪堆积过多' if goal_type == 'gain' else '避免过快减重导致肌肉流失和代谢下降'}
"""
        else:
            current_diet_info = f"""
【用户当前饮食情况】
- 用户暂无近30天的饮食记录
- 建议基于基础代谢率(BMR)制定初始{goal_text}计划
- {'增重期间建议热量摄入为BMR的1.5-1.8倍' if goal_type == 'gain' else '减重期间建议热量摄入为BMR的1.2-1.4倍，确保不低于BMR'}
"""
        
        # 获取用户当前数据用于提示词
        avg_intake = log_data.get('avg_daily_intake', bmr * 1.2) if log_data else bmr * 1.2
        exercise_duration = log_data.get('exercise_duration', 0) if log_data else 0
        steps = log_data.get('steps', 6000) if log_data else 6000
        
        prompt = f"""【角色】你是一位资深的注册营养师和运动教练，拥有10年以上临床经验。

【任务】根据用户的目标{goal_text}需求，制定详细的、个性化的每日饮食和运动计划。**重要：所有建议必须基于用户的具体情况，不要使用模板化的通用建议。**

**⚠️ 关键提醒：用户的目标是{goal_text}，{'不是减重' if goal_type == 'gain' else '不是增重'}。请确保所有建议都围绕{goal_text}目标制定，{'建议增加热量摄入和力量训练' if goal_type == 'gain' else '建议减少热量摄入（但不要低于BMR）、增加有氧运动、保持力量训练以维持肌肉'}。**

【用户基本信息】
- 年龄: {age}岁
- 性别: {gender}
- 身高: {height}cm
- 当前体重: {current_weight}kg
- 基础代谢率(BMR): {bmr}kcal
- BMI: {profile_data.get('bmi', '未知')}

【目标设定】
- **目标{goal_text}**: {target_weight_change_kg}kg（{'需要增加体重' if goal_type == 'gain' else '需要减少体重'}）
- 计划周期: {weeks}周
- 平均每周需要{goal_text}: 约{target_weight_change_kg / weeks:.2f}kg/周
- 平均每日需要热量{'盈余（需要增加摄入）' if goal_type == 'gain' else '缺口（需要减少摄入）'}: 约{abs(daily_calorie_change):.0f}kcal
- **重要**：{'增重期间需要创造热量盈余，增加蛋白质和力量训练以促进肌肉增长' if goal_type == 'gain' else '减重期间需要创造热量缺口，但不要低于BMR，增加有氧运动促进脂肪燃烧，保持力量训练维持肌肉量'}

{current_diet_info}

【要求】
1. 制定每日饮食建议（不需要具体到每一餐，只需要每日总量和主要食物类型）：
   - 每日总热量摄入建议（kcal），必须基于用户当前摄入量({avg_intake:.0f}kcal)和BMR({bmr}kcal)计算。{'建议在现有基础上逐步增加，但不要过快' if goal_type == 'gain' else '建议在现有基础上适当减少，但不要低于BMR，避免代谢下降'}
   - 碳水化合物摄入量（g）和主要来源：请根据用户年龄({age}岁)、性别({gender})和当前饮食习惯，提供至少5-6种具体的、多样化的食物来源（不要只使用示例中的食物，要提供个性化的选择）。{'增重期间可以适当增加碳水摄入' if goal_type == 'gain' else '减重期间可以适当减少碳水摄入，但不要完全避免，选择复合碳水'}
   - 蛋白质摄入量（g）和主要来源：请提供至少5-6种具体的、{'适合增重的优质蛋白质来源' if goal_type == 'gain' else '适合减重期间维持肌肉的优质蛋白质来源'}（考虑用户性别和年龄，提供多样化的选择）。{'增重期间需要充足的蛋白质支持肌肉增长' if goal_type == 'gain' else '减重期间需要充足的蛋白质（每公斤体重2.0g以上）以维持肌肉量，防止肌肉流失'}
   - 脂肪摄入量（g）和主要来源：请提供至少4-5种健康脂肪来源（考虑用户当前脂肪摄入比例，提供个性化的建议）。{'增重期间可以适当增加健康脂肪' if goal_type == 'gain' else '减重期间控制脂肪摄入，但不要完全避免，选择健康脂肪'}
   - 膳食纤维建议（g），基于用户当前摄入情况。{'增重期间保持充足纤维' if goal_type == 'gain' else '减重期间增加纤维摄入，有助于增加饱腹感'}
   - 每日饮水量建议（L），考虑用户体重({current_weight}kg)和活动量。{'增重期间保持充足水分' if goal_type == 'gain' else '减重期间需要充足水分，有助于代谢和饱腹感'}

2. 制定每日运动建议（必须个性化，不要使用模板化的建议）：
   - 有氧运动类型、时长和强度：根据用户当前运动习惯({exercise_duration:.0f}分钟/天)和步数({steps:.0f}步/天)，提供具体的、渐进式的建议（不要只写"快走或慢跑"，要给出更具体的运动类型和强度说明）。{'增重期间有氧运动以中等强度为主，避免过度消耗' if goal_type == 'gain' else '减重期间有氧运动以中高强度为主，促进脂肪燃烧，建议每周4-5次，每次40-60分钟'}
   - 力量训练建议：根据用户年龄和性别，提供具体的训练方案（不要只写"力量训练"，要具体说明训练内容和频率）。{'增重期间重点增加力量训练以促进肌肉增长，建议每周3-4次' if goal_type == 'gain' else '减重期间保持力量训练以维持肌肉量，防止代谢下降，建议每周2-3次，重点维持而非增长'}
   - 日常活动建议（步数等）：基于用户当前步数，给出具体的目标。{'增重期间建议8000-10000步/天' if goal_type == 'gain' else '减重期间建议10000-12000步/天，增加日常活动量'}
   - 休息和恢复建议：提供具体的休息安排。{'增重期间保证充足休息以支持肌肉恢复和增长' if goal_type == 'gain' else '减重期间保证充足休息，避免过度训练导致代谢下降'}

3. 注意事项和风险提示：
   - 必须基于用户的具体情况（年龄、性别、当前体重、目标{goal_text}速度）提供个性化的注意事项
   - 风险提示要具体，不要使用通用的模板
   - {'避免过快增重导致脂肪堆积过多，建议每周增重0.5-1kg' if goal_type == 'gain' else '避免过快减重导致肌肉流失、代谢下降和反弹风险，建议每周减重0.5-1kg，不要超过1.5kg'}
   - {'增重期间注意营养均衡，避免只增脂肪，要增加肌肉量' if goal_type == 'gain' else '减重期间注意营养均衡，避免肌肉流失，保持力量训练，不要过度节食'}

【重要】请确保：
- 所有建议必须个性化，不要直接使用示例中的内容
- 食物来源要多样化，至少提供5-6种不同的食物
- 运动建议要具体，不要使用"快走或慢跑"这样的通用描述，要给出更具体的建议
- 注意事项和风险提示要针对用户的具体情况

【输出格式】严格使用JSON格式（**以下仅为格式示例，请根据用户具体情况生成个性化内容，不要直接使用示例中的食物和运动类型**）：
{{
  "daily_diet": {{
    "total_calories": <基于用户当前摄入量和目标{goal_text}计算的具体数值，{'建议在现有基础上增加' if goal_type == 'gain' else '建议在现有基础上减少，但不要低于BMR'}>,
    "carbohydrates": {{
      "amount": <具体数值>,
      "unit": "g",
      "sources": ["<至少5-6种个性化的碳水来源，不要使用示例中的食物>"]
    }},
    "protein": {{
      "amount": <具体数值>,
      "unit": "g",
      "sources": ["<至少5-6种个性化的蛋白质来源，考虑用户性别和年龄>"]
    }},
    "fat": {{
      "amount": <具体数值>,
      "unit": "g",
      "sources": ["<至少4-5种个性化的脂肪来源>"]
    }},
    "fiber": {{
      "amount": <具体数值>,
      "unit": "g"
    }},
    "water": {{
      "amount": <基于用户体重和活动量计算>,
      "unit": "L"
    }},
    "notes": ["<个性化的饮食建议，至少3条，不要使用模板化语言>"]
  }},
  "daily_exercise": {{
    "aerobic": {{
      "type": "<具体的运动类型，不要只写'快走或慢跑'，要给出更具体的建议>",
      "duration": <具体数值>,
      "unit": "分钟",
      "frequency": "<具体的频率，如'每周3次，周一、三、五'>",
      "intensity": "<具体的强度说明，如'心率控制在最大心率的65-75%'>"
    }},
    "strength": {{
      "type": "<具体的训练类型，不要只写'力量训练'，要说明训练内容>",
      "duration": <具体数值>,
      "unit": "分钟",
      "frequency": "<具体的频率>",
      "focus": "<具体的训练重点，如'上肢推拉训练+下肢蹲举训练'>"
    }},
    "steps": {{
      "target": <基于用户当前步数的具体目标>,
      "unit": "步"
    }},
    "rest": "<具体的休息建议，不要使用模板化语言>"
  }},
  "notes": ["<至少3条个性化的注意事项，基于用户年龄、性别、目标{goal_text}速度>"],
  "risks": ["<至少2条具体的风险提示，针对用户情况，{'增重期间注意避免脂肪堆积' if goal_type == 'gain' else '减重期间注意避免肌肉流失和代谢下降'}>"]
}}

**再次强调：**
1. 请生成个性化的、具体的内容，不要直接使用示例中的食物列表、运动类型和注意事项
2. **用户的目标是{goal_text}**，{'所有建议必须围绕增重目标，包括增加热量摄入、增加力量训练等' if goal_type == 'gain' else '所有建议必须围绕减重目标，包括减少热量摄入（不低于BMR）、增加有氧运动、保持力量训练维持肌肉等'}
3. {'增重期间的重点是增加肌肉量，避免只增脂肪' if goal_type == 'gain' else '减重期间的重点是减少脂肪，同时维持肌肉量，避免代谢下降'}
"""
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
            return self._generate_simulation_daily_plan({}, 0, 4, None, 'gain')
        except Exception as e:
            print(f"❌ 解析AI响应时出错: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return self._generate_simulation_daily_plan({}, 0, 4, None, 'gain')

    def _generate_simulation_daily_plan(self, profile_data, target_weight_change_kg, weeks, log_data=None, goal_type='gain'):
        """生成模拟的每日计划（基于规则）"""
        goal_text = '增重' if goal_type == 'gain' else '减重'
        print(f"📝 【模拟模式】使用基于规则的算法生成每日{goal_text}计划")
        print(f"   目标{goal_text}: {target_weight_change_kg}kg, 周期: {weeks}周")
        
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
            # 基于当前平均摄入量，计算所需的热量变化
            total_calories_needed = abs(target_weight_change_kg) * 7700
            daily_calorie_change = total_calories_needed / (weeks * 7)
            if goal_type == 'gain':
                target_calories = avg_intake + daily_calorie_change
            else:
                # 减重时，确保不低于BMR
                target_calories = max(bmr, avg_intake - daily_calorie_change)
            
            # 使用历史营养素比例作为参考
            carb_pct = log_data.get('carb_percent', 50)
            protein_pct = log_data.get('protein_percent', 20)
            fat_pct = log_data.get('fat_percent', 30)
            
            print(f"📊 基于历史记录: 当前平均摄入{avg_intake:.0f}kcal，目标摄入{target_calories:.0f}kcal")
        else:
            # 没有历史记录，使用BMR计算
            total_calories_needed = abs(target_weight_change_kg) * 7700
            daily_calorie_change = total_calories_needed / (weeks * 7)
            if goal_type == 'gain':
                target_calories = bmr * 1.5 + daily_calorie_change  # BMR * 1.5 作为基础活动量
            else:
                # 减重时，确保不低于BMR
                target_calories = max(bmr, bmr * 1.3 - daily_calorie_change)
            
            # 使用标准比例
            carb_pct = 50
            protein_pct = 20
            fat_pct = 30
        
        # 计算营养素分配
        if goal_type == 'gain':
            # 增重期间适当增加蛋白质和碳水
            protein_grams = current_weight * 1.8  # 每公斤体重1.8g蛋白质
        else:
            # 减重期间保持较高蛋白质以维持肌肉
            protein_grams = current_weight * 2.0  # 每公斤体重2.0g蛋白质
        carb_grams = (target_calories * (carb_pct / 100)) / 4  # 基于历史比例或标准比例
        fat_grams = (target_calories * (fat_pct / 100)) / 9
        
        goal_text = '增重' if goal_type == 'gain' else '减重'
        print(f"✅ 模拟{goal_text}计划计算完成: 目标热量={int(target_calories)}kcal, 蛋白质={int(protein_grams)}g")
        
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
                    "运动前后1小时内补充碳水" if goal_type == 'gain' else "运动前后适当补充蛋白质，避免运动后立即大量摄入碳水",
                    "睡前可适量补充蛋白质" if goal_type == 'gain' else "睡前避免大量进食，可适量补充蛋白质"
                ]
            },
            "daily_exercise": {
                "aerobic": {
                    "type": "快走或慢跑" if goal_type == 'gain' else "快走、慢跑或HIIT训练",
                    "duration": 30 if goal_type == 'gain' else 40,
                    "unit": "分钟",
                    "frequency": "每周3-4次" if goal_type == 'gain' else "每周4-5次",
                    "intensity": "中等强度（心率控制在最大心率的60-70%）" if goal_type == 'gain' else "中高强度（心率控制在最大心率的65-80%）"
                },
                "strength": {
                    "type": "力量训练",
                    "duration": 45,
                    "unit": "分钟",
                    "frequency": "每周2-3次",
                    "focus": "全身大肌群（深蹲、卧推、硬拉等）" if goal_type == 'gain' else "全身大肌群（深蹲、卧推、硬拉等），重点维持肌肉量"
                },
                "steps": {
                    "target": 8000 if goal_type == 'gain' else 10000,
                    "unit": "步"
                },
                "rest": "每周至少1-2天完全休息，保证充足睡眠"
            },
            "notes": [
                "增重期间注意营养均衡，避免只增脂肪" if goal_type == 'gain' else "减重期间注意营养均衡，避免肌肉流失",
                "力量训练有助于增加肌肉量" if goal_type == 'gain' else "力量训练有助于维持肌肉量，防止代谢下降",
                "保证充足睡眠（7-9小时）有助于恢复和增重" if goal_type == 'gain' else "保证充足睡眠（7-9小时）有助于恢复和减重"
            ],
            "risks": [
                "过快增重可能导致脂肪增加过多",
                "热量摄入过高可能影响消化系统"
            ] if goal_type == 'gain' else [
                "过快减重可能导致肌肉流失和代谢下降",
                "热量摄入过低可能导致营养不良和反弹风险"
            ]
        }

# 全局AI服务实例
ai_service = AIService()

