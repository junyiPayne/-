from flask import jsonify
from datetime import datetime
import logging
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class APIException(Exception):
    """API异常基类"""
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)

class ValidationError(APIException):
    """参数验证错误"""
    def __init__(self, message="参数验证失败", data=None):
        super().__init__(400, message, data)

class AuthenticationError(APIException):
    """认证错误"""
    def __init__(self, message="认证失败"):
        super().__init__(401, message)

class PermissionDeniedError(APIException):
    """权限不足"""
    def __init__(self, message="权限不足"):
        super().__init__(403, message)

class NotFoundError(APIException):
    """资源不存在"""
    def __init__(self, message="资源不存在"):
        super().__init__(404, message)

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        return jsonify({
            'code': e.code,
            'message': e.message,
            'data': e.data,
            'timestamp': datetime.utcnow().isoformat()
        }), e.code
    
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({
            'code': 404,
            'message': "请求的资源不存在",
            'timestamp': datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有未捕获的异常"""
        if isinstance(e, HTTPException):
            return e
        
        # 记录详细错误信息到日志
        logger.error(f"Unhandled Exception: {e}", exc_info=True)
        
        # 生产环境不暴露详细错误信息
        is_production = not app.config.get('DEBUG', False)
        if is_production:
            error_message = "服务器内部错误，请稍后重试"
        else:
            error_message = f"服务器内部错误: {str(e)}"
        
        return jsonify({
            'code': 500,
            'message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

