import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import os
import warnings
import traceback

# 忽略特定的警告
warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl')


class ExcelSplitterMixer:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel 文件拆分与合并工具 (by wjgboy)")
        # 不允许改变窗口大小
        self.root.resizable(False, False)

        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # 拆分标签页
        self.split_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.split_frame, text="拆分文件")

        # 合并标签页
        self.merge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.merge_frame, text="合并文件")

        # 初始化变量
        self.init_split_variables()
        self.init_merge_variables()

        self.create_split_widgets()
        self.create_merge_widgets()

    def init_split_variables(self):
        self.split_file_path = tk.StringVar()
        self.split_worksheet_index = tk.IntVar(value=1)
        self.split_by_column_index = tk.IntVar(value=1)
        self.split_title_row_start = tk.IntVar(value=1)
        self.split_title_row_end = tk.IntVar(value=1)
        self.split_keep_title = tk.BooleanVar(value=True)
        self.split_output_directory = tk.StringVar(value="")

    def init_merge_variables(self):
        self.merge_files_to_merge = []
        self.merge_title_row_start = tk.IntVar(value=1)
        self.merge_title_row_end = tk.IntVar(value=1)
        self.merge_output_file = tk.StringVar(value="")

    def create_split_widgets(self):
        # 文件选择部分
        ttk.Label(self.split_frame, text="需要拆分的文件").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.split_frame, textvariable=self.split_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.split_frame, text="浏览", command=self.split_browse_file).grid(row=0, column=2, padx=5, pady=5)

        # 拆分工作表选择
        ttk.Label(self.split_frame, text="拆分工作表").grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.split_worksheet_radio_frame = ttk.Frame(self.split_frame)
        self.split_worksheet_radio_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.split_by_index = ttk.Radiobutton(
            self.split_worksheet_radio_frame,
            text="第",
            variable=self.split_worksheet_index,
            value=1
        )
        self.split_by_index.grid(row=0, column=0)

        self.split_worksheet_entry = ttk.Entry(self.split_worksheet_radio_frame, width=5)
        self.split_worksheet_entry.grid(row=0, column=1)
        self.split_worksheet_entry.insert(0, "1")

        ttk.Label(self.split_worksheet_radio_frame, text="个工作表").grid(row=0, column=2)

        self.split_by_name = ttk.Radiobutton(
            self.split_worksheet_radio_frame,
            text="工作表名:",
            variable=self.split_worksheet_index,
            value=2
        )
        self.split_by_name.grid(row=0, column=3)

        self.split_worksheet_name = ttk.Entry(self.split_worksheet_radio_frame, width=15)
        self.split_worksheet_name.grid(row=0, column=4)

        # 默认选中第一个单选按钮
        self.split_worksheet_index.set(1)

        # 拆分关键列
        ttk.Label(self.split_frame, text="拆分关键列").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.split_by_column_frame = ttk.Frame(self.split_frame)
        self.split_by_column_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.split_by_column_frame, text="第").grid(row=0, column=0)
        self.split_by_column_entry = ttk.Entry(self.split_by_column_frame, width=5)
        self.split_by_column_entry.grid(row=0, column=1)
        self.split_by_column_entry.insert(0, "1")
        ttk.Label(self.split_by_column_frame, text="列").grid(row=0, column=2)

        # 标题行范围
        ttk.Label(self.split_frame, text="标题行范围").grid(row=3, column=0, sticky="w", padx=5, pady=5)

        self.split_title_row_frame = ttk.Frame(self.split_frame)
        self.split_title_row_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.split_title_row_frame, text="从第").grid(row=0, column=0)
        self.split_title_row_start_entry = ttk.Entry(self.split_title_row_frame, width=5)
        self.split_title_row_start_entry.grid(row=0, column=1)
        self.split_title_row_start_entry.insert(0, "1")
        ttk.Label(self.split_title_row_frame, text="行到第").grid(row=0, column=2)
        self.split_title_row_end_entry = ttk.Entry(self.split_title_row_frame, width=5)
        self.split_title_row_end_entry.grid(row=0, column=3)
        self.split_title_row_end_entry.insert(0, "1")
        ttk.Label(self.split_title_row_frame, text="行").grid(row=0, column=4)

        # 拆分后的文件标题行设置
        ttk.Label(self.split_frame, text="拆分后的文件是否保留标题行").grid(row=4, column=0, sticky="w", padx=5, pady=5)

        self.split_title_option_frame = ttk.Frame(self.split_frame)
        self.split_title_option_frame.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Radiobutton(
            self.split_title_option_frame,
            text="是",
            variable=self.split_keep_title,
            value=True
        ).grid(row=0, column=0)

        ttk.Radiobutton(
            self.split_title_option_frame,
            text="否",
            variable=self.split_keep_title,
            value=False
        ).grid(row=0, column=1)

        # 拆分后文件保存目录
        ttk.Label(self.split_frame, text="拆分后文件保存目录").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.split_frame, textvariable=self.split_output_directory, width=50).grid(row=5, column=1, padx=5,
                                                                                             pady=5)
        ttk.Button(self.split_frame, text="选择目录", command=self.split_choose_output_directory).grid(row=5, column=2,
                                                                                                   padx=5, pady=5)

        # 操作按钮
        ttk.Button(self.split_frame, text="开始拆分", command=self.split_file).grid(row=6, column=0, columnspan=3, pady=10)

    def create_merge_widgets(self):
        # 选择要合并的文件
        ttk.Label(self.merge_frame, text="选择要合并的文件").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.merge_files_frame = ttk.Frame(self.merge_frame)
        self.merge_files_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.merge_files_listbox = tk.Listbox(self.merge_files_frame, width=50, height=5)
        self.merge_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.merge_files_scrollbar = tk.Scrollbar(self.merge_files_frame)
        self.merge_files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.merge_files_listbox.config(yscrollcommand=self.merge_files_scrollbar.set)
        self.merge_files_scrollbar.config(command=self.merge_files_listbox.yview)

        ttk.Button(self.merge_frame, text="添加文件", command=self.merge_browse_files).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.merge_frame, text="清除文件", command=self.clear_merge_files).grid(row=1, column=1, padx=5, pady=5)

        # 标题行范围
        ttk.Label(self.merge_frame, text="标题行范围").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.merge_title_row_frame = ttk.Frame(self.merge_frame)
        self.merge_title_row_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.merge_title_row_frame, text="从第").grid(row=0, column=0)
        self.merge_title_row_start_entry = ttk.Entry(self.merge_title_row_frame, width=5)
        self.merge_title_row_start_entry.grid(row=0, column=1)
        self.merge_title_row_start_entry.insert(0, "1")
        ttk.Label(self.merge_title_row_frame, text="行到第").grid(row=0, column=2)
        self.merge_title_row_end_entry = ttk.Entry(self.merge_title_row_frame, width=5)
        self.merge_title_row_end_entry.grid(row=0, column=3)
        self.merge_title_row_end_entry.insert(0, "1")
        ttk.Label(self.merge_title_row_frame, text="行").grid(row=0, column=4)

        # 合并后文件保存路径
        ttk.Label(self.merge_frame, text="合并后文件保存路径").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.merge_frame, textvariable=self.merge_output_file, width=50).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(self.merge_frame, text="选择文件", command=self.merge_choose_output_file).grid(row=3, column=2, padx=5,
                                                                                              pady=5)

        # 操作按钮
        ttk.Button(self.merge_frame, text="合并文件", command=self.merge_files).grid(row=4, column=0, columnspan=3, pady=10)

    def split_browse_file(self):
        filetypes = (("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="选择Excel文件", filetypes=filetypes)
        if filename:
            self.split_file_path.set(filename)

    def split_choose_output_directory(self):
        directory = filedialog.askdirectory(title="选择拆分文件保存目录")
        if directory:
            self.split_output_directory.set(directory)

    def split_file(self):
        file_path = self.split_file_path.get()
        if not file_path:
            messagebox.showerror("错误", "请先选择需要拆分的文件")
            return

        output_dir = self.split_output_directory.get()
        if not output_dir:
            messagebox.showerror("错误", "请选择拆分后文件保存目录")
            return

        try:
            # 获取工作表
            sheet_name = None
            sheet_index = None

            if self.split_worksheet_index.get() == 2 and self.split_worksheet_name.get():
                sheet_name = self.split_worksheet_name.get()
            else:
                try:
                    sheet_index = int(self.split_worksheet_entry.get()) - 1  # python索引从0开始
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的工作表索引")
                    return

            # 获取拆分列
            try:
                split_by_col_index = int(self.split_by_column_entry.get()) - 1  # 列索引从0开始
            except ValueError:
                messagebox.showerror("错误", "请输入有效的列索引")
                return

            # 获取标题行范围
            try:
                title_start_row = int(self.split_title_row_start_entry.get())
                title_end_row = int(self.split_title_row_end_entry.get())
            except ValueError:
                messagebox.showerror("错误", "请输入有效的标题行范围")
                return

            # 是否保留标题行
            keep_title = self.split_keep_title.get()

            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_index, header=None)

            # 获取拆分列的唯一值
            unique_values = df.iloc[title_end_row:, split_by_col_index].unique()

            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 按唯一值拆分文件
            result_files = []
            file_count = 0  # 用于统计生成的文件数量
            total_rows = 0  # 用于统计总行数
            file_row_counts = []  # 用于统计每个文件的行数
            for value in unique_values:
                if pd.isna(value):
                    continue  # 跳过NaN值

                # 清理文件名，去除非法字符
                cleaned_value = self.clean_filename(str(value))
                if not cleaned_value:
                    continue  # 跳过无效的文件名

                # 获取匹配的行
                filtered_df = df[df.iloc[:, split_by_col_index] == value]

                # 如果保留标题行，则包含标题行
                if keep_title:
                    result_df = pd.concat([df.iloc[title_start_row - 1:title_end_row], filtered_df])
                else:
                    result_df = filtered_df

                # 保存为新文件
                output_file = os.path.join(output_dir,
                                           f"{os.path.splitext(os.path.basename(file_path))[0]}_{cleaned_value}.xlsx")
                result_df.to_excel(output_file, index=False, header=False)
                result_files.append(output_file)

                # 统计行数
                file_count += 1
                data_rows = len(result_df) - (title_end_row - title_start_row + 1) if keep_title else len(result_df)
                total_rows += data_rows
                file_row_counts.append((os.path.basename(output_file), data_rows))

            # 显示拆分结果
            result_text = f"拆分文件成功！共生成 {file_count} 个文件，总数据行数（不包含标题行）：{total_rows}\n生成的文件有：\n"
            for file_name, row_count in file_row_counts:
                result_text += f"{file_name} (数据行数：{row_count})\n"
            result_text += f"\n文件已保存到: {output_dir}"

            messagebox.showinfo("拆分完成", result_text)

            # 自动打开保存目录
            self.open_directory(output_dir)

        except Exception as e:
            messagebox.showerror("错误", f"处理文件时出错: {str(e)}")
            traceback.print_exc()

    def clean_filename(self, filename):
        # 清理文件名，去除非法字符
        invalid_chars = '<>:"/\\|?*'
        cleaned_filename = ''.join(c for c in filename if c not in invalid_chars)
        cleaned_filename = cleaned_filename.strip()
        if not cleaned_filename:
            return None
        return cleaned_filename

    def open_directory(self, directory):
        # 在Windows上打开文件夹
        if os.name == 'nt':
            os.startfile(directory)
        # 在macOS上打开文件夹
        elif os.name == 'posix':
            os.system(f'open "{directory}"')
        # 在Linux上打开文件夹
        else:
            os.system(f'xdg-open "{directory}"')

    def merge_browse_files(self):
        filetypes = (("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        filenames = filedialog.askopenfilenames(title="选择要合并的Excel文件", filetypes=filetypes)
        if filenames:
            self.merge_files_to_merge.extend(filenames)
            self.merge_files_listbox.delete(0, tk.END)
            for file in self.merge_files_to_merge:
                self.merge_files_listbox.insert(tk.END, os.path.basename(file))

    def clear_merge_files(self):
        self.merge_files_to_merge = []
        self.merge_files_listbox.delete(0, tk.END)

    def merge_choose_output_file(self):
        filetypes = (("Excel files", "*.xlsx"), ("All files", "*.*"))
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=filetypes,
            title="保存合并后的文件"
        )
        if filename:
            self.merge_output_file.set(filename)

    def merge_files(self):
        if not self.merge_files_to_merge:
            messagebox.showinfo("提示", "请先选择要合并的文件")
            return

        output_file = self.merge_output_file.get()
        if not output_file:
            messagebox.showerror("错误", "请选择合并后文件的保存路径")
            return

        try:
            # 获取标题行设置
            try:
                title_start_row = int(self.merge_title_row_start_entry.get())
                title_end_row = int(self.merge_title_row_end_entry.get())
            except ValueError:
                messagebox.showerror("错误", "请输入有效的标题行范围")
                return

            # 合并所有文件
            merged_df = pd.DataFrame()
            total_rows = 0  # 用于统计总行数
            file_row_counts = []  # 用于统计每个文件的行数

            # 标题行是否已添加
            title_added = False

            for file in self.merge_files_to_merge:
                # 读取文件内容
                df = pd.read_excel(file, header=None)

                # 获取标题行
                title_df = df.iloc[title_start_row - 1:title_end_row]

                # 获取数据行
                data_rows = df.iloc[title_end_row:]

                # 如果标题行尚未添加，则添加标题行
                if not title_added:
                    merged_df = pd.concat([merged_df, title_df])
                    title_added = True

                # 添加数据行
                merged_df = pd.concat([merged_df, data_rows])

                # 统计行数
                data_row_count = len(data_rows)
                total_rows += data_row_count
                file_row_counts.append((os.path.basename(file), data_row_count))

            # 保存合并后的文件
            merged_df.to_excel(output_file, index=False, header=False)

            # 显示合并结果
            result_text = f"文件合并完成！\n"
            result_text += f"总数据行数（不包含标题行）：{total_rows}\n\n"
            result_text += "每个文件的数据行数：\n"
            for file_name, row_count in file_row_counts:
                result_text += f"{file_name}: {row_count} 行\n"
            result_text += f"\n合并文件已保存到: {output_file}"

            messagebox.showinfo("合并完成", result_text)

            # 自动打开合并文件所在目录
            output_dir = os.path.dirname(output_file)
            self.open_directory(output_dir)

        except Exception as e:
            messagebox.showerror("错误", f"合并文件时出错: {str(e)}")
            traceback.print_exc()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelSplitterMixer(root)
    root.mainloop()

