import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import pandas as pd
import duckdb
import subprocess  # 用于打开文件


class CrossTableQueryTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel跨表查询工具")
        self.root.geometry("500x460")  # 设置窗口大小

        # 创建控件
        self.label1 = tk.Label(root, text="1. 选择2个Excel文件比对查询")
        self.label1.place(x=4, y=10, width=200)

        # 数据源文件操作按钮
        self.btn_add = tk.Button(root, text="添加", command=self.add_table)
        self.btn_add.place(x=240, y=10, width=60, height=22)

        self.btn_delete = tk.Button(root, text="删除", command=self.delete_table)
        self.btn_delete.place(x=320, y=10, width=60, height=22)

        self.table_frame = tk.Frame(root)
        self.table_frame.place(x=10, y=45, width=480, height=75)

        self.table_tree = ttk.Treeview(self.table_frame, columns=("file_name", "alias", "file_path"), show="headings")
        self.table_tree.heading("file_name", text="文件名")
        self.table_tree.heading("alias", text="别名")
        self.table_tree.heading("file_path", text="文件路径")
        self.table_tree.column("file_name", width=120)
        self.table_tree.column("alias", width=45)
        self.table_tree.column("file_path", width=313)
        self.table_tree.pack()

        self.label2 = tk.Label(root, text="2.选择一个Excel文件保存查询结果")
        self.label2.place(x=4, y=125, width=220)

        # 保存路径和浏览按钮
        self.label_save_path = tk.Label(root, text="保存路径:")
        self.label_save_path.place(x=4, y=155, width=80)

        self.entry_save_path = tk.Entry(root, width=40)
        self.entry_save_path.place(x=80, y=155, width=340)

        self.btn_browse = tk.Button(root, text="浏览", command=self.browse_save_path)
        self.btn_browse.place(x=430, y=155, width=60, height=22)

        self.label3 = tk.Label(root, text="3.编写SQL查询语句")
        self.label3.place(x=15, y=185, width=120)

        self.txt_query = tk.Text(root, height=10, width=50)
        self.txt_query.place(x=10, y=210, width=480, height=200)

        self.btn_execute = tk.Button(root, text="执行查询", command=self.execute_query)
        self.btn_execute.place(x=100, y=420, width=300)

        self.conn = duckdb.connect()
        self.tables = {}
        self.table_count = 0

    def add_table(self):
        if self.table_count >= 2:
            messagebox.showerror("Error", "最多只能添加两个Excel文件。")
            return
        file_path = filedialog.askopenfilename(filetypes=[("Excel or csv files", "*.xlsx *.xls *.csv")])
        if file_path:
            file_name = os.path.basename(file_path)
            alias = f"table{self.table_count + 1}"
            self.tables[alias] = file_path
            self.table_tree.insert("", "end", values=(file_name, alias, file_path))
            self.table_count += 1

    def delete_table(self):
        if not self.table_tree.selection():
            messagebox.showerror("Error", "请先选择要删除的数据源文件。")
            return
        selected_item = self.table_tree.selection()[0]
        alias = self.table_tree.item(selected_item)["values"][1]
        del self.tables[alias]
        self.table_tree.delete(selected_item)
        self.table_count -= 1

    def browse_save_path(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")]) or self.entry_save_path.get()
        if save_path:
            self.entry_save_path.delete(0, tk.END)
            self.entry_save_path.insert(0, save_path)

    def execute_query(self):
        if not self.tables:
            messagebox.showerror("Error", "请先添加Excel文件。")
            return
        if not self.txt_query.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "请输入SQL查询语句。")
            return
        if not self.entry_save_path.get():
            messagebox.showerror("Error", "请输入保存路径。")
            return
        try:
            # 读取Excel文件并加载到DuckDB中
            for alias, file_path in self.tables.items():
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path, encoding='GBK')  # 指定编码
                elif file_path.endswith(".xls") or file_path.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                else:
                    raise ValueError("不支持的文件类型")
                self.conn.register(alias, df)
            query = self.txt_query.get("1.0", tk.END).strip()
            result = self.conn.execute(query).fetchdf()
            # 保存结果到新的Excel文件
            result.to_excel(self.entry_save_path.get(), index=False)
            messagebox.showinfo("Success", "查询执行成功，结果已保存到新的Excel文件。")
            # 自动打开生成的XLSX文件
            subprocess.Popen([self.entry_save_path.get()], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"执行查询时发生错误: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CrossTableQueryTool(root)
    root.mainloop()