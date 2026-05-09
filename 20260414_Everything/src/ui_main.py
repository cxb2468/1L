#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主界面模块
用于构建应用的用户界面，包括工具栏和搜索功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any
import logging
import os
import subprocess
import time

# 配置日志
import sys
from logging.handlers import RotatingFileHandler

# 创建自定义的流处理器，处理Unicode编码问题
class UnicodeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            # 尝试使用UTF-8编码写入
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # 如果编码失败，使用替代方案
            msg = self.format(record)
            # 将Unicode字符替换为安全的表示形式
            msg = msg.encode('utf-8', 'replace').decode('ascii', 'replace')
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()

# 创建文件处理器（支持UTF-8）
file_handler = logging.FileHandler('ui_main.log', encoding='utf-8')

# 创建流处理器
stream_handler = UnicodeStreamHandler()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)

class MainWindow:
    """主窗口类 - 支持Everything 1.4和1.5版本"""
    
    def __init__(self, root: tk.Tk, sdk_adapter, config_manager):
        """
        初始化主窗口
        :param root: Tk根窗口
        :param sdk_adapter: SDK适配器
        :param config_manager: 配置管理器
        """
        self.root = root
        self.sdk_adapter = sdk_adapter
        self.config_manager = config_manager
        
        # 获取窗口配置
        window_config = self.config_manager.get_window_config()
        self.root.title(window_config.get("title", "Everything搜索助手"))
        width = window_config.get('width', 1200)
        height = window_config.get('height', 700)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(800, 500)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 排序状态
        self.sort_by = 'name'
        self.sort_ascending = True
        self.current_results = []
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建搜索区域
        self._create_search_area()
        
        # 创建结果显示区域
        self._create_result_area()
        
        # 最后创建状态栏（确保在最底部）
        self._create_status_bar()
        
        # 绑定快捷键
        self.root.bind('<Return>', lambda e: self._search_from_entry())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<F5>', lambda e: self._search_from_entry())
        
        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self._on_window_configure)
        
        # 启动时检测环境
        self.root.after(500, self._update_everything_status)
        
        # 启动定期状态检测（每3秒检测一次）
        self._start_status_polling()
    
    def _on_window_configure(self, event):
        """
        窗口大小或位置变化时的回调
        """
        # 只处理主窗口的大小变化（忽略子控件）
        if event.widget == self.root:
            # 使用after延迟保存，避免频繁写入
            if hasattr(self, '_save_window_config_id'):
                self.root.after_cancel(self._save_window_config_id)
            self._save_window_config_id = self.root.after(500, self._save_window_size)
    
    def _save_window_size(self):
        """
        保存窗口大小到配置文件
        """
        try:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # 只保存合理的尺寸（避免最小化时保存错误尺寸）
            if width > 200 and height > 200:
                window_config = self.config_manager.get_window_config()
                window_config['width'] = width
                window_config['height'] = height
                self.config_manager.set_window_config(window_config)
                logger.info(f"保存窗口尺寸: {width}x{height}")
        except Exception as e:
            logger.error(f"保存窗口尺寸时出错: {e}")
    
    def _create_toolbar(self):
        """
        创建快捷按钮区域 - 优化布局，减小占用空间
        """
        toolbar_frame = ttk.LabelFrame(self.main_frame, text="快速搜索", padding=3)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 获取快捷按钮区域配置
        toolbar_config = self.config_manager.get_toolbar_config()
        self.buttons_per_row = toolbar_config.get("buttons_per_row", 5)
        
        # 获取快捷按钮配置
        buttons_config = self.config_manager.get_toolbar_buttons()
        
        # 创建快捷按钮容器框架 - 使用网格布局
        self.buttons_container = ttk.Frame(toolbar_frame)
        self.buttons_container.pack(fill=tk.X, expand=True, padx=2, pady=2)
        
        # 绑定右键菜单（保存绑定函数供后续使用）
        self._toolbar_context_menu_handler = self._create_toolbar_context_menu(toolbar_frame)
        self._create_toolbar_context_menu(self.buttons_container)
        
        # 创建快捷按钮
        self._create_toolbar_buttons(buttons_config)
    
    def _create_toolbar_buttons(self, buttons_config):
        """
        创建快捷按钮
        """
        # 清除现有快捷按钮
        for widget in self.buttons_container.winfo_children():
            widget.destroy()
        
        # 清除列配置
        for col in range(self.buttons_per_row):
            self.buttons_container.grid_columnconfigure(col, weight=0)
        
        # 创建快捷按钮（网格布局，使用配置的每行快捷按钮数）
        for i, button_config in enumerate(buttons_config):
            # 直接使用配置中的文本（已经包含图标）
            display_text = button_config.get("text", "")
            
            # 创建快捷按钮 - 宽度自适应文本内容
            button = tk.Button(
                self.buttons_container,
                text=display_text,
                font=('Microsoft YaHei', 9),
                bg=button_config["bg_color"],
                fg=button_config["text_color"],
                activebackground=button_config.get("hover_color", self._lighten_color(button_config["bg_color"])),
                activeforeground='white',
                relief='flat',
                cursor='hand2',
                padx=12,
                pady=4,
                command=lambda query=button_config["search_query"]: self._set_search_query(query)
            )
            # 添加悬停效果
            hover_color = button_config.get("hover_color", self._lighten_color(button_config["bg_color"]))
            button.bind('<Enter>', lambda e, b=button, h=hover_color: b.config(bg=h))
            button.bind('<Leave>', lambda e, b=button, c=button_config["bg_color"]: b.config(bg=c))
            # 绑定右键菜单
            if hasattr(self, '_toolbar_context_menu_handler'):
                button.bind('<Button-3>', self._toolbar_context_menu_handler)
            # 放置快捷按钮（使用网格布局，不拉伸宽度）
            row = i // self.buttons_per_row
            col = i % self.buttons_per_row
            button.grid(row=row, column=col, padx=3, pady=2, sticky='w')
            # 设置列权重为0，不自动拉伸
            self.buttons_container.grid_columnconfigure(col, weight=0)
    
    def _create_toolbar_context_menu(self, parent):
        """
        创建快捷按钮区域右键菜单
        """
        # 创建右键菜单（只创建一次）
        if not hasattr(self, '_toolbar_context_menu'):
            self._toolbar_context_menu = tk.Menu(self.root, tearoff=0)
            self._toolbar_context_menu.add_command(label="设置每行快捷按钮数...", command=self._show_buttons_per_row_dialog)
            self._toolbar_context_menu.add_separator()
            
            # 添加快捷按钮菜单项
            self._toolbar_context_menu.add_command(label="添加快捷按钮...", command=self._show_add_button_dialog)
            self._toolbar_context_menu.add_separator()
            
            # 添加快捷按钮配置子菜单
            self._button_config_menu = tk.Menu(self._toolbar_context_menu, tearoff=0)
            self._toolbar_context_menu.add_cascade(label="配置快捷按钮", menu=self._button_config_menu)
            
            # 添加快捷按钮子菜单项
            self._refresh_button_config_menu()
        
        def show_context_menu(event):
            # 每次显示菜单前刷新按钮列表
            self._refresh_button_config_menu()
            self._toolbar_context_menu.post(event.x_root, event.y_root)
        
        # 绑定到父组件及其所有子组件
        parent.bind('<Button-3>', show_context_menu)
        
        # 递归绑定到所有子组件
        def bind_to_all_children(widget):
            try:
                widget.bind('<Button-3>', show_context_menu)
                for child in widget.winfo_children():
                    bind_to_all_children(child)
            except tk.TclError:
                # 某些组件可能不支持绑定
                pass
        
        bind_to_all_children(parent)
        
        # 返回绑定函数，供后续创建的按钮使用
        return show_context_menu
    
    def _refresh_button_config_menu(self):
        """
        刷新快捷按钮配置子菜单
        """
        # 清除现有菜单项
        if hasattr(self, '_button_config_menu'):
            self._button_config_menu.delete(0, tk.END)
            
            # 获取当前按钮配置
            buttons_config = self.config_manager.get_toolbar_buttons()
            
            # 为每个按钮添加菜单项
            for i, button_config in enumerate(buttons_config, 1):
                button_text = button_config.get("text", f"按钮{i}")
                # 截断过长的文本
                display_text = button_text[:20] + "..." if len(button_text) > 20 else button_text
                self._button_config_menu.add_command(
                    label=f"{i}. {display_text}",
                    command=lambda idx=i-1: self._show_button_config_dialog(idx)
                )
            
            # 如果没有按钮，显示提示
            if not buttons_config:
                self._button_config_menu.add_command(label="(无快捷按钮)", state='disabled')
    
    def _show_buttons_per_row_dialog(self):
        """
        显示设置每行快捷按钮数的对话框
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("设置每行快捷按钮数")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 说明标签
        ttk.Label(dialog, text="请输入每行显示的快捷按钮数量 (1-50):", 
                  font=('Microsoft YaHei', 10)).pack(pady=15)
        
        # 输入框
        current_value = self.buttons_per_row
        entry_var = tk.StringVar(value=str(current_value))
        entry = ttk.Entry(dialog, textvariable=entry_var, width=10, justify='center')
        entry.pack(pady=5)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def on_ok():
            try:
                value = int(entry_var.get())
                if 1 <= value <= 50:
                    # 保存配置
                    toolbar_config = self.config_manager.get_toolbar_config()
                    toolbar_config["buttons_per_row"] = value
                    self.config_manager.set_toolbar_config(toolbar_config)
                    
                    # 更新当前值
                    self.buttons_per_row = value
                    
                    # 即时更新界面
                    buttons_config = self.config_manager.get_toolbar_buttons()
                    self._create_toolbar_buttons(buttons_config)
                    
                    logger.info(f"更新每行快捷按钮数为: {value}")
                    dialog.destroy()
                else:
                    tk.messagebox.showwarning("输入错误", "请输入1-50之间的数字", parent=dialog)
            except ValueError:
                tk.messagebox.showwarning("输入错误", "请输入有效的数字", parent=dialog)
        
        def on_cancel():
            dialog.destroy()
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="确定", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def _show_button_config_dialog(self, button_index: int):
        """
        显示单个快捷按钮配置对话框
        :param button_index: 按钮索引
        """
        # 获取当前按钮配置
        buttons_config = self.config_manager.get_toolbar_buttons()
        
        if button_index < 0 or button_index >= len(buttons_config):
            tk.messagebox.showerror("错误", "按钮索引无效")
            return
        
        button_config = buttons_config[button_index]
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(f"配置快捷按钮 #{button_index + 1}")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标选择
        ttk.Label(main_frame, text="选择图标:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        
        # 图标选项
        icon_options = [
            ("📄 文档", "📄"),
            ("📏 文件大小", "📏"),
            ("🎬 视频", "🎬"),
            ("🖼 图片", "🖼"),
            ("🎵 音频", "🎵"),
            ("📦 压缩包", "📦"),
            ("⚙ 程序", "⚙"),
            ("📁 文件夹", "📁"),
            ("🕐 时间", "🕐"),
            ("📥 下载", "📥"),
            ("📋 列表", "📋"),
            ("🔍 搜索", "🔍"),
            ("⭐ 收藏", "⭐"),
            ("💼 工作", "💼"),
            ("🏠 主页", "🏠"),
            ("📊 图表", "📊"),
            ("📝 笔记", "📝"),
            ("🔧 工具", "🔧"),
            ("🎮 游戏", "🎮"),
            ("💾 保存", "💾"),
        ]
        
        # 尝试从当前配置中解析图标和文本
        current_text = button_config.get("text", "")
        current_icon = icon_options[0][1]  # 默认图标
        current_display_text = current_text
        
        # 查找当前使用的图标（必须在开头）
        for display, icon in icon_options:
            if current_text.startswith(icon):
                current_icon = icon
                # 移除图标部分，保留剩余文本
                current_display_text = current_text[len(icon):].strip()
                break
        
        # 找到当前图标对应的显示文本
        current_icon_display = icon_options[0][0]
        for display, icon in icon_options:
            if icon == current_icon:
                current_icon_display = display
                break
        
        icon_var = tk.StringVar(value=current_icon_display)
        
        icon_combo = ttk.Combobox(main_frame, textvariable=icon_var, values=[opt[0] for opt in icon_options], state='readonly', width=40)
        icon_combo.pack(fill=tk.X, pady=(0, 15))
        
        # 显示文本（不包含图标）
        ttk.Label(main_frame, text="显示文本:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        text_var = tk.StringVar(value=current_display_text)
        text_entry = ttk.Entry(main_frame, textvariable=text_var, font=('Microsoft YaHei', 10), width=40)
        text_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 搜索字符串
        ttk.Label(main_frame, text="搜索字符串:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        query_var = tk.StringVar(value=button_config.get("search_query", ""))
        query_entry = ttk.Entry(main_frame, textvariable=query_var, font=('Microsoft YaHei', 10), width=40)
        query_entry.pack(fill=tk.X, pady=(0, 20))
        
        def on_ok():
            try:
                # 获取选中的图标
                selected_icon_display = icon_combo.get()
                selected_icon = next((opt[1] for opt in icon_options if opt[0] == selected_icon_display), "📄")
                
                # 构建显示文本
                display_text = text_var.get().strip()
                if display_text:
                    full_text = f"{selected_icon} {display_text}"
                else:
                    full_text = selected_icon_display
                
                # 更新按钮配置
                buttons_config[button_index]["text"] = full_text
                buttons_config[button_index]["search_query"] = query_var.get().strip()
                
                # 保存配置
                self.config_manager.set_toolbar_buttons(buttons_config)
                
                # 即时更新界面
                self._create_toolbar_buttons(buttons_config)
                
                logger.info(f"更新快捷按钮 #{button_index + 1} 配置: {full_text}")
                dialog.destroy()
            except Exception as e:
                logger.error(f"保存快捷按钮配置时出错: {e}")
                tk.messagebox.showerror("错误", f"保存配置时出错: {e}", parent=dialog)
        
        def on_delete():
            """删除当前快捷按钮"""
            # 确认删除
            result = tk.messagebox.askyesno(
                "确认删除",
                f"确定要删除快捷按钮 \"#{button_index + 1} {button_config.get('text', '')}\" 吗？\n\n" +
                "删除后无法恢复，其他按钮的编号会自动更新。",
                icon='warning',
                parent=dialog
            )
            
            if result:
                try:
                    # 删除当前按钮
                    deleted_button = buttons_config.pop(button_index)
                    
                    # 保存配置
                    self.config_manager.set_toolbar_buttons(buttons_config)
                    
                    # 即时更新界面
                    self._create_toolbar_buttons(buttons_config)
                    
                    logger.info(f"删除快捷按钮 #{button_index + 1}: {deleted_button.get('text', '')}")
                    dialog.destroy()
                    
                    # 显示成功提示
                    tk.messagebox.showinfo("删除成功", "快捷按钮已成功删除！", parent=self.root)
                except Exception as e:
                    logger.error(f"删除快捷按钮时出错: {e}")
                    tk.messagebox.showerror("错误", f"删除失败: {str(e)}", parent=dialog)
        
        def on_cancel():
            dialog.destroy()
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=on_ok, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=on_delete, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel, width=12).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def _show_add_button_dialog(self):
        """
        显示添加快捷按钮对话框
        """
        # 检查是否已达到上限
        buttons_config = self.config_manager.get_toolbar_buttons()
        if len(buttons_config) >= 50:
            messagebox.showwarning(
                "添加快捷按钮",
                "快捷按钮数量已达到上限（50个），无法继续添加。\n\n" +
                "请先删除一些按钮后再添加新的。",
                parent=self.root
            )
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加快捷按钮")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标选择
        ttk.Label(main_frame, text="选择图标:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        
        # 图标选项
        icon_options = [
            ("📄 文档", "📄"),
            ("📏 文件大小", "📏"),
            ("🎬 视频", "🎬"),
            ("🖼 图片", "🖼"),
            ("🎵 音频", "🎵"),
            ("📦 压缩包", "📦"),
            ("⚙ 程序", "⚙"),
            ("📁 文件夹", "📁"),
            ("🕐 时间", "🕐"),
            ("📥 下载", "📥"),
            ("📋 列表", "📋"),
            ("🔍 搜索", "🔍"),
            ("⭐ 收藏", "⭐"),
            ("💼 工作", "💼"),
            ("🏠 主页", "🏠"),
            ("📊 图表", "📊"),
            ("📝 笔记", "📝"),
            ("🔧 工具", "🔧"),
            ("🎮 游戏", "🎮"),
            ("💾 保存", "💾"),
        ]
        
        icon_var = tk.StringVar(value=icon_options[0][0])
        icon_combo = ttk.Combobox(main_frame, textvariable=icon_var, values=[opt[0] for opt in icon_options], state='readonly', width=40)
        icon_combo.pack(fill=tk.X, pady=(0, 15))
        
        # 显示文本
        ttk.Label(main_frame, text="显示文本:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        text_var = tk.StringVar(value="")
        text_entry = ttk.Entry(main_frame, textvariable=text_var, font=('Microsoft YaHei', 10), width=40)
        text_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 搜索字符串
        ttk.Label(main_frame, text="搜索字符串:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        query_var = tk.StringVar(value="")
        query_entry = ttk.Entry(main_frame, textvariable=query_var, font=('Microsoft YaHei', 10), width=40)
        query_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 插入位置选择
        ttk.Label(main_frame, text="插入位置:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        
        position_options = ["添加到末尾"]
        for i, btn in enumerate(buttons_config, 1):
            btn_text = btn.get("text", f"按钮{i}")
            display_text = btn_text[:15] + "..." if len(btn_text) > 15 else btn_text
            position_options.append(f"在 [{i}. {display_text}] 之前")
        
        position_var = tk.StringVar(value=position_options[0])
        position_combo = ttk.Combobox(main_frame, textvariable=position_var, values=position_options, state='readonly', width=40)
        position_combo.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮颜色选择
        ttk.Label(main_frame, text="按钮颜色:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        
        color_options = [
            ("绿色", "#4CAF50", "#388E3C"),
            ("蓝色", "#2196F3", "#1976D2"),
            ("橙色", "#FF9800", "#F57C00"),
            ("紫色", "#9C27B0", "#7B1FA2"),
            ("蓝灰色", "#607D8B", "#455A64"),
            ("棕色", "#795548", "#5D4037"),
            ("红色", "#F44336", "#D32F2F"),
            ("深紫色", "#673AB7", "#512DA8"),
        ]
        
        color_var = tk.StringVar(value=color_options[0][0])
        color_combo = ttk.Combobox(main_frame, textvariable=color_var, values=[opt[0] for opt in color_options], state='readonly', width=40)
        color_combo.pack(fill=tk.X, pady=(0, 20))
        
        def on_ok():
            try:
                # 获取选中的图标
                selected_icon_display = icon_combo.get()
                selected_icon = next((opt[1] for opt in icon_options if opt[0] == selected_icon_display), "📄")
                
                # 构建显示文本
                display_text = text_var.get().strip()
                if not display_text:
                    messagebox.showwarning("输入错误", "请输入显示文本", parent=dialog)
                    return
                
                full_text = f"{selected_icon} {display_text}"
                
                # 获取搜索字符串
                search_query = query_var.get().strip()
                if not search_query:
                    messagebox.showwarning("输入错误", "请输入搜索字符串", parent=dialog)
                    return
                
                # 获取选中的颜色
                selected_color_name = color_combo.get()
                color_info = next((opt for opt in color_options if opt[0] == selected_color_name), color_options[0])
                bg_color = color_info[1]
                hover_color = color_info[2]
                
                # 获取插入位置
                position_text = position_var.get()
                insert_index = len(buttons_config)  # 默认添加到末尾
                
                if position_text != "添加到末尾":
                    # 解析位置（格式："在 [1. xxx] 之前"）
                    try:
                        # 提取序号
                        import re
                        match = re.search(r'\[(\d+)\.', position_text)
                        if match:
                            insert_index = int(match.group(1)) - 1
                    except:
                        pass
                
                # 创建新按钮配置
                new_button = {
                    "text": full_text,
                    "search_query": search_query,
                    "bg_color": bg_color,
                    "text_color": "white",
                    "hover_color": hover_color
                }
                
                # 插入到指定位置
                buttons_config.insert(insert_index, new_button)
                
                # 保存配置
                self.config_manager.set_toolbar_buttons(buttons_config)
                
                # 即时更新界面
                self._create_toolbar_buttons(buttons_config)
                
                logger.info(f"添加新快捷按钮: {full_text} 在位置 {insert_index + 1}")
                dialog.destroy()
                
                # 显示成功提示
                messagebox.showinfo("添加成功", f"快捷按钮 \"{full_text}\" 已成功添加！", parent=self.root)
                
            except Exception as e:
                logger.error(f"添加快捷按钮时出错: {e}")
                messagebox.showerror("错误", f"添加失败: {str(e)}", parent=dialog)
        
        def on_cancel():
            dialog.destroy()
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=on_ok, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel, width=12).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def _lighten_color(self, color, factor=0.1):
        """
        使颜色变亮
        :param color: 颜色代码
        :param factor: 变亮因子
        :return: 变亮后的颜色
        """
        try:
            color = color.lstrip('#')
            r = int(color[:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color
    
    def _create_search_area(self):
        """
        创建搜索区域 - 优化布局
        """
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Microsoft YaHei', 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.focus()
        
        # 添加搜索语法提示
        self.search_entry.insert(0, "输入关键词搜索...")
        self.search_entry.config(foreground='gray')
        
        def on_entry_click(event):
            if self.search_entry.get() == "输入关键词搜索...":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, "输入关键词搜索...")
                self.search_entry.config(foreground='gray')
        
        self.search_entry.bind('<FocusIn>', on_entry_click)
        self.search_entry.bind('<FocusOut>', on_focus_out)
        
        # 搜索按钮 - 使用更醒目的样式
        self.search_button = tk.Button(
            search_frame,
            text="🔍 搜索",
            font=('Microsoft YaHei', 10, 'bold'),
            bg='#ff6b6b', fg='white',
            activebackground='#ff5252', activeforeground='white',
            relief='flat', cursor='hand2',
            padx=15, pady=5,
            command=self._search_from_entry
        )
        self.search_button.pack(side=tk.LEFT, padx=5)
        self.search_button.bind('<Enter>', lambda e: self.search_button.config(bg='#ff7b7b'))
        self.search_button.bind('<Leave>', lambda e: self.search_button.config(bg='#ff6b6b'))
        
        # 清空按钮
        clear_btn = tk.Button(
            search_frame,
            text="清空",
            font=('Microsoft YaHei', 9),
            bg='#95a5a6', fg='white',
            activebackground='#7f8c8d', activeforeground='white',
            relief='flat', cursor='hand2',
            padx=10, pady=5,
            command=self._clear_search
        )
        clear_btn.pack(side=tk.LEFT)
        clear_btn.bind('<Enter>', lambda e: clear_btn.config(bg='#a5b5b6'))
        clear_btn.bind('<Leave>', lambda e: clear_btn.config(bg='#95a5a6'))
    
    def _create_result_area(self):
        """
        创建结果显示区域 - 优化布局
        """
        result_frame = ttk.Frame(self.main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        
        # 创建Treeview
        columns = ('name', 'path', 'size', 'date')
        self.tree = ttk.Treeview(
            result_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # 设置列标题
        self._update_column_headers()
        
        # 从配置加载列宽
        self.column_widths = self.config_manager.get_column_widths()
        self.tree.column('name', width=self.column_widths.get('name', 250), anchor='w')
        self.tree.column('path', width=self.column_widths.get('path', 550), anchor='w')
        self.tree.column('size', width=self.column_widths.get('size', 100), anchor='e')
        self.tree.column('date', width=self.column_widths.get('date', 150), anchor='center')
        
        # 绑定列宽调整事件
        self.tree.bind('<ButtonRelease-1>', self._on_column_resize)
        
        # 绑定标题栏点击事件
        self.tree.heading('name', command=lambda: self._on_header_click('name'))
        self.tree.heading('path', command=lambda: self._on_header_click('path'))
        self.tree.heading('size', command=lambda: self._on_header_click('size'))
        self.tree.heading('date', command=lambda: self._on_header_click('date'))
        
        # 创建滚动条
        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self._open_selected_item)
        
        # 绑定右键菜单
        self.tree.bind('<Button-3>', self._show_context_menu)
    
    def _on_column_resize(self, event):
        """
        列宽调整时的回调 - 保存列宽到配置
        """
        # 检查是否是列标题区域（通过y坐标判断）
        if event.y < 25:  # 列标题区域的高度
            # 延迟保存，避免频繁写入
            if hasattr(self, '_save_column_widths_id'):
                self.root.after_cancel(self._save_column_widths_id)
            self._save_column_widths_id = self.root.after(500, self._save_column_widths)
    
    def _save_column_widths(self):
        """
        保存当前列宽到配置文件
        """
        try:
            # 获取当前列宽
            current_widths = {
                'name': self.tree.column('name', 'width'),
                'path': self.tree.column('path', 'width'),
                'size': self.tree.column('size', 'width'),
                'date': self.tree.column('date', 'width')
            }
            # 保存到配置
            self.config_manager.set_column_widths(current_widths)
            logger.info(f"保存列宽配置: {current_widths}")
        except Exception as e:
            logger.error(f"保存列宽时出错: {e}")
    
    def _create_status_bar(self):
        """
        创建状态栏 - 显示所有状态信息
        """
        status_frame = ttk.Frame(self.main_frame, relief='sunken', padding=2)
        status_frame.pack(fill=tk.X, pady=(3, 0))
        
        # 状态标签 - 显示操作状态
        tips = self.config_manager.config.get('tips', '就绪 - 点击列标题可排序')
        self.status_var = tk.StringVar(value=tips)
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Microsoft YaHei', 9),
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Everything状态 - 显示在右侧
        self.everything_status_var = tk.StringVar(value="正在检测...")
        self.everything_status_label = ttk.Label(
            status_frame,
            textvariable=self.everything_status_var,
            font=('Microsoft YaHei', 9)
        )
        self.everything_status_label.pack(side=tk.RIGHT, padx=10)
        
        # 搜索进度条
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=100)
        self.progress.pack(side=tk.RIGHT, padx=5)
    
    def _perform_search(self, query: str):
        """
        执行搜索
        :param query: 搜索查询
        """
        try:
            # 禁用搜索按钮并显示进度条
            self.search_button.config(state='disabled')
            self.progress.start()
            self.status_var.set(f"正在搜索: {query} ({self._get_sort_desc()})...")
            self.root.update()
            
            # 执行搜索
            logger.info(f"执行搜索: {query}，排序方式: {self._get_sort_desc()}")
            results = self.sdk_adapter.search(query, self.sort_by, self.sort_ascending)
            
            # 显示结果
            self._display_results(results)
            
            display_count = len(results)
            folder_count = sum(1 for r in results if r['is_folder'])
            file_count = display_count - folder_count
            
            status_message = f"找到 {display_count} 个结果 ({folder_count} 文件夹/{file_count} 文件) | {self._get_sort_desc()}"
            self.status_var.set(status_message)
            logger.info(status_message)
        except Exception as e:
            error_message = f"搜索时出错: {str(e)}"
            self.status_var.set(error_message)
            logger.error(error_message)
            self._display_results([])
        finally:
            # 恢复搜索按钮状态并隐藏进度条
            self.search_button.config(state='normal')
            self.progress.stop()
    
    def _set_search_query(self, query: str):
        """
        将搜索语法设置到文本框中（不执行搜索）
        :param query: 搜索查询字符串
        """
        # 清除占位符文本
        self.search_entry.delete(0, tk.END)
        self.search_entry.config(foreground='black')
        # 设置搜索语法
        self.search_var.set(query)
        # 更新状态栏提示
        self.status_var.set(f"已加载搜索语法: {query[:50]}{'...' if len(query) > 50 else ''} - 点击搜索按钮执行")
        logger.info(f"快捷按钮设置搜索语法: {query}")
        # 将焦点设置到搜索框，方便用户编辑
        self.search_entry.focus()
    
    def _search_from_entry(self):
        """
        从输入框执行搜索
        """
        query = self.search_var.get().strip()
        if query:
            self._perform_search(query)
    
    def _get_sort_desc(self):
        """
        获取当前排序的描述文字
        :return: 排序描述
        """
        sort_names = {
            'name': '文件名',
            'path': '路径',
            'size': '大小',
            'date': '修改时间'
        }
        direction = "升序" if self.sort_ascending else "降序"
        return f"{sort_names.get(self.sort_by, self.sort_by)} {direction}"
    
    def _update_column_headers(self):
        """
        更新列标题，显示当前排序指示器 ▲/▼
        """
        arrow = " ▲" if self.sort_ascending else " ▼"
        
        headers = {
            'name': '文件名',
            'path': '路径',
            'size': '大小',
            'date': '修改时间'
        }
        
        for col, text in headers.items():
            if col == self.sort_by:
                self.tree.heading(col, text=text + arrow)
            else:
                self.tree.heading(col, text=text)
    
    def _on_header_click(self, column):
        """
        点击列标题时的排序切换
        :param column: 列名
        """
        if self.sort_by == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_by = column
            self.sort_ascending = True
        
        self._update_column_headers()
        
        query = self.search_var.get().strip()
        if query:
            self._perform_search(query)
        else:
            self.status_var.set(f"排序已设置为: {self._get_sort_desc()}，请输入搜索关键词")
    
    def _clear_search(self):
        """
        清空搜索
        """
        self.search_var.set("")
        # 清空Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_results = []
        self.status_var.set("就绪")
    
    def _display_results(self, results: List[Dict[str, Any]]):
        """
        显示搜索结果
        :param results: 搜索结果列表
        """
        # 清空Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 保存当前结果
        self.current_results = results
        
        # 添加结果
        for item in results:
            # 格式化文件大小
            def format_file_size(size_bytes, is_folder=False):
                if is_folder:
                    return "文件夹"
                if size_bytes == 0:
                    return "0 B"
                elif size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024**2:
                    return f"{size_bytes/1024:.2f} KB"
                elif size_bytes < 1024**3:
                    return f"{size_bytes/1024**2:.2f} MB"
                else:
                    return f"{size_bytes/1024**3:.2f} GB"
            
            # 格式化修改时间
            date_modified = item.get('date_modified')
            date_str = date_modified.strftime('%Y-%m-%d %H:%M:%S') if date_modified else ""
            

            
            # 插入到Treeview
            self.tree.insert('', tk.END, values=(
                item['file_name'],
                item['dir_name'],
                format_file_size(item['file_size'], item['is_folder']),
                date_str
            ))
    
    def _open_selected_item(self, event):
        """
        打开选中的项目
        :param event: 事件对象
        """
        try:
            selection = self.tree.selection()
            if not selection:
                return
            idx = self.tree.index(selection[0])
            if 0 <= idx < len(self.current_results):
                item = self.current_results[idx]
                self._open_item(item)
        except Exception:
            pass
    
    def _open_item(self, item):
        """
        打开项目
        :param item: 项目信息
        """
        try:
            import os
            os.startfile(item['full_path_name'])
        except Exception:
            pass
    
    def _open_item_folder(self, item):
        """
        打开项目所在文件夹
        :param item: 项目信息
        """
        try:
            import os
            folder_path = item['dir_name']
            os.startfile(folder_path)
        except Exception:
            pass
    
    def _copy_item_path(self, item):
        """
        复制项目路径到剪贴板
        :param item: 项目信息
        """
        try:
            import tkinter as tk
            path = item['full_path_name']
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.status_var.set(f"已复制路径到剪贴板: {path}")
        except Exception:
            pass
    
    def _refresh_search(self):
        """
        刷新搜索
        """
        query = self.search_var.get().strip()
        if query:
            self._perform_search(query)
        else:
            self.status_var.set("请输入搜索关键词")
    
    def _update_everything_status(self):
        """
        更新Everything状态信息 - 在状态栏显示
        如果Everything未运行但能找到安装路径，询问用户是否启动
        """
        try:
            is_running = self.sdk_adapter.is_everything_running()
            
            if is_running:
                # 使用实际通信成功的版本，而不是进程检测版本
                comm_version = self.sdk_adapter.get_communication_version()
                if comm_version:
                    status_text = f"{chr(0x2705)} Everything {comm_version} 运行中"
                else:
                    status_text = f"{chr(0x2705)} Everything 运行中"
                # 同时更新主状态栏
                self.status_var.set(f"已连接 Everything - 可以开始搜索")
                self.everything_status_var.set(status_text)
                # 日志记录时移除 emoji 字符，避免编码问题
                log_status_text = status_text.replace(chr(0x2705), "[OK]")
                logger.info(f"Everything状态: {log_status_text}")
            else:
                # Everything未运行，检查是否可以启动
                exe_path = self.sdk_adapter.find_everything_exe()
                
                if exe_path:
                    # 找到可执行文件，询问用户是否启动
                    self._show_start_everything_dialog(exe_path)
                else:
                    # 未找到可执行文件
                    status_text = f"{chr(0x26A0)} Everything 未运行"
                    self.everything_status_var.set(status_text)
                    self.status_var.set("未找到 Everything，请手动启动 Everything 后再进行搜索")
                    logger.warning("未找到Everything可执行文件")
                
        except Exception as e:
            status_text = f"{chr(0x274C)} 状态检测失败"
            self.everything_status_var.set(status_text)
            self.status_var.set(f"状态检测出错: {str(e)[:50]}")
            logger.error(f"更新Everything状态时出错: {str(e)}")
    
    def _show_start_everything_dialog(self, exe_path: str):
        """
        显示是否启动Everything的确认对话框
        :param exe_path: Everything.exe的路径
        """
        from tkinter import messagebox
        
        # 更新状态栏提示
        self.everything_status_var.set("⚠️ Everything 未运行")
        self.status_var.set(f"检测到Everything: {exe_path}")
        
        # 显示确认对话框
        dialog_message = f"Everything 未运行，是否启动？\n\n路径: {exe_path}\n\n点击【是】启动 Everything\n点击【否】保持当前状态"
        result = messagebox.askyesno(
            "启动 Everything",
            dialog_message,
            icon='question'
        )
        
        if result:
            # 用户选择启动
            logger.info(f"用户选择启动Everything: {exe_path}")
            self.everything_status_var.set(f"{chr(0x1F680)} 正在启动 Everything...")
            self.status_var.set("正在启动 Everything，请稍候...")
            
            # 尝试启动
            if self.sdk_adapter.start_everything(exe_path):
                logger.info("Everything启动命令已发送")
                # 短暂延迟后将本应用恢复到前台
                self.root.after(500, self._bring_window_to_front)
                # 等待几秒后检查启动结果
                self.root.after(3000, self._check_everything_started)
            else:
                logger.error("启动Everything失败")
                self.everything_status_var.set(f"{chr(0x274C)} 启动Everything失败")
                self.status_var.set("启动 Everything 失败，请手动启动")
                messagebox.showerror("启动失败", "无法启动 Everything，请手动启动后再试。")
        else:
            # 用户选择不启动
            logger.info("用户选择不启动Everything")
            self.everything_status_var.set("⚠️ Everything 未运行")
            self.status_var.set("Everything 未运行 - 请手动启动后再进行搜索")
    
    def _check_everything_started(self):
        """
        检查Everything是否已成功启动
        """
        try:
            # 重新检测Everything状态
            is_running = self.sdk_adapter.is_everything_running()
            
            if is_running:
                # 使用实际通信成功的版本
                comm_version = self.sdk_adapter.get_communication_version()
                if comm_version:
                    status_text = f"{chr(0x2705)} Everything {comm_version} 运行中"
                else:
                    status_text = f"{chr(0x2705)} Everything 运行中"
                self.status_var.set(f"已连接 Everything - 可以开始搜索")
                logger.info("Everything已成功启动")
            else:
                status_text = "⚠️ Everything 启动中..."
                self.status_var.set("等待 Everything 启动完成...")
                # 继续等待
                self.root.after(2000, self._check_everything_started)
            
            self.everything_status_var.set(status_text)
        except Exception as e:
            logger.error(f"检查Everything启动状态时出错: {e}")
            self.everything_status_var.set(f"{chr(0x274C)} 启动检测失败")
            self.status_var.set(f"检测启动状态时出错: {str(e)[:50]}")
    
    def _bring_window_to_front(self):
        """
        将本应用窗口恢复到前台
        """
        try:
            # 使用Windows API将窗口置顶
            import ctypes
            from ctypes import wintypes
            
            # 获取窗口句柄
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            # 将窗口置顶
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            self.root.focus_force()
            
            # 使用Windows API强制激活窗口
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(self.root.winfo_id(), SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(self.root.winfo_id())
            
            logger.info("应用窗口已恢复到前台")
        except Exception as e:
            logger.warning(f"恢复窗口到前台失败: {e}")
            # 备用方案：使用Tkinter方法
            try:
                self.root.lift()
                self.root.focus_force()
            except:
                pass
    
    def _start_status_polling(self):
        """
        启动定期状态轮询
        每3秒检测一次Everything通信状态
        """
        self._poll_everything_status()
    
    def _poll_everything_status(self):
        """
        定期轮询Everything状态
        """
        try:
            # 检测当前通信状态
            can_communicate = self.sdk_adapter.is_everything_running()
            
            # 获取当前显示的状态
            current_status = self.everything_status_var.get()
            
            # 根据通信状态更新显示
            if can_communicate:
                # 可以通信，更新为运行中状态
                # 使用实际通信成功的版本
                comm_version = self.sdk_adapter.get_communication_version()
                if comm_version:
                    status_text = f"{chr(0x2705)} Everything {comm_version} 运行中"
                else:
                    status_text = f"{chr(0x2705)} Everything 运行中"
                
                # 只有在状态变化时才更新
                if "运行中" not in current_status:
                    self.everything_status_var.set(status_text)
                    self.status_var.set("已连接 Everything - 可以开始搜索")
                    # 日志记录时移除 emoji 字符，避免编码问题
                    log_status_text = status_text.replace(chr(0x2705), "[OK]")
                    logger.info(f"Everything状态更新: {log_status_text}")
            else:
                # 无法通信
                if "未运行" not in current_status and "启动" not in current_status:
                    status_text = f"{chr(0x26A0)} Everything 未运行"
                    self.everything_status_var.set(status_text)
                    self.status_var.set("Everything 通信中断 - 请检查Everything是否运行")
                    logger.warning("Everything通信检测失败")
            
            # 安排下一次检测（3秒后）
            self._status_polling_id = self.root.after(3000, self._poll_everything_status)
        except Exception as e:
            logger.error(f"定期状态检测出错: {e}")
            # 出错也继续轮询
            self._status_polling_id = self.root.after(3000, self._poll_everything_status)
    
    def _stop_status_polling(self):
        """
        停止定期状态轮询
        """
        if hasattr(self, '_status_polling_id'):
            self.root.after_cancel(self._status_polling_id)
    
    def _show_context_menu(self, event):
        """
        显示右键菜单
        :param event: 事件对象
        """
        try:
            # 选中右键点击的项目
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                
                # 获取选中的结果
                idx = self.tree.index(item)
                if 0 <= idx < len(self.current_results):
                    selected_item = self.current_results[idx]
                    
                    # 创建右键菜单
                    self.context_menu = tk.Menu(self.root, tearoff=0)
                    self.context_menu.add_command(label="打开", command=lambda: self._open_item(selected_item))
                    self.context_menu.add_command(label="打开所在文件夹", command=lambda: self._open_item_folder(selected_item))
                    self.context_menu.add_command(label="复制路径", command=lambda: self._copy_item_path(selected_item))
                    self.context_menu.add_separator()
                    self.context_menu.add_command(label="刷新", command=self._refresh_search)
                    
                    # 显示菜单
                    self.context_menu.post(event.x_root, event.y_root)
        except Exception:
            pass
    
    def update_status(self):
        """
        更新状态
        """
        self.everything_status_var.set(f"Everything状态: {'运行中' if self.sdk_adapter.is_everything_running() else '未运行'}")
