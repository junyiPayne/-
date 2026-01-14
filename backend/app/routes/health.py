"""健康检查路由"""
from flask import Blueprint, jsonify
from app import db
from datetime import datetime
from sqlalchemy import text
import os

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        # 记录详细错误信息（用于调试）
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"数据库健康检查失败: {str(e)}", exc_info=True)
    
    # 检查磁盘空间（可选）
    try:
        import shutil
        disk_usage = shutil.disk_usage('/')
        disk_free_gb = disk_usage.free / (1024 ** 3)
        disk_status = 'healthy' if disk_free_gb > 1 else 'low_space'
    except:
        disk_status = 'unknown'
    
    # 返回健康状态
    status = 'healthy' if db_status == 'healthy' else 'unhealthy'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': db_status,
            'disk': disk_status
        },
        'version': os.environ.get('APP_VERSION', '1.0.0')
    }), 200 if status == 'healthy' else 503

@bp.route('/ready', methods=['GET'])
def readiness_check():
    """就绪检查接口（用于Kubernetes等容器编排）"""
    try:
        # 检查数据库连接
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@bp.route('/live', methods=['GET'])
def liveness_check():
    """存活检查接口（用于Kubernetes等容器编排）"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
