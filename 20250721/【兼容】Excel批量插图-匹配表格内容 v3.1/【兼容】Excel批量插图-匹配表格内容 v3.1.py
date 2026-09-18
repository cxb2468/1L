"""
    需要库：
    pip install xlwings
"""

import os
import re
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk
from typing import Dict

import xlwings as xw


class ExcelImageMatcherPro:
    def __init__(self, master):
        self.master = master
        master.title("Excel批量插图-匹配表格内容 v3.1")
        master.geometry("480x590")

        self.col_image_map: Dict[str, str] = {}
        self.row_image_map: Dict[str, str] = {}
        self.topmost_var = tk.BooleanVar(value=True)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.center_window(master)
        self.create_column_tab()  # 创建列日志组件 self.col_log
        self.create_row_tab()      # 创建行日志组件 self.row_log
        self.create_status_bar()

        master.attributes('-topmost', self.topmost_var.get())

        self._create_help_tags()   # 初始化标签（必须在日志组件创建后调用）
        self.show_help_guide()     # 显示帮助文本

        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """标签页切换时自动显示帮助信息"""
        self.show_help_guide()

    def _create_help_tags(self):
        """创建日志文本颜色标签"""
        for log in [self.col_log, self.row_log]:
            log.tag_config("title", foreground="#7B1FA2",
                           font=('Microsoft YaHei', 9, 'bold'))
            log.tag_config("success", foreground="#388E3C")
            log.tag_config("warning", foreground="#FF8F00")
            log.tag_config("error", foreground="#D32F2F")
            log.tag_config("info", foreground="#1976D2")
            log.tag_config("preview", foreground="#616161")

    def center_window(self, window):
        """窗口居中显示"""
        window.withdraw()
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"+{x}+{y}")
        window.deiconify()

    def show_help_guide(self, target_log=None):
        """显示操作指南（可指定目标日志组件）"""
        help_text = """【新手操作指南 - 点下方"帮助"按钮可再次显示】

    1. 准备工作：
        - 打开Excel文件
        - 准备图片文件夹（支持jpg/png/webp/bmp格式）

    2. 参数设置：
        - 匹配列/行：包含名称的列或行（如A列或1行）
        - 插入列/行：图片要插入的位置（如B列或2行）
        - 边距：图片与单元格边界的距离（推荐2，0表示撑满）

    3. 执行步骤：
        (1) 选择图片文件夹
        (2) 点击"执行匹配插入"按钮

    ★ 注意事项：
        - 图片名称需与单元格内容完全一致（不区分大小写）
        - 示例：单元格"产品A" → 图片"产品A.jpg"
        - 插入过程中请不要操作Excel
        - 遇到问题可复制日志中的错误提示，在论坛回复帖子反馈。
        - 点右下角灰色文字可直达软件发布页（52pojie.cn论坛）
        """

        # 确定目标日志组件
        if target_log is None:
            current_tab = self.notebook.index("current")
            target_log = self.col_log if current_tab == 0 else self.row_log

        # 清空当前日志并显示帮助信息
        target_log.config(state="normal")
        target_log.delete(1.0, tk.END)
        target_log.insert(tk.END, help_text, "info")
        target_log.see("1.0")  # 滚动到顶部
        target_log.config(state="disabled")

    def create_column_tab(self):
        """创建列匹配标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  列匹配模式  ")

        # 描述框架
        desc_frame = ttk.Frame(tab)
        desc_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(desc_frame, text="列匹配模式：按垂直方向匹配插入，适合单列数据匹配。",
                  foreground="gray").pack(anchor="w")

        # 参数框架
        param_frame = ttk.LabelFrame(tab, text="列匹配参数", padding=10)
        param_frame.pack(fill="x", padx=10, pady=5)

        # 单行参数输入
        input_row = ttk.Frame(param_frame)
        input_row.pack(pady=10)

        ttk.Label(input_row, text="待匹配列:").pack(side="left", padx=5)
        self.col_match = ttk.Entry(input_row, width=8)
        self.col_match.pack(side="left", padx=5)
        self.col_match.insert(0, "A")

        ttk.Label(input_row, text="插入列:").pack(side="left", padx=5)
        self.col_insert = ttk.Entry(input_row, width=8)
        self.col_insert.pack(side="left", padx=5)
        self.col_insert.insert(0, "B")

        ttk.Label(input_row, text="边距:").pack(side="left", padx=5)
        self.col_margin = ttk.Entry(input_row, width=8)
        self.col_margin.pack(side="left", padx=5)
        self.col_margin.insert(0, "2")

        # 文件夹选择
        folder_frame = ttk.Frame(param_frame)
        folder_frame.pack(fill="x", pady=10)

        self.col_folder_var = tk.StringVar()
        ttk.Label(folder_frame, text="图片文件夹:").pack(side="left", padx=5)
        ttk.Entry(folder_frame, textvariable=self.col_folder_var, width=30,
                  state="readonly").pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(folder_frame, text="浏览...", command=lambda: self.select_folder(self.col_folder_var, mode="column"))\
            .pack(side="left", padx=5)

        # 执行按钮
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(btn_frame, text="执行列匹配插入", command=self.run_column_match)\
            .pack(fill="x", expand=True)

        # 日志框架
        log_frame = ttk.Frame(tab)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.col_log = tk.Text(log_frame, wrap=tk.WORD, height=10,
                               state="disabled", font=('Microsoft YaHei', 9))
        scroll = ttk.Scrollbar(log_frame, command=self.col_log.yview)
        self.col_log.configure(yscrollcommand=scroll.set)

        self.col_log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def create_row_tab(self):
        """创建行匹配标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  行匹配模式  ")

        # 描述框架
        desc_frame = ttk.Frame(tab)
        desc_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(desc_frame, text="行匹配模式：按水平方向匹配插入，适合单行数据匹配。",
                  foreground="gray").pack(anchor="w")

        # 参数框架
        param_frame = ttk.LabelFrame(tab, text="行匹配参数", padding=10)
        param_frame.pack(fill="x", padx=10, pady=5)

        # 单行参数输入
        input_row = ttk.Frame(param_frame)
        input_row.pack(pady=10)

        ttk.Label(input_row, text="待匹配行:").pack(side="left", padx=5)
        self.row_match = ttk.Entry(input_row, width=8)
        self.row_match.pack(side="left", padx=5)
        self.row_match.insert(0, "1")

        ttk.Label(input_row, text="插入行:").pack(side="left", padx=5)
        self.row_insert = ttk.Entry(input_row, width=8)
        self.row_insert.pack(side="left", padx=5)
        self.row_insert.insert(0, "2")

        ttk.Label(input_row, text="边距:").pack(side="left", padx=5)
        self.row_margin = ttk.Entry(input_row, width=8)
        self.row_margin.pack(side="left", padx=5)
        self.row_margin.insert(0, "2")

        # 文件夹选择
        folder_frame = ttk.Frame(param_frame)
        folder_frame.pack(fill="x", pady=10)

        self.row_folder_var = tk.StringVar()
        ttk.Label(folder_frame, text="图片文件夹:").pack(side="left", padx=5)
        ttk.Entry(folder_frame, textvariable=self.row_folder_var, width=30,
                  state="readonly").pack(side="left", padx=5, expand=True, fill="x")
        ttk.Button(folder_frame, text="浏览...", command=lambda: self.select_folder(self.row_folder_var, mode="row"))\
            .pack(side="left", padx=5)

        # 执行按钮
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(btn_frame, text="执行行匹配插入", command=self.run_row_match)\
            .pack(fill="x", expand=True)

        # 日志框架
        log_frame = ttk.Frame(tab)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.row_log = tk.Text(log_frame, wrap=tk.WORD, height=10,
                               state="disabled", font=('Microsoft YaHei', 9))
        scroll = ttk.Scrollbar(log_frame, command=self.row_log.yview)
        self.row_log.configure(yscrollcommand=scroll.set)

        self.row_log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.master, padding=(8, 4))
        status_frame.pack(side="bottom", fill="x")

        # 置顶按钮
        ttk.Checkbutton(
            status_frame, text="窗口置顶", variable=self.topmost_var,
            command=lambda: self.master.attributes(
                '-topmost', self.topmost_var.get())
        ).pack(side="left", padx=(0, 10))

        # 帮助按钮
        ttk.Button(
            status_frame, text="帮助", width=8,
            command=self.show_help_guide
        ).pack(side="left", padx=(0, 10))

        # 作者信息
        author_label = tk.Label(status_frame, text="By wkdxz", fg="gray", cursor="hand2",
                                font=('Microsoft YaHei', 9))
        author_label.bind("<Enter>", lambda e: author_label.config(fg="blue"))
        author_label.bind("<Leave>", lambda e: author_label.config(fg="gray"))
        author_label.bind(
            "<Button-1>", lambda e: webbrowser.open("https://www.52pojie.cn/thread-2030255-1-1.html"))
        author_label.pack(side="right")

    def select_folder(self, var_tk_stringvar, mode):
        """选择图片文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            var_tk_stringvar.set(folder_path)
            log_widget = self.col_log if mode == "column" else self.row_log

            self.log_message("开始加载图片...", log_widget, append=False)

            current_image_map = self.build_image_map_from_folder(folder_path)

            if mode == "column":
                self.col_image_map = current_image_map
            elif mode == "row":
                self.row_image_map = current_image_map

            if len(current_image_map) > 0:
                self.log_message(
                    f"加载完成：找到 {len(current_image_map)} 张支持的图片。", log_widget)
            else:
                self.log_message("警告: 未找到任何支持的图片文件。", log_widget)

            self.preview_insert_positions(mode)

    def build_image_map_from_folder(self, folder_path: str) -> Dict[str, str]:
        """构建图片名称到路径的映射"""
        image_map: Dict[str, str] = {}
        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(extensions):
                        name_without_ext = os.path.splitext(
                            file)[0].strip().lower()
                        image_map[name_without_ext] = os.path.abspath(
                            os.path.join(root, file))  # 使用绝对路径
        except Exception as e:
            self.log_message(
                f"构建图片映射出错: {e}", self.col_log if 'col' in self._current_mode else self.row_log)
        return image_map

    def validate_column_params(self) -> Dict:
        """验证列模式参数有效性"""
        params = {
            'match_col': self.col_match.get().upper(),
            'insert_col': self.col_insert.get().upper(),
            'margin': self.col_margin.get()
        }
        if not re.match(r'^[A-Z]{1,3}$', params['match_col']):
            raise ValueError("匹配列格式错误 (例如: A, B, AA)")
        if not re.match(r'^[A-Z]{1,3}$', params['insert_col']):
            raise ValueError("插入列格式错误 (例如: A, B, AA)")
        if not params['margin'].isdigit() or int(params['margin']) < 0:
            raise ValueError("边距必须是非负数字")
        return {
            'match_col': params['match_col'],
            'insert_col': params['insert_col'],
            'start_row': 2,
            'margin': int(params['margin'])
        }

    def validate_row_params(self) -> Dict:
        """验证行模式参数有效性"""
        params = {
            'match_row': self.row_match.get(),
            'insert_row': self.row_insert.get(),
            'margin': self.row_margin.get()
        }
        if not params['match_row'].isdigit() or int(params['match_row']) < 1:
            raise ValueError("匹配行必须是大于0的数字")
        if not params['insert_row'].isdigit() or int(params['insert_row']) < 1:
            raise ValueError("插入行必须是大于0的数字")
        if not params['margin'].isdigit() or int(params['margin']) < 0:
            raise ValueError("边距必须是非负数字")
        return {
            'match_row': int(params['match_row']),
            'insert_row': int(params['insert_row']),
            'margin': int(params['margin'])
        }

    def excel_operation(self, app):
        """Excel操作上下文管理器"""
        class ExcelOperation:
            def __init__(self, app):
                self.app = app
                self.wb = None
                self.ws = None

            def __enter__(self):
                try:
                    self.wb = self.app.books.active
                    if not self.wb:
                        raise Exception("没有活动的Excel工作簿。")
                    self.ws = self.wb.sheets.active
                    if not self.ws:
                        raise Exception("活动工作簿中没有活动的工作表。")
                    return self.wb, self.ws
                except Exception as e:
                    raise Exception(f"无法访问活动工作簿或工作表: {str(e)}")

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return ExcelOperation(app)

    def insert_image(self, ws, image_path, cell_addr, margin, log_widget):
        """插入图片到指定单元格"""
        try:
            # 确保使用绝对路径
            abs_image_path = os.path.abspath(image_path)
            if not os.path.exists(abs_image_path):
                self.log_message(f"错误: 图片文件不存在 - {abs_image_path}", log_widget)
                return False

            # 获取目标单元格
            target_cell = ws.range(cell_addr)

            # 计算插入位置和大小
            left = target_cell.left + margin
            top = target_cell.top + margin
            width = target_cell.width - 2 * margin
            height = target_cell.height - 2 * margin

            # 插入图片
            ws.pictures.add(abs_image_path,
                            left=left,
                            top=top,
                            width=width,
                            height=height)
            return True

        except Exception as e:
            error_msg = f"插入图片失败: {str(e)}"
            self.log_message(error_msg, log_widget)
            return False

    def run_column_match(self):
        """执行列匹配插入"""
        self.log_message("开始列匹配处理...", self.col_log, append=False)
        try:
            if not self.col_folder_var.get():
                messagebox.showwarning("提示", "请先选择图片文件夹！")
                self.log_message("错误: 未选择图片文件夹。", self.col_log)
                return

            params = self.validate_column_params()
            app = xw.apps.active or xw.App(visible=True)

            with self.excel_operation(app) as (wb, ws):
                max_row = ws.used_range.last_cell.row
                success_inserts = 0
                processed_excel_rows = 0
                non_empty_match_cells = 0

                self.log_message(
                    f"将在列 {params['match_col']} 中查找名称，图片插入到列 {params['insert_col']}，从行 {params['start_row']} 开始。",
                    self.col_log)

                for row_num_excel in range(params['start_row'], max_row + 1):
                    processed_excel_rows += 1
                    match_cell_addr = f"{params['match_col']}{row_num_excel}"

                    cell_value = ws.range(match_cell_addr).value
                    name_to_match = str(cell_value).strip(
                    ) if cell_value is not None else ""

                    if not name_to_match:
                        continue

                    non_empty_match_cells += 1
                    insert_cell_addr = f"{params['insert_col']}{row_num_excel}"
                    lower_name_to_match = name_to_match.lower()

                    if lower_name_to_match in self.col_image_map:
                        image_file_path = os.path.abspath(
                            self.col_image_map[lower_name_to_match])
                        if not os.path.exists(image_file_path):
                            self.log_message(
                                f"错误: 图片文件不存在 - {image_file_path}",
                                self.col_log)
                            continue

                        if self.insert_image(ws, image_file_path, insert_cell_addr, params['margin'], self.col_log):
                            success_inserts += 1
                            self.log_message(
                                f"{match_cell_addr}：{name_to_match} → {insert_cell_addr}：{os.path.basename(image_file_path)}",
                                self.col_log)
                    else:
                        self.log_message(
                            f"{match_cell_addr}：{name_to_match} → 未找到匹配图片",
                            self.col_log)

                summary = f"\n共处理 {processed_excel_rows} 行数据，成功插入 {success_inserts} 张图片。"
                self.log_message(summary, self.col_log)

        except Exception as e:
            error_msg = f"列匹配错误: {str(e)}"
            self.log_message(error_msg, self.col_log)
            messagebox.showerror("错误", error_msg)

    def run_row_match(self):
        """执行行匹配插入"""
        self.log_message("开始行匹配处理...", self.row_log, append=False)
        try:
            if not self.row_folder_var.get():
                messagebox.showwarning("提示", "请先选择图片文件夹！")
                self.log_message("错误: 未选择图片文件夹。", self.row_log)
                return

            params = self.validate_row_params()
            app = xw.apps.active or xw.App(visible=True)

            with self.excel_operation(app) as (wb, ws):
                max_col = ws.used_range.last_cell.column
                success_inserts = 0
                processed_excel_cols = 0
                non_empty_match_cells = 0

                self.log_message(
                    f"将在行 {params['match_row']} 中查找名称，图片插入到行 {params['insert_row']}。",
                    self.row_log)

                for col_num_excel in range(1, max_col + 1):
                    processed_excel_cols += 1
                    match_cell_addr = f"{xw.utils.col_name(col_num_excel)}{params['match_row']}"

                    cell_value = ws.range(match_cell_addr).value
                    name_to_match = str(cell_value).strip(
                    ) if cell_value is not None else ""

                    if not name_to_match:
                        continue

                    non_empty_match_cells += 1
                    insert_cell_addr = f"{xw.utils.col_name(col_num_excel)}{params['insert_row']}"
                    lower_name_to_match = name_to_match.lower()

                    if lower_name_to_match in self.row_image_map:
                        image_file_path = os.path.abspath(
                            self.row_image_map[lower_name_to_match])
                        if not os.path.exists(image_file_path):
                            self.log_message(
                                f"错误: 图片文件不存在 - {image_file_path}",
                                self.row_log)
                            continue

                        if self.insert_image(ws, image_file_path, insert_cell_addr, params['margin'], self.row_log):
                            success_inserts += 1
                            self.log_message(
                                f"{match_cell_addr}：{name_to_match} → {insert_cell_addr}：{os.path.basename(image_file_path)}",
                                self.row_log)
                    else:
                        self.log_message(
                            f"{match_cell_addr}：{name_to_match} → 未找到匹配图片",
                            self.row_log)

                summary = f"\n共处理 {processed_excel_cols} 列数据，成功插入 {success_inserts} 张图片。"
                self.log_message(summary, self.row_log)

        except Exception as e:
            error_msg = f"行匹配错误: {str(e)}"
            self.log_message(error_msg, self.row_log)
            messagebox.showerror("错误", error_msg)

    def preview_insert_positions(self, mode):
        """预览插入位置"""
        image_map = self.col_image_map if mode == "column" else self.row_image_map
        log_widget = self.col_log if mode == "column" else self.row_log

        if not image_map:
            self.log_message("没有图片可供预览。请先选择图片文件夹。", log_widget)
            return

        self.log_message("【插入位置预览】", log_widget, tags="title")
        for name, path in image_map.items():
            self.log_message(
                f"{name} -> {os.path.basename(path)}", log_widget, tags="preview")

    def log_message(self, message, log_widget, append=True, tags=None, clear=False):
        """记录日志消息"""
        log_widget.config(state="normal")
        if clear:
            log_widget.delete(1.0, tk.END)
        if not append:
            log_widget.delete(1.0, tk.END)
        log_widget.insert(tk.END, message + "\n", tags)
        log_widget.see(tk.END)
        log_widget.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelImageMatcherPro(root)
    root.mainloop()
