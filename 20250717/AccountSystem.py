# 台账登记系统 - 主程序
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import json
import os
from datetime import datetime
import csv
import requests
from bs4 import BeautifulSoup


class AccountSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("台账登记系统 - By:xianyuwangyou&Trae AI编程工具")
        width = 1000
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(True, True)
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        # 数据文件路径
        self.data_file = "account_data.json"
        self.config_file = "config.json"

        # 初始化数据
        self.accounts = self.load_data()
        self.load_config()
        self.current_version = "V1.1"

        # 检查新版本
        self.check_for_updates()

        # 营销人和产品列表将从配置文件加载
        self.sort_directions = {
            "id": "asc",
            "marketer": "asc",
            "product": "asc",
            "amount": "asc",
            "date": "asc",
            "notes": "asc"
        }

        # 创建界面
        self.create_widgets()

    def load_data(self):
        """从JSON文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                messagebox.showerror("错误", f"加载数据失败: {str(e)}")
                return []
        return []

    def save_data(self):
        """将数据保存到JSON文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=4)
            # messagebox.showinfo("成功", "数据已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {str(e)}")

    def export_data(self):
        """将数据导出为CSV文件"""
        # 获取保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            title="选择保存路径",
            initialfile=f"台账导出{datetime.now().strftime('%Y%m%d')}"
        )
        if not file_path:
            return  # 用户取消保存

        # 定义CSV列名
        fieldnames = ["id", "marketer", "product", "amount", "date", "notes"]

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for record in self.accounts:
                    # 确保所有字段存在，缺失的用空字符串填充
                    writer.writerow({
                        "id": record.get("id", ""),
                        "marketer": record.get("marketer", ""),
                        "product": record.get("product", ""),
                        "amount": record.get("amount", ""),
                        "date": record.get("date", ""),
                        "notes": record.get("notes", "")
                    })
            messagebox.showinfo("成功", "数据已成功导出为CSV文件！")
        except Exception as e:
            messagebox.showerror("错误", f"导出数据失败: {str(e)}")

    def add_account(self):
        """添加新台账记录"""
        # 直接获取主界面输入控件内容
        marketer = self.marketer_combo.get()
        product = self.product_combo.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()
        notes = self.notes_text.get(1.0, tk.END).strip()

        # 严格验证必填项（排除默认选项）
        if marketer in ["请选择营销人", ""] or product in ["请选择产品名称", ""]:
            messagebox.showwarning("警告", "请选择有效的营销人和产品名称")
            return
        # 确保数量为正浮点数
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("数量必须大于0")
        except ValueError:
            messagebox.showwarning("警告", "请输入有效数量（正数）")
            return

        # 输入验证（移除非必要的重复验证）
        # 计算新ID（取最大ID+1，确保唯一性）
        max_id = max((record["id"] for record in self.accounts), default=0) if self.accounts else 0
        new_record = {
            "id": max_id + 1,
            "marketer": marketer,
            "product": product,
            "amount": amount,
            "date": date,
            "notes": notes
        }
        self.accounts.append(new_record)
        self.save_data()
        self.update_account_list()
        messagebox.showinfo("成功登记", f"添加成功！编号：{max_id + 1}")

        # 清空录入区域
        self.marketer_combo.set("请选择营销人")  # 重置营销人下拉框
        self.product_combo.set("请选择产品名称")  # 重置产品下拉框
        self.amount_entry.delete(0, tk.END)  # 清空金额输入框
        self.date_entry.set_date(datetime.now())  # 重置日期为当前日期
        self.notes_text.delete(1.0, tk.END)  # 清空备注文本框

    def update_account_list(self):
        """更新台账列表显示"""
        # 清空现有项目
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)

        # 按ID降序排序记录
        sorted_accounts = sorted(self.accounts, key=lambda x: x["id"], reverse=True)
        # 添加所有记录（按ID降序显示）
        for record in sorted_accounts:
            self.account_tree.insert("", tk.END, values=(
                record.get("id", ""),
                record.get("marketer", ""),
                record.get("product", ""),
                record.get("amount", ""),
                record.get("date", ""),
                record.get("notes", "")
            ))

    def load_config(self):
        """从配置文件加载营销人和产品列表"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.marketers = config.get('marketers', ["请选择营销人"])
                    self.products = config.get('products', ["请选择产品名称"])
                    self.update_check = config.get('update_check', {
                        "latest_version_url": "https://wwvu.lanzouq.com/b0138zm9za",
                        "download_url": "https://wwvu.lanzouq.com/b0138zm9uf",
                        "password": "e2sd"
                    })
            except (json.JSONDecodeError, Exception) as e:
                messagebox.showerror("错误", f"加载配置失败: {str(e)}")
                self.marketers = ["请选择营销人", "张三", "李四", "王五", "赵六"]
                self.products = ["请选择产品名称", "产品A", "产品B", "产品C", "产品D"]
        else:
            # 如果配置文件不存在，使用默认值并保存
            self.marketers = ["请选择营销人", "张三", "李四", "王五", "赵六"]
            self.products = ["请选择产品名称", "产品A", "产品B", "产品C", "产品D"]
            self.save_config()

    def save_config(self):
        """保存营销人和产品列表到配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'marketers': self.marketers,
                    'products': self.products,
                    'update_check': self.update_check
                }, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def check_for_updates(self):
        """检查新版本"""
        latest_version_url = self.update_check.get("latest_version_url", "https://wwvu.lanzouq.com/b0138zm9za")
        download_url = self.update_check.get("download_url", "https://wwvu.lanzouq.com/b0138zm9uf")
        password = self.update_check.get("password", "e2sd")

        try:
            response = requests.get(latest_version_url, timeout=10)
            response.raise_for_status()
            # 提取网页标题
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else ""
            # 假设标题格式为“最新版本号Vx.x”
            latest_version = title.split("V")[-1] if "V" in title else ""

            if latest_version and latest_version > self.current_version.split("V")[-1]:
                # 检测到新版本
                choice = messagebox.askyesno("新版本检测", f"发现新版本V{latest_version}！是否前往下载？\n下载密码: {password}")
                if choice:
                    import webbrowser
                    webbrowser.open(download_url)
                    self.root.destroy()  # 关闭主窗口
        except Exception as e:
            pass  # 静默处理版本检查错误

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 只有选中项目时才显示菜单
        if self.account_tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def on_double_click(self, event):
        """双击事件处理函数"""
        item = self.account_tree.identify_row(event.y)
        if item:
            self.account_tree.selection_set(item)  # 选中双击的行
            self.edit_selected()  # 调用编辑方法

    def edit_selected(self):
        """编辑选中的记录"""
        selected_items = self.account_tree.selection()
        if not selected_items:
            return

        item = selected_items[0]  # 获取第一个选中项
        values = self.account_tree.item(item)["values"]  # 获取该行的值

        # 将数据填充到输入控件中
        self.marketer_combo.set(values[1])  # 营销人
        self.product_combo.set(values[2])  # 产品名称
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, values[3])  # 数量
        self.date_entry.set_date(values[4])  # 日期

        # 清空备注并插入新内容
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, values[5])  # 备注

        # 保存选中的ID以便更新时使用
        self.selected_id = values[0]

        # 切换按钮状态为编辑模式
        self.save_button.config(text="更新", command=self.update_selected)

    def update_selected(self):
        """更新选中的记录"""
        # 获取更新后的数据
        marketer = self.marketer_combo.get()
        product = self.product_combo.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()
        notes = self.notes_text.get(1.0, tk.END).strip()

        # 验证营销人和产品是否选择
        if marketer in ["请选择营销人", ""] or product in ["请选择产品名称", ""]:
            messagebox.showwarning("警告", "请选择有效的营销人和产品名称")
            return

        # 验证数量是否为正数
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("数量必须大于0")
        except ValueError:
            messagebox.showwarning("警告", "请输入有效数量（正数）")
            return

        # 更新数据
        for record in self.accounts:
            if record["id"] == self.selected_id:
                record["marketer"] = marketer
                record["product"] = product
                record["amount"] = amount
                record["date"] = date
                record["notes"] = notes
                break

        # 保存更新并刷新列表
        self.save_data()
        self.update_account_list()
        messagebox.showinfo("成功", "记录已更新")

        # 恢复按钮为添加模式
        self.save_button.config(text="添加", command=self.add_account)
        # 清空选中ID
        if hasattr(self, 'selected_id'):
            del self.selected_id

    def delete_selected(self):
        """删除选中的记录"""
        selected_items = self.account_tree.selection()
        if not selected_items:
            return

        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除选中的{len(selected_items)}条记录吗?"):
            return

        # 获取选中记录的ID
        selected_ids = []
        for item in selected_items:
            record_id = int(self.account_tree.item(item, "values")[0])
            selected_ids.append(record_id)

        # 过滤掉选中的记录
        self.accounts = [record for record in self.accounts if record["id"] not in selected_ids]

        # 保存更改并更新显示
        self.save_data()
        self.update_account_list()

    def sort_by(self, col):
        """根据列名排序台账记录（升序/降序切换）"""
        current_dir = self.sort_directions[col]
        new_dir = "desc" if current_dir == "asc" else "asc"
        self.sort_directions[col] = new_dir

        # 定义排序键函数（处理数值和字符串类型）
        if col == "id":
            key_func = lambda x: int(x[col])
        elif col == "amount":
            key_func = lambda x: float(x[col])
        else:
            key_func = lambda x: x[col]

        # 执行排序（reverse参数控制升序/降序）
        self.accounts.sort(key=key_func, reverse=(new_dir == "desc"))
        self.update_account_list()

    def open_manager_window(self):
        """打开营销人和产品管理窗口"""
        # 创建管理窗口
        self.manager_window = tk.Toplevel(self.root)
        self.manager_window.title("营销人与产品管理")
        width = 450
        height = 400
        x = (self.manager_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.manager_window.winfo_screenheight() // 2) - (height // 2)
        self.manager_window.geometry(f"{width}x{height}+{x}+{y}")
        self.manager_window.resizable(True, True)

        # 隐藏主窗口
        # self.root.withdraw()

        # 设置管理窗口关闭事件
        # self.manager_window.protocol("WM_DELETE_WINDOW", self.on_manager_window_close)

        # 创建标签页控件
        notebook = ttk.Notebook(self.manager_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建营销人标签页
        marketer_frame = ttk.Frame(notebook)
        notebook.add(marketer_frame, text="营销人管理")

        # 创建产品标签页
        product_frame = ttk.Frame(notebook)
        notebook.add(product_frame, text="产品管理")

        # 初始化营销人管理界面
        self.init_manager_tab(marketer_frame, 'marketer')

        # 初始化产品管理界面
        self.init_manager_tab(product_frame, 'product')

    def on_manager_window_close(self):
        """管理窗口关闭事件处理"""
        self.manager_window.destroy()
        self.root.deiconify()  # 恢复显示主窗口

    def init_manager_tab(self, parent_frame, item_type):
        """初始化管理标签页界面"""
        # 创建操作框架
        operation_frame = ttk.Frame(parent_frame)
        operation_frame.pack(fill=tk.X, pady=(10, 10))

        # 创建列表框架
        list_frame = ttk.Frame(parent_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建列表
        columns = ("id", "name")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        # 设置列标题和宽度
        tree.heading("id", text="序号")
        tree.heading("name", text="名称")
        tree.column("id", width=10, anchor=tk.CENTER)
        tree.column("name", width=240, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 根据类型获取数据
        if item_type == 'marketer':
            data = self.marketers[1:]
            title = "营销人"
        else:
            data = self.products[1:]
            title = "产品"

        # 填充列表数据
        for i, item in enumerate(data, 1):
            tree.insert("", tk.END, values=(i, item))

        # 添加名称输入框
        ttk.Label(operation_frame, text=f"{title}名称:").pack(side=tk.LEFT, padx=5)
        name_entry = ttk.Entry(operation_frame, width=20)
        name_entry.pack(side=tk.LEFT, padx=5, pady=10)

        # 添加按钮
        def add_item():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("警告", f"请输入{title}名称")
                return

            # 检查重复
            if item_type == 'marketer':
                if name in self.marketers:
                    messagebox.showwarning("警告", f"该{title}已存在")
                    return
                self.marketers.append(name)
            else:
                if name in self.products:
                    messagebox.showwarning("警告", f"该{title}已存在")
                    return
                self.products.append(name)

            # 保存配置
            self.save_config()

            # 刷新列表
            for item in tree.get_children():
                tree.delete(item)
            if item_type == 'marketer':
                data = self.marketers[1:]
            else:
                data = self.products[1:]
            for i, item in enumerate(data, 1):
                tree.insert("", tk.END, values=(i, item))

            # 清空输入框
            name_entry.delete(0, tk.END)

            # 更新主窗口下拉菜单
            self.update_comboboxes()

        def delete_item():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("警告", f"请选择要删除的{title}")
                return

            # 获取选中项名称
            item_id = tree.item(selected[0], "values")[1]

            # 从列表中删除
            if item_type == 'marketer':
                if item_id in self.marketers:
                    self.marketers.remove(item_id)
            else:
                if item_id in self.products:
                    self.products.remove(item_id)

            # 保存配置
            self.save_config()

            # 刷新列表
            for item in tree.get_children():
                tree.delete(item)
            if item_type == 'marketer':
                data = self.marketers[1:]
            else:
                data = self.products[1:]
            for i, item in enumerate(data, 1):
                tree.insert("", tk.END, values=(i, item))

            # 更新主窗口下拉菜单
            self.update_comboboxes()

        # 创建按&#65533;&#65533;&#65533;行框架
        button_row1 = ttk.Frame(operation_frame)
        button_row1.pack(side=tk.TOP, fill=tk.X, pady=2)
        button_row2 = ttk.Frame(operation_frame)
        button_row2.pack(side=tk.TOP, fill=tk.X, pady=2)

        # 添加按钮到第一行
        ttk.Button(button_row1, text=f"添加{title}", command=add_item).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_row1, text=f"删除{title}", command=delete_item).pack(side=tk.LEFT, padx=3)

        # 为营销人管理添加导入导出按钮
        if item_type == 'marketer':
            def export_marketers():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="导出营销人数据",
                    initialfile=f"营销人列表{datetime.now().strftime('%Y%m%d')}"
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            # 排除第一个默认选项
                            for marketer in self.marketers[1:]:
                                f.write(marketer + '\n')
                        messagebox.showinfo("成功", f"营销人数据已导出到: {file_path}")
                    except Exception as e:
                        messagebox.showerror("错误", f"导出失败: {str(e)}")

            def import_marketers():
                file_path = filedialog.askopenfilename(
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="导入营销人数据"
                )
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # 读取所有非空行
                            marketers = [line.strip() for line in f if line.strip()]

                        # 排除重复项并保留原有顺序
                        existing_marketers = set(self.marketers)
                        new_marketers = [p for p in marketers if p not in existing_marketers]

                        if new_marketers:
                            self.marketers.extend(new_marketers)
                            self.save_config()

                            # 刷&#65533;&#65533;&#65533;列表
                            for item in tree.get_children():
                                tree.delete(item)
                            data = self.marketers[1:]
                            for i, item in enumerate(data, 1):
                                tree.insert("", tk.END, values=(i, item))

                            # 更新主窗口下拉菜单
                            self.update_comboboxes()
                            messagebox.showinfo("成功", f"成功导入{len(new_marketers)}个营销人")
                        else:
                            messagebox.showinfo("提示", "没有发现新的营销人数据或所有营销人已存在")
                    except Exception as e:
                        messagebox.showerror("错误", f"导入失败: {str(e)}")

            # 添加导出/导入按钮到第二行
            ttk.Button(button_row2, text="导出营销人", command=export_marketers).pack(side=tk.LEFT, padx=3)
            ttk.Button(button_row2, text="导入营销人", command=import_marketers).pack(side=tk.LEFT, padx=3)
        # 为产品管理添加导入导出按钮
        if item_type == 'product':
            def export_products():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="导出产品数据",
                    initialfile=f"产品列表{datetime.now().strftime('%Y%m%d')}"
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            # 排除第一个默认选项
                            for product in self.products[1:]:
                                f.write(product + '\n')
                        messagebox.showinfo("成功", f"产品数据已导出到: {file_path}")
                    except Exception as e:
                        messagebox.showerror("错误", f"导出失败: {str(e)}")

            def import_products():
                file_path = filedialog.askopenfilename(
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="导入产品数据"
                )
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # 读取所有非空行
                            products = [line.strip() for line in f if line.strip()]

                        # 排除重复项并保留原有顺序
                        existing_products = set(self.products)
                        new_products = [p for p in products if p not in existing_products]

                        if new_products:
                            self.products.extend(new_products)
                            self.save_config()

                            # 刷新列表
                            for item in tree.get_children():
                                tree.delete(item)
                            data = self.products[1:]
                            for i, item in enumerate(data, 1):
                                tree.insert("", tk.END, values=(i, item))

                            # 更新主窗口下拉菜单
                            self.update_comboboxes()
                            messagebox.showinfo("成功", f"成功导入{len(new_products)}个产品")
                        else:
                            messagebox.showinfo("提示", "没有发现新的产品数据或所有产品已存在")
                    except Exception as e:
                        messagebox.showerror("错误", f"导入失败: {str(e)}")

            # 添加导出/导入按钮到第二行
            ttk.Button(button_row2, text="导出产品", command=export_products).pack(side=tk.LEFT, padx=3)
            ttk.Button(button_row2, text="导入产品", command=import_products).pack(side=tk.LEFT, padx=3)

        # 保存引用以便后续操作
        if item_type == 'marketer':
            self.marketer_tree = tree
        else:
            self.product_tree = tree

    def open_batch_entry_window(self):
        """打开批量录入窗口"""
        # 创建批量录入窗口
        self.batch_window = tk.Toplevel(self.root)
        self.batch_window.title("批量录入")
        width = 600
        height = 600
        x = (self.batch_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.batch_window.winfo_screenheight() // 2) - (height // 2)
        self.batch_window.geometry(f"{width}x{height}+{x}+{y}")
        self.batch_window.resizable(True, True)

        # 创建主框架
        main_frame = ttk.Frame(self.batch_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 营销人和日期选择区域
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        # 营销人选择
        ttk.Label(top_frame, text="营销人:", width=10).grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        self.batch_marketer_var = tk.StringVar(value=self.marketers[0])
        self.batch_marketer_combo = ttk.Combobox(top_frame, textvariable=self.batch_marketer_var, values=self.marketers,
                                                 state="readonly", width=20)
        self.batch_marketer_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # 日期选择
        ttk.Label(top_frame, text="日期:", width=10).grid(row=0, column=2, padx=10, pady=10, sticky=tk.E)
        self.batch_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.batch_date_entry = DateEntry(top_frame, textvariable=self.batch_date_var, width=18,
                                          date_pattern='yyyy-mm-dd')
        self.batch_date_entry.grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)

        # 产品列表区域
        ttk.Label(main_frame, text="产品列表", font=('SimHei', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))

        # 创建带滚动条的框架
        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        scroll_frame.config(height=200)

        # 画布和滚动条
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        self.product_frame = ttk.Frame(canvas)

        self.product_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.product_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # 添加标题栏
        title_frame = ttk.Frame(self.product_frame)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(title_frame, text="产品选择", width=20, anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)
        ttk.Label(title_frame, text="数量输入", width=15, anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)
        ttk.Label(title_frame, text="操作", width=6, anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)

        # 初始添加一行产品输入
        self.product_rows = []
        self.add_product_row()

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # 添加产品按钮
        add_button = ttk.Button(button_frame, text="添加产品", command=self.add_product_row)
        add_button.pack(side=tk.LEFT, padx=10)

        # 保存按钮
        save_button = ttk.Button(button_frame, text="批量保存到台账", command=self.save_batch_records)
        save_button.pack(side=tk.RIGHT, padx=10)

    def add_product_row(self):
        """添加一行产品和数量输入"""
        row_frame = ttk.Frame(self.product_frame)
        row_frame.pack(fill=tk.X, pady=2)

        # 产品选择
        product_var = tk.StringVar(value=self.products[0])
        product_combo = ttk.Combobox(row_frame, textvariable=product_var, values=self.products, state="readonly",
                                     width=20)
        product_combo.pack(side=tk.LEFT, padx=5)

        # 数量输入
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(row_frame, textvariable=amount_var, width=15)
        amount_entry.pack(side=tk.LEFT, padx=5)

        # 删除按钮
        def remove_row():
            row_frame.destroy()
            self.product_rows.remove((product_var, amount_var))

        delete_button = ttk.Button(row_frame, text="删除", command=remove_row)
        delete_button.pack(side=tk.LEFT, padx=5)

        # 保存引用
        self.product_rows.append((product_var, amount_var))

    def save_batch_records(self):
        """保存批量录入的记录"""
        marketer = self.batch_marketer_var.get()
        date = self.batch_date_var.get()

        # 验证营销人选择
        if marketer == "请选择营销人":
            messagebox.showwarning("警告", "请选择营销人")
            return

        # 收集所有产品记录
        records = []
        for product_var, amount_var in self.product_rows:
            product = product_var.get()
            amount_text = amount_var.get()

            # 验证产品选择
            if product == "请选择产品名称":
                messagebox.showwarning("警告", "请选择所有产品名称")
                return

            # 验证数量
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", f"产品 '{product}' 的数量输入无效")
                return

            records.append((product, amount))

        # 验证至少有一个产品
        if not records:
            messagebox.showwarning("警告", "请添加至少一个产品")
            return

        # 计算新ID的起始值
        max_id = max((record["id"] for record in self.accounts), default=0) if self.accounts else 0

        # 添加所有记录
        new_records_count = 0
        for product, amount in records:
            max_id += 1
            new_record = {
                "id": max_id,
                "marketer": marketer,
                "product": product,
                "amount": amount,
                "date": date,
                "notes": ""
            }
            self.accounts.append(new_record)
            new_records_count += 1

        # 保存数据并更新列表
        self.save_data()
        self.update_account_list()

        # 关闭窗口并提示
        self.batch_window.destroy()
        messagebox.showinfo("成功", f"批量录入成功，共添加 {new_records_count} 条记录")

    def update_comboboxes(self):
        """更新主窗口中的下拉菜单"""
        # 保存当前选中值
        current_marketer = self.marketer_var.get()
        current_product = self.product_var.get()

        # 更新营销人下拉菜单
        self.marketer_var.set('')
        self.marketer_combo['values'] = self.marketers

        # 恢复选中值，如果原选中值不存在则设为默认
        if current_marketer in self.marketers:
            self.marketer_var.set(current_marketer)
        else:
            self.marketer_var.set(self.marketers[0] if self.marketers else '')

        # 更新产品下拉菜单
        self.product_var.set('')
        self.product_combo['values'] = self.products

        # 恢复选中值，如果原选中值不存在则设为默认
        if current_product in self.products:
            self.product_var.set(current_product)
        else:
            self.product_var.set(self.products[0] if self.products else '')

    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建左右分栏框架
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建输入区域
        input_frame = ttk.LabelFrame(left_frame, text="添加新记录", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 设置统一组件宽度和间距
        widget_width = 20
        label_width = 8
        padx_value = 10
        pady_value = 8

        # 配置网格列权重，使输入框列可扩展
        input_frame.columnconfigure(1, weight=1)

        # 营销人选择
        ttk.Label(input_frame, text="营销人:", width=label_width).grid(row=0, column=0, padx=padx_value, pady=pady_value,
                                                                    sticky=tk.E)
        self.marketer_var = tk.StringVar(value=self.marketers[0])
        self.marketer_combo = ttk.Combobox(input_frame, textvariable=self.marketer_var, values=self.marketers,
                                           state="readonly", width=widget_width)
        self.marketer_combo.grid(row=0, column=1, padx=padx_value, pady=pady_value, sticky=tk.W + tk.E)

        # 产品名称选择
        ttk.Label(input_frame, text="产品名称:", width=label_width).grid(row=1, column=0, padx=padx_value, pady=pady_value,
                                                                     sticky=tk.E)
        self.product_var = tk.StringVar(value=self.products[0])
        self.product_combo = ttk.Combobox(input_frame, textvariable=self.product_var, values=self.products,
                                          state="readonly", width=widget_width)
        self.product_combo.grid(row=1, column=1, padx=padx_value, pady=pady_value, sticky=tk.W + tk.E)

        # 数量输入
        ttk.Label(input_frame, text="数量:", width=label_width).grid(row=2, column=0, padx=padx_value, pady=pady_value,
                                                                   sticky=tk.E)
        self.amount_entry = ttk.Entry(input_frame, width=widget_width)
        self.amount_entry.grid(row=2, column=1, padx=padx_value, pady=pady_value, sticky=tk.W + tk.E)

        # 日期显示
        ttk.Label(input_frame, text="日期:", width=label_width).grid(row=3, column=0, padx=padx_value, pady=pady_value,
                                                                   sticky=tk.E)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = DateEntry(input_frame, textvariable=self.date_var, width=widget_width,
                                    date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=3, column=1, padx=padx_value, pady=pady_value, sticky=tk.W + tk.E)

        # 备注输入
        ttk.Label(input_frame, text="备注:", width=label_width).grid(row=4, column=0, padx=padx_value, pady=pady_value,
                                                                   sticky=tk.NE)
        self.notes_text = tk.Text(input_frame, width=widget_width + 5, height=6)
        self.notes_text.grid(row=4, column=1, padx=padx_value, pady=pady_value, sticky=tk.W + tk.E + tk.N + tk.S)

        # 添加按钮
        add_button = ttk.Button(input_frame, text="添加记录", command=self.add_account, width=widget_width)
        add_button.grid(row=5, column=1, padx=padx_value, pady=(pady_value, 2), sticky=tk.W + tk.E)

        # 批量录入按钮
        batch_button = ttk.Button(input_frame, text="批量录入", command=self.open_batch_entry_window, width=widget_width)
        batch_button.grid(row=6, column=1, padx=padx_value, pady=(2, pady_value), sticky=tk.W + tk.E)

        # 将按钮赋值给 self.save_button
        self.save_button = add_button  # 添加这行代码

        # 创建操作按钮区域
        button_frame = ttk.Frame(left_frame, padding="10")
        button_frame.pack(fill=tk.X)

        # 导出按钮
        export_button = ttk.Button(button_frame, text="导出台账", command=self.export_data, width=widget_width)
        export_button.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X)

        # 添加管理按钮
        manage_button = ttk.Button(button_frame, text="管理营销人与产品", command=self.open_manager_window, width=widget_width)
        manage_button.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X)

        # 创建台账列表区域
        list_frame = ttk.LabelFrame(right_frame, text="台账记录", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格容器，用于放置Treeview和垂直滚动条
        table_container = ttk.Frame(list_frame)
        table_container.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ("id", "marketer", "product", "amount", "date", "notes")
        self.account_tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode='extended')

        # 设置列标题
        self.account_tree.heading("id", text="ID", anchor="w", command=lambda col="id": self.sort_by(col))
        self.account_tree.heading("marketer", text="营销人", anchor="w", command=lambda col="marketer": self.sort_by(col))
        self.account_tree.heading("product", text="产品名称", anchor="w", command=lambda col="product": self.sort_by(col))
        self.account_tree.heading("amount", text="数量", anchor="w", command=lambda col="amount": self.sort_by(col))
        self.account_tree.heading("date", text="日期", anchor="w", command=lambda col="date": self.sort_by(col))
        self.account_tree.heading("notes", text="备注", anchor="w", command=lambda col="notes": self.sort_by(col))

        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="删除选中记录", command=self.delete_selected)

        # 绑定右键菜单事件
        self.account_tree.bind("<Button-3>", self.show_context_menu)
        self.account_tree.heading("marketer", text="营销人")
        self.account_tree.heading("product", text="产品名称")
        self.account_tree.heading("amount", text="数量")
        self.account_tree.heading("date", text="日期")
        self.account_tree.heading("notes", text="备注")

        # 设置列宽
        self.account_tree.column("id", width=30, anchor=tk.W)
        self.account_tree.column("marketer", width=60, anchor=tk.W)
        self.account_tree.column("product", width=150, anchor=tk.W)
        self.account_tree.column("amount", width=100, anchor=tk.W)
        self.account_tree.column("date", width=100, anchor=tk.W)
        self.account_tree.column("notes", width=300, anchor=tk.W)

        # 添加滚动条
        vscrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.account_tree.yview)
        hscrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.account_tree.xview)
        self.account_tree.configure(yscroll=vscrollbar.set, xscroll=hscrollbar.set)
        self.account_tree.bind('<Double-1>', self.on_double_click)  # 绑定双击事件

        # 布局表格和滚动条
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.account_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 初始更新台账列表
        self.update_account_list()

        # 创建底部版本信息框架
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # 添加版本号标签（左下角）
        self.version_label = ttk.Label(bottom_frame, text=f"当前版本号：{self.current_version}")
        self.version_label.pack(side=tk.LEFT)


if __name__ == "__main__":
    root = tk.Tk()
    app = AccountSystem(root)
    root.mainloop()