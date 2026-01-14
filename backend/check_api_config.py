#!/usr/bin/env python3
"""检查AI API配置和连接状态"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 60)
print("AI API 配置检查")
print("=" * 60)

# 检查API Key配置
deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
qwen_key = os.environ.get('QWEN_API_KEY', '')
provider = os.environ.get('AI_PROVIDER', 'deepseek')

print(f"\n1. API Key 配置状态:")
print(f"   DEEPSEEK_API_KEY: {'✅ 已设置' if deepseek_key else '❌ 未设置'}")
if deepseek_key:
    print(f"     长度: {len(deepseek_key)} 字符")
    print(f"     前8个字符: {deepseek_key[:8]}...")
    print(f"     格式检查: {'✅ 格式正确 (sk-开头)' if deepseek_key.startswith('sk-') else '⚠️ 格式可能不正确'}")

print(f"   QWEN_API_KEY: {'✅ 已设置' if qwen_key else '❌ 未设置'}")
if qwen_key:
    print(f"     长度: {len(qwen_key)} 字符")
    print(f"     前8个字符: {qwen_key[:8]}...")

print(f"\n2. 当前使用的服务:")
print(f"   AI_PROVIDER: {provider}")

# 检查.env文件
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    print(f"\n3. .env 文件:")
    print(f"   ✅ 找到 .env 文件: {env_file}")
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        has_deepseek = any('DEEPSEEK_API_KEY' in line for line in lines)
        has_qwen = any('QWEN_API_KEY' in line for line in lines)
        print(f"   包含 DEEPSEEK_API_KEY: {'✅' if has_deepseek else '❌'}")
        print(f"   包含 QWEN_API_KEY: {'✅' if has_qwen else '❌'}")
else:
    print(f"\n3. .env 文件:")
    print(f"   ⚠️ 未找到 .env 文件")
    print(f"   环境变量可能来自系统环境或shell配置")

# 测试API连接（如果配置了）
if deepseek_key and provider == 'deepseek':
    print(f"\n4. 测试 DeepSeek API 连接:")
    try:
        import requests
        url = "https://api.deepseek.com/v1/models"
        headers = {
            "Authorization": f"Bearer {deepseek_key}"
        }
        print(f"   正在测试连接...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ API连接成功！")
            models = response.json()
            if 'data' in models:
                print(f"   可用模型数量: {len(models['data'])}")
        elif response.status_code == 401:
            print(f"   ❌ API Key无效或已过期")
            try:
                error = response.json()
                print(f"   错误信息: {error.get('error', {}).get('message', '未知错误')}")
            except:
                print(f"   响应: {response.text[:200]}")
        elif response.status_code == 429:
            print(f"   ⚠️ API请求频率限制")
        else:
            print(f"   ⚠️ API返回状态码: {response.status_code}")
            try:
                error = response.json()
                print(f"   错误信息: {error.get('error', {}).get('message', response.text[:200])}")
            except:
                print(f"   响应: {response.text[:200]}")
    except ImportError:
        print(f"   ⚠️ requests模块未安装，无法测试连接")
        print(f"   请运行: pip install requests")
    except Exception as e:
        error_type = type(e).__name__
        if 'Timeout' in error_type:
            print(f"   ❌ 连接超时（10秒）")
        elif 'Connection' in error_type:
            print(f"   ❌ 无法连接到API服务器，请检查网络")
        else:
            print(f"   ❌ 测试失败: {str(e)}")
            print(f"   错误类型: {error_type}")
elif qwen_key and provider == 'qwen':
    print(f"\n4. 测试 Qwen API 连接:")
    print(f"   ⚠️ Qwen API测试功能暂未实现")
else:
    print(f"\n4. API连接测试:")
    print(f"   ⚠️ 未配置API Key，无法测试连接")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

# 提供配置建议
if not deepseek_key and not qwen_key:
    print("\n💡 配置建议:")
    print("   1. 在 backend 目录下创建 .env 文件")
    print("   2. 添加以下内容:")
    print("      DEEPSEEK_API_KEY=your_api_key_here")
    print("      AI_PROVIDER=deepseek")
    print("   3. 或者设置系统环境变量:")
    print("      export DEEPSEEK_API_KEY=your_api_key_here")
    print("      export AI_PROVIDER=deepseek")
