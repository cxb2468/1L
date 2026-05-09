import ctypes
import datetime
import struct
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json


# ==================== 调用Everything SDK 的核心功能 ====================

def get_python_datetime_from_win_filetime(filetime):
    """Convert windows filetime winticks to python datetime.datetime."""
    WINDOWS_TICKS = int(1 / 10 ** -7)
    WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()
    WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS

    winticks = struct.unpack('<Q', filetime)[0]
    microsecs = (winticks - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
    return datetime.datetime.fromtimestamp(microsecs)


def find_everything_dll():
    """查找Everything DLL文件，返回找到的路径或None"""
    dll_paths = [
        "./Everything64.dll",
        "./Everything32.dll",
        "Everything64.dll",
        "Everything32.dll",
        "C:/Program Files/Everything/Everything64.dll",
        "C:/Program Files (x86)/Everything/Everything32.dll",
        "C:/Program Files/Everything/Everything.dll",
        "C:/Program Files (x86)/Everything/Everything.dll"
    ]

    for path in dll_paths:
        if os.path.exists(path):
            return path
    return None


def check_everything_running(everything_dll):
    """检查Everything是否正在运行且数据库已加载

    Returns:
        (bool, str): (是否正常运行, 错误信息)
    """
    try:
        # 尝试使用 Everything_IsDBLoaded (1.4.1+)
        try:
            is_loaded = everything_dll.Everything_IsDBLoaded()
            if not is_loaded:
                return False, "Everything 正在启动中，数据库尚未加载完成，请稍后再试"
            return True, ""
        except AttributeError:
            # 旧版本没有 IsDBLoaded，尝试执行一个空查询来检测
            pass

        # 备用方法：执行一个空查询检测错误码
        everything_dll.Everything_SetSearchW("")
        everything_dll.Everything_SetRequestFlags(0x00000001)  # 只需要文件名

        if not everything_dll.Everything_QueryW(True):
            # 查询失败，获取错误码
            try:
                error_code = everything_dll.Everything_GetLastError()
                # EVERYTHING_ERROR_IPC = 2 (Everything未运行)
                # EVERYTHING_ERROR_INVALIDCALL = 8 (无效调用)
                if error_code == 2:
                    return False, "Everything 未运行或未安装\n请先启动 Everything 软件"
                elif error_code == 8:
                    return False, "Everything 调用失败，请检查版本兼容性"
                else:
                    return False, f"Everything 错误 (代码: {error_code})"
            except:
                return False, "Everything 未响应，请确保 Everything 正在运行"

        return True, ""

    except Exception as e:
        return False, f"检测 Everything 状态时出错: {str(e)}"


def send_query_to_everything(query_str, sort_by='name', sort_ascending=True):
    EVERYTHING_REQUEST_FILE_NAME = 0x00000001
    EVERYTHING_REQUEST_PATH = 0x00000002
    EVERYTHING_REQUEST_SIZE = 0x00000010
    EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
    EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100

    try:
        # 1. 首先检查DLL是否存在
        dll_path = find_everything_dll()
        if dll_path is None:
            raise Exception(
                "未找到 Everything SDK DLL 文件\n"
                "请从 https://www.voidtools.com/support/everything/sdk/ 下载 SDK，\n"
                "并将 Everything64.dll 或 Everything32.dll 放在以下位置之一：\n"
                "  &#8226; 程序所在目录\n"
                "  &#8226; C:/Program Files/Everything/"
            )

        # 2. 加载DLL
        try:
            everything_dll = ctypes.WinDLL(dll_path)
        except Exception as e:
            raise Exception(f"无法加载 DLL ({dll_path}): {str(e)}\n请检查 DLL 文件是否损坏或架构不匹配（32/64位）")

        # 3. 检查Everything是否正在运行
        is_running, error_msg = check_everything_running(everything_dll)
        if not is_running:
            raise Exception(error_msg)

        # 4. 设置API参数类型
        everything_dll.Everything_GetResultDateModified.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
        everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

        # 5. 执行查询
        everything_dll.Everything_SetSearchW(query_str)
        everything_dll.Everything_SetRequestFlags(
            EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH |
            EVERYTHING_REQUEST_SIZE | EVERYTHING_REQUEST_DATE_MODIFIED |
            EVERYTHING_REQUEST_ATTRIBUTES
        )

        # 排序映射（修正版）
        sort_map = {
            'name': (1, 2),  # (升序, 降序)
            'path': (3, 4),  # (升序, 降序)
            'size': (5, 6),  # (升序, 降序)
            'ext': (7, 8),  # (升序, 降序)
            'date': (11, 12)  # (升序, 降序)
        }

        sort_asc, sort_desc = sort_map.get(sort_by, (1, 2))
        sort_id = sort_asc if sort_ascending else sort_desc
        everything_dll.Everything_SetSort(sort_id)

        # 6. 执行查询
        if not everything_dll.Everything_QueryW(True):
            try:
                error_code = everything_dll.Everything_GetLastError()
                error_messages = {
                    0: "无错误",
                    1: "内存不足",
                    2: "Everything 未运行（IPC错误）",
                    3: "注册类失败",
                    4: "创建窗口失败",
                    5: "注册热键失败",
                    6: "语法错误",
                    7: "超时",
                    8: "无效调用",
                    9: "无效数据"
                }
                err_desc = error_messages.get(error_code, f"未知错误 (代码: {error_code})")
                raise Exception(f"查询失败: {err_desc}")
            except:
                raise Exception("查询执行失败")

        num_results = everything_dll.Everything_GetNumResults()

        filename = ctypes.create_unicode_buffer(1024)
        date_modified_filetime = ctypes.c_ulonglong(1)
        file_size = ctypes.c_ulonglong(1)

        result_list = []
        for i in range(min(num_results, 10000)):
            everything_dll.Everything_GetResultFullPathNameW(i, filename, 1024)
            full_path_name = ctypes.wstring_at(filename)
            everything_dll.Everything_GetResultDateModified(i, date_modified_filetime)
            everything_dll.Everything_GetResultSize(i, file_size)

            is_folder = False
            try:
                is_folder = bool(everything_dll.Everything_IsFolderResult(i))
            except AttributeError:
                try:
                    attrs = everything_dll.Everything_GetResultAttributes(i)
                    is_folder = bool(attrs & 0x10)
                except:
                    if 'folder:' in query_str.lower():
                        is_folder = True
                    else:
                        basename = os.path.basename(full_path_name)
                        if file_size.value == 0 and '.' not in basename:
                            is_folder = True

            result_list.append({
                'full_path_name': full_path_name,
                'file_name': os.path.basename(full_path_name),
                'dir_name': os.path.dirname(full_path_name),
                'date_modified': get_python_datetime_from_win_filetime(date_modified_filetime),
                'file_size': file_size.value,
                'is_folder': is_folder
            })
        return result_list, num_results

    except Exception as e:
        raise Exception(f"{str(e)}")


def format_file_size(size_bytes, is_folder=False):
    """格式化文件大小显示，文件夹显示为 <文件夹>"""
    if is_folder:
        return "<文件夹>"

    if size_bytes == 0:
        return "0 B"
    elif size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"


# ==================== 配置文件加载 ====================

def load_config():
    """加载配置文件，如果不存在则使用默认配置"""
    default_config = {
        "buttons": [
            {"text": "&#127916; 视频", "query": "*.mp4|*.avi|*.mkv|*.mov|*.wmv|*.flv|*.webm|*.m4v|*.mpg|*.mpeg",
             "bg_color": "#e74c3c", "hover_color": "#c0392b"},
            {"text": "&#127925; 音频", "query": "*.mp3|*.wav|*.flac|*.aac|*.ogg|*.wma|*.m4a|*.opus",
             "bg_color": "#9b59b6", "hover_color": "#8e44ad"},
            {"text": "&#128444;&#65039; 图片", "query": "*.jpg|*.jpeg|*.png|*.gif|*.bmp|*.webp|*.svg|*.ico|*.tiff|*.raw",
             "bg_color": "#3498db", "hover_color": "#2980b9"},
            {"text": "&#128196; 文档", "query": "*.pdf|*.doc|*.docx|*.txt|*.xls|*.xlsx|*.ppt|*.pptx|*.md|*.rtf",
             "bg_color": "#2ecc71", "hover_color": "#27ae60"},
            {"text": "&#128230; 压缩包", "query": "*.zip|*.rar|*.7z|*.tar|*.gz|*.bz2|*.xz|*.iso", "bg_color": "#f39c12",
             "hover_color": "#e67e22"},
            {"text": "&#9881;&#65039; 程序", "query": "*.exe|*.msi|*.bat|*.cmd|*.ps1|*.sh|*.com", "bg_color": "#95a5a6",
             "hover_color": "#7f8c8d"},
            {"text": "&#128193; 文件夹", "query": "folder:", "bg_color": "#1abc9c", "hover_color": "#16a085"},
            {"text": "&#128336; 今天修改", "query": "dm:today", "bg_color": "#34495e", "hover_color": "#2c3e50"},
            {"text": "&#128207; 大文件", "query": "size:>100MB", "bg_color": "#e67e22", "hover_color": "#d35400"}
        ],
        "window": {"title": "Everything 搜索工具", "width": 1200, "height": 700},
        "tips": "就绪 - 点击列标题可排序，多条件用 | 分隔表示'或'"
    }

    config_paths = ['./config.json', 'config.json', '../config.json']

    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'buttons' not in config:
                        config['buttons'] = default_config['buttons']
                    if 'window' not in config:
                        config['window'] = default_config['window']
                    if 'tips' not in config:
                        config['tips'] = default_config['tips']
                    return config
            except Exception as e:
                print(f"加载配置文件失败 {path}: {e}")
                continue

    return default_config


# ==================== Tkinter GUI 界面 ====================

class EverythingGUI:
    def __init__(self, root):
        self.root = root
        self.config = load_config()

        win_config = self.config.get('window', {})
        self.root.title(win_config.get('title', 'Everything 搜索工具'))
        width = win_config.get('width', 1200)
        height = win_config.get('height', 700)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(800, 500)

        self.style = ttk.Style()
        self.current_results = []
        self.search_thread = None
        self.btn_widgets = []

        # 排序状态
        self.sort_by = 'name'
        self.sort_ascending = True

        self.create_widgets()
        self.setup_layout()

        # 绑定快捷键
        self.root.bind('<Return>', lambda e: self.on_search())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<F5>', lambda e: self.on_search())

        # 启动时检测环境
        self.root.after(500, self.check_environment)

    def create_widgets(self):
        # === 顶部快捷按钮区域 ===
        self.quick_frame = ttk.LabelFrame(self.root, text="快速搜索", padding=5)

        buttons_config = self.config.get('buttons', [])
        for btn_config in buttons_config:
            text = btn_config.get('text', '按钮')
            query = btn_config.get('query', '')
            bg_color = btn_config.get('bg_color', '#4a90d9')
            hover_color = btn_config.get('hover_color', '#5ba0e9')

            btn = tk.Button(
                self.quick_frame,
                text=text,
                font=('Microsoft YaHei', 10),
                bg=bg_color, fg='white',
                activebackground=hover_color, activeforeground='white',
                relief='flat', cursor='hand2',
                command=lambda q=query, t=text: self.quick_search(q, t)
            )
            btn.bind('<Enter>', lambda e, b=btn, h=hover_color: b.config(bg=h))
            btn.bind('<Leave>', lambda e, b=btn, c=bg_color: b.config(bg=c))
            self.btn_widgets.append(btn)

        # === 搜索栏区域 ===
        self.search_frame = ttk.Frame(self.root)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            font=('Microsoft YaHei', 14)
        )
        self.search_entry.focus()

        self.search_btn = tk.Button(
            self.search_frame,
            text="&#128269; 搜索",
            font=('Microsoft YaHei', 11, 'bold'),
            bg='#ff6b6b', fg='white',
            activebackground='#ff5252', activeforeground='white',
            relief='flat', cursor='hand2',
            command=self.on_search
        )
        self.search_btn.bind('<Enter>', lambda e: self.search_btn.config(bg='#ff7b7b'))
        self.search_btn.bind('<Leave>', lambda e: self.search_btn.config(bg='#ff6b6b'))

        # === 结果列表区域 ===
        self.list_frame = ttk.Frame(self.root)

        columns = ('name', 'path', 'size', 'date')
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        self.update_column_headers()

        self.tree.column('name', width=250, anchor='w')
        self.tree.column('path', width=550, anchor='w')
        self.tree.column('size', width=100, anchor='e')
        self.tree.column('date', width=150, anchor='center')

        # 绑定标题栏点击事件
        self.tree.heading('name', command=lambda: self.on_header_click('name'))
        self.tree.heading('path', command=lambda: self.on_header_click('path'))
        self.tree.heading('size', command=lambda: self.on_header_click('size'))
        self.tree.heading('date', command=lambda: self.on_header_click('date'))

        self.vsb = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # 右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="打开文件", command=self.open_selected)
        self.context_menu.add_command(label="打开所在文件夹", command=self.open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制完整路径", command=self.copy_path)

        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-1>', lambda e: self.open_selected())

        # === 状态栏 ===
        self.status_frame = ttk.Frame(self.root, relief='sunken', padding=2)
        tips = self.config.get('tips', '就绪 - 点击列标题可排序')
        self.status_var = tk.StringVar(value=tips)
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            anchor='w',
            font=('Microsoft YaHei', 9)
        )

        self.progress = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=100
        )

    def check_environment(self):
        """启动时检测环境状态"""
        dll_path = find_everything_dll()
        if dll_path is None:
            self.status_var.set("&#9888;&#65039; 未找到 Everything SDK DLL，搜索功能不可用")
            messagebox.showwarning(
                "环境检查",
                "未找到 Everything SDK DLL 文件\n\n"
                "请从官网下载 SDK 并将 DLL 文件放在程序目录：\n"
                "https://www.voidtools.com/support/everything/sdk/\n\n"
                "需要文件：Everything64.dll 或 Everything32.dll"
            )
        else:
            # 尝试加载并检测Everything是否运行
            try:
                everything_dll = ctypes.WinDLL(dll_path)
                is_running, error_msg = check_everything_running(everything_dll)
                if not is_running:
                    self.status_var.set(f"&#9888;&#65039; {error_msg}")
                    messagebox.showwarning(
                        "环境检查",
                        f"{error_msg}\n\n"
                        "请确保：\n"
                        "1. Everything 软件已安装\n"
                        "2. Everything 正在运行（在系统托盘查看图标）\n"
                        "3. 如果是首次安装，请等待索引建立完成"
                    )
                else:
                    self.status_var.set(f"&#9989; 已连接 Everything ({dll_path})")
            except Exception as e:
                self.status_var.set(f"&#9888;&#65039; DLL加载失败: {str(e)[:50]}")

    def update_column_headers(self):
        """更新列标题，显示当前排序指示器 ▲/▼"""
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

    def on_header_click(self, column):
        """点击列标题时的排序切换"""
        if self.sort_by == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_by = column
            self.sort_ascending = True

        self.update_column_headers()

        query = self.search_var.get().strip()
        if query:
            self.on_search()
        else:
            self.status_var.set(f"排序已设置为: {self.get_sort_desc()}，请输入搜索关键词")

    def get_sort_desc(self):
        """获取当前排序的描述文字"""
        sort_names = {
            'name': '文件名',
            'path': '路径',
            'size': '大小',
            'date': '修改时间'
        }
        direction = "升序" if self.sort_ascending else "降序"
        return f"{sort_names.get(self.sort_by, self.sort_by)} {direction}"

    def setup_layout(self):
        self.quick_frame.pack(fill=tk.X, padx=10, pady=5)
        for btn in self.btn_widgets:
            btn.pack(side=tk.LEFT, padx=3, pady=3)

        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_btn.pack(side=tk.LEFT, padx=5)

        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress.pack(side=tk.RIGHT, padx=5)

    def quick_search(self, query, title):
        self.search_var.set(query)
        self.on_search()

    def on_search(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.progress.start()
        self.status_var.set(f"正在搜索: {query} ({self.get_sort_desc()})...")
        self.search_btn.config(state='disabled')

        self.search_thread = threading.Thread(
            target=self.do_search,
            args=(query, self.sort_by, self.sort_ascending)
        )
        self.search_thread.daemon = True
        self.search_thread.start()

    def do_search(self, query, sort_by, sort_ascending):
        try:
            results, total = send_query_to_everything(query, sort_by, sort_ascending)
            self.root.after(0, self.update_results, results, total, query)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_results(self, results, total, query):
        self.current_results = results

        for item in results:
            self.tree.insert('', tk.END, values=(
                item['file_name'],
                item['dir_name'],
                format_file_size(item['file_size'], item['is_folder']),
                item['date_modified'].strftime('%Y-%m-%d %H:%M:%S')
            ))

        self.progress.stop()
        self.search_btn.config(state='normal')

        display_count = len(results)
        folder_count = sum(1 for r in results if r['is_folder'])
        file_count = display_count - folder_count

        if total > display_count:
            self.status_var.set(
                f"找到 {total} 个结果 (显示前 {display_count} 个，"
                f"{folder_count} 文件夹/{file_count} 文件) | {self.get_sort_desc()}"
            )
        else:
            self.status_var.set(
                f"找到 {total} 个结果 ({folder_count} 文件夹/{file_count} 文件) | {self.get_sort_desc()}"
            )

    def show_error(self, msg):
        self.progress.stop()
        self.search_btn.config(state='normal')
        self.status_var.set(f"&#10060; {msg[:80]}")
        messagebox.showerror("搜索错误", msg)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            idx = self.tree.index(item)
            if 0 <= idx < len(self.current_results):
                is_folder = self.current_results[idx]['is_folder']
                self.context_menu.entryconfig(0, label="打开文件夹" if is_folder else "打开文件")
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_item(self):
        selection = self.tree.selection()
        if not selection:
            return None
        idx = self.tree.index(selection[0])
        if 0 <= idx < len(self.current_results):
            return self.current_results[idx]
        return None

    def open_selected(self):
        item = self.get_selected_item()
        if item:
            try:
                os.startfile(item['full_path_name'])
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开: {str(e)}")

    def open_folder(self):
        item = self.get_selected_item()
        if item:
            try:
                os.startfile(item['dir_name'])
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开文件夹: {str(e)}")

    def copy_path(self):
        item = self.get_selected_item()
        if item:
            self.root.clipboard_clear()
            self.root.clipboard_append(item['full_path_name'])
            self.status_var.set(f"已复制路径: {item['full_path_name'][:50]}...")


def main():
    root = tk.Tk()
    app = EverythingGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()