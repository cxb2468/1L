# -*- coding: utf-8 -*-
import os
os.environ["NUMEXPR_MAX_THREADS"] = "8"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
import wave
import threading
from datetime import datetime
from db_manager import DBManager
import json
import time
from v2v import SpeechRecognizer as AliyunRecognizer
from pystray import Icon, Menu, MenuItem
from PIL import Image
import pandas as pd
import keyboard
from config import Config
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class VoiceRecorder:
    def __init__(self):
        logging.info('初始化VoiceRecorder应用...')
        self.root = tk.Tk()
        self.root.title("闪念胶囊")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFFFFF")  # 使用纯白背景
        self.is_hidden = False  # 添加窗口状态跟踪变量
        logging.info('主窗口初始化完成')
        
        # 设置窗口样式
        self.root.tk_setPalette(background='#FFFFFF', foreground='#333333')
        
        # 创建主框架并添加内边距
        main_frame = tk.Frame(self.root, bg="#FFFFFF", padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建隐藏按钮
        hide_button = ttk.Button(
            self.root,
            text="—",
            style="TButton",
            cursor="hand2",
            command=self.hide_window
        )
        hide_button.place(relx=0.85, rely=0.02)
        
        # 初始化系统托盘图标
        self.setup_tray_icon()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定快捷键事件
        keyboard.on_press_key('F5', lambda e: self.toggle_window(None))
        # 注册全局F7快捷键
        keyboard.on_press_key('F7', self.toggle_recording)
        
        # 初始化音频系统
        try:
            self.player = pyaudio.PyAudio()
        except Exception as e:
            print(f"初始化音频系统时出错: {e}")
        
        # 设置录音参数
        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # 当前播放的音频
        self.current_playing = None
        
        # 初始化数据库管理器
        self.db_manager = DBManager()
        
        # 创建标题标签
        title_label = tk.Label(
            main_frame,
            text="闪念胶囊 ",
            font=("Microsoft YaHei UI Light", 28, "bold"),
            bg="#FFFFFF",
            fg="#1a73e8"
        )
        title_label.pack(pady=(0, 20))
        
        # 创建副标题标签
        subtitle_label = tk.Label(
            main_frame,
            text="一句话的事儿",
            font=("Microsoft YaHei UI Light", 13, "bold"),
            bg="#FFFFFF",
            fg="#1a73e8"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # 创建语音识别方案选择框架
        recognition_frame = tk.Frame(main_frame, bg="#F5F5F5", padx=15, pady=10)
        recognition_frame.pack(pady=15)
        
        # 创建录音按钮
        record_button = ttk.Button(
            recognition_frame,
            text="按住录音",
            style="TButton",
            cursor="hand2"
        )
        record_button.pack(side=tk.LEFT, padx=20)

        # 绑定录音按钮事件
        record_button.bind('<ButtonPress-1>', self.start_recording)
        record_button.bind('<ButtonRelease-1>', self.stop_recording)
        
        # 录音状态变量
        self.recording_thread = None
        self.stop_recording_event = None

        # 创建标签
        ###ttk.Label(
        ##    recognition_frame,
        #    text="音频文件:",
        #    style="TLabel"
        #).pack(side=tk.LEFT, padx=5)###
        
        # 创建浏览音频文件按钮
        browse_button = ttk.Button(
            recognition_frame,
            text="音频转文字",
            style="TButton",
            cursor="hand2",
            command=self.browse_audio_file
        )
        browse_button.pack(side=tk.LEFT, padx=20)

        # 创建导出按钮
        export_button = ttk.Button(
            recognition_frame,
            text="导出表格",
            style="TButton",
            cursor="hand2",
            command=self.export_to_excel
        )
        export_button.pack(side=tk.LEFT, padx=20)

        # 创建表格区域
        table_frame = tk.Frame(main_frame, bg="#F5F5F5", padx=15, pady=15)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        # 创建帮助按钮
        help_button = ttk.Button(
            recognition_frame,
            text="帮助",
            style="TButton",
            cursor="hand2",
            command=self.show_help
        )
        help_button.pack(side=tk.LEFT, padx=20)

        # 创建设置按钮
        settings_button = ttk.Button(
            recognition_frame,
            text="设置",
            style="TButton",
            cursor="hand2",
            command=self.show_settings
        )
        settings_button.pack(side=tk.LEFT, padx=20)

        # 创建Treeview控件
        columns = ("id", "play", "text_content", "created_time", "operation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10, selectmode="extended")

        # 设置列标题
        self.tree.heading("id", text="ID")
        self.tree.heading("play", text="播放")
        self.tree.heading("text_content", text="识别内容")
        self.tree.heading("created_time", text="创建时间")
        self.tree.heading("operation", text="操作")

        # 设置列宽
        self.tree.column("id", width=30)
        self.tree.column("play", width=30)
        self.tree.column("text_content", width=350)
        self.tree.column("created_time", width=150)
        self.tree.column("operation", width=30)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定表格点击事件和键盘事件
        self.tree.bind('<ButtonRelease-1>', self.on_tree_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Delete>', self.delete_selected_items)

        # 加载录音记录
        self.load_recordings()

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 获取点击位置的item
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # 选中被点击的行
            self.tree.selection_set(item)
            # 创建右键菜单
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="播放", command=lambda: self.play_selected_audio(item))
            menu.add_command(label="复制文字", command=lambda: self.copy_text_content(item))
            menu.add_command(label="删除", command=lambda: self.delete_selected_item(item))
            # 显示菜单
            menu.post(event.x_root, event.y_root)

    def play_selected_audio(self, item):
        """播放选中的音频"""
        values = self.tree.item(item)["values"]
        if len(values) >= 2:
            file_path = values[0]  # 获取第一列的ID
            recordings = self.db_manager.get_all_recordings()
            for recording in recordings:
                if recording[0] == file_path:  # 匹配ID
                    self.play_audio(recording[1])  # 使用对应的文件路径
                    break

    def copy_text_content(self, item):
        """复制文字内容到剪贴板"""
        values = self.tree.item(item)["values"]
        if len(values) >= 3:
            text_content = values[2]  # 获取第三列的文字内容
            self.root.clipboard_clear()
            self.root.clipboard_append(text_content)
            self.root.update()

    def delete_selected_item(self, item):
        """删除选中的记录"""
        values = self.tree.item(item)["values"]
        if len(values) >= 1:
            recording_id = values[0]  # 获取记录ID
            if self.db_manager.delete_recording(recording_id):
                self.load_recordings()  # 刷新显示

    def on_tree_click(self, event):
        """处理表格点击事件"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            selection = self.tree.selection()
            if not selection:  # 检查是否有选中的项
                return
            item = selection[0]
            if str(column) == "#2":  # 点击播放列
                self.play_selected_audio(item)
            elif str(column) == "#5":  # 点击删除列
                if messagebox.askyesno("确认删除", "确定要删除这条记录吗？"):
                    self.delete_selected_item(item)

    def play_audio(self, file_path):
        """播放音频文件"""
        try:
            if self.current_playing:
                self.stop_playing()
            
            if os.path.exists(file_path):
                wf = wave.open(file_path, 'rb')
                self.current_playing = self.player.open(
                    format=self.player.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # 在新线程中播放音频
                def play_stream():
                    data = wf.readframes(self.CHUNK)
                    while data and self.current_playing:
                        self.current_playing.write(data)
                        data = wf.readframes(self.CHUNK)
                    wf.close()
                    if self.current_playing:
                        self.current_playing.stop_stream()
                        self.current_playing.close()
                        self.current_playing = None
                
                threading.Thread(target=play_stream, daemon=True).start()
            else:
                print(f"音频文件不存在: {file_path}")
        except Exception as e:
            print(f"播放音频时出错: {e}")

    def hide_window(self):
        """隐藏主窗口"""
        self.root.withdraw()

    def setup_tray_icon(self):
        """设置系统托盘图标"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_icon.png")
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                self.tray_icon = Icon(
                    "闪念胶囊",
                    image,
                    menu=Menu(
                        MenuItem("显示", lambda: self.root.deiconify()),
                        MenuItem("退出", lambda: self.on_closing())
                    )
                )
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            else:
                print(f"找不到图标文件: {icon_path}")
        except Exception as e:
            print(f"初始化系统托盘图标时出错: {e}")

    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
            if hasattr(self, 'audio'):
                self.audio.terminate()
            if hasattr(self, 'stream') and self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.root.quit()
        except Exception as e:
            print(f"关闭程序时出错: {e}")
            self.root.destroy()

    def run(self):
        """运行应用程序"""
        self.root.mainloop()

    def load_recordings(self):
        """加载录音记录到表格"""
        # 清空现有记录
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 从数据库获取记录
        recordings = self.db_manager.get_all_recordings()
        for recording in recordings:
            # 创建一个包含播放按钮和删除按钮的记录
            values = list(recording)
            values[1] = "▶"  # 使用Unicode字符作为播放按钮
            values.append("✕")  # 使用Unicode字符作为删除按钮
            self.tree.insert("", tk.END, values=values)
            
        # 设置播放列和操作列的样式
        style = ttk.Style()
        style.configure("Treeview", font=("Microsoft YaHei", 11))
        self.tree.tag_configure("center", anchor="center")
        for item in self.tree.get_children():
            self.tree.set(item, "play", "▶")
            self.tree.set(item, "operation", "✕")
            self.tree.item(item, tags=("center",))

    def toggle_recording(self, event):
        """切换录音状态"""
        if not hasattr(self, '_last_toggle_time'):
            self._last_toggle_time = 0
        
        # 防止重复触发，设置最小间隔时间（500毫秒）
        current_time = time.time()
        if current_time - self._last_toggle_time < 0.5:
            return
        
        self._last_toggle_time = current_time
        
        if self.is_recording:
            self.stop_recording(event)
        else:
            # 更新录音按钮状态
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for btn in child.winfo_children():
                                if isinstance(btn, ttk.Button) and btn.cget('text') == '按住录音':
                                    btn.configure(style='Recording.TButton')
                                    btn.configure(text='录音中...')
                                    break
            self.start_recording(event)

    def start_recording(self, event):
        """开始录音"""
        if self.is_recording:
            logging.warning('录音已在进行中，忽略重复的开始录音请求')
            return
        
        logging.info('开始录音...')
        
        self.is_recording = True
        self.frames = []
        self.stop_recording_event = threading.Event()
        
        # 更新录音按钮状态
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button) and btn.cget('text') == '按住录音':
                                btn.configure(style='Recording.TButton')
                                btn.configure(text='录音中...')
                                break
        
        # 生成录音文件名
        timestamp = int(time.time())
        self.current_recording_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "recordings",
            f"recording_{timestamp}.wav"
        )
        
        # 确保recordings目录存在
        os.makedirs(os.path.dirname(self.current_recording_file), exist_ok=True)
        
        # 开始录音线程
        self.recording_thread = threading.Thread(
            target=self.record_audio,
            args=(self.current_recording_file, self.stop_recording_event)
        )
        self.recording_thread.start()

    def stop_recording(self, event):
        """停止录音"""
        if not self.is_recording:
            logging.warning('当前没有进行中的录音，忽略停止录音请求')
            return
        
        logging.info('停止录音并开始处理...')
        
        self.stop_recording_event.set()
        if self.recording_thread:
            self.recording_thread.join()
        
        self.is_recording = False
        
        # 恢复录音按钮状态
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button) and btn.cget('text') == '录音中...':
                                btn.configure(style='TButton')
                                btn.configure(text='按住录音')
                                break
        
        # 进行语音识别
        text_content = self.perform_speech_recognition()
        logging.info(f'语音识别结果: {text_content}')
        
        if text_content:  # 只有在有识别结果时才保存和更新界面
            # 保存到数据库
            self.db_manager.add_recording(self.current_recording_file, text_content)
            # 刷新显示
            self.load_recordings()
            # 确保界面更新
            self.root.update_idletasks()
        else:
            logging.warning('未获取到有效的语音识别结果')

    def record_audio(self, filename, stop_event):
        """录音过程"""
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        while not stop_event.is_set():
            try:
                data = stream.read(self.CHUNK)
                self.frames.append(data)
            except Exception as e:
                print(f"录音过程出错: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        
        # 保存录音文件
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))

    def perform_speech_recognition(self):
        """执行语音识别"""
        try:
            # 使用阿里云识别
            recognizer = AliyunRecognizer()
            return recognizer.recognize(self.current_recording_file)
        except Exception as e:
            print(f"语音识别出错: {e}")
            return ""

    def toggle_window(self, event=None):
        """切换窗口显示状态"""
        if self.is_hidden:
            self.show_window()
        else:
            self.hide_window()

    def hide_window(self):
        """隐藏主窗口"""
        self.root.withdraw()
        self.is_hidden = True

    def show_window(self):
        """显示并激活窗口"""
        self.root.deiconify()
        self.root.update_idletasks()  # 强制更新窗口状态
        self.root.lift()             # 确保窗口置顶
        self.root.focus_force()      # 强制获取焦点
        # 短暂置顶确保窗口可见（解决被其他窗口遮挡问题）
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.is_hidden = False

    def export_to_excel(self):
        """导出录音记录到Excel文件"""
        try:
            # 获取保存文件路径
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[("Excel files", "*.xlsx")],
                title="保存Excel文件"
            )
            
            if not file_path:
                return
            
            # 获取所有录音记录
            recordings = self.db_manager.get_all_recordings()
            
            # 创建DataFrame
            df = pd.DataFrame(
                recordings,
                columns=['ID', '文件路径', '识别内容', '创建时间']
            )
            
            # 保存为Excel文件
            df.to_excel(file_path, index=False)
            
            messagebox.showinfo("导出成功", f"数据已成功导出到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("导出失败", f"导出过程中出错：\n{str(e)}")

    def browse_audio_file(self):
        """浏览并处理音频文件"""
        try:
            file_path = filedialog.askopenfilename(
                title="选择音频文件",
                filetypes=[("WAV文件", "*.wav")]
            )
            
            if file_path:
                try:
                    # 初始化阿里云语音识别器
                    recognizer = AliyunRecognizer()
                    # 识别音频文件
                    text_content = recognizer.recognize(file_path)
                    
                    if text_content:
                        # 将文件复制到recordings目录
                        filename = os.path.basename(file_path)
                        new_path = os.path.join('recordings', filename)
                        os.makedirs('recordings', exist_ok=True)
                        
                        if file_path != new_path:
                            import shutil
                            shutil.copy2(file_path, new_path)
                        
                        # 保存到数据库
                        self.db_manager.add_recording(new_path, text_content)
                        # 刷新显示
                        self.load_recordings()
                        messagebox.showinfo("成功", "音频文件处理完成")
                    else:
                        messagebox.showwarning("警告", "未能识别出文字内容")
                except Exception as e:
                    messagebox.showerror("错误", f"处理音频文件时出错：{str(e)}")
                    logging.error(f"处理音频文件时出错: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"选择文件时出错：{str(e)}")
            logging.error(f"选择文件时出错: {str(e)}")

    def delete_selected_items(self, event):
        """删除选中的多条记录"""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的记录吗？"):
            for item in selection:
                values = self.tree.item(item)["values"]
                if len(values) >= 1:
                    recording_id = values[0]  # 获取记录ID
                    self.db_manager.delete_recording(recording_id)
            self.load_recordings()  # 刷新显示

    def show_help(self):
        """显示使用说明对话框"""
        help_text = """
闪念胶囊使用说明：

版本信息：
- 版本号：v1.2.0
- 更新日期：2025-03-7
- 开发者：hfol85 @吾爱破解论坛

1. 快捷键功能：
   - F7：快速开始/停止录音
   - Ctrl+F5：显示/隐藏主窗口

2. 录音操作：
   - 点击或按住"按住录音"按钮开始录音
   - 松开按钮或再次点击停止录音
   - 录音过程中按钮变红显示"录音中..."

3. 语音识别方案：
   - 阿里云：在线语音识别（需配置密钥）
   - DeepSeek：文本优化和纠错

4. 表格操作：
   - 点击"▶"播放录音
   - 点击"✕"删除记录
   - 右键点击记录可显示更多操作：
     * 播放
     * 复制文字
     * 删除

5. 其他功能：
   - 点击"音频转文字"可导入音频文件进行识别
   - 点击"导出表格"可将记录导出为Excel文件
   - 点击"—"最小化到系统托盘
   - 系统托盘图标右键可显示/退出程序

注意：首次使用需在设置中配置阿里云API和DeepSeek API密钥。
        """
        
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("使用说明")
        help_dialog.geometry("600x700")
        help_dialog.configure(bg="#F5F5F5")
        
        # 创建文本框
        text_widget = tk.Text(
            help_dialog,
            font=("Microsoft YaHei", 12),
            bg="#F5F5F5",
            fg="#333333",
            padx=20,
            pady=20,
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 插入帮助文本
        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(help_dialog, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设置对话框模态
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # 使对话框居中显示
        help_dialog.update_idletasks()
        width = help_dialog.winfo_width()
        height = help_dialog.winfo_height()
        x = (help_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (height // 2)
        help_dialog.geometry(f"{width}x{height}+{x}+{y}")

        # 设置Treeview样式
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#333333",
            fieldbackground="#FFFFFF",
            font=("Microsoft YaHei UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#F8F9FA",
            foreground="#1a73e8",
            font=("Microsoft YaHei UI", 10, "bold")
        )
        style.map(
            "Treeview",
            background=[('selected', '#E8F0FE')],
            foreground=[('selected', '#1a73e8')]
        )

    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("400x400")
        settings_window.resizable(False, False)
        
        # 设置模态窗口
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 创建设置框架
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 从配置文件加载当前设置
        from config import Config
        config = Config()
        aliyun_settings = config.aliyun_config
        
        # 创建标签页
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 阿里云设置页
        aliyun_frame = ttk.Frame(notebook, padding="10")
        notebook.add(aliyun_frame, text="阿里云API设置")
        
        # 阿里云API设置
        ttk.Label(aliyun_frame, text="Access Key ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        access_key_id = ttk.Entry(aliyun_frame, width=40)
        access_key_id.insert(0, aliyun_settings.get('access_key_id', ''))
        access_key_id.grid(row=0, column=1, pady=5)
        
        ttk.Label(aliyun_frame, text="Access Key Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        access_key_secret = ttk.Entry(aliyun_frame, width=40)
        access_key_secret.insert(0, aliyun_settings.get('access_key_secret', ''))
        access_key_secret.grid(row=1, column=1, pady=5)
        
        ttk.Label(aliyun_frame, text="App Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        app_key = ttk.Entry(aliyun_frame, width=40)
        app_key.insert(0, aliyun_settings.get('app_key', ''))
        app_key.grid(row=2, column=1, pady=5)

        # DeepSeek API设置
        deepseek_frame = ttk.Frame(notebook, padding="10")
        notebook.add(deepseek_frame, text="DeepSeek API设置")
        
        ttk.Label(deepseek_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        deepseek_api_key = ttk.Entry(deepseek_frame, width=40)
        deepseek_api_key.insert(0, config.deepseek_config.get('api_key', ''))
        deepseek_api_key.grid(row=0, column=1, pady=5)
        

        
        # 保存按钮和功能
        def save_settings():
            nonlocal config  # 声明config为非局部变量
            try:
                # 读取现有配置
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新配置
                config_data['aliyun'] = {
                    'access_key_id': access_key_id.get(),
                    'access_key_secret': access_key_secret.get(),
                    'app_key': app_key.get(),
                    'region_id': aliyun_settings.get('region_id', '')
                }
                
                # 更新DeepSeek配置
                config_data['deepseek'] = {
                    'api_key': deepseek_api_key.get(),
                    'base_url': config.deepseek_base_url
                }
                
                # 保存配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=False)
                
                # 重新加载配置
                config = Config()
                config.load_config()
                
                messagebox.showinfo("成功", "设置已保存，请重启软件以应用新的设置。")
                settings_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"保存设置时出错：{str(e)}")
        
        # 创建保存按钮
        save_button = ttk.Button(frame, text="保存", command=save_settings)
        save_button.pack(pady=10)

    def delete_selected_items(self, event):
        """删除选中的多条记录"""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的记录吗？"):
            for item in selection:
                values = self.tree.item(item)["values"]
                if len(values) >= 1:
                    recording_id = values[0]  # 获取记录ID
                    self.db_manager.delete_recording(recording_id)
            self.load_recordings()  # 刷新显示