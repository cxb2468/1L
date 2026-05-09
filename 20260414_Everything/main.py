#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everything搜索辅助应用
基于Everything SDK的增强型搜索工具
支持Everything 1.4和1.5版本
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from version_detector import detect_everything_version
    from sdk_adapter import EverythingSDKAdapter
    from config_manager import ConfigManager
    from ui_main import MainWindow
    from user_interaction import ask_for_version, create_manual_version_info
except ImportError as e:
    print(f"错误: 无法导入必要的模块: {e}")
    print("请确保 src 目录下包含所有必需的模块文件")
    sys.exit(1)

def main():
    """应用主入口"""
    # 检测Everything版本
    version_info = detect_everything_version()
    
    # 检查版本检测是否成功
    if not version_info.get("installed") or version_info.get("version") is None:
        # 创建临时窗口用于显示版本选择对话框
        temp_root = tk.Tk()
        temp_root.withdraw()  # 隐藏主窗口
        
        # 显示版本选择对话框
        selected_version = ask_for_version(temp_root)
        
        if selected_version:
            # 根据用户选择创建版本信息
            version_info = create_manual_version_info(selected_version)
        else:
            # 用户取消了版本选择，退出应用
            temp_root.destroy()
            return
        
        temp_root.destroy()
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 初始化SDK适配器
    sdk_adapter = EverythingSDKAdapter(version_info)
    
    # 创建主窗口
    root = tk.Tk()
    app = MainWindow(root, sdk_adapter, config_manager)
    
    # 启动应用
    root.mainloop()

if __name__ == "__main__":
    main()
