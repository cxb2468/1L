#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面文件自动归档工具
功能：自动定期归档桌面的Word、Excel、PowerPoint等Office文档
作者：AI Assistant
版本：1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import threading
import time
from datetime import datetime, timedelta
import shutil
import json
import logging
from pathlib import Path
# import schedule  # 已在scheduler模块中使用
from typing import Dict, List, Tuple

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_scanner import FileScanner
from modules.archive_manager import ArchiveManager
from modules.config_manager import ConfigManager
from modules.scheduler import TaskScheduler
from modules.logger import AppLogger

class DesktopArchiveApp:
    """桌面文件归档应用主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.logger = AppLogger()
        self.file_scanner = FileScanner()
        self.archive_manager = ArchiveManager()
        self.scheduler = TaskScheduler()
        
        # 加载配置
        self.config = self.config_manager.load_config()
        
        # 创建GUI
        self.create_widgets()
        self.setup_layout()
        
        # 启动后台任务
        self.start_background_tasks()
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("桌面文件自动归档工具 v1.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
            
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="桌面文件自动归档工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 状态框架
        self.create_status_frame(main_frame)
        
        # 设置框架
        self.create_settings_frame(main_frame)
        
        # 日志框架
        self.create_log_frame(main_frame)
        
        # 控制按钮框架
        self.create_control_frame(main_frame)
        
    def create_status_frame(self, parent):
        """创建状态显示框架"""
        status_frame = ttk.LabelFrame(parent, text="运行状态", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # 监控状态
        ttk.Label(status_frame, text="监控状态:").grid(row=0, column=0, sticky=tk.W)
        self.status_var = tk.StringVar(value="已停止")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                     foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 下次归档时间
        ttk.Label(status_frame, text="下次归档:").grid(row=1, column=0, sticky=tk.W)
        self.next_archive_var = tk.StringVar(value="未设置")
        ttk.Label(status_frame, textvariable=self.next_archive_var).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 已归档文件数
        ttk.Label(status_frame, text="已归档文件:").grid(row=2, column=0, sticky=tk.W)
        self.archived_count_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.archived_count_var).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0))
            
    def create_settings_frame(self, parent):
        """创建设置框架"""
        settings_frame = ttk.LabelFrame(parent, text="归档设置", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # 桌面路径
        ttk.Label(settings_frame, text="桌面路径:").grid(row=0, column=0, sticky=tk.W)
        self.desktop_path_var = tk.StringVar(value=self.get_desktop_path())
        desktop_entry = ttk.Entry(settings_frame, textvariable=self.desktop_path_var, width=50)
        desktop_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(settings_frame, text="浏览", 
                  command=self.browse_desktop_path).grid(row=0, column=2)
        
        # 归档目录
        ttk.Label(settings_frame, text="归档目录:").grid(row=1, column=0, sticky=tk.W)
        self.archive_path_var = tk.StringVar(value=self.config.get('archive_path', 
                                                                  os.path.join(os.path.expanduser('~'), 'Documents', 'DesktopArchive')))
        archive_entry = ttk.Entry(settings_frame, textvariable=self.archive_path_var, width=50)
        archive_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(settings_frame, text="浏览", 
                  command=self.browse_archive_path).grid(row=1, column=2)
        
        # 归档频率
        ttk.Label(settings_frame, text="归档频率:").grid(row=2, column=0, sticky=tk.W)
        self.frequency_var = tk.StringVar(value=self.config.get('frequency', '每天'))
        frequency_combo = ttk.Combobox(settings_frame, textvariable=self.frequency_var,
                                      values=['每小时', '每天', '每周', '每月'], state='readonly')
        frequency_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # 归档时间
        ttk.Label(settings_frame, text="归档时间:").grid(row=3, column=0, sticky=tk.W)
        time_frame = ttk.Frame(settings_frame)
        time_frame.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        self.hour_var = tk.StringVar(value=self.config.get('hour', '18'))
        self.minute_var = tk.StringVar(value=self.config.get('minute', '00'))
        
        hour_spin = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.hour_var, width=3)
        hour_spin.grid(row=0, column=0)
        ttk.Label(time_frame, text=":").grid(row=0, column=1)
        minute_spin = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.minute_var, width=3)
        minute_spin.grid(row=0, column=2)
        
        # 文件类型选择
        ttk.Label(settings_frame, text="文件类型:").grid(row=4, column=0, sticky=tk.W)
        file_types_frame = ttk.Frame(settings_frame)
        file_types_frame.grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        self.word_var = tk.BooleanVar(value=self.config.get('include_word', True))
        self.excel_var = tk.BooleanVar(value=self.config.get('include_excel', True))
        self.ppt_var = tk.BooleanVar(value=self.config.get('include_ppt', True))
        self.pdf_var = tk.BooleanVar(value=self.config.get('include_pdf', True))
        
        ttk.Checkbutton(file_types_frame, text="Word文档", variable=self.word_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(file_types_frame, text="Excel表格", variable=self.excel_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Checkbutton(file_types_frame, text="PowerPoint", variable=self.ppt_var).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        ttk.Checkbutton(file_types_frame, text="PDF文档", variable=self.pdf_var).grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
    def create_log_frame(self, parent):
        """创建日志显示框架"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 创建文本框和滚动条
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_control_frame(self, parent):
        """创建控制按钮框架"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # 开始/停止按钮
        self.start_stop_btn = ttk.Button(control_frame, text="开始监控", 
                                        command=self.toggle_monitoring)
        self.start_stop_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 立即归档按钮
        ttk.Button(control_frame, text="立即归档", 
                  command=self.manual_archive).grid(row=0, column=1, padx=(0, 10))
        
        # 保存设置按钮
        ttk.Button(control_frame, text="保存设置", 
                  command=self.save_settings).grid(row=0, column=2, padx=(0, 10))
        
        # 打开归档目录按钮
        ttk.Button(control_frame, text="打开归档目录", 
                  command=self.open_archive_folder).grid(row=0, column=3)
        
    def setup_layout(self):
        """设置布局"""
        # 初始化日志显示
        self.add_log("应用程序已启动")
        self.add_log(f"桌面路径: {self.desktop_path_var.get()}")
        self.add_log(f"归档目录: {self.archive_path_var.get()}")
        
    def get_desktop_path(self):
        """获取桌面路径"""
        return os.path.join(os.path.expanduser('~'), 'Desktop')
        
    def browse_desktop_path(self):
        """浏览桌面路径"""
        path = filedialog.askdirectory(initialdir=self.desktop_path_var.get())
        if path:
            self.desktop_path_var.set(path)
            
    def browse_archive_path(self):
        """浏览归档路径"""
        path = filedialog.askdirectory(initialdir=self.archive_path_var.get())
        if path:
            self.archive_path_var.set(path)
            
    def add_log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # 记录到文件
        self.logger.info(message)
        
    def toggle_monitoring(self):
        """切换监控状态"""
        if self.status_var.get() == "已停止":
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """开始监控"""
        try:
            # 保存当前设置
            self.save_settings()
            
            # 启动调度器
            self.scheduler.start(self.config, self.perform_archive, self.add_log)
            
            # 更新状态
            self.status_var.set("运行中")
            self.status_label.configure(foreground="green")
            self.start_stop_btn.configure(text="停止监控")
            
            self.add_log("开始监控桌面文件")
            
            # 更新下次归档时间
            self.update_next_archive_time()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动监控失败: {str(e)}")
            self.add_log(f"启动监控失败: {str(e)}")
            
    def stop_monitoring(self):
        """停止监控"""
        try:
            self.scheduler.stop()
            
            # 更新状态
            self.status_var.set("已停止")
            self.status_label.configure(foreground="red")
            self.start_stop_btn.configure(text="开始监控")
            self.next_archive_var.set("未设置")
            
            self.add_log("已停止监控")
            
        except Exception as e:
            messagebox.showerror("错误", f"停止监控失败: {str(e)}")
            self.add_log(f"停止监控失败: {str(e)}")
            
    def manual_archive(self):
        """手动归档"""
        try:
            self.add_log("开始手动归档...")
            
            # 执行归档
            result = self.perform_archive()
            
            if result['success']:
                self.add_log(f"归档完成，处理了 {result['count']} 个文件")
                self.archived_count_var.set(str(int(self.archived_count_var.get()) + result['count']))
                messagebox.showinfo("成功", f"归档完成！\n处理了 {result['count']} 个文件")
            else:
                self.add_log(f"归档失败: {result['error']}")
                messagebox.showerror("错误", f"归档失败: {result['error']}")
                
        except Exception as e:
            error_msg = f"手动归档失败: {str(e)}"
            self.add_log(error_msg)
            messagebox.showerror("错误", error_msg)
            
    def perform_archive(self):
        """执行归档操作"""
        try:
            desktop_path = self.desktop_path_var.get()
            archive_path = self.archive_path_var.get()
            
            # 获取文件类型设置
            file_types = []
            if self.word_var.get():
                file_types.extend(['.doc', '.docx'])
            if self.excel_var.get():
                file_types.extend(['.xls', '.xlsx'])
            if self.ppt_var.get():
                file_types.extend(['.ppt', '.pptx'])
            if self.pdf_var.get():
                file_types.append('.pdf')
                
            # 扫描文件
            files = self.file_scanner.scan_files(desktop_path, file_types)
            
            # 归档文件
            count = self.archive_manager.archive_files(files, archive_path)
            
            return {'success': True, 'count': count}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def save_settings(self):
        """保存设置"""
        try:
            config = {
                'desktop_path': self.desktop_path_var.get(),
                'archive_path': self.archive_path_var.get(),
                'frequency': self.frequency_var.get(),
                'hour': self.hour_var.get(),
                'minute': self.minute_var.get(),
                'include_word': self.word_var.get(),
                'include_excel': self.excel_var.get(),
                'include_ppt': self.ppt_var.get(),
                'include_pdf': self.pdf_var.get()
            }
            
            self.config_manager.save_config(config)
            self.config = config
            
            self.add_log("设置已保存")
            messagebox.showinfo("成功", "设置已保存")
            
        except Exception as e:
            error_msg = f"保存设置失败: {str(e)}"
            self.add_log(error_msg)
            messagebox.showerror("错误", error_msg)
            
    def open_archive_folder(self):
        """打开归档目录"""
        archive_path = self.archive_path_var.get()
        if os.path.exists(archive_path):
            os.startfile(archive_path)
        else:
            messagebox.showwarning("警告", "归档目录不存在")
            
    def update_next_archive_time(self):
        """更新下次归档时间显示"""
        # 这里应该根据调度器的设置计算下次执行时间
        # 简化实现，显示一个估计时间
        frequency = self.frequency_var.get()
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        
        now = datetime.now()
        if frequency == "每小时":
            next_time = now.replace(minute=minute, second=0, microsecond=0) + timedelta(hours=1)
        elif frequency == "每天":
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
        elif frequency == "每周":
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            days_ahead = 0 - now.weekday()  # 周一
            if days_ahead <= 0:
                days_ahead += 7
            next_time += timedelta(days=days_ahead)
        else:  # 每月
            next_time = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                if next_time.month == 12:
                    next_time = next_time.replace(year=next_time.year + 1, month=1)
                else:
                    next_time = next_time.replace(month=next_time.month + 1)
                    
        self.next_archive_var.set(next_time.strftime("%Y-%m-%d %H:%M"))
        
    def start_background_tasks(self):
        """启动后台任务"""
        # 启动定时更新线程
        def update_loop():
            while True:
                try:
                    if self.status_var.get() == "运行中":
                        self.update_next_archive_time()
                    time.sleep(60)  # 每分钟更新一次
                except:
                    break
                    
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
    def on_closing(self):
        """关闭应用程序"""
        try:
            self.stop_monitoring()
            self.add_log("应用程序正在关闭...")
            time.sleep(0.5)  # 给日志一点时间写入
        except:
            pass
        finally:
            self.root.destroy()
            
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = DesktopArchiveApp()
        app.run()
    except Exception as e:
        messagebox.showerror("致命错误", f"应用程序启动失败: {str(e)}")
        
if __name__ == "__main__":
    main()