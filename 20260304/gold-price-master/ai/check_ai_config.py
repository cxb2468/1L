#!/usr/bin/env python
# coding: utf-8
"""
AI服务配置检查工具
帮助用户诊断和修复AI服务配置问题
"""

import sys
import os

# 添加项目根目录到 Python 路径
# 获取当前文件的父目录的父目录（即项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import config
import requests
import json

def check_api_configuration():
    """检查API配置状态"""
    print("=== AI服务配置检查 ===\n")
    
    # 检查环境变量文件
    env_file = ".env"
    if os.path.exists(env_file):
        print("✓ 检测到 .env 配置文件")
        # 读取配置文件检查内容
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "your_" in content:
                print("⚠ 配置文件中包含占位符，请替换为实际的API密钥")
            else:
                print("✓ 配置文件格式正确")
    else:
        print("✗ 未找到 .env 配置文件")
        print("  请复制 .env.example 为 .env 并配置API密钥")
        return False
    
    # 检查各服务配置状态
    print("\n各AI服务配置状态:")
    
    services_status = {
        "阿里云百炼": {
            "configured": bool(config.ALIYUN_API_KEY and not config.ALIYUN_API_KEY.startswith('your_')),
            "key": config.ALIYUN_API_KEY
        },
        "百度文心一言": {
            "configured": bool(config.BAIDU_API_KEY and config.BAIDU_SECRET_KEY and 
                             not config.BAIDU_API_KEY.startswith('your_') and 
                             not config.BAIDU_SECRET_KEY.startswith('your_')),
            "key": config.BAIDU_API_KEY
        },
        "讯飞星火": {
            "configured": bool(config.XUNFEI_API_KEY and not config.XUNFEI_API_KEY.startswith('your_')),
            "key": config.XUNFEI_API_KEY
        }
    }
    
    configured_count = 0
    for service, info in services_status.items():
        if info["configured"]:
            key_preview = info["key"][:8] + "..." if len(info["key"]) > 8 else info["key"]
            print(f"✓ {service}: 已配置 (密钥: {key_preview})")
            configured_count += 1
        else:
            print(f"✗ {service}: 未配置或配置不完整")
    
    print(f"\n总计: {configured_count}/3 个服务已配置")
    
    if configured_count == 0:
        print("\n💡 建议:")
        print("1. 复制 .env.example 为 .env")
        print("2. 从对应平台申请API密钥")
        print("3. 将密钥填入 .env 文件对应位置")
        return False
    else:
        print(f"\n✓ 系统可以使用 {configured_count} 个AI服务")
        return True

def test_api_connectivity():
    """测试API连通性（仅测试配置是否正确，不实际调用付费接口）"""
    print("\n=== API连通性测试 ===")
    
    if not config.is_configured():
        print("✗ 无配置的API服务，跳过连通性测试")
        return
    
    # 测试阿里云API密钥格式
    if config.ALIYUN_API_KEY and not config.ALIYUN_API_KEY.startswith('your_'):
        print("✓ 阿里云API密钥格式检查通过")
    
    # 测试百度API密钥格式
    if config.BAIDU_API_KEY and config.BAIDU_SECRET_KEY and \
       not config.BAIDU_API_KEY.startswith('your_') and \
       not config.BAIDU_SECRET_KEY.startswith('your_'):
        print("✓ 百度API密钥格式检查通过")
    
    # 测试讯飞API密钥格式
    if config.XUNFEI_API_KEY and not config.XUNFEI_API_KEY.startswith('your_'):
        print("✓ 讯飞API密钥格式检查通过")

def show_setup_guide():
    """显示设置指南"""
    print("\n=== AI服务设置指南 ===")
    print("""
1. 阿里云百炼设置:
   - 访问: https://dashscope.console.aliyun.com/
   - 或访问: https://help.aliyun.com/document_detail/2214717.html
   - 注册阿里云账号并开通DashScope服务
   - 在控制台创建API密钥
   - 将密钥填入 .env 文件的 ALIYUN_API_KEY 字段

2. 百度文心一言设置:
   - 访问: https://cloud.baidu.com/product/wenxinworkshop
   - 创建应用获取API Key和Secret Key
   - 分别填入 BAIDU_API_KEY 和 BAIDU_SECRET_KEY 字段

3. 讯飞星火设置:
   - 访问: https://www.xfyun.cn/services/spark
   - 注册开发者账号获取API密钥
   - 将密钥填入 XUNFEI_API_KEY 字段

注意事项:
- 建议至少配置一个服务以获得最佳体验
- 多个服务可以提供更好的容错能力
- 免费额度通常足够日常使用
""")

def main():
    """主函数"""
    print("AI行情分析配置检查工具")
    print("=" * 40)
    
    # 检查配置
    config_ok = check_api_configuration()
    
    # 测试连通性
    test_api_connectivity()
    
    # 显示设置指南
    show_setup_guide()
    
    if config_ok:
        print("\n✅ 配置检查完成，AI分析功能可以正常使用")
    else:
        print("\n❌ 需要配置API密钥才能使用AI分析功能")

if __name__ == "__main__":
    main()