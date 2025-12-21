from flask import Blueprint, request, current_app, jsonify
from app import db
from app.models.system import SystemSetting
from app.utils.decorators import admin_required
from app.utils.response import success_response, error_response
import os
import shutil
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/backup', methods=['POST'])
@admin_required
def create_backup():
    """创建系统备份 (仅限SQLite)"""
    # 检查是否是SQLite
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not db_uri.startswith('sqlite:///'):
        return error_response(message="当前仅支持SQLite数据库备份")
    
    db_path = db_uri.replace('sqlite:///', '')
    if not os.path.exists(db_path):
        # 尝试绝对路径或相对于instance文件夹
        db_path = os.path.join(current_app.instance_path, 'bs_system.db')
        if not os.path.exists(db_path):
             # 再次尝试直接在根目录
             db_path = 'bs_system.db'
             if not os.path.exists(db_path):
                return error_response(message="找不到数据库文件")

    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"bs_system_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        shutil.copy2(db_path, backup_path)
        return success_response(data={'filename': backup_filename, 'path': backup_path}, message="备份成功")
    except Exception as e:
        return error_response(message=f"备份失败: {str(e)}")

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
