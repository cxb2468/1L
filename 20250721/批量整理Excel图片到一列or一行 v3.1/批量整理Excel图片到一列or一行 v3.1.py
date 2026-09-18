import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import xlwings as xw


class ExcelImageAdjustTool:
    def __init__(self, master):
        self.master = master
        master.title("整理Excel图片工具 v3.1")
        master.geometry("430x520")

        # 初始化变量
        self.topmost_var = tk.BooleanVar(value=True)
        self.first_run = True
        self.layout_var = tk.StringVar(value="column")  # 默认为列布局

        # 样式配置
        self.style = ttk.Style()
        self._configure_styles()

        # 主界面布局
        self._setup_main_layout()
        self._create_main_ui()
        self.create_status_bar()

        # 初始状态
        self.center_window(master)
        master.attributes('-topmost', self.topmost_var.get())
        self._show_initial_tips()

    def _configure_styles(self):
        """配置控件样式"""
        self.style.configure('TLabel', font=('Microsoft YaHei', 9))
        self.style.configure('TButton', font=('Microsoft YaHei', 9))
        self.style.configure('Accent.TButton', font=(
            'Microsoft YaHei', 9, 'bold'))
        self.style.configure('Status.TFrame')

    def _setup_main_layout(self):
        """初始化主布局结构"""
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.configure(bg='#F0F0F0')

    def _create_main_ui(self):
        """创建主界面组件"""
        main_frame = ttk.Frame(self.master)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 0))

        # 参数输入区
        param_frame = ttk.LabelFrame(main_frame, text="调整参数", padding=(12, 8))
        param_frame.pack(fill="x", padx=3, pady=(6, 4))

        # 起始单元格输入
        input_row1 = ttk.Frame(param_frame)
        input_row1.pack(fill="x", pady=(0, 5))

        ttk.Label(input_row1, text="起始单元格:").pack(side="left", padx=(0, 2))
        self.start_cell_entry = ttk.Entry(
            input_row1, width=8, justify='center')
        self.start_cell_entry.pack(side="left", padx=(5, 15))
        self.start_cell_entry.insert(0, "C2")

        ttk.Label(input_row1, text="边距:").pack(side="left", padx=(0, 2))
        self.margin_entry = ttk.Entry(input_row1, width=4, justify='center')
        self.margin_entry.pack(side="left", padx=(5, 15))
        self.margin_entry.insert(0, "2")

        # 布局选择
        input_row2 = ttk.Frame(param_frame)
        input_row2.pack(fill="x", pady=(0, 5))

        ttk.Label(input_row2, text="排列方式:").pack(side="left", padx=(0, 2))

        layout_frame = ttk.Frame(input_row2)
        layout_frame.pack(side="left", padx=(5, 0))

        ttk.Radiobutton(layout_frame, text="按列排列", value="column",
                        variable=self.layout_var).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(layout_frame, text="按行排列", value="row",
                        variable=self.layout_var).pack(side="left")

        # 执行按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=8, pady=6)

        self.execute_btn = ttk.Button(
            btn_frame, text="执行调整",
            command=self.adjust_images,
            style='Accent.TButton'
        )
        self.execute_btn.pack(fill="x", padx=8, pady=(0, 8))

        # 日志区域
        self.log_panel = self._create_log_panel(main_frame)
        self.log_panel.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._configure_log_tags()

    def _create_log_panel(self, parent):
        """创建日志显示面板"""
        frame = ttk.Frame(parent)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        text = tk.Text(
            frame, height=10, wrap=tk.WORD, state="disabled",
            bg="#FFFFFF", padx=10, pady=8, font=('Microsoft YaHei', 9),
            relief="flat", highlightthickness=1,
            highlightbackground="#CCCCCC"
        )
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)

        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        return frame

    def _configure_log_tags(self):
        """配置日志标签样式"""
        text_widget = self.log_panel.children['!text']
        tag_config = {
            'title': {'foreground': '#7B1FA2', 'font': ('Microsoft YaHei', 9, 'bold')},
            'help': {'foreground': '#2E75B6'},
            'error': {'foreground': '#D32F2F'},
            'success': {'foreground': '#388E3C'},
            'warning': {'foreground': '#FF8F00'},
            'status': {'foreground': '#5B9BD5'}
        }
        for tag, config in tag_config.items():
            text_widget.tag_config(tag, **config)

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.master, padding=(8, 4))
        status_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(5, 5))

        # 置顶按钮
        self.topmost_btn = ttk.Checkbutton(
            status_frame, text="窗口置顶", variable=self.topmost_var,
            command=self.toggle_topmost
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

    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.master.attributes('-topmost', self.topmost_var.get())
        self.log_message(
            f"窗口置顶 {'已启用' if self.topmost_var.get() else '已禁用'}",
            "status")

    def _show_initial_tips(self):
        """显示初始提示"""
        if self.first_run:
            self.first_run = False
            self.show_help_guide()
        else:
            self.log_message("提示：点击'帮助'按钮查看详细使用说明", "info", clear=True)

    def show_help_guide(self):
        """显示详细帮助指南"""
        guide = """【新手操作指南 - 点下方"帮助"按钮可再次显示】

1. 准备阶段：
   - 确保Excel文件已打开且包含需要调整的图片
   - 图片应按调整顺序排列（左上角纵向顺序优先）

2. 参数说明：
   - 起始单元格：图片排列的起始位置（如C2表示从C2单元格开始）
   - 边距：图片与单元格边界的距离（推荐2，0表示撑满）
   - 排列方式：可选择按列排列（向下排）或按行排列（向右排）

3. 执行操作：
   - 点击"执行调整"按钮开始处理
   - 程序会自动将图片对齐到指定单元格
   - 调整过程中请勿操作Excel

小技巧：
- 遇到错误时请检查图片是否被锁定
- 建议调整前备份原始文件
- 出现问题可复制日志中的错误提示，在论坛回复帖子反馈。
- 点右下角灰色文字可直达软件发布页（52pojie.cn论坛）"""
        self.log_message(guide, "help", clear=True)

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

    def validate_inputs(self):
        """验证输入参数有效性"""
        try:
            # 验证起始单元格格式
            start_cell = self.start_cell_entry.get().strip().upper()
            import re
            if not re.match(r'^[A-Z]{1,3}[1-9][0-9]*$', start_cell):
                return False, "起始单元格格式无效，应为如'A1'、'C3'等格式"

            # 提取列和行
            col = ''.join(c for c in start_cell if c.isalpha())
            row = int(''.join(c for c in start_cell if c.isdigit()))

            if not col or not row:
                return False, "起始单元格解析错误"

            margin = self.margin_entry.get().strip()
            if not margin.isdigit() or int(margin) < 0:
                return False, "边距必须是非负整数"

            return True, ""
        except Exception as e:
            return False, f"验证错误: {str(e)}"

    def set_ui_state(self, enabled):
        """设置UI控件的可用状态"""
        state = "normal" if enabled else "disabled"
        self.start_cell_entry.configure(state=state)
        self.margin_entry.configure(state=state)
        self.execute_btn.configure(state=state)
        self.help_btn.configure(state=state)
        self.topmost_btn.configure(state=state)

    def parse_cell_address(self, cell_address):
        """解析单元格地址，返回列和行"""
        import re
        match = re.match(r'^([A-Z]+)(\d+)$', cell_address.upper())
        if not match:
            raise ValueError(f"无效的单元格地址: {cell_address}")
        col, row = match.groups()
        return col, int(row)

    def adjust_images(self):
        """执行图片调整操作"""
        try:
            # 验证输入
            valid, msg = self.validate_inputs()
            if not valid:
                self.log_message(f"参数错误: {msg}", "error", clear=True)
                return

            # 获取参数
            start_cell = self.start_cell_entry.get().upper()
            margin = int(self.margin_entry.get())
            layout_mode = self.layout_var.get()  # "column" 或 "row"

            # 解析起始单元格
            start_col, start_row = self.parse_cell_address(start_cell)

            # 检查Excel状态
            try:
                app = xw.apps.active
                if not app:
                    raise Exception("请先打开Excel程序")

                wb = app.books.active
                if not wb:
                    raise Exception("没有活动的Excel工作簿")

                ws = wb.sheets.active
                if not ws:
                    raise Exception("活动工作簿中没有活动的工作表")

            except Exception as e:
                self.log_message(f"Excel错误: {str(e)}", "error", clear=True)
                return

            # 获取并排序图片
            pictures = [shape for shape in ws.shapes
                        if shape.type in ['picture', 'linked_picture']]
            if not pictures:
                self.log_message("当前工作表中未找到任何图片", "warning", clear=True)
                return

            # 显示确认对话框
            layout_text = "一列" if layout_mode == "column" else "一行"
            if not tk.messagebox.askyesno("确认操作",
                                          f"此操作将把当前工作表的图片调整为{layout_text}，且不可撤销。\n是否继续操作？"):
                self.log_message("操作已取消", "status", clear=True)
                return

            pictures.sort(key=lambda x: (x.top, x.left))

            # 执行调整
            self.set_ui_state(False)
            self.log_message(f"开始调整图片位置为{layout_text}...", "info", clear=True)

            success = 0
            for i, pic in enumerate(pictures):
                try:
                    if layout_mode == "column":  # 按列排列（向下排）
                        target_row = start_row + i
                        target_col = start_col
                    else:  # 按行排列（向右排）
                        target_row = start_row
                        target_col = self.increment_column(start_col, i)

                    cell = ws.range(f"{target_col}{target_row}")

                    pic.lock_aspect_ratio = False
                    pic.top = cell.top + margin
                    pic.left = cell.left + margin
                    pic.width = cell.width - 2 * margin
                    pic.height = cell.height - 2 * margin

                    self.log_message(
                        f"已调整第{i+1}张图片到 {target_col}{target_row}", "success")
                    success += 1

                except Exception as e:
                    self.log_message(
                        f"调整第{i+1}张图片失败: {str(e)}", "error")

            # 输出结果
            total = len(pictures)
            if success == total:
                self.log_message(f"操作完成，成功调整 {success}/{total} 张图片", "success")
            elif success > 0:
                self.log_message(
                    f"操作部分完成，成功调整 {success}/{total} 张图片", "warning")
            else:
                self.log_message("操作失败，未能调整任何图片", "error")

        except Exception as e:
            self.log_message(f"系统错误: {str(e)}", "error")
        finally:
            self.set_ui_state(True)

    def increment_column(self, col_str, increment):
        """将Excel列标识增加指定数量"""
        # 将列标识转换为数字
        col_num = 0
        for c in col_str:
            col_num = col_num * 26 + (ord(c) - ord('A') + 1)

        # 增加指定数量
        col_num += increment

        # 将数字转回列标识
        result = ""
        while col_num > 0:
            remainder = (col_num - 1) % 26
            result = chr(ord('A') + remainder) + result
            col_num = (col_num - 1) // 26

        return result


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelImageAdjustTool(root)
    root.mainloop()
