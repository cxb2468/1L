#!/usr/bin/env python
# coding: utf-8
"""
AI服务入口导航工具
帮助用户快速找到各平台的API密钥获取入口
"""

import webbrowser
import sys
import os

def show_platform_options():
    """显示各平台选项"""
    platforms = {
        "1": {
            "name": "阿里云百炼(DashScope)",
            "urls": [
                "https://dashscope.console.aliyun.com/",
                "https://help.aliyun.com/document_detail/2214717.html"
            ],
            "description": "阿里云推出的通义千问系列大模型服务平台"
        },
        "2": {
            "name": "百度千帆大模型平台", 
            "urls": [
                "https://qianfan.cloud.baidu.com/",
                "https://cloud.baidu.com/doc/WENXINWORKSHOP/s/jlil56u11"
            ],
            "description": "百度文心一言大模型服务平台"
        },
        "3": {
            "name": "讯飞星火认知大模型",
            "urls": [
                "https://xinghuo.xfyun.cn/",
                "https://www.xfyun.cn/doc/spark/Web.html"
            ],
            "description": "科大讯飞推出的大语言模型平台"
        },
        "4": {
            "name": "查看详细配置指南",
            "urls": ["API_KEY_GUIDE.md"],
            "description": "打开本地配置指南文档"
        }
    }
    
    print("=== AI服务入口导航 ===\n")
    print("请选择要访问的平台:")
    print("-" * 40)
    
    for key, platform in platforms.items():
        print(f"{key}. {platform['name']}")
        print(f"   简介: {platform['description']}")
        print()
    
    return platforms

def open_urls(platform_info):
    """打开指定平台的URL"""
    urls = platform_info["urls"]
    
    print(f"\n正在打开 {platform_info['name']} 的相关页面...")
    
    for i, url in enumerate(urls, 1):
        try:
            if url.endswith('.md'):
                # 本地文件，使用默认程序打开
                if os.path.exists(url):
                    print(f"  {i}. 打开本地文档: {url}")
                    os.startfile(url)  # Windows
                else:
                    print(f"  {i}. 本地文档不存在: {url}")
            else:
                # 网页链接
                print(f"  {i}. 打开网页: {url}")
                webbrowser.open(url)
        except Exception as e:
            print(f"  {i}. 打开失败: {e}")

def main():
    """主函数"""
    print("AI行情分析 - API密钥获取助手")
    print("=" * 50)
    
    platforms = show_platform_options()
    
    while True:
        try:
            choice = input("请输入选项编号 (1-4)，或输入 'q' 退出: ").strip()
            
            if choice.lower() == 'q':
                print("再见!")
                break
            
            if choice in platforms:
                platform_info = platforms[choice]
                open_urls(platform_info)
                
                if choice != "4":  # 不是查看指南的情况下询问是否继续
                    continue_choice = input("\n是否继续查看其他平台? (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        break
            else:
                print("无效选项，请重新选择!")
                
        except KeyboardInterrupt:
            print("\n\n程序被中断，再见!")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()