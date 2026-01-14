from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, UserProfile, DailyLog, Report, ReportHistory
from app.models.role import Role
from app import db
import os
import json
import hashlib
import tempfile
import io
from datetime import datetime, timedelta
from fpdf import FPDF  # type: ignore
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

report_bp = Blueprint('report', __name__)

def get_chinese_font_path():
    """Find a suitable Chinese font on the system."""
    candidates = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
    ]
    
    for path in candidates:
        if os.path.exists(path):
            print(f"Found font: {path}")
            return path
            
    print("No Chinese font found in candidates")
    return None

def generate_chart_image(linear_data, ai_data, weeks, current_weight):
    """生成体重预测曲线图表，返回图片字节流"""
    try:
        # 设置中文字体
        font_path = get_chinese_font_path()
        if font_path:
            try:
                prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.sans-serif'] = [prop.get_name()]
            except:
                pass
        
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 生成X轴数据（周数）
        x_data = list(range(weeks + 1))
        x_labels = [f'第{i}周' if i == 0 else f'第{i}周' for i in range(weeks + 1)]
        
        # 绘制线性预测线
        if linear_data and len(linear_data) == weeks + 1:
            ax.plot(x_data, linear_data, '--', color='#409EFF', linewidth=2, 
                   marker='o', markersize=4, label='线性预测 (能量平衡)')
        
        # 绘制AI修正预测线
        if ai_data and len(ai_data) == weeks + 1:
            ax.plot(x_data, ai_data, '-', color='#67C23A', linewidth=3,
                   marker='s', markersize=5, label='AI 修正预测')
        
        # 设置图表样式
        ax.set_xlabel('时间', fontsize=12)
        ax.set_ylabel('体重 (kg)', fontsize=12)
        ax.set_title('体重变化预测曲线', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xticks(x_data)
        ax.set_xticklabels(x_labels, rotation=0)
        
        # 设置Y轴范围，让图表更美观
        if linear_data or ai_data:
            all_values = []
            if linear_data:
                all_values.extend(linear_data)
            if ai_data:
                all_values.extend(ai_data)
            if all_values:
                min_val = min(all_values)
                max_val = max(all_values)
                margin = (max_val - min_val) * 0.1
                ax.set_ylim([min_val - margin, max_val + margin])
        
        plt.tight_layout()
        
        # 保存到字节流
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    except Exception as e:
        print(f"Chart generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

class HealthReportPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')  # A4 portrait
        # Set page margins (left, top, right)
        self.set_margins(15, 20, 15)
        # Set auto page break
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        # Add font
        font_path = get_chinese_font_path()
        self.has_chinese_font = False
        
        try:
            if font_path:
                # Check if font already added (check lowercase key)
                if 'chinese' not in self.fonts and 'Chinese' not in self.fonts:
                    self.add_font('Chinese', fname=font_path)
                self.set_font('Chinese', '', 16)
                self.has_chinese_font = True
            else:
                raise Exception("No Chinese font found")
        except Exception as e:
            print(f"Header Font Error: {e}")
            self.set_font('Helvetica', 'B', 16)
            self.has_chinese_font = False
            
        try:
            # Use explicit width instead of 0 to avoid width issues
            page_width = self.w - 2 * self.l_margin
            if self.has_chinese_font:
                self.cell(page_width, 10, '学生健康与运动监测报告', 0, 1, 'C')
            else:
                self.cell(page_width, 10, 'Health and Exercise Monitor Report', 0, 1, 'C')
        except Exception as e:
             print(f"Header Cell Error: {e}")
             self.set_font('Helvetica', 'B', 16)
             page_width = self.w - 2 * self.l_margin
             self.cell(page_width, 10, 'Health Report', 0, 1, 'C')
             
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        try:
            if getattr(self, 'has_chinese_font', False):
                self.set_font('Chinese', '', 8)
            else:
                self.set_font('Helvetica', 'I', 8)
        except:
            self.set_font('Helvetica', 'I', 8)
        page_width = self.w - 2 * self.l_margin
        self.cell(page_width, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_fpdf(user, profile, logs, simulation_data=None):
    pdf = HealthReportPDF()
    pdf.add_page()
    
    # Calculate page width (usable width in mm)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin  # A4 width: 210mm, margins: 15mm each side = 180mm
    
    # Font setup
    font_path = get_chinese_font_path()
    has_chinese = False

    try:
        if font_path:
            if 'chinese' not in pdf.fonts and 'Chinese' not in pdf.fonts:
                pdf.add_font('Chinese', fname=font_path)
            pdf.set_font('Chinese', '', 11)
            has_chinese = True
        else:
            raise Exception("No Chinese font found")
    except Exception as e:
        print(f"Font setup error: {e}")
        pdf.set_font('Helvetica', '', 11)
        has_chinese = False
        
    # Helper to safely get attribute
    def get_attr(obj, attr, default='未知'):
        if obj is None:
            return default
        val = getattr(obj, attr, None)
        return val if val is not None else default
    
    # Helper to format weight (handle None)
    def format_weight(weight):
        if weight is None:
            return '未记录'
        return f'{weight} kg'
    
    # Helper function to add a table row
    def add_table_row(label, value, col_width=60):
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        # Label column
        if has_chinese:
            pdf.set_font('Chinese', '', 11)
        else:
            pdf.set_font('Helvetica', 'B', 10)
        
        # Clean text to avoid unsupported characters if using Helvetica
        label_str = str(label)
        if not has_chinese:
            label_str = label_str.encode('ascii', 'replace').decode('ascii')
            
        pdf.cell(col_width, 7, label_str, 0, 0, 'L')
        
        # Value column
        if has_chinese:
            pdf.set_font('Chinese', '', 10)
        else:
            pdf.set_font('Helvetica', '', 10)
            
        value_str = str(value)
        if not has_chinese:
            value_str = value_str.encode('ascii', 'replace').decode('ascii')
            
        remaining_width = page_width - col_width
        
        # Check if value fits in remaining width
        text_width = pdf.get_string_width(value_str)
        if text_width > remaining_width - 5:
            # Use multi_cell if text is too long
            pdf.set_x(x_start + col_width)
            pdf.multi_cell(remaining_width, 7, value_str, 0, 'L')
            # Reset x position for next row
            pdf.set_x(x_start)
        else:
            pdf.cell(remaining_width, 7, value_str, 0, 1, 'L')

    # 1. Basic Info Section
    if has_chinese:
        pdf.set_font('Chinese', '', 14)
        title_1 = '一、基本信息'
    else:
        pdf.set_font('Helvetica', 'B', 13)
        title_1 = 'I. Basic Information'
    pdf.cell(page_width, 10, title_1, 0, 1, 'L')
    
    if has_chinese:
        pdf.set_font('Chinese', '', 10)
    else:
        pdf.set_font('Helvetica', '', 10)
    pdf.ln(2)
    
    name = user.real_name or user.username
    gender_val = get_attr(profile, 'gender', None)
    if has_chinese:
        gender = "男" if gender_val == "male" else ("女" if gender_val == "female" else "未知")
        labels = ['姓名', '性别', '年龄', '身高', '体重', 'BMI']
        age_unit = '岁'
    else:
        gender = "Male" if gender_val == "male" else ("Female" if gender_val == "female" else "Unknown")
        labels = ['Name', 'Gender', 'Age', 'Height', 'Weight', 'BMI']
        age_unit = 'years'
    
    add_table_row(labels[0], name)
    add_table_row(labels[1], gender)
    add_table_row(labels[2], f'{get_attr(profile, "age")} {age_unit}')
    add_table_row(labels[3], f'{get_attr(profile, "height_cm")} cm')
    add_table_row(labels[4], f'{get_attr(profile, "weight_kg")} kg')
    add_table_row(labels[5], get_attr(profile, "bmi"))
    
    pdf.ln(5)

    # 2. Body Indicators Section
    if has_chinese:
        pdf.set_font('Chinese', '', 14)
        title_2 = '二、身体指标分析'
    else:
        pdf.set_font('Helvetica', 'B', 13)
        title_2 = 'II. Body Indicators Analysis'
    pdf.cell(page_width, 10, title_2, 0, 1, 'L')
    
    if has_chinese:
        pdf.set_font('Chinese', '', 10)
    else:
        pdf.set_font('Helvetica', '', 10)
    pdf.ln(2)
    
    body_fat_cat = get_attr(profile, "body_fat_category", "")
    if has_chinese:
        body_fat_text = f'{get_attr(profile, "body_fat_percent")}%'
        if body_fat_cat and body_fat_cat != "未知":
            body_fat_text += f' ({body_fat_cat})'
        labels_2 = ['体脂率', '基础代谢率 (BMR)', '腰臀比 (WHR)', '体型评价']
    else:
        body_fat_text = f'{get_attr(profile, "body_fat_percent")}%'
        if body_fat_cat and body_fat_cat != "Unknown":
            body_fat_text += f' ({body_fat_cat})'
        labels_2 = ['Body Fat', 'BMR', 'WHR', 'Physique']
    
    add_table_row(labels_2[0], body_fat_text)
    add_table_row(labels_2[1], f'{get_attr(profile, "bmr")} kcal')
    add_table_row(labels_2[2], get_attr(profile, "whr"))
    add_table_row(labels_2[3], get_attr(profile, "weight_category"))
    
    pdf.ln(5)

    # 3. Simulation Section (Optional)
    if simulation_data:
        if has_chinese:
            pdf.set_font('Chinese', '', 14)
            title_sim = '三、干预方案模拟'
        else:
            pdf.set_font('Helvetica', 'B', 13)
            title_sim = 'III. Intervention Simulation'
        pdf.cell(page_width, 10, title_sim, 0, 1, 'L')
        pdf.ln(2)

        diet = simulation_data.get('dietPlan', {}) or simulation_data.get('diet_plan', {})
        exercise = simulation_data.get('exercisePlan', {}) or simulation_data.get('exercise_plan', {})
        result = simulation_data.get('simulationResult', {}) or simulation_data.get('simulation_result', {})
        
        # 调试输出
        print(f"[PDF Debug] diet: {diet}")
        print(f"[PDF Debug] exercise: {exercise}")
        print(f"[PDF Debug] result: {result}")
        print(f"[PDF Debug] suggestions: {result.get('suggestions', [])}")

        if has_chinese:
            pdf.set_font('Chinese', '', 11)
            pdf.cell(page_width, 8, '1. 干预方案参数', 0, 1, 'L')
            pdf.set_font('Chinese', '', 10)
        else:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(page_width, 8, '1. Parameters', 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)

        # 兼容不同的字段名格式
        carb = diet.get('carb') or diet.get('carbohydrate', 50)
        protein = diet.get('protein', 20)
        fat = diet.get('fat', 30)
        calories = diet.get('calories') or diet.get('calorie', 2000)
        aerobic_freq = exercise.get('aerobicFreq') or exercise.get('aerobic_freq') or exercise.get('aerobicFreq', 3)
        aerobic_duration = exercise.get('aerobicDuration') or exercise.get('aerobic_duration') or exercise.get('aerobicDuration', 30)
        steps = exercise.get('steps') or exercise.get('daily_steps', 6000)
        
        params_text = f"膳食: 碳水{carb}% / 蛋白{protein}% / 脂肪{fat}% | 总热量: {calories} kcal\n"
        params_text += f"运动: 有氧 {aerobic_freq}次/周 ({aerobic_duration}min) | 日常步数: {steps}步"
        
        if not has_chinese:
            params_text = params_text.encode('ascii', 'replace').decode('ascii')
        pdf.multi_cell(page_width, 6, params_text, 1, 'L')
        pdf.ln(4)

        if has_chinese:
            pdf.set_font('Chinese', '', 11)
            pdf.cell(page_width, 8, '2. AI 预测结果', 0, 1, 'L')
            pdf.set_font('Chinese', '', 10)
        else:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(page_width, 8, '2. AI Prediction', 0, 1, 'L')
            pdf.set_font('Helvetica', '', 10)

        # 兼容不同的字段名格式
        weight_change = result.get('weight') or result.get('weight_change', '0 kg')
        fat_change = result.get('fat') or result.get('fat_change', '0%')
        res_text = f"预计体重变化: {weight_change} | 预计体脂变化: {fat_change}"
        if not has_chinese:
            res_text = res_text.encode('ascii', 'replace').decode('ascii')
        pdf.cell(page_width, 8, res_text, 0, 1, 'L')
        pdf.ln(2)

        # 生成并插入曲线预览图表
        linear_data = simulation_data.get('linearData', []) or simulation_data.get('linear_data', [])
        ai_data = simulation_data.get('aiData', []) or simulation_data.get('ai_data', [])
        weeks = simulation_data.get('weeks', 4)
        current_weight = get_attr(profile, 'weight_kg', 60)
        
        # 调试输出
        print(f"[PDF Debug] linear_data: {linear_data[:3] if linear_data else None}... (length: {len(linear_data) if linear_data else 0})")
        print(f"[PDF Debug] ai_data: {ai_data[:3] if ai_data else None}... (length: {len(ai_data) if ai_data else 0})")
        print(f"[PDF Debug] weeks: {weeks}")
        
        if linear_data or ai_data:
            chart_image = generate_chart_image(linear_data, ai_data, weeks, current_weight)
            if chart_image:
                try:
                    # 保存图表到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_chart:
                        tmp_chart.write(chart_image)
                        tmp_chart_path = tmp_chart.name
                    
                    # 插入图表到PDF（宽度占满页面，高度自适应）
                    chart_width = page_width
                    chart_height = chart_width * 0.6  # 保持比例
                    
                    # 检查是否需要新页面
                    if pdf.get_y() + chart_height > pdf.h - 30:
                        pdf.add_page()
                    
                    # 添加图表标题
                    pdf.ln(2)
                    if has_chinese:
                        pdf.set_font('Chinese', '', 10)
                        pdf.cell(page_width, 6, '体重变化预测曲线', 0, 1, 'L')
                    else:
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(page_width, 6, 'Weight Prediction Chart', 0, 1, 'L')
                    pdf.ln(2)
                    
                    pdf.image(tmp_chart_path, x=pdf.l_margin, y=pdf.get_y(), w=chart_width, h=chart_height)
                    pdf.ln(chart_height + 3)
                    
                    # 清理临时文件
                    try:
                        os.remove(tmp_chart_path)
                    except:
                        pass
                    print("[PDF Debug] Chart inserted successfully")
                except Exception as e:
                    print(f"Failed to insert chart: {e}")
                    import traceback
                    traceback.print_exc()
                    pdf.ln(2)
            else:
                print("[PDF Debug] Chart image generation returned None")
        else:
            print(f"[PDF Debug] No chart data: linear_data={bool(linear_data)}, ai_data={bool(ai_data)}")

        if result.get('suggestions'):
            # 添加标题
            pdf.ln(3)
            if has_chinese:
                # 尝试使用加粗，如果失败则使用普通字体但增大字号
                try:
                    pdf.set_font('Chinese', 'B', 11)
                except:
                    # 如果加粗字体不存在，使用普通字体但稍微增大字号
                    pdf.set_font('Chinese', '', 12)
                pdf.cell(page_width, 8, '3. AI 专家建议', 0, 1, 'L')
                pdf.set_font('Chinese', '', 9)
            else:
                pdf.set_font('Helvetica', 'B', 11)
                pdf.cell(page_width, 8, '3. AI Suggestions', 0, 1, 'L')
                pdf.set_font('Helvetica', '', 9)
            
            pdf.ln(2)
            
            # 添加建议列表，确保文本正确换行
            suggestions = result.get('suggestions', [])
            for idx, sugg in enumerate(suggestions):
                if not sugg or not str(sugg).strip():
                    continue
                    
                # 处理建议文本
                sugg_text = str(sugg).strip()
                
                # 如果文本太长，需要分段处理
                # 计算文本宽度（考虑中文字符）
                if has_chinese:
                    # 中文字符宽度大约是英文字符的2倍
                    max_chars_per_line = int(page_width / 3)  # 估算每行字符数
                else:
                    max_chars_per_line = int(page_width / 2)
                
                # 如果文本超过一行，使用multi_cell
                if len(sugg_text) > max_chars_per_line:
                    # 添加项目符号
                    bullet = "• " if has_chinese else "- "
                    full_text = bullet + sugg_text
                    if not has_chinese:
                        full_text = full_text.encode('ascii', 'replace').decode('ascii')
                    
                    # 使用multi_cell自动换行，行高6mm，左对齐
                    pdf.multi_cell(page_width, 6, full_text, 0, 'L')
                    pdf.ln(1)  # 建议之间的间距
                else:
                    # 文本较短，使用单行
                    bullet = "• " if has_chinese else "- "
                    full_text = bullet + sugg_text
                    if not has_chinese:
                        full_text = full_text.encode('ascii', 'replace').decode('ascii')
                    
                    pdf.cell(page_width, 6, full_text, 0, 1, 'L')
        
        pdf.ln(5)

    # 4. Recent Logs Section
    section_num = '四' if simulation_data else '三'
    section_title = '近期日志记录 (最近30天)'
    no_records = '暂无近期记录'
    if not has_chinese:
        section_num = 'IV' if simulation_data else 'III'
        section_title = 'Recent Logs (Last 30 Days)'
        no_records = 'No recent records'
        
    if has_chinese:
        pdf.set_font('Chinese', '', 14)
    else:
        pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(page_width, 10, f'{section_num}、{section_title}', 0, 1, 'L')
    
    if has_chinese:
        pdf.set_font('Chinese', '', 10)
    else:
        pdf.set_font('Helvetica', '', 10)
    pdf.ln(2)
    
    if logs:
        for idx, log in enumerate(logs):
            # Check if we need a new page
            if pdf.get_y() > pdf.h - 40:  # Leave space for footer
                pdf.add_page()
            
            # Date header with background
            pdf.set_fill_color(230, 230, 230)
            if has_chinese:
                pdf.set_font('Chinese', '', 11)
                date_label = f'日期: {log.log_date}'
            else:
                pdf.set_font('Helvetica', 'B', 10)
                date_label = f'Date: {log.log_date}'
            pdf.cell(page_width, 8, date_label, 1, 1, 'L', fill=True)
            
            if has_chinese:
                pdf.set_font('Chinese', '', 9)
            else:
                pdf.set_font('Helvetica', '', 9)
            
            # Log details in a compact format
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            # Use two columns for better space utilization
            col_width = (page_width - 5) / 2
            
            # Left column
            pdf.set_x(x_start)
            if has_chinese:
                intake_text = f'摄入: {log.calorie_intake} kcal'
                expend_text = f'消耗: {log.calorie_expenditure} kcal'
                weight_text = f'体重: {format_weight(log.daily_weight)}'
                ai_label = 'AI建议:'
            else:
                intake_text = f'Intake: {log.calorie_intake} kcal'
                expend_text = f'Expenditure: {log.calorie_expenditure} kcal'
                weight_text = f'Weight: {format_weight(log.daily_weight)}'
                ai_label = 'AI Suggestions:'

            pdf.cell(col_width, 6, intake_text, 0, 0, 'L')
            
            # Right column
            pdf.set_x(x_start + col_width + 5)
            pdf.cell(col_width, 6, expend_text, 0, 1, 'L')
            
            # Weight on next line
            pdf.set_x(x_start)
            pdf.cell(page_width, 6, weight_text, 0, 1, 'L')
            
            # AI suggestions
            if log.ai_suggestions:
                try:
                    suggestions = json.loads(log.ai_suggestions) if isinstance(log.ai_suggestions, str) else log.ai_suggestions
                    if isinstance(suggestions, list) and suggestions:
                        pdf.set_x(x_start + 5)
                        if has_chinese:
                            pdf.set_font('Chinese', '', 8)
                        else:
                            pdf.set_font('Helvetica', '', 8)
                        pdf.cell(page_width - 10, 5, ai_label, 0, 1, 'L')
                        for suggestion in suggestions:
                            suggestion_text = str(suggestion).strip() if suggestion else ''
                            if suggestion_text:
                                pdf.set_x(x_start + 10)
                                bullet = '• ' if has_chinese else '- '
                                full_text = f'{bullet}{suggestion_text}'
                                if not has_chinese:
                                    full_text = full_text.encode('ascii', 'replace').decode('ascii')
                                    
                                text_width = pdf.get_string_width(full_text)
                                if text_width > page_width - 15:
                                    pdf.multi_cell(page_width - 15, 5, full_text, 0, 'L')
                                else:
                                    pdf.cell(page_width - 15, 5, full_text, 0, 1, 'L')
                    elif suggestions:
                        suggestion_text = str(suggestions).strip()
                        if suggestion_text:
                            pdf.set_x(x_start + 5)
                            if has_chinese:
                                pdf.set_font('Chinese', '', 8)
                                full_text = f'AI建议: {suggestion_text}'
                            else:
                                pdf.set_font('Helvetica', '', 8)
                                full_text = f'AI Suggestions: {suggestion_text}'
                                full_text = full_text.encode('ascii', 'replace').decode('ascii')
                                
                            text_width = pdf.get_string_width(full_text)
                            if text_width > page_width - 10:
                                pdf.multi_cell(page_width - 10, 5, full_text, 0, 'L')
                            else:
                                pdf.cell(page_width - 10, 5, full_text, 0, 1, 'L')
                except (json.JSONDecodeError, TypeError, AttributeError):
                    suggestion_text = str(log.ai_suggestions).strip()
                    if suggestion_text:
                        pdf.set_x(x_start + 5)
                        if has_chinese:
                            pdf.set_font('Chinese', '', 8)
                            full_text = f'AI建议: {suggestion_text}'
                        else:
                            pdf.set_font('Helvetica', '', 8)
                            full_text = f'AI Suggestions: {suggestion_text}'
                            full_text = full_text.encode('ascii', 'replace').decode('ascii')
                            
                        text_width = pdf.get_string_width(full_text)
                        if text_width > page_width - 10:
                            pdf.multi_cell(page_width - 10, 5, full_text, 0, 'L')
                        else:
                            pdf.cell(page_width - 10, 5, full_text, 0, 1, 'L')
            
            if has_chinese:
                pdf.set_font('Chinese', '', 9)
            else:
                pdf.set_font('Helvetica', '', 9)
            pdf.ln(3)  # Spacing between log entries
    else:
        pdf.cell(page_width, 8, no_records, 0, 1, 'L')
        
    # Footer with generation time
    pdf.ln(5)
    if has_chinese:
        pdf.set_font('Chinese', '', 9)
        generated_text = f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    else:
        pdf.set_font('Helvetica', '', 9)
        generated_text = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    pdf.cell(page_width, 8, generated_text, 0, 1, 'R')
    
    # Return PDF as bytes
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Write PDF to temporary file
        pdf.output(tmp_path, dest='F')
        
        # Read the file as bytes
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        
        return pdf_bytes
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except:
            pass

@report_bp.route('/intervention/export', methods=['POST'])
@jwt_required()
def export_intervention_report():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '缺少模拟数据'}), 400

        # 1. 读取用户已提交的健康报告
        report = Report.query.filter_by(user_id=user.id).first()
        
        if not report or not report.pdf_content:
            # 如果没有报告，使用当前数据生成
            profile = UserProfile.query.filter_by(user_id=user.id).first()
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            logs = DailyLog.query.filter(
                DailyLog.user_id == user.id,
                DailyLog.log_date >= thirty_days_ago
            ).order_by(DailyLog.log_date.desc()).all()
            
            # 生成新的PDF，包含干预数据
            pdf_bytes = generate_pdf_fpdf(user, profile, logs, simulation_data=data)
        else:
            # 如果有已提交的报告，基于报告数据生成新PDF
            # 从报告中提取用户和档案信息（报告PDF中已包含这些信息）
            profile = UserProfile.query.filter_by(user_id=user.id).first()
            
            # 获取日志数据（用于报告中的日志部分）
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            logs = DailyLog.query.filter(
                DailyLog.user_id == user.id,
                DailyLog.log_date >= thirty_days_ago
            ).order_by(DailyLog.log_date.desc()).all()
            
            # 生成包含干预数据的PDF（这会复用报告中的基本信息）
            pdf_bytes = generate_pdf_fpdf(user, profile, logs, simulation_data=data)
        
        # 3. Return PDF
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=intervention_report.pdf'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Intervention Export Error: {e}")
        return jsonify({'code': 500, 'message': f'导出失败: {str(e)}'}), 500

@report_bp.route('/preview', methods=['GET'])
@jwt_required()
def preview_report():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
            
        # 1. Fetch Data
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        
        # Get logs for the last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        logs = DailyLog.query.filter(
            DailyLog.user_id == user.id,
            DailyLog.log_date >= thirty_days_ago
        ).order_by(DailyLog.log_date.desc()).all()
        
        # 2. Generate PDF
        pdf_bytes = generate_pdf_fpdf(user, profile, logs)
        
        # 3. Return PDF
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=report_preview.pdf'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Preview Error: {e}")
        return jsonify({'code': 500, 'message': f'预览失败: {str(e)}'}), 500

@report_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_report():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
            
        # 1. Fetch Data
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        
        # Get logs for the last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        logs = DailyLog.query.filter(
            DailyLog.user_id == user.id,
            DailyLog.log_date >= thirty_days_ago
        ).order_by(DailyLog.log_date.desc()).all()
        
        # 2. 准备报告数据用于哈希计算（排除时间戳等动态内容）
        # 构建报告数据的字符串表示用于哈希计算
        # 辅助函数：统一处理None值
        def safe_str(val):
            """将值转换为字符串，None统一处理为空字符串"""
            if val is None:
                return ""
            if isinstance(val, float):
                # 浮点数统一格式，避免精度问题（包括0.0）
                return f"{val:.2f}"
            if isinstance(val, int):
                return str(val)
            return str(val) if val else ""
        
        report_data_str = f"{user.id}|{safe_str(user.real_name or user.username)}|"
        
        # 添加profile数据（包含所有影响报告内容的字段）
        if profile:
            report_data_str += f"{safe_str(profile.age)}|{safe_str(profile.height_cm)}|{safe_str(profile.weight_kg)}|{safe_str(profile.gender)}|"
            report_data_str += f"{safe_str(profile.waist_cm)}|{safe_str(profile.hip_cm)}|"
            report_data_str += f"{safe_str(profile.body_fat_percent)}|{safe_str(profile.bmr)}|{safe_str(profile.whr)}|"
            report_data_str += f"{safe_str(profile.weight_category)}|{safe_str(profile.body_fat_category)}|"
            report_data_str += f"{safe_str(profile.bmi)}|"
        else:
            report_data_str += "|||||||||||"  # 11个空字段
        
        # 添加日志数据（只包含数据内容，确保排序稳定）
        # 按日期排序，确保顺序一致
        sorted_logs = sorted(logs, key=lambda x: (x.log_date, x.id))
        
        for log in sorted_logs:
            log_data_str = f"{log.log_date}|{safe_str(log.calorie_intake)}|{safe_str(log.calorie_expenditure)}|{safe_str(log.daily_weight)}|"
            log_data_str += f"{safe_str(log.carb_percent)}|{safe_str(log.protein_percent)}|{safe_str(log.fat_percent)}|"
            log_data_str += f"{safe_str(log.fiber_grams)}|{safe_str(log.alcohol_grams)}|"
            if log.ai_suggestions:
                # AI建议也需要包含，因为它影响报告内容
                ai_str = str(log.ai_suggestions) if not isinstance(log.ai_suggestions, str) else log.ai_suggestions
                log_data_str += f"{ai_str}|"
            else:
                log_data_str += "|"
            report_data_str += log_data_str
        
        # 计算报告数据的哈希值
        new_data_hash = hashlib.md5(report_data_str.encode('utf-8')).hexdigest()
        
        # 调试：打印哈希计算使用的数据（前200个字符）
        current_app.logger.info(f"New report data hash (first 200 chars): {report_data_str[:200]}...")
        current_app.logger.info(f"New hash: {new_data_hash}")
        
        # 3. Save to DB - 更新或创建报告（每个用户只有一个报告）
        report = Report.query.filter_by(user_id=user.id).first()
        is_new = report is None
        
        if is_new:
            # 生成PDF
            pdf_bytes = generate_pdf_fpdf(user, profile, logs)
            
            # 创建新报告，保存数据哈希
            report = Report(
                user_id=user.id,
                title=f"{user.real_name or user.username} - 健康报告 - {datetime.now().strftime('%Y-%m-%d')}",
                file_path='',
                pdf_content=pdf_bytes,
                data_hash=new_data_hash,  # 保存数据哈希
                status='submitted'
            )
            db.session.add(report)
            db.session.flush()  # 获取report.id
            
            # 记录创建日志
            history = ReportHistory(
                report_id=report.id,
                modified_by_id=user.id,
                action='created',
                description='用户提交了报告'
            )
            db.session.add(history)
            
            try:
                db.session.commit()
            except Exception as db_error:
                db.session.rollback()
                raise db_error
            
            return jsonify({
                'code': 200, 
                'message': '报告提交成功',
                'data': report.to_dict()
            })
        else:
            # 检查报告数据是否有变化（比较保存的数据哈希）
            old_data_hash = report.data_hash
            
            # 调试：打印比较信息
            current_app.logger.info(f"Old hash from DB: {old_data_hash}")
            current_app.logger.info(f"New hash calculated: {new_data_hash}")
            current_app.logger.info(f"Hash comparison: {old_data_hash == new_data_hash if old_data_hash else 'No old hash'}")
            
            if old_data_hash and old_data_hash == new_data_hash:
                # 报告数据没有变化，不更新报告
                current_app.logger.info("Report data unchanged, skipping update")
                return jsonify({
                    'code': 400,
                    'message': '当前报告已经是最新，请修改报告内容再提交',
                    'data': report.to_dict()
                }), 400
            
            # 调试：数据有变化
            current_app.logger.info("Report data changed, updating report")
            
            # 报告数据有变化，生成新PDF并更新报告
            pdf_bytes = generate_pdf_fpdf(user, profile, logs)
            
            report.title = f"{user.real_name or user.username} - 健康报告 - {datetime.now().strftime('%Y-%m-%d')}"
            report.pdf_content = pdf_bytes
            report.data_hash = new_data_hash  # 更新数据哈希
            report.status = 'submitted'
            report.updated_at = datetime.utcnow()
            
            # 记录更新日志
            history = ReportHistory(
                report_id=report.id,
                modified_by_id=user.id,
                action='updated',
                description='用户更新了报告'
            )
            db.session.add(history)
            
            try:
                db.session.commit()
            except Exception as db_error:
                db.session.rollback()
                raise db_error
            
            return jsonify({
                'code': 200, 
                'message': '报告更新成功',
                'data': report.to_dict()
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        current_app.logger.error(f"Submit Error: {e}")
        return jsonify({'code': 500, 'message': f'提交失败: {str(e)}'}), 500

@report_bp.route('/view/<int:report_id>', methods=['GET'])
@jwt_required()
def view_report(report_id):
    """查看报告PDF（管理员可查看所有，老师只能查看学生的，学生只能查看自己的）"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # Get report
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'code': 404, 'message': '报告不存在'}), 404
        
        # Get report owner
        report_owner = User.query.get(report.user_id)
        if not report_owner:
            return jsonify({'code': 404, 'message': '报告所有者不存在'}), 404
        
        # Check permissions
        if current_user.role.code == 'admin':
            # 管理员可以查看所有报告
            pass
        elif current_user.role.code == 'teacher':
            # 老师只能查看学生的报告
            if report_owner.role.code != 'student':
                return jsonify({'code': 403, 'message': '只能查看学生的报告'}), 403
        else:
            # 学生只能查看自己的报告
            if report.user_id != current_user.id:
                return jsonify({'code': 403, 'message': '无权查看此报告'}), 403
        
        # Check if PDF content exists
        if not report.pdf_content:
            return jsonify({'code': 404, 'message': '报告PDF内容不存在'}), 404
        
        # Return PDF
        response = make_response(report.pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=report_{report.id}.pdf'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"View Report Error: {e}")
        return jsonify({'code': 500, 'message': f'查看失败: {str(e)}'}), 500

@report_bp.route('/list', methods=['GET'])
@jwt_required()
def list_reports():
    """获取报告列表，支持权限控制（每个用户只有一个报告）"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    # 获取可选的user_id参数（用于查看特定用户的报告）
    target_user_id = request.args.get('user_id', type=int)
    include_history = request.args.get('include_history', 'false').lower() == 'true'
    
    # 权限控制
    if current_user.role.code == 'admin':
        # 管理员可以查看所有报告
        if target_user_id:
            report = Report.query.filter_by(user_id=target_user_id).first()
            reports = [report] if report else []
        else:
            reports = Report.query.order_by(Report.updated_at.desc()).all()
    elif current_user.role.code == 'teacher':
        # 老师只能查看学生的报告
        if target_user_id:
            # 检查目标用户是否是学生
            target_user = User.query.get(target_user_id)
            if not target_user:
                return jsonify({'code': 404, 'message': '用户不存在'}), 404
            if target_user.role.code != 'student':
                return jsonify({'code': 403, 'message': '只能查看学生的报告'}), 403
            report = Report.query.filter_by(user_id=target_user_id).first()
            reports = [report] if report else []
        else:
            # 获取所有学生的报告
            student_role = Role.query.filter_by(code='student').first()
            if student_role:
                student_ids = [u.id for u in User.query.filter_by(role_id=student_role.id).all()]
                reports = Report.query.filter(Report.user_id.in_(student_ids)).order_by(Report.updated_at.desc()).all()
            else:
                reports = []
    else:
        # 学生只能查看自己的报告
        if target_user_id and target_user_id != current_user.id:
            return jsonify({'code': 403, 'message': '无权查看其他用户的报告'}), 403
        report = Report.query.filter_by(user_id=current_user.id).first()
        reports = [report] if report else []
        
    return jsonify({
        'code': 200,
        'data': [r.to_dict(include_history=include_history) for r in reports]
    })

