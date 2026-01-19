"""
GPU 工具模块
用于检测和使用 GPU 运行 ConvNeXt 模型
"""
import torch
import logging

logger = logging.getLogger(__name__)

def check_gpu_availability():
    """
    检查 GPU 是否可用
    
    Returns:
        dict: {
            'available': bool,
            'device': str,
            'device_name': str,
            'cuda_version': str,
            'gpu_count': int
        }
    """
    result = {
        'available': False,
        'device': 'cpu',
        'device_name': 'CPU',
        'cuda_version': None,
        'gpu_count': 0
    }
    
    try:
        if torch.cuda.is_available():
            result['available'] = True
            result['device'] = 'cuda:0'
            result['device_name'] = torch.cuda.get_device_name(0)
            result['cuda_version'] = torch.version.cuda
            result['gpu_count'] = torch.cuda.device_count()
            
            logger.info(f"✅ GPU 可用: {result['device_name']}")
            logger.info(f"   CUDA 版本: {result['cuda_version']}")
            logger.info(f"   GPU 数量: {result['gpu_count']}")
        else:
            logger.warning("⚠️ GPU 不可用，将使用 CPU")
    except Exception as e:
        logger.error(f"❌ GPU 检测失败: {str(e)}")
    
    return result

def get_device():
    """
    获取可用的设备（GPU 或 CPU）
    
    Returns:
        torch.device: 设备对象
    """
    gpu_info = check_gpu_availability()
    
    if gpu_info['available']:
        device = torch.device('cuda:0')
        logger.info(f"🚀 使用 GPU: {gpu_info['device_name']}")
    else:
        device = torch.device('cpu')
        logger.info("💻 使用 CPU")
    
    return device

def load_convnext_model(model_path=None, num_classes=None):
    """
    加载 ConvNeXt 模型
    
    Args:
        model_path: 模型文件路径（可选）
        num_classes: 分类数量（可选）
    
    Returns:
        model: ConvNeXt 模型
        device: 设备对象
    """
    try:
        import torchvision.models as models
        
        device = get_device()
        
        # 加载 ConvNeXt 模型
        # 如果提供了模型路径，从文件加载
        if model_path:
            model = torch.load(model_path, map_location=device)
            logger.info(f"📦 从文件加载模型: {model_path}")
        else:
            # 使用预训练的 ConvNeXt 模型
            # 根据 num_classes 决定使用哪个变体
            if num_classes:
                # 自定义分类数
                model = models.convnext_tiny(pretrained=True)
                # 修改最后一层
                model.classifier[-1] = torch.nn.Linear(
                    model.classifier[-1].in_features, 
                    num_classes
                )
            else:
                # 使用默认的预训练模型
                model = models.convnext_tiny(pretrained=True)
            
            logger.info("📦 加载预训练 ConvNeXt 模型")
        
        # 将模型移动到设备
        model = model.to(device)
        model.eval()  # 设置为评估模式
        
        logger.info(f"✅ 模型已加载到 {device}")
        
        return model, device
        
    except ImportError:
        logger.error("❌ torchvision 未安装，无法加载 ConvNeXt 模型")
        raise ImportError("请安装 torchvision: pip install torchvision")
    except Exception as e:
        logger.error(f"❌ 模型加载失败: {str(e)}")
        raise

def predict_with_model(model, input_tensor, device=None):
    """
    使用模型进行预测
    
    Args:
        model: ConvNeXt 模型
        input_tensor: 输入张量
        device: 设备对象（可选）
    
    Returns:
        predictions: 预测结果
    """
    if device is None:
        device = get_device()
    
    # 确保输入在正确的设备上
    input_tensor = input_tensor.to(device)
    
    # 进行预测
    with torch.no_grad():
        outputs = model(input_tensor)
        predictions = torch.nn.functional.softmax(outputs, dim=1)
    
    return predictions

# 初始化时检查 GPU
_gpu_info = check_gpu_availability()
