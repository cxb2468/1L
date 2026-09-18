import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class SiteEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("网站列表编辑器")
        self.root.geometry("800x600")

        # 数据变量
        self.sites = []
        self.current_index = -1

        # 创建UI
        self.create_widgets()

        # 加载数据
        self.load_data()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # 网站列表标题
        ttk.Label(control_frame, text="网站列表编辑器", font=('Arial', 14, 'bold')).pack(pady=(0, 15))

        # 网站名称输入
        ttk.Label(control_frame, text="网站名称:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(control_frame, textvariable=self.name_var, width=30)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        # URL输入
        ttk.Label(control_frame, text="URL:").pack(anchor=tk.W)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(control_frame, textvariable=self.url_var, width=30)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))

        # 换行符提示
        ttk.Label(control_frame, text="提示: 在名称中使用\\n实现换行", foreground="gray").pack(anchor=tk.W, pady=(0, 15))

        # 操作按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="添加", command=self.add_site).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="编辑", command=self.edit_site).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="删除", command=self.delete_site).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        btn_frame2 = ttk.Frame(control_frame)
        btn_frame2.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame2, text="上移", command=self.move_up).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame2, text="下移", command=self.move_down).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        ttk.Button(btn_frame2, text="保存", command=self.save_changes).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame2, text="取消", command=self.cancel_edit).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # 文件操作按钮
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, pady=(15, 5))

        ttk.Button(file_frame, text="保存到文件", command=self.save_to_file).pack(side=tk.LEFT, padx=2, fill=tk.X,
                                                                             expand=True)
        ttk.Button(file_frame, text="从文件加载", command=self.load_from_file).pack(side=tk.LEFT, padx=2, fill=tk.X,
                                                                               expand=True)

        # 右侧网站列表显示
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 网站列表
        self.tree = ttk.Treeview(list_frame, columns=("name", "url"), show="headings")
        self.tree.heading("name", text="网站名称")
        self.tree.heading("url", text="URL")
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("url", width=400, anchor=tk.W)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_data(self):
        try:
            with open("sites_data.js", "r", encoding="utf-8") as f:
                content = f.read()
                # 提取JSON部分
                json_str = content[content.find("["): content.rfind("]") + 1]
                self.sites = json.loads(json_str)
                self.update_list()
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或格式错误，使用默认数据
            self.sites = [
                {"name": "读取出错", "url": "没有sites_data.js文件"},
            ]
            self.update_list()

    def update_list(self):
        self.tree.delete(*self.tree.get_children())
        for site in self.sites:
            self.tree.insert("", tk.END, values=(site["name"], site["url"]))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_index = self.tree.index(selected[0])
            site = self.sites[self.current_index]
            self.name_var.set(site["name"])
            self.url_var.set(site["url"])
        else:
            self.current_index = -1
            self.name_var.set("")
            self.url_var.set("")

    def add_site(self):
        self.current_index = -1
        self.name_var.set("")
        self.url_var.set("")
        self.name_entry.focus()

    def edit_site(self):
        if self.current_index >= 0:
            self.name_entry.focus()

    def delete_site(self):
        if self.current_index >= 0:
            if messagebox.askyesno("确认", "确定要删除这个网站吗?"):
                self.sites.pop(self.current_index)
                self.update_list()
                self.current_index = -1
                self.name_var.set("")
                self.url_var.set("")

    def move_up(self):
        if self.current_index > 0:
            self.sites[self.current_index], self.sites[self.current_index - 1] = \
                self.sites[self.current_index - 1], self.sites[self.current_index]
            self.update_list()
            self.tree.selection_set(self.tree.get_children()[self.current_index - 1])

    def move_down(self):
        if 0 <= self.current_index < len(self.sites) - 1:
            self.sites[self.current_index], self.sites[self.current_index + 1] = \
                self.sites[self.current_index + 1], self.sites[self.current_index]
            self.update_list()
            self.tree.selection_set(self.tree.get_children()[self.current_index + 1])

    def save_changes(self):
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()

        if not name or not url:
            messagebox.showerror("错误", "网站名称和URL不能为空")
            return

        # 确保URL以http://或https://开头
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
            self.url_var.set(url)

        site = {"name": name, "url": url}

        if self.current_index >= 0:
            # 更新现有条目
            self.sites[self.current_index] = site
        else:
            # 添加新条目
            self.sites.append(site)

        self.update_list()

    def cancel_edit(self):
        if self.current_index >= 0:
            site = self.sites[self.current_index]
            self.name_var.set(site["name"])
            self.url_var.set(site["url"])
        else:
            self.name_var.set("")
            self.url_var.set("")

    def save_to_file(self):
        content = f"// 网站数据 - 由Python编辑器维护\nvar sitesData = {json.dumps(self.sites, ensure_ascii=False, indent=4)};"

        try:
            with open("sites_data.js", "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("成功", "数据已保存到sites_data.js")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错:\n{str(e)}")

    def load_from_file(self):
        filepath = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("JavaScript文件", "*.js"), ("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 提取JSON部分
                    json_str = content[content.find("["): content.rfind("]") + 1]
                    self.sites = json.loads(json_str)
                    self.update_list()
                messagebox.showinfo("成功", "数据已加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载文件时出错:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SiteEditor(root)
    root.mainloop()