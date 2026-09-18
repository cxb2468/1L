"""
    需要库：
    pip install xlwings natsort pypinyin
"""

import os
import re
import tkinter as tk
import webbrowser
from tkinter import filedialog, ttk
from typing import List, Tuple

import xlwings as xw
from natsort import natsorted  # 自然排序要用到
from pypinyin import lazy_pinyin  # 拼音排序要用到


class ImageInsertTool:
    def __init__(self, master):
        self.master = master
        master.title("Excel批量插图工具 - 【不匹配】表格内容 v3.0")
        master.geometry("430x450")

        # 初始化变量
        self.topmost_var = tk.BooleanVar(value=True)
        self.image_files: List[str] = []
        self.direction_var = tk.StringVar(value="向下")
        self.col_var = tk.StringVar(value="C")
        self.start_row_var = tk.StringVar(value="3")
        self.margin_var = tk.StringVar(value="2")
        self.first_run = True  # 首次运行标志

        # 界面布局设置
        self.center_window(master)
        self._setup_main_layout()
        self._create_insert_ui()

        self.style = ttk.Style()
        self._configure_styles()

        self.create_status_bar()
        master.attributes('-topmost', self.topmost_var.get())

        # 首次加载显示操作指南
        self.show_help_guide()

    def show_help_guide(self):
        """显示帮助指南"""
        guide = """【新手操作指南 - 点下方“帮助”按钮可再次显示】

1. 准备阶段：
   - 确保Excel文件已打开
   - 准备好要插入的图片文件（支持jpg/png/webp/bmp格式）

2. 参数设置：
   - 目标列：图片要插入的列（如C表示C列）
   - 起始行：从第几行开始插入（如3表示从第3行开始）
   - 边距：图片与单元格边界的距离（推荐2，0表示撑满）
   - 方向：选择图片插入方向（向下或向右）

3. 执行操作：
   - 点击"选择图片文件"按钮选择图片
   - 预览确认插入位置是否正确
   - 点击"插入图片"按钮完成操作

小技巧：
- 可以多次选择不同图片分批插入
- 图片会按文件名自动排序
- 插入过程中请不要操作Excel
- 遇到问题可复制日志中的错误提示，在论坛回复帖子反馈。
- 点右下角灰色文字可直达软件发布页（52pojie.cn论坛）
"""
        self.log_message(guide, "info", clear=True)

    def _configure_styles(self):
        """配置控件样式"""
        self.style.configure('TLabel', font=('Microsoft YaHei', 9))
        self.style.configure('TButton', font=('Microsoft YaHei', 9))
        self.style.configure('Accent.TButton', font=(
            'Microsoft YaHei', 9, 'bold'))
        self.style.configure('Warning.TLabel', foreground='red',
                             font=('Microsoft YaHei', 9, 'bold'))

        if hasattr(self, 'log_panel'):
            text_widget = self.log_panel.children['!text']
            tag_colors = {
                'error': '#D32F2F',
                'success': '#388E3C',
                'info': '#1976D2',
                'title': '#7B1FA2',
                'preview': '#616161',
                'warning': '#FF8F00'
            }
            for tag, color in tag_colors.items():
                text_widget.tag_config(tag, foreground=color)

    def _setup_main_layout(self):
        """初始化主布局结构"""
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.configure(bg='#F0F0F0')

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

    def _create_insert_ui(self):
        """创建图片插入相关控件"""
        main_frame = ttk.Frame(self.master)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 0))
        main_frame.grid_columnconfigure(0, weight=1)

        param_frame = ttk.LabelFrame(main_frame, text="插入参数", padding=(12, 8))
        param_frame.pack(fill="x", padx=3, pady=(6, 4))
        center_frame = ttk.Frame(param_frame)
        center_frame.pack()

        self.param_input_row_frame = ttk.Frame(center_frame)
        self.param_input_row_frame.pack(pady=5)

        # 参数输入控件
        ttk.Label(self.param_input_row_frame, text="目标列:").pack(
            side="left", padx=(0, 2))
        self.col_entry = ttk.Entry(self.param_input_row_frame, width=4,
                                   textvariable=self.col_var, justify='center')
        self.col_entry.pack(side="left", padx=(5, 15))

        ttk.Label(self.param_input_row_frame, text="起始行:").pack(
            side="left", padx=(0, 2))
        self.start_row_entry = ttk.Entry(self.param_input_row_frame, width=4,
                                         textvariable=self.start_row_var, justify='center')
        self.start_row_entry.pack(side="left", padx=(5, 15))

        ttk.Label(self.param_input_row_frame, text="边距:").pack(
            side="left", padx=(0, 2))
        self.margin_entry = ttk.Entry(self.param_input_row_frame, width=4,
                                      textvariable=self.margin_var, justify='center')
        self.margin_entry.pack(side="left", padx=(5, 15))

        ttk.Label(self.param_input_row_frame, text="方向:").pack(
            side="left", padx=(0, 2))
        self.direction_combo = ttk.Combobox(
            self.param_input_row_frame,
            textvariable=self.direction_var,
            values=["向下", "向右"],
            width=5,
            state='readonly'
        )
        self.direction_combo.pack(side="left", padx=(5, 5))
        self.direction_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.show_insertion_preview() if self.image_files else None)

        # 操作按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=8, pady=6)
        btn_container = ttk.Frame(btn_frame)
        btn_container.pack()

        self.select_btn = ttk.Button(
            btn_container, text="选择图片文件", width=20,
            command=self.select_images, style='Accent.TButton'
        )
        self.select_btn.pack(side="left", expand=True, padx=8)
        self.insert_btn = ttk.Button(
            btn_container, text="插入图片", width=20,
            command=self.insert_images, style='Accent.TButton'
        )
        self.insert_btn.pack(side="left", expand=True, padx=8)

        self.log_panel = self.create_log_panel(main_frame)
        self.log_panel.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._show_initial_tips()

    def create_log_panel(self, parent) -> ttk.Frame:
        """创建日志显示面板"""
        frame = ttk.Frame(parent)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        text = tk.Text(
            frame, height=10, wrap=tk.WORD, state="disabled", bg="#FFFFFF",
            padx=10, pady=8, font=('Microsoft YaHei', 9), relief="flat",
            highlightthickness=1, highlightbackground="#CCCCCC"
        )
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        return frame

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(
            self.master, style='Status.TFrame', padding=(8, 4))
        status_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(5, 5))

        # 置顶按钮
        self.topmost_btn = ttk.Checkbutton(
            status_frame, text="窗口置顶", variable=self.topmost_var,
            command=lambda: self.master.attributes(
                '-topmost', self.topmost_var.get())
        )
        self.topmost_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 帮助按钮
        self.help_btn = ttk.Button(
            status_frame, text="帮助", width=8,
            command=self.show_help_guide
        )
        self.help_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 作者信息
        self.status_label = tk.Label(
            status_frame, text="By wkdxz", fg="gray", cursor="hand2",
            font=('Microsoft YaHei', 9)
        )
        self.status_label.bind("<Enter>", lambda e: self.status_label.config(
            fg="blue", font=('Microsoft YaHei', 9, 'underline')))
        self.status_label.bind("<Leave>", lambda e: self.status_label.config(
            fg="gray", font=('Microsoft YaHei', 9)))
        self.status_label.bind(
            "<Button-1>", lambda e: webbrowser.open("https://www.52pojie.cn/thread-2030255-1-1.html"))
        self.status_label.pack(side=tk.RIGHT)

    def _show_initial_tips(self):
        """显示初始提示"""
        if self.first_run:
            self.first_run = False
        else:
            self.log_message("提示：点击底部'帮助'按钮查看详细操作指南", "info", clear=True)

    def validate_inputs(self) -> Tuple[bool, str]:
        """验证输入参数有效性"""
        try:
            if not re.match(r'^[A-Za-z]{1,3}$', self.col_var.get()):
                return False, "列号必须是1-3个字母"
            if not self.start_row_var.get().isdigit() or int(self.start_row_var.get()) < 1:
                return False, "起始行必须是大于0的整数"
            if not self.margin_var.get().isdigit() or int(self.margin_var.get()) < 0:
                return False, "边距必须是非负整数"
            return True, ""
        except Exception as e:
            return False, f"验证错误: {str(e)}"

    def select_images(self):
        """选择图片文件并排序"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.webp;*.bmp")]
        )
        if files:
            try:
                self.image_files = sorted(
                    natsorted(files),
                    key=lambda x: lazy_pinyin(
                        os.path.basename(x), errors='ignore')
                )
                self.show_insertion_preview()
            except Exception as e:
                self.log_message(f"文件加载失败: {str(e)}", "error", clear=True)
        else:
            self.image_files = []
            self.log_message("未选择任何图片文件。请点击'选择图片文件'按钮重新选择。",
                             "info", clear=True)

    def show_insertion_preview(self):
        """显示插入顺序预览"""
        if not self.image_files:
            self.log_message("没有图片可供预览。请先选择图片。", "info", clear=True)
            return

        valid, msg = self.validate_inputs()
        if not valid:
            self.log_message(f"参数错误无法预览: {msg}", "error", clear=True)
            self.show_help_guide()
            self.log_message(f"\n参数错误: {msg}", "error")
            return

        try:
            col = self.col_var.get().upper()
            start_row = int(self.start_row_var.get())
            direction = self.direction_var.get()

            self.log_message("【插入顺序预览】", "title", clear=True)
            current_row = start_row
            current_col_str = col
            for idx, path in enumerate(self.image_files, 1):
                filename = os.path.basename(path)
                line = f"{idx:02d}: {filename}"
                if direction == "向下":
                    cell_addr = f"{col}{current_row}"
                    current_row += 1
                else:  # 向右
                    if idx == 1:
                        cell_addr = f"{current_col_str}{start_row}"
                    else:
                        current_col_str = self._calculate_next_column(
                            current_col_str)
                        cell_addr = f"{current_col_str}{start_row}"
                line += f" -> {cell_addr}"
                self.log_message(line, "preview")
            self.log_message(f"\n-> 点击【插入图片】按钮执行操作", "info")
        except Exception as e:
            self.log_message(f"预览生成失败: {str(e)}", "error", clear=True)
            self.show_help_guide()
            self.log_message(f"\n预览错误: {str(e)}", "error")

    def _calculate_next_column(self, current_col_str: str) -> str:
        """计算列名的下一列"""
        if not current_col_str:
            return 'A'
        num = 0
        for char in current_col_str.upper():
            num = num * 26 + (ord(char) - ord('A') + 1)
        num += 1
        new_col_str = ""
        while num > 0:
            num, remainder = divmod(num - 1, 26)
            new_col_str = chr(ord('A') + remainder) + new_col_str
        return new_col_str

    def insert_images(self):
        """执行图片插入操作"""
        if not self.image_files:
            self.log_message("请先选择图片文件。", "warning", clear=True)
            self.show_help_guide()
            self.log_message("\n提示: 请先选择图片文件。", "warning")
            return

        valid, msg = self.validate_inputs()
        if not valid:
            self.log_message(f"参数错误: {msg}", "error", clear=True)
            self.show_help_guide()
            self.log_message(f"\n参数错误: {msg}", "error")
            return

        try:
            direction = self.direction_var.get()
            self.log_message(f"开始插入图片(方向: {direction})...", "info", clear=True)
            self.set_ui_state(False)
            app = xw.apps.active
            if not app:
                raise Exception("请先打开Excel程序，并确保目标工作簿和工作表已激活。")
            if not app.books.active:
                raise Exception("没有活动的Excel工作簿。请打开一个工作簿。")
            if not app.books.active.sheets.active:
                raise Exception("活动工作簿中没有活动的工作表。请选择一个工作表。")

            with self.ExcelOperation(app) as (wb, ws):
                success = 0
                total = len(self.image_files)
                self.log_message(f"共发现 {total} 张待插入图片", "info")
                for idx, img_path in enumerate(self.image_files, 1):
                    if self.process_image(ws, img_path, idx, direction):
                        success += 1

                if total > 0:
                    if success == total:
                        self.log_message(
                            f"操作完成，成功插入 {success}/{total} 张图片。", "success")
                    elif success > 0:
                        self.log_message(
                            f"操作部分完成，成功插入 {success}/{total} 张图片。请检查日志中的错误信息。", "warning")
                    else:
                        self.log_message(f"操作失败，未能插入任何图片。请检查日志。", "error")

        except Exception as e:
            self.log_message(f"操作失败: {str(e)}", "error")
        finally:
            self.set_ui_state(True)

    class ExcelOperation:
        """Excel操作上下文管理器"""

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

    def process_image(self, ws, img_path: str, index: int, direction: str) -> bool:
        """处理单张图片插入"""
        try:
            col_str = self.col_var.get().upper()
            start_row_num = int(self.start_row_var.get())
            margin_points = int(self.margin_var.get())

            abs_path = os.path.abspath(img_path)
            if not os.path.isfile(abs_path):
                raise FileNotFoundError(f"文件不存在: {abs_path}")

            target_cell_obj = self.get_target_cell(
                ws, col_str, start_row_num, index, direction)

            left = target_cell_obj.left + margin_points
            top = target_cell_obj.top + margin_points
            width = target_cell_obj.width - 2 * margin_points
            height = target_cell_obj.height - 2 * margin_points

            if width <= 0 or height <= 0:
                self.log_message(
                    f"警告({index}): {os.path.basename(img_path)} -> {target_cell_obj.address.replace('$', '')} 单元格太小或边距太大，无法放置图片。", "warning")
                width = max(1, width)
                height = max(1, height)

            try:
                shape = ws.api.Shapes.AddPicture(
                    Filename=abs_path,
                    LinkToFile=0,
                    SaveWithDocument=-1,
                    Left=left,
                    Top=top,
                    Width=width,
                    Height=height
                )
                shape.LockAspectRatio = 0
            except Exception as api_error:
                self.log_message(
                    f"插入失败({index}): 调用Excel API插入图片 '{os.path.basename(img_path)}' 到 {target_cell_obj.address.replace('$', '')} 时出错 - {str(api_error)}", "error")
                return False

            self.log_message(
                f"成功插入 {index:02d}: {os.path.basename(img_path)} -> {target_cell_obj.address.replace('$', '')}",
                "success"
            )
            return True

        except FileNotFoundError as e:
            self.log_message(f"插入失败({index}): 文件错误 - {str(e)}", "error")
            return False
        except Exception as e:
            cell_addr_str = "未知单元格"
            try:
                target_cell_obj_for_error = self.get_target_cell(
                    ws, self.col_var.get().upper(), int(self.start_row_var.get()), index, direction)
                cell_addr_str = target_cell_obj_for_error.address.replace(
                    '$', '')
            except:
                pass
            self.log_message(
                f"插入失败({index}): 处理图片 '{os.path.basename(img_path)}' (目标 {cell_addr_str}) 时发生意外错误 - {str(e)}", "error")
            return False

    def get_target_cell(self, ws, col_char: str, start_row_num: int, item_index: int, direction: str) -> xw.Range:
        """获取目标单元格对象"""
        if direction == "向下":
            return ws.range(f"{col_char}{start_row_num + item_index - 1}")
        else:  # 向右
            current_col_num = 0
            for char_idx, char_val in enumerate(reversed(col_char.upper())):
                current_col_num += (ord(char_val) -
                                    ord('A') + 1) * (26 ** char_idx)

            target_col_num = current_col_num + item_index - 1

            new_col_str = ""
            temp_num = target_col_num
            while temp_num > 0:
                temp_num, remainder = divmod(temp_num - 1, 26)
                new_col_str = chr(ord('A') + remainder) + new_col_str
            return ws.range(f"{new_col_str}{start_row_num}")

    def set_ui_state(self, enabled: bool):
        """设置UI元素状态"""
        state = 'normal' if enabled else 'disabled'
        self.select_btn.configure(state=state)
        self.insert_btn.configure(state=state)
        self.help_btn.configure(state=state)

        if hasattr(self, 'col_entry'):
            self.col_entry.configure(state=state)
        if hasattr(self, 'start_row_entry'):
            self.start_row_entry.configure(state=state)
        if hasattr(self, 'margin_entry'):
            self.margin_entry.configure(state=state)
        if hasattr(self, 'direction_combo'):
            combo_state = 'readonly' if enabled else 'disabled'
            self.direction_combo.configure(state=combo_state)

        if hasattr(self, 'topmost_btn'):
            self.topmost_btn.configure(state=state)

    def log_message(self, message: str, msg_type: str = "info", clear: bool = False):
        """记录日志消息"""
        if not hasattr(self, 'log_panel') or '!text' not in self.log_panel.children:
            print(f"Log panel or text widget not ready. Message: {message}")
            return

        text_widget = self.log_panel.children['!text']
        text_widget.configure(state='normal')
        if clear:
            text_widget.delete(1.0, tk.END)

        if msg_type:
            text_widget.insert('end', f"{message}\n", (msg_type,))
        else:
            text_widget.insert('end', f"{message}\n")

        # 如果是清空并显示帮助内容，滚动到第一行
        if clear and message.strip().startswith("【新手操作指南"):
            text_widget.see('1.0')  # 滚动到第一行
        else:
            text_widget.see('end')  # 其他情况滚动到最后一行

        text_widget.configure(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageInsertTool(root)
    root.mainloop()
