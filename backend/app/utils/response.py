from flask import jsonify
from datetime import datetime

def success_response(data=None, message="success", code=200):
    """成功响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }), code

def error_response(message="error", code=400, data=None):
    """错误响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }), code

