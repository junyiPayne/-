"""
GPU 测试路由
用于测试 GPU 是否正常工作
"""
from flask import Blueprint, jsonify
from app.utils.gpu_utils import check_gpu_availability, get_device
import torch

bp = Blueprint('gpu_test', __name__)

@bp.route('/gpu/status', methods=['GET'])
def gpu_status():
    """获取 GPU 状态"""
    try:
        gpu_info = check_gpu_availability()
        
        # 尝试创建一个简单的张量来测试 GPU
        device = get_device()
        test_tensor = torch.randn(1, 3, 224, 224).to(device)
        test_result = test_tensor.sum().item()
        
        return jsonify({
            'code': 200,
            'message': 'GPU 状态检查成功',
            'data': {
                'gpu_available': gpu_info['available'],
                'device': gpu_info['device'],
                'device_name': gpu_info['device_name'],
                'cuda_version': gpu_info['cuda_version'],
                'gpu_count': gpu_info['gpu_count'],
                'test_result': test_result,
                'status': '正常'
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'GPU 状态检查失败: {str(e)}',
            'data': {
                'gpu_available': False,
                'error': str(e)
            }
        }), 500

@bp.route('/gpu/convnext', methods=['GET'])
def test_convnext():
    """测试 ConvNeXt 模型加载"""
    try:
        from app.utils.gpu_utils import load_convnext_model
        
        model, device = load_convnext_model()
        
        # 创建一个测试输入
        test_input = torch.randn(1, 3, 224, 224).to(device)
        
        # 进行预测
        with torch.no_grad():
            output = model(test_input)
        
        return jsonify({
            'code': 200,
            'message': 'ConvNeXt 模型测试成功',
            'data': {
                'device': str(device),
                'model_loaded': True,
                'output_shape': list(output.shape),
                'status': '正常'
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'ConvNeXt 模型测试失败: {str(e)}',
            'data': {
                'error': str(e)
            }
        }), 500
