#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户交互模块
用于处理版本检测失败时的用户交互，允许手动选择Everything版本
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_interaction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VersionSelectionDialog:
    """
    版本选择对话框
    用于在版本检测失败时让用户手动选择Everything版本
    """
    
    def __init__(self, parent=None):
        """
        初始化版本选择对话框
        :param parent: 父窗口
        """
        self.parent = parent
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """
        显示版本选择对话框
        :return: 用户选择的版本，'1.4' 或 '1.5'，如果取消返回None
        """
        # 创建对话框
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("选择Everything版本")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # 使对话框模态
        self.dialog.grab_set()
        
        # 创建内容
        content_frame = ttk.Frame(self.dialog, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(
            content_frame,
            text="无法自动检测Everything版本",
            font=('Microsoft YaHei', 12, 'bold')
        ).pack(pady=(0, 15))
        
        # 提示信息
        ttk.Label(
            content_frame,
            text="请手动选择您正在使用的Everything版本:",
            font=('Microsoft YaHei', 10)
        ).pack(pady=(0, 15))
        
        # 版本选择
        self.version_var = tk.StringVar(value="1.4")
        
        version_frame = ttk.Frame(content_frame)
        version_frame.pack(pady=(0, 20))
        
        ttk.Radiobutton(
            version_frame,
            text="Everything 1.4",
            variable=self.version_var,
            value="1.4",
            style="TRadiobutton"
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(
            version_frame,
            text="Everything 1.5",
            variable=self.version_var,
            value="1.5",
            style="TRadiobutton"
        ).pack(anchor=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="确定",
            command=self._on_ok,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel,
            style="TButton"
        ).pack(side=tk.RIGHT)
        
        # 等待对话框关闭
        self.dialog.wait_window()
        
        return self.result
    
    def _on_ok(self):
        """
        确定按钮点击事件
        """
        self.result = self.version_var.get()
        logger.info(f"用户选择了Everything版本: {self.result}")
        self.dialog.destroy()
    
    def _on_cancel(self):
        """
        取消按钮点击事件
        """
        self.result = None
        logger.info("用户取消了版本选择")
        self.dialog.destroy()

def ask_for_version(parent=None) -> Optional[str]:
    """
    请求用户选择Everything版本
    :param parent: 父窗口
    :return: 用户选择的版本，'1.4' 或 '1.5'，如果取消返回None
    """
    dialog = VersionSelectionDialog(parent)
    return dialog.show()

def create_manual_version_info(version: str) -> Dict[str, any]:
    """
    根据用户选择的版本创建版本信息
    :param version: 用户选择的版本，'1.4' 或 '1.5'
    :return: 版本信息字典
    """
    is_1_4 = version == "1.4"
    is_1_5 = version == "1.5"
    
    version_tuple = (1, 4) if is_1_4 else (1, 5)
    
    return {
        "installed": True,
        "install_path": None,  # 手动选择时无法确定安装路径
        "version": version_tuple,
        "major_version": version_tuple[0],
        "minor_version": version_tuple[1],
        "is_1_5": is_1_5,
        "is_1_4": is_1_4,
        "is_running": False,  # 手动选择时无法确定运行状态
        "process_version": None
    }

# 测试函数
def test_version_selection():
    """
    测试版本选择对话框
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    version = ask_for_version(root)
    print(f"用户选择的版本: {version}")
    
    if version:
        version_info = create_manual_version_info(version)
        print(f"创建的版本信息: {version_info}")
    
    root.destroy()

if __name__ == "__main__":
    test_version_selection()
