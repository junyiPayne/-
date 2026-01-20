"""用户个性化设置路由"""
from flask import Blueprint, request, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.user_settings import UserSettings
from app.models.user import User
from app.utils.decorators import login_required
from app.utils.response import success_response
from app.utils.errors import ValidationError
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid

bp = Blueprint('settings', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('', methods=['GET'])
@login_required
def get_settings():
    """获取当前用户的个性化设置"""
    user_id = get_jwt_identity()
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    
    if settings:
        return success_response(data=settings.to_dict())
    else:
        # 返回默认设置
        default_settings = {
            'fontSize': 14,
            'fontFamily': 'Arial, sans-serif',
            'fontColor': '#303133',
            'customFontName': None,
            'customFontUrl': None,
            'headerColor': '#304156',
            'headerUseGradient': False,
            'headerGradientType': 'linear',
            'headerGradientColor1': '#304156',
            'headerGradientColor2': '#409EFF',
            'headerGradientDirection': 'to right',
            'sidebarColor': '#fff',
            'sidebarUseGradient': False,
            'sidebarGradientType': 'linear',
            'sidebarGradientColor1': '#fff',
            'sidebarGradientColor2': '#f0f2f5',
            'sidebarGradientDirection': 'to bottom',
            'contentBackgroundColor': '#f0f2f5',
            'backgroundImageUrl': None,
            'backgroundImageOpacity': 1.0,
            'logoSize': 40
        }
        return success_response(data=default_settings)

@bp.route('', methods=['POST'])
@login_required
def save_settings():
    """保存当前用户的个性化设置"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
    
    # 更新设置
    if 'fontSize' in data:
        settings.fontSize = data['fontSize']
    if 'fontFamily' in data:
        settings.fontFamily = data['fontFamily']
    if 'fontColor' in data:
        settings.fontColor = data['fontColor']
    if 'customFontName' in data:
        settings.customFontName = data['customFontName']
    if 'customFontUrl' in data:
        settings.customFontUrl = data['customFontUrl']
    if 'headerColor' in data:
        settings.headerColor = data['headerColor']
    if 'headerUseGradient' in data:
        settings.headerUseGradient = data['headerUseGradient']
    if 'headerGradientType' in data:
        settings.headerGradientType = data['headerGradientType']
    if 'headerGradientColor1' in data:
        settings.headerGradientColor1 = data['headerGradientColor1']
    if 'headerGradientColor2' in data:
        settings.headerGradientColor2 = data['headerGradientColor2']
    if 'headerGradientDirection' in data:
        settings.headerGradientDirection = data['headerGradientDirection']
    if 'sidebarColor' in data:
        settings.sidebarColor = data['sidebarColor']
    if 'sidebarUseGradient' in data:
        settings.sidebarUseGradient = data['sidebarUseGradient']
    if 'sidebarGradientType' in data:
        settings.sidebarGradientType = data['sidebarGradientType']
    if 'sidebarGradientColor1' in data:
        settings.sidebarGradientColor1 = data['sidebarGradientColor1']
    if 'sidebarGradientColor2' in data:
        settings.sidebarGradientColor2 = data['sidebarGradientColor2']
    if 'sidebarGradientDirection' in data:
        settings.sidebarGradientDirection = data['sidebarGradientDirection']
    if 'contentBackgroundColor' in data:
        settings.contentBackgroundColor = data['contentBackgroundColor']
    if 'backgroundImageUrl' in data:
        settings.backgroundImageUrl = data['backgroundImageUrl']
    if 'backgroundImageOpacity' in data:
        settings.backgroundImageOpacity = data['backgroundImageOpacity']
    if 'logoSize' in data:
        settings.logoSize = data['logoSize']
    
    db.session.commit()
    
    return success_response(data=settings.to_dict(), message="设置已保存")

@bp.route('/background-image', methods=['POST'])
@login_required
def upload_background_image():
    """上传背景图片（用户级别）"""
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        raise ValidationError("没有文件部分")
    file = request.files['file']
    if file.filename == '':
        raise ValidationError("没有选择文件")
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 生成唯一文件名（包含用户ID，避免冲突）
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        unique_filename = f"background_{user_id}_{uuid.uuid4().hex}.{file_ext}"
        
        # 使用用户ID创建子目录
        upload_folder = os.path.join(current_app.root_path, 'app', 'static', 'backgrounds', str(user_id))
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            
        filepath = os.path.join(upload_folder, unique_filename)
        
        try:
            # 先删除旧文件（如果存在）
            settings = UserSettings.query.filter_by(user_id=user_id).first()
            if settings and settings.backgroundImageUrl:
                # 从URL中提取文件名
                old_url = settings.backgroundImageUrl
                if '/background-image/' in old_url:
                    old_filename = old_url.split('/background-image/')[-1]
                    old_filepath = os.path.join(upload_folder, old_filename)
                    if os.path.exists(old_filepath) and os.path.isfile(old_filepath):
                        try:
                            os.remove(old_filepath)
                        except Exception as e:
                            print(f"删除旧背景图片文件失败: {e}")
            
            # 处理图片
            image = Image.open(file)
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
            
            # 确保文件已保存
            import time
            max_retries = 5
            file_saved = False
            for i in range(max_retries):
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    if file_size > 0:
                        file_saved = True
                        break
                time.sleep(0.1)
            
            if not file_saved:
                raise Exception(f"文件保存失败，文件不存在或为空: {filepath}")
            
            # 保存背景图片路径到用户设置
            if not settings:
                settings = UserSettings(user_id=user_id)
                db.session.add(settings)
            
            file_url = f"/api/settings/background-image/{user_id}/{unique_filename}"
            settings.backgroundImageUrl = file_url
            db.session.commit()
            
            return success_response(data={'url': file_url, 'filename': unique_filename}, message="背景图片上传成功")
        except Exception as e:
            if current_app.config.get('DEBUG'):
                print(f"[DEBUG] 背景图片上传失败: {str(e)}")
            raise ValidationError(f"图片处理失败: {str(e)}")
    else:
        raise ValidationError("不支持的文件类型")

@bp.route('/background-image/<int:user_id>/<filename>', methods=['GET'])
@login_required
def serve_background_image(user_id, filename):
    """提供背景图片文件（仅当前用户可以访问自己的图片）"""
    current_user_id = get_jwt_identity()
    
    # 只能访问自己的图片
    if current_user_id != user_id:
        from flask import abort
        abort(403)
    
    upload_folder = os.path.join(current_app.root_path, 'app', 'static', 'backgrounds', str(user_id))
    filepath = os.path.join(upload_folder, filename)
    
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return send_from_directory(upload_folder, filename)
    else:
        from flask import abort
        abort(404)
