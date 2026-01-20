from flask import Blueprint, request, current_app, jsonify, send_from_directory
from app import db
from app.models.system import SystemSetting
from app.utils.decorators import admin_required
from app.utils.response import success_response, error_response
from app.utils.errors import ValidationError
from werkzeug.utils import secure_filename
from PIL import Image
import os
import shutil
import uuid
import gzip
import subprocess
from datetime import datetime
from urllib.parse import urlparse

bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/backup', methods=['POST'])
@admin_required
def create_backup():
    """创建系统备份（支持 SQLite 和 MySQL）"""
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # SQLite 备份
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            # 尝试绝对路径或相对于instance文件夹
            db_path = os.path.join(current_app.instance_path, 'bs_system.db')
            if not os.path.exists(db_path):
                 # 再次尝试直接在根目录
                 db_path = 'bs_system.db'
                 if not os.path.exists(db_path):
                    return error_response(message="找不到SQLite数据库文件")

        backup_filename = f"bs_system_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(db_path, backup_path)
            return success_response(data={'filename': backup_filename, 'path': backup_path, 'type': 'sqlite'}, message="SQLite备份成功")
        except Exception as e:
            return error_response(message=f"备份失败: {str(e)}")
    
    # MySQL 备份
    elif db_uri.startswith('mysql'):
        # 从 URI 解析连接信息
        # mysql+pymysql://user:password@host:port/database
        parsed = urlparse(db_uri.replace('mysql+pymysql://', 'mysql://'))
        
        db_user = parsed.username or os.environ.get('DB_USER', 'bs_user')
        db_password = parsed.password or os.environ.get('DB_PASSWORD', 'password')
        db_host = parsed.hostname or os.environ.get('DB_HOST', 'localhost')
        db_port = parsed.port or int(os.environ.get('DB_PORT', 3306))
        db_name = parsed.path.lstrip('/').split('?')[0] or os.environ.get('DB_NAME', 'bs_system')
        
        backup_filename = f"bs_system_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            # 使用 mysqldump 命令备份
            cmd = [
                'mysqldump',
                f'--host={db_host}',
                f'--port={db_port}',
                f'--user={db_user}',
                f'--password={db_password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                db_name
            ]
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode != 0:
                return error_response(message=f"MySQL备份失败: {result.stderr}")
            
            # 压缩备份文件（可选）
            import gzip
            compressed_filename = f"{backup_filename}.gz"
            compressed_path = os.path.join(backup_dir, compressed_filename)
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(backup_path)  # 删除未压缩的文件
            
            return success_response(
                data={'filename': compressed_filename, 'path': compressed_path, 'type': 'mysql'}, 
                message="MySQL备份成功"
            )
        except FileNotFoundError:
            return error_response(message="未找到 mysqldump 命令，请确保 MySQL 客户端工具已安装")
        except Exception as e:
            return error_response(message=f"MySQL备份失败: {str(e)}")
    
    else:
        return error_response(message=f"不支持的数据库类型: {db_uri.split('://')[0]}")

@bp.route('/maintenance', methods=['GET'])
def get_maintenance_status():
    """获取维护模式状态"""
    setting = SystemSetting.query.filter_by(key='maintenance_mode').first()
    is_maintenance = setting.value == 'true' if setting else False
    return success_response(data={'maintenance': is_maintenance})

@bp.route('/maintenance', methods=['POST'])
@admin_required
def toggle_maintenance():
    """切换维护模式"""
    data = request.get_json()
    enable = data.get('enable', False)
    
    setting = SystemSetting.query.filter_by(key='maintenance_mode').first()
    if not setting:
        setting = SystemSetting(key='maintenance_mode', value='false', description='系统维护模式开关')
        db.session.add(setting)
    
    setting.value = 'true' if enable else 'false'
    db.session.commit()
    
    status_text = "开启" if enable else "关闭"
    return success_response(data={'maintenance': enable}, message=f"系统维护模式已{status_text}")

@bp.route('/system-logo', methods=['POST'])
@admin_required
def upload_system_logo():
    """上传系统图标（仅管理员）"""
    if 'file' not in request.files:
        raise ValidationError("没有文件部分")
    file = request.files['file']
    if file.filename == '':
        raise ValidationError("没有选择文件")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 生成唯一文件名
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
        unique_filename = f"system_logo_{uuid.uuid4().hex}.{file_ext}"
        
        upload_folder = os.path.join(current_app.root_path, 'app', 'static', 'system')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        filepath = os.path.join(upload_folder, unique_filename)
        
        try:
            # 处理图片
            image = Image.open(file)
            # 如果是RGBA模式（如PNG），转换为RGB
            if image.mode in ('RGBA', 'P'):
                # 对于PNG等透明图片，保持RGBA模式
                if file_ext.lower() in ['png', 'webp']:
                    # 调整大小，保持宽高比，最大尺寸 80x80
                    image.thumbnail((80, 80), Image.Resampling.LANCZOS)
                    image.save(filepath, 'PNG', optimize=True)
                else:
                    # 转换为RGB
                    image = image.convert('RGB')
                    image.thumbnail((80, 80), Image.Resampling.LANCZOS)
                    image.save(filepath, 'JPEG', quality=90)
            else:
                # 调整大小，保持宽高比，最大尺寸 80x80
                image.thumbnail((80, 80), Image.Resampling.LANCZOS)
                if file_ext.lower() in ['png', 'webp']:
                    image.save(filepath, 'PNG', optimize=True)
                else:
                    image.save(filepath, 'JPEG', quality=90)
            
            # 保存图标路径到系统设置
            setting = SystemSetting.query.filter_by(key='system_logo').first()
            if not setting:
                setting = SystemSetting(
                    key='system_logo',
                    value=unique_filename,
                    description='系统图标文件名'
                )
                db.session.add(setting)
            else:
                # 删除旧图标文件
                old_filename = setting.value
                if old_filename:
                    old_filepath = os.path.join(upload_folder, old_filename)
                    if os.path.exists(old_filepath):
                        try:
                            os.remove(old_filepath)
                        except Exception as e:
                            print(f"删除旧图标文件失败: {e}")
                
                setting.value = unique_filename
            
            db.session.commit()
            
            file_url = f"/api/admin/system-logo/{unique_filename}"
            return success_response(data={'url': file_url, 'filename': unique_filename}, message="系统图标上传成功")
        except Exception as e:
            raise ValidationError(f"图片处理失败: {str(e)}")
    else:
        raise ValidationError("不支持的文件类型，仅支持: png, jpg, jpeg, gif, svg, webp")

@bp.route('/system-logo', methods=['GET'])
def get_system_logo_url():
    """获取系统图标URL"""
    setting = SystemSetting.query.filter_by(key='system_logo').first()
    if setting and setting.value:
        logo_url = f"/api/admin/system-logo/{setting.value}"
        return success_response(data={'url': logo_url, 'filename': setting.value})
    else:
        return success_response(data={'url': None, 'filename': None})

@bp.route('/system-logo/<filename>', methods=['GET'])
def get_system_logo_image(filename):
    """获取系统图标图片"""
    upload_folder = os.path.join(current_app.root_path, 'app', 'static', 'system')
    return send_from_directory(upload_folder, filename)

@bp.route('/background-image', methods=['POST'])
@admin_required
def upload_background_image():
    """上传背景图片（仅管理员）"""
    # 调试信息
    if current_app.config.get('DEBUG'):
        print(f"[DEBUG] 收到背景图片上传请求")
        print(f"[DEBUG] request.method: {request.method}")
        print(f"[DEBUG] request.path: {request.path}")
        print(f"[DEBUG] request.url: {request.url}")
    
    if 'file' not in request.files:
        raise ValidationError("没有文件部分")
    file = request.files['file']
    if file.filename == '':
        raise ValidationError("没有选择文件")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 生成唯一文件名
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"background_{uuid.uuid4().hex}.{file_ext}"
        
        # 使用与 system-logo 相同的路径结构
        upload_folder = os.path.join(current_app.root_path, 'app', 'static', 'backgrounds')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            
        filepath = os.path.join(upload_folder, unique_filename)
        
        try:
            # 先删除旧文件（如果存在）- 在保存新文件之前删除，确保覆盖
            setting = SystemSetting.query.filter_by(key='background_image').first()
            if setting and setting.value:
                old_filename = setting.value
                # 删除主路径的文件
                old_filepath = os.path.join(upload_folder, old_filename)
                if os.path.exists(old_filepath) and os.path.isfile(old_filepath):
                    try:
                        os.remove(old_filepath)
                        if current_app.config.get('DEBUG'):
                            print(f"[DEBUG] 已删除旧背景图片: {old_filepath}")
                    except Exception as e:
                        print(f"删除旧背景图片文件失败: {e}")
                # 也尝试删除备用路径的文件
                alt_folder = os.path.join(current_app.root_path, 'static', 'backgrounds')
                alt_old_filepath = os.path.join(alt_folder, old_filename)
                if os.path.exists(alt_old_filepath) and os.path.isfile(alt_old_filepath):
                    try:
                        os.remove(alt_old_filepath)
                    except:
                        pass
            
            # 处理图片 - 背景图片不需要压缩，保持原图质量
            image = Image.open(file)
            # 如果是RGBA模式（如PNG），转换为RGB
            if image.mode in ('RGBA', 'P'):
                if file_ext.lower() in ['png', 'webp']:
                    image.save(filepath, 'PNG', optimize=True)
                else:
                    image = image.convert('RGB')
                    image.save(filepath, 'JPEG', quality=95)
            else:
                if file_ext.lower() in ['png', 'webp']:
                    image.save(filepath, 'PNG', optimize=True)
                else:
                    image.save(filepath, 'JPEG', quality=95)
            
            # 确保文件已保存 - 验证文件存在且可读
            import time
            max_retries = 5
            file_saved = False
            for i in range(max_retries):
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    # 检查文件大小，确保文件已完全写入
                    file_size = os.path.getsize(filepath)
                    if file_size > 0:
                        file_saved = True
                        break
                time.sleep(0.1)
            
            if not file_saved:
                raise Exception(f"文件保存失败，文件不存在或为空: {filepath}")
            
            # 保存背景图片路径到系统设置
            if not setting:
                setting = SystemSetting(
                    key='background_image',
                    value=unique_filename,
                    description='系统背景图片'
                )
                db.session.add(setting)
            else:
                setting.value = unique_filename
            
            db.session.commit()
            
            # 返回完整的URL路径
            file_url = f"/api/admin/background-image/{unique_filename}"
            if current_app.config.get('DEBUG'):
                print(f"[DEBUG] 背景图片上传成功: {file_url}")
                print(f"[DEBUG] 文件路径: {filepath}")
                print(f"[DEBUG] 文件大小: {os.path.getsize(filepath)} 字节")
            
            return success_response(data={'url': file_url, 'filename': unique_filename}, message="背景图片上传成功")
        except Exception as e:
            if current_app.config.get('DEBUG'):
                print(f"[DEBUG] 背景图片上传失败: {str(e)}")
            raise ValidationError(f"图片处理失败: {str(e)}")
    else:
        raise ValidationError("不支持的文件类型")

@bp.route('/background-image', methods=['GET'])
def get_background_image():
    """获取背景图片URL"""
    setting = SystemSetting.query.filter_by(key='background_image').first()
    if setting and setting.value:
        file_url = f"/api/admin/background-image/{setting.value}"
        return success_response(data={'url': file_url})
    return success_response(data={'url': None})

@bp.route('/background-image/<filename>', methods=['GET'])
def serve_background_image(filename):
    """提供背景图片文件"""
    # 使用与 system-logo 相同的路径结构
    upload_folder = os.path.join(current_app.root_path, 'app', 'static', 'backgrounds')
    filepath = os.path.join(upload_folder, filename)
    
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return send_from_directory(upload_folder, filename)
    else:
        # 尝试备用路径（如果 root_path 指向不同位置）
        alt_folder = os.path.join(current_app.root_path, 'static', 'backgrounds')
        alt_filepath = os.path.join(alt_folder, filename)
        if os.path.exists(alt_filepath) and os.path.isfile(alt_filepath):
            return send_from_directory(alt_folder, filename)
        
        # 调试信息
        if current_app.config.get('DEBUG'):
            print(f"[DEBUG] 背景图片路径检查:")
            print(f"  主路径: {filepath} (存在: {os.path.exists(filepath)})")
            print(f"  备用路径: {alt_filepath} (存在: {os.path.exists(alt_filepath)})")
            print(f"  root_path: {current_app.root_path}")
        
        # 返回 404，但不显示错误消息（前端会处理）
        from flask import abort
        abort(404)
