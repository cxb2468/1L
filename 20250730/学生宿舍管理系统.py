import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


class DormManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("学生宿舍管理系统")

        try:
            # 创建数据库连接
            self.conn = sqlite3.connect('dorm_management.db')
            self.create_tables()

            # 创建主界面
            self.create_gui()
        except Exception as e:
            messagebox.showerror("错误", f"系统初始化失败: {str(e)}")
            self.root.destroy()

    def create_tables(self):
        try:
            cursor = self.conn.cursor()
            # 创建学生信息表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT,
                dorm_number TEXT,
                bed_number INTEGER,
                check_in_date TEXT,
                phone TEXT,
                credits REAL
            )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"数据库表创建失败: {str(e)}")

    def create_gui(self):
        try:
            # 创建左侧输入框架
            input_frame = ttk.LabelFrame(self.root, text="学生信息录入", padding=10)
            input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

            # 创建搜索框架
            search_frame = ttk.LabelFrame(input_frame, text="搜索", padding=5)
            search_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

            ttk.Label(search_frame, text="学号/姓名:").pack(side=tk.LEFT, padx=5)
            self.search_entry = ttk.Entry(search_frame)
            self.search_entry.pack(side=tk.LEFT, padx=5)
            ttk.Button(search_frame, text="搜索", command=lambda: self.safe_callback(self.search_student)).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(search_frame, text="显示全部", command=lambda: self.safe_callback(self.update_display)).pack(
                side=tk.LEFT, padx=5)

            # 创建输入字段
            ttk.Label(input_frame, text="学号:").grid(row=1, column=0, sticky="w")
            self.student_id_entry = ttk.Entry(input_frame)
            self.student_id_entry.grid(row=1, column=1, padx=5, pady=2)

            ttk.Label(input_frame, text="姓名:").grid(row=2, column=0, sticky="w")
            self.name_entry = ttk.Entry(input_frame)
            self.name_entry.grid(row=2, column=1, padx=5, pady=2)

            ttk.Label(input_frame, text="性别:").grid(row=3, column=0, sticky="w")
            self.gender_var = tk.StringVar()
            ttk.Radiobutton(input_frame, text="男", variable=self.gender_var, value="男").grid(row=3, column=1,
                                                                                             sticky="w")
            ttk.Radiobutton(input_frame, text="女", variable=self.gender_var, value="女").grid(row=3, column=1,
                                                                                             sticky="e")

            ttk.Label(input_frame, text="宿舍号:").grid(row=4, column=0, sticky="w")
            self.dorm_entry = ttk.Entry(input_frame)
            self.dorm_entry.grid(row=4, column=1, padx=5, pady=2)

            ttk.Label(input_frame, text="床位号:").grid(row=5, column=0, sticky="w")
            self.bed_entry = ttk.Entry(input_frame)
            self.bed_entry.grid(row=5, column=1, padx=5, pady=2)

            ttk.Label(input_frame, text="电话:").grid(row=6, column=0, sticky="w")
            self.phone_entry = ttk.Entry(input_frame)
            self.phone_entry.grid(row=6, column=1, padx=5, pady=2)

            ttk.Label(input_frame, text="学分:").grid(row=7, column=0, sticky="w")
            self.credits_entry = ttk.Entry(input_frame)
            self.credits_entry.grid(row=7, column=1, padx=5, pady=2)

            # 创建按钮
            button_frame = ttk.Frame(input_frame)
            button_frame.grid(row=8, column=0, columnspan=2, pady=10)

            ttk.Button(button_frame, text="添加", command=lambda: self.safe_callback(self.add_student)).pack(side=tk.LEFT,
                                                                                                           padx=5)
            ttk.Button(button_frame, text="修改", command=lambda: self.safe_callback(self.update_student)).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="删除", command=lambda: self.safe_callback(self.delete_student)).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="清空", command=lambda: self.safe_callback(self.clear_entries)).pack(
                side=tk.LEFT, padx=5)

            # 创建右侧显示框架
            display_frame = ttk.LabelFrame(self.root, text="学生列表", padding=10)
            display_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            # 创建树形视图
            self.tree = ttk.Treeview(display_frame, columns=("学号", "姓名", "性别", "宿舍号", "床位号", "入住时间", "电话", "学分"),
                                     show="headings")

            # 设置列标题
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)

            self.tree.grid(row=0, column=0, sticky="nsew")

            # 添加滚动条
            scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.tree.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            self.tree.configure(yscrollcommand=scrollbar.set)

            # 绑定选择事件
            self.tree.bind("<<TreeviewSelect>>", lambda e: self.safe_callback(self.on_select))

            # 更新显示
            self.update_display()
        except Exception as e:
            raise Exception(f"界面创建失败: {str(e)}")

    def safe_callback(self, func):
        try:
            return func()
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"数据库操作失败: {str(e)}")
            return None
        except ValueError as e:
            messagebox.showerror("输入错误", f"输入数据格式错误: {str(e)}")
            return None
        except Exception as e:
            messagebox.showerror("系统错误", f"操作失败: {str(e)}")
            return None

    def search_student(self):
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.update_display()
            return

        try:
            # 清空现有显示
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 搜索并显示匹配的学生信息
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM students 
                WHERE student_id LIKE ? OR name LIKE ?
            """, (f"%{search_text}%", f"%{search_text}%"))

            results = cursor.fetchall()
            if not results:
                messagebox.showinfo("提示", "未找到匹配的学生信息")

            for student in results:
                self.tree.insert("", tk.END, values=student)
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}")

    def add_student(self):
        # 获取输入数据
        try:
            student_data = self.get_entry_data()
            if not all([student_data["student_id"], student_data["name"], student_data["gender"],
                        student_data["dorm_number"], student_data["bed_number"]]):
                raise ValueError("请填写所有必要信息！")

            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_data["student_id"], student_data["name"], student_data["gender"],
                  student_data["dorm_number"], student_data["bed_number"],
                  datetime.now().strftime("%Y-%m-%d"), student_data["phone"], student_data["credits"]))
            self.conn.commit()
            self.update_display()
            self.clear_entries()
            messagebox.showinfo("成功", "学生信息添加成功！")
        except sqlite3.IntegrityError:
            raise Exception("该学号已存在！")
        except Exception as e:
            raise Exception(f"添加失败: {str(e)}")

    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            raise Exception("请先选择要修改的学生！")

        try:
            student_data = self.get_entry_data()
            if not all([student_data["student_id"], student_data["name"], student_data["gender"],
                        student_data["dorm_number"], student_data["bed_number"]]):
                raise ValueError("请填写所有必要信息！")

            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE students 
            SET name=?, gender=?, dorm_number=?, bed_number=?, phone=?, credits=?
            WHERE student_id=?
            ''', (student_data["name"], student_data["gender"], student_data["dorm_number"],
                  student_data["bed_number"], student_data["phone"], student_data["credits"],
                  student_data["student_id"]))

            if cursor.rowcount == 0:
                raise Exception("未找到要更新的学生记录")

            self.conn.commit()
            self.update_display()
            self.clear_entries()
            messagebox.showinfo("成功", "学生信息更新成功！")
        except Exception as e:
            raise Exception(f"更新失败: {str(e)}")

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            raise Exception("请先选择要删除的学生！")

        try:
            if messagebox.askyesno("确认", "确定要删除选中的学生信息吗？"):
                student_id = self.tree.item(selected[0])["values"][0]
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))

                if cursor.rowcount == 0:
                    raise Exception("未找到要删除的学生记录")

                self.conn.commit()
                self.update_display()
                self.clear_entries()
                messagebox.showinfo("成功", "学生信息删除成功！")
        except Exception as e:
            raise Exception(f"删除失败: {str(e)}")

    def clear_entries(self):
        try:
            self.student_id_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.gender_var.set("")
            self.dorm_entry.delete(0, tk.END)
            self.bed_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.credits_entry.delete(0, tk.END)
            self.search_entry.delete(0, tk.END)
        except Exception as e:
            raise Exception(f"清空输入框失败: {str(e)}")

    def get_entry_data(self):
        try:
            bed_number = self.bed_entry.get()
            credits = self.credits_entry.get() or 0

            # 验证床位号为整数
            if bed_number:
                bed_number = int(bed_number)

            # 验证学分为数字
            if credits:
                credits = float(credits)

            return {
                "student_id": self.student_id_entry.get().strip(),
                "name": self.name_entry.get().strip(),
                "gender": self.gender_var.get(),
                "dorm_number": self.dorm_entry.get().strip(),
                "bed_number": bed_number,
                "phone": self.phone_entry.get().strip(),
                "credits": credits
            }
        except ValueError:
            raise ValueError("床位号必须为整数，学分必须为数字")
        except Exception as e:
            raise Exception(f"获取输入数据失败: {str(e)}")

    def update_display(self):
        try:
            # 清空现有显示
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 获取并显示所有学生信息
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM students")
            for student in cursor.fetchall():
                self.tree.insert("", tk.END, values=student)
        except Exception as e:
            raise Exception(f"更新显示失败: {str(e)}")

    def on_select(self):
        try:
            selected = self.tree.selection()
            if selected:
                values = self.tree.item(selected[0])["values"]
                self.student_id_entry.delete(0, tk.END)
                self.student_id_entry.insert(0, values[0])
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, values[1])
                self.gender_var.set(values[2])
                self.dorm_entry.delete(0, tk.END)
                self.dorm_entry.insert(0, values[3])
                self.bed_entry.delete(0, tk.END)
                self.bed_entry.insert(0, values[4])
                self.phone_entry.delete(0, tk.END)
                self.phone_entry.insert(0, values[6])
                self.credits_entry.delete(0, tk.END)
                self.credits_entry.insert(0, values[7])
        except Exception as e:
            raise Exception(f"选择记录失败: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = DormManagementSystem(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("系统错误", f"程序启动失败: {str(e)}")
        root.destroy()