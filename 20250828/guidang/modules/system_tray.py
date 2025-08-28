# -*- coding: utf-8 -*-
"""
系统托盘模块
提供系统托盘功能，支持后台运行和快速访问
"""

import os
import threading
from datetime import datetime
from typing import Callable, Optional
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("警告: pystray或PIL未安装，系统托盘功能不可用")

class SystemTray:
    """系统托盘管理器"""
    
    def __init__(self, app_name: str = "桌面文件归档工具"):
        self.app_name = app_name
        self.icon = None
        self.is_running = False
        
        # 回调函数
        self.show_callback = None
        self.hide_callback = None
        self.quit_callback = None
        self.archive_callback = None
        self.settings_callback = None
        
        if not TRAY_AVAILABLE:
            print("系统托盘功能不可用，请安装 pystray 和 Pillow")
            
    def create_icon_image(self, color: str = "blue") -> Optional[Image.Image]:
        """创建托盘图标
        
        Args:
            color: 图标颜色
            
        Returns:
            PIL图像对象
        """
        if not TRAY_AVAILABLE:
            return None
            
        try:
            # 创建一个简单的图标
            width = 64
            height = 64
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 绘制一个文件夹图标
            # 文件夹底部
            draw.rectangle([10, 25, 54, 50], fill=color, outline='black', width=2)
            # 文件夹标签
            draw.rectangle([10, 20, 30, 25], fill=color, outline='black', width=2)
            # 文档图标
            draw.rectangle([20, 30, 35, 45], fill='white', outline='black', width=1)
            draw.rectangle([25, 35, 45, 50], fill='white', outline='black', width=1)
            
            return image
            
        except Exception as e:
            print(f"创建图标失败: {str(e)}")
            return None
            
    def create_menu(self) -> Optional[pystray.Menu]:
        """创建右键菜单
        
        Returns:
            pystray菜单对象
        """
        if not TRAY_AVAILABLE:
            return None
            
        try:
            menu_items = [
                pystray.MenuItem("显示主窗口", self._on_show, default=True),
                pystray.MenuItem("立即归档", self._on_archive),
                pystray.MenuItem("设置", self._on_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("关于", self._on_about),
                pystray.MenuItem("退出", self._on_quit)
            ]
            
            return pystray.Menu(*menu_items)
            
        except Exception as e:
            print(f"创建菜单失败: {str(e)}")
            return None
            
    def start(self, show_callback: Callable = None, hide_callback: Callable = None,
             quit_callback: Callable = None, archive_callback: Callable = None,
             settings_callback: Callable = None):
        """启动系统托盘
        
        Args:
            show_callback: 显示主窗口的回调函数
            hide_callback: 隐藏主窗口的回调函数
            quit_callback: 退出应用的回调函数
            archive_callback: 执行归档的回调函数
            settings_callback: 打开设置的回调函数
        """
        if not TRAY_AVAILABLE:
            print("系统托盘不可用")
            return
            
        # 设置回调函数
        self.show_callback = show_callback
        self.hide_callback = hide_callback
        self.quit_callback = quit_callback
        self.archive_callback = archive_callback
        self.settings_callback = settings_callback
        
        try:
            # 创建图标和菜单
            icon_image = self.create_icon_image()
            menu = self.create_menu()
            
            if icon_image and menu:
                self.icon = pystray.Icon(
                    name=self.app_name,
                    icon=icon_image,
                    title=self.app_name,
                    menu=menu
                )
                
                # 在新线程中运行托盘
                self.is_running = True
                tray_thread = threading.Thread(target=self._run_tray, daemon=True)
                tray_thread.start()
                
                print("系统托盘已启动")
            else:
                print("创建系统托盘失败")
                
        except Exception as e:
            print(f"启动系统托盘失败: {str(e)}")
            
    def stop(self):
        """停止系统托盘"""
        if self.icon and self.is_running:
            try:
                self.is_running = False
                self.icon.stop()
                print("系统托盘已停止")
            except Exception as e:
                print(f"停止系统托盘失败: {str(e)}")
                
    def _run_tray(self):
        """运行系统托盘的主循环"""
        try:
            if self.icon:
                self.icon.run()
        except Exception as e:
            print(f"系统托盘运行错误: {str(e)}")
            
    def _on_show(self, icon, item):
        """显示主窗口"""
        if self.show_callback:
            self.show_callback()
            
    def _on_archive(self, icon, item):
        """执行归档"""
        if self.archive_callback:
            # 在新线程中执行，避免阻塞托盘
            thread = threading.Thread(target=self.archive_callback, daemon=True)
            thread.start()
            
    def _on_settings(self, icon, item):
        """打开设置"""
        if self.settings_callback:
            self.settings_callback()
        elif self.show_callback:
            # 如果没有专门的设置回调，就显示主窗口
            self.show_callback()
            
    def _on_about(self, icon, item):
        """显示关于信息"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # 创建一个临时的根窗口（不显示）
            root = tk.Tk()
            root.withdraw()
            
            about_text = f"""{self.app_name}
版本: 1.0.0

一个功能强大的桌面文件自动归档工具
支持Word、Excel、PowerPoint、PDF等文档的自动归档

特性:
• 定时自动归档
• 灵活的归档规则
• 系统托盘支持
• 详细的操作日志

作者: AI Assistant"""
            
            messagebox.showinfo("关于", about_text)
            root.destroy()
            
        except Exception as e:
            print(f"显示关于信息失败: {str(e)}")
            
    def _on_quit(self, icon, item):
        """退出应用"""
        if self.quit_callback:
            self.quit_callback()
        else:
            # 默认行为：停止托盘
            self.stop()
            
    def show_notification(self, title: str, message: str, timeout: int = 3):
        """显示系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
            timeout: 显示时间（秒）
        """
        if not TRAY_AVAILABLE or not self.icon:
            print(f"通知: {title} - {message}")
            return
            
        try:
            self.icon.notify(message, title)
        except Exception as e:
            print(f"显示通知失败: {str(e)}")
            print(f"通知内容: {title} - {message}")
            
    def update_icon(self, color: str = "blue"):
        """更新托盘图标
        
        Args:
            color: 新的图标颜色
        """
        if not TRAY_AVAILABLE or not self.icon:
            return
            
        try:
            new_image = self.create_icon_image(color)
            if new_image:
                self.icon.icon = new_image
        except Exception as e:
            print(f"更新图标失败: {str(e)}")
            
    def update_title(self, title: str):
        """更新托盘图标标题
        
        Args:
            title: 新的标题
        """
        if not TRAY_AVAILABLE or not self.icon:
            return
            
        try:
            self.icon.title = title
        except Exception as e:
            print(f"更新标题失败: {str(e)}")
            
    def is_available(self) -> bool:
        """检查系统托盘是否可用
        
        Returns:
            系统托盘是否可用
        """
        return TRAY_AVAILABLE
        
    def get_status(self) -> dict:
        """获取系统托盘状态
        
        Returns:
            状态信息字典
        """
        return {
            'available': TRAY_AVAILABLE,
            'running': self.is_running,
            'icon_created': self.icon is not None
        }

class TrayNotificationManager:
    """托盘通知管理器"""
    
    def __init__(self, tray: SystemTray):
        self.tray = tray
        self.notification_queue = []
        self.is_processing = False
        
    def add_notification(self, title: str, message: str, priority: str = 'normal'):
        """添加通知到队列
        
        Args:
            title: 通知标题
            message: 通知内容
            priority: 优先级 ('low', 'normal', 'high')
        """
        notification = {
            'title': title,
            'message': message,
            'priority': priority,
            'timestamp': datetime.now()
        }
        
        # 根据优先级插入到合适位置
        if priority == 'high':
            self.notification_queue.insert(0, notification)
        else:
            self.notification_queue.append(notification)
            
        # 开始处理队列
        if not self.is_processing:
            self._process_queue()
            
    def _process_queue(self):
        """处理通知队列"""
        if not self.notification_queue:
            self.is_processing = False
            return
            
        self.is_processing = True
        
        def process_next():
            if self.notification_queue:
                notification = self.notification_queue.pop(0)
                self.tray.show_notification(
                    notification['title'], 
                    notification['message']
                )
                
                # 延迟处理下一个通知
                threading.Timer(4.0, process_next).start()
            else:
                self.is_processing = False
                
        process_next()
        
    def clear_queue(self):
        """清空通知队列"""
        self.notification_queue.clear()
        self.is_processing = False