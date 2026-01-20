"""
GPU 测试路由
用于测试 GPU 是否正常工作
"""
from flask import Blueprint, jsonify
from app.utils.gpu_utils import check_gpu_availability, get_device, TORCH_AVAILABLE

bp = Blueprint('gpu_test', __name__)

@bp.route('/gpu/status', methods=['GET'])
def gpu_status():
    """获取 GPU 状态"""
    try:
        gpu_info = check_gpu_availability()
        
        # 如果 PyTorch 未安装，直接返回状态
        if not TORCH_AVAILABLE:
            return jsonify({
                'code': 200,
                'message': 'PyTorch 未安装，GPU 功能不可用',
                'data': {
                    'gpu_available': False,
                    'device': 'cpu',
                    'device_name': 'CPU',
                    'cuda_version': None,
                    'gpu_count': 0,
                    'torch_installed': False,
                    'status': 'PyTorch 未安装',
                    'install_hint': 'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117'
                }
            })
        
        # 尝试创建一个简单的张量来测试 GPU
        import torch
        device = get_device()
        if device is None:
            test_result = None
        else:
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
                'torch_installed': True,
                'status': '正常'
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'GPU 状态检查失败: {str(e)}',
            'data': {
                'gpu_available': False,
                'torch_installed': TORCH_AVAILABLE,
                'error': str(e)
            }
        }), 500

@bp.route('/gpu/convnext', methods=['GET'])
def test_convnext():
    """测试 ConvNeXt 模型加载"""
    try:
        if not TORCH_AVAILABLE:
            return jsonify({
                'code': 400,
                'message': 'PyTorch 未安装，无法加载模型',
                'data': {
                    'torch_installed': False,
                    'install_hint': 'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117'
                }
            }), 400
        
        from app.utils.gpu_utils import load_convnext_model
        import torch
        
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
    except ImportError as e:
        return jsonify({
            'code': 400,
            'message': f'依赖缺失: {str(e)}',
            'data': {
                'torch_installed': TORCH_AVAILABLE,
                'error': str(e),
                'install_hint': 'pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117'
            }
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'ConvNeXt 模型测试失败: {str(e)}',
            'data': {
                'torch_installed': TORCH_AVAILABLE,
                'error': str(e)
            }
        }), 500
