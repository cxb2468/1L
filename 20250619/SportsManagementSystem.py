import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
from collections import defaultdict
from openpyxl import Workbook


class SportsManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("运动会积分管理系统 v1.4 by [url=http://www.52pojie.cn]www.52pojie.cn[/url]")

        # 初始化数据结构
        self.grades = {}  # 存储年级和班级信息
        self.score_rules = {1: 7, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}  # 默认积分规则
        # 存储分数信息（年级->班级->详细信息）
        self.scores = defaultdict(lambda: defaultdict(lambda: {
            "total": 0,
            "manual": False  # 标记是否手动修改过
        }))
        self.details = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.history = []  # 操作历史（用于撤销）
        self.redo_stack = []  # 恢复栈（用于重做）
        self.current_grade = None  # 当前显示的年级

        # 初始化界面
        self.create_widgets()
        self.load_data()
        self.load_details()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # 确保窗口显示在最前
        self.root.after(100, self.root.deiconify)

    def create_widgets(self):
        """创建程序界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 控制按钮（修改退出按钮命令）
        buttons = [
            ("设置年级班级", self.set_grades_classes),
            ("设置积分规则", self.set_score_rules),
            ("添加比赛成绩", self.add_result),
            ("修改班级总分", self.modify_total_score),
            ("撤销操作", self.undo_last),
            ("恢复操作", self.redo_last),
            ("保存数据", self.save_data),  # 保留手动保存
            ("清空所有数据", self.clear_all_data),  # 新增清空数据按钮
            ("导出数据到 Excel", self.export_to_excel),
            ("退出系统", self.on_close)  # 改为调用关闭处理
        ]

        for text, cmd in buttons:
            ttk.Button(control_frame, text=text, command=cmd).pack(pady=5)

        # 右侧显示区域
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 年级选项卡
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    # 核心功能方法 --------------------------------------------------
    def set_grades_classes(self):
        """设置年级和班级"""
        input_str = simpledialog.askstring(
            "设置年级班级",
            "格式：年级:班级数（多个用逗号分隔）\n示例：1:5,2:6,3:4",
            parent=self.root
        )
        if input_str:
            try:
                self.grades.clear()
                for item in input_str.split(','):
                    grade, classes = item.strip().split(':')
                    self.grades[int(grade)] = [str(i + 1) for i in range(int(classes))]
                self.update_display()
                messagebox.showinfo("成功", "年级班级设置已更新", parent=self.root)
                self.auto_save_data()  # 自动保存数据
            except Exception as e:
                messagebox.showerror("输入错误", f"格式错误：{str(e)}", parent=self.root)

    def set_score_rules(self):
        """设置积分规则"""
        dialog = tk.Toplevel(self.root)
        dialog.transient(self.root)  # 设为子窗口
        dialog.grab_set()  # 独占焦点
        dialog.title("设置积分规则")

        # 显示当前规则
        ttk.Label(dialog, text="当前积分规则：").grid(row=0, column=0, padx=5, pady=5)
        rules_text = "\n".join([f"第{k}名：{v}分" for k, v in sorted(self.score_rules.items())])
        ttk.Label(dialog, text=rules_text).grid(row=0, column=1, padx=5, pady=5)

        # 输入新规则
        ttk.Label(dialog, text="输入新规则（格式：名次:积分，多个逗号分隔）：").grid(row=1, column=0, columnspan=2)
        entry = ttk.Entry(dialog, width=30)
        entry.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        def apply_rules():
            """应用新规则"""
            try:
                new_rules = {}
                for pair in entry.get().split(','):
                    pos, score = pair.strip().split(':')
                    new_rules[int(pos)] = int(score)
                self.score_rules = new_rules
                dialog.destroy()
                messagebox.showinfo("成功", "积分规则已更新", parent=self.root)
                self.auto_save_data()  # 自动保存数据
            except Exception as e:
                messagebox.showerror("输入错误", f"格式错误：{str(e)}", parent=dialog)

        ttk.Button(dialog, text="确定", command=apply_rules).grid(row=3, column=0, pady=5)
        ttk.Button(dialog, text="取消", command=dialog.destroy).grid(row=3, column=1, pady=5)

    def add_result(self):
        """添加比赛成绩"""
        if not self.grades:
            messagebox.showerror("错误", "请先设置年级班级", parent=self.root)
            return

        grade = simpledialog.askinteger("输入年级", "请输入年级：", parent=self.root)
        if grade not in self.grades:
            messagebox.showerror("错误", "该年级不存在", parent=self.root)
            return

        input_str = simpledialog.askstring(
            "输入比赛结果",
            "请输入各名次对应班级（格式：名次:班级，多个用逗号分隔）\n示例：1:3,2:5,3:1",
            parent=self.root
        )
        if not input_str:
            return

        entries = []
        try:
            for pair in input_str.split(','):
                pos, cls = pair.strip().split(':')
                pos = int(pos)
                if cls not in self.grades[grade]:
                    messagebox.showerror("错误", f"班级 {cls} 不存在", parent=self.root)
                    return
                entries.append((pos, cls))
        except Exception as e:
            messagebox.showerror("输入错误", f"格式错误：{str(e)}", parent=self.root)
            return

        # 记录操作历史
        history_entry = {'type': 'add', 'grade': grade, 'entries': []}
        valid_entries = False

        for pos, cls in entries:
            score = self.score_rules.get(pos, 0)
            if score > 0:
                self.scores[grade][cls]["total"] += score
                self.details[grade][cls][pos] += 1
                history_entry['entries'].append({'class': cls, 'position': pos, 'score': score})
                valid_entries = True

        if valid_entries:
            print(f"Updated details after adding result for class {cls} in grade {grade}:", self.details[grade][cls])
            self.history.append(history_entry)
            self.redo_stack.clear()
            self.update_display()
            self.show_grade_tab(grade)
            messagebox.showinfo("成功", "成绩添加成功", parent=self.root)
            self.auto_save_data()  # 自动保存数据
            self.save_details()
        else:
            messagebox.showinfo("提示", "没有有效成绩输入", parent=self.root)

    def modify_total_score(self):
        """手动修改班级总分"""
        if not self.grades:
            messagebox.showerror("错误", "请先设置年级班级", parent=self.root)
            return

        grade = simpledialog.askinteger("输入年级", "请输入年级：", parent=self.root)
        if grade not in self.grades:
            messagebox.showerror("错误", "该年级不存在", parent=self.root)
            return

        class_num = simpledialog.askstring(
            "输入班级",
            f"可选班级：{', '.join(self.grades[grade])}",
            parent=self.root
        )
        if class_num not in self.grades[grade]:
            messagebox.showerror("错误", "该班级不存在", parent=self.root)
            return

        old_total = self.scores[grade][class_num]["total"]
        new_total = simpledialog.askinteger(
            "修改总分",
            f"当前总分：{old_total}\n请输入新的总分：",
            parent=self.root,
            initialvalue=old_total
        )

        if new_total is not None and new_total >= 0:
            # 记录历史用于撤销
            self.history.append({
                'type': 'modify',
                'grade': grade,
                'class': class_num,
                'old_total': old_total,
                'new_total': new_total
            })

            self.scores[grade][class_num]["total"] = new_total
            self.scores[grade][class_num]["manual"] = True
            self.redo_stack.clear()
            self.update_display()
            self.show_grade_tab(grade)
            messagebox.showinfo("成功", "总分修改成功", parent=self.root)
            self.auto_save_data()  # 自动保存数据

    def undo_last(self):
        """撤销操作"""
        if not self.history:
            messagebox.showinfo("提示", "没有可撤销的操作", parent=self.root)
            return

        last_action = self.history.pop()
        self.redo_stack.append(last_action)

        # 兼容旧版本数据
        if 'type' not in last_action:
            last_action['type'] = 'add'

        if last_action['type'] == 'add':
            grade = last_action['grade']
            for entry in last_action['entries']:
                cls = entry['class']
                pos = entry['position']
                score = entry['score']
                self.scores[grade][cls]["total"] -= score
                self.details[grade][cls][pos] -= 1
                if self.details[grade][cls][pos] == 0:
                    del self.details[grade][cls][pos]
        elif last_action['type'] == 'modify':
            grade = last_action['grade']
            cls = last_action['class']
            self.scores[grade][cls]["total"] = last_action['old_total']
            self.scores[grade][cls]["manual"] = (last_action['old_total'] != 0)

        self.update_display()
        self.show_grade_tab(grade)
        messagebox.showinfo("成功", "已撤销上次操作", parent=self.root)
        self.auto_save_data()  # 自动保存数据
        self.save_details()

    def redo_last(self):
        """恢复操作"""
        if not self.redo_stack:
            messagebox.showinfo("提示", "没有可恢复的操作", parent=self.root)
            return

        last_action = self.redo_stack.pop()
        self.history.append(last_action)

        if last_action['type'] == 'add':
            grade = last_action['grade']
            for entry in last_action['entries']:
                cls = entry['class']
                pos = entry['position']
                score = entry['score']
                self.scores[grade][cls]["total"] += score
                self.details[grade][cls][pos] += 1
        elif last_action['type'] == 'modify':
            grade = last_action['grade']
            cls = last_action['class']
            self.scores[grade][cls]["total"] = last_action['new_total']
            self.scores[grade][cls]["manual"] = True

        self.update_display()
        self.show_grade_tab(grade)
        messagebox.showinfo("成功", "已恢复上次操作", parent=self.root)
        self.auto_save_data()  # 自动保存数据
        self.save_details()

    def update_display(self):
        """更新界面显示"""
        # 清空现有显示
        for child in self.notebook.winfo_children():
            child.destroy()

        if not self.grades:
            return

        # 为每个年级创建显示页
        for grade in sorted(self.grades.keys()):
            frame = ttk.Frame(self.notebook)
            # 将年级信息存储在frame中
            frame.grade = grade
            self.notebook.add(frame, text=f"{grade}年级")

            # 总积分表格
            total_score_frame = ttk.Frame(frame)
            total_score_frame.pack(fill=tk.BOTH, expand=True)

            total_score_tree = ttk.Treeview(
                total_score_frame,
                columns=("班级", "总积分"),
                show="headings"
            )
            vsb_total = ttk.Scrollbar(total_score_frame, orient="vertical", command=total_score_tree.yview)
            total_score_tree.configure(yscrollcommand=vsb_total.set)

            total_score_tree.heading("班级", text="班级")
            total_score_tree.heading("总积分", text="总积分")
            total_score_tree.column("班级", width=120, anchor='center')
            total_score_tree.column("总积分", width=120, anchor='center')

            total_score_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb_total.pack(side=tk.RIGHT, fill=tk.Y)

            # 插入总积分数据
            class_scores = [(cls, data["total"]) for cls, data in self.scores[grade].items()]
            for cls, score in sorted(class_scores, key=lambda x: x[1], reverse=True):
                total_score_tree.insert("", tk.END, values=(cls, score))

            # 单项成绩详情表格
            detail_frame = ttk.Frame(frame)
            detail_frame.pack(fill=tk.BOTH, expand=True)

            columns = ("班级", "第1名", "第2名", "第3名", "第4名", "第5名", "第6名")
            detail_tree = ttk.Treeview(
                detail_frame,
                columns=columns,
                show="headings"
            )
            vsb_detail = ttk.Scrollbar(detail_frame, orient="vertical", command=detail_tree.yview)
            detail_tree.configure(yscrollcommand=vsb_detail.set)

            for col in columns:
                detail_tree.heading(col, text=col)
                detail_tree.column(col, width=100, anchor='center')

            detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb_detail.pack(side=tk.RIGHT, fill=tk.Y)

            # 插入单项成绩详情数据
            for cls in sorted(self.grades[grade]):
                row_data = [cls]
                for pos in range(1, 7):
                    row_data.append(self.details[grade][cls].get(pos, 0))
                print(f"Inserting row data for class {cls} in grade {grade}:", row_data)
                detail_tree.insert("", tk.END, values=row_data)

    def save_data(self):
        """手动保存数据（保留原功能）"""
        data = {
            "grades": self.grades,
            "score_rules": self.score_rules,
            "scores": {
                str(grade): {
                    cls: {
                        "total": info["total"],
                        "manual": info["manual"]
                    } for cls, info in classes.items()
                } for grade, classes in self.scores.items()
            }
        }
        print("Saving data:", data)
        try:
            with open("sports_data.json", "w") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("成功", "数据已保存", parent=self.root)
        except Exception as e:
            messagebox.showerror("保存错误", f"数据保存失败：{str(e)}", parent=self.root)

    def auto_save_data(self):
        """自动保存数据（无提示，仅错误信息）"""
        data = {
            "grades": self.grades,
            "score_rules": self.score_rules,
            "scores": {
                str(grade): {
                    cls: {
                        "total": info["total"],
                        "manual": info["manual"]
                    } for cls, info in classes.items()
                } for grade, classes in self.scores.items()
            }
        }
        print("Auto saving data:", data)
        try:
            with open("sports_data.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("自动保存错误", f"数据保存失败：{str(e)}", parent=self.root)

    def load_data(self):
        """从文件加载数据"""
        try:
            with open("sports_data.json", "r") as f:
                data = json.load(f)
                print("Loaded data:", data)
                self.grades = {int(k): v for k, v in data["grades"].items()}
                # 修复积分规则键类型（字符串转整数）
                loaded_rules = data.get("score_rules", {})
                self.score_rules = {int(k): v for k, v in loaded_rules.items()}

                self.scores = defaultdict(lambda: defaultdict(lambda: {
                    "total": 0,
                    "manual": False
                }))
                for grade, classes in data["scores"].items():
                    for cls, info in classes.items():
                        self.scores[int(grade)][cls] = {
                            "total": info["total"],
                            "manual": info["manual"]
                        }
                self.update_display()
        except FileNotFoundError:
            print("Data file not found. Starting with default values.")
        except Exception as e:
            messagebox.showerror("加载错误", f"数据加载失败：{str(e)}", parent=self.root)

    def save_details(self):
        """保存单项成绩详情数据"""
        details_data = {
            str(grade): {
                cls: dict(details) for cls, details in classes.items()
            } for grade, classes in self.details.items()
        }
        try:
            with open("sports_details.json", "w") as f:
                json.dump(details_data, f, indent=2)
                print("Details data saved successfully.")
        except Exception as e:
            messagebox.showerror("保存错误", f"单项成绩详情数据保存失败：{str(e)}", parent=self.root)

    def load_details(self):
        """加载单项成绩详情数据"""
        try:
            with open("sports_details.json", "r") as f:
                details_data = json.load(f)
                print("Loaded details data:", details_data)
                self.details = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
                for grade, classes in details_data.items():
                    for cls, details in classes.items():
                        for pos, count in details.items():
                            try:
                                self.details[int(grade)][cls][int(pos)] = count
                            except ValueError:
                                print(f"Error converting key to int: grade={grade}, class={cls}, pos={pos}")
                self.update_display()
        except FileNotFoundError:
            print("Details data file not found. Starting with default values.")
        except Exception as e:
            messagebox.showerror("加载错误", f"单项成绩详情数据加载失败：{str(e)}", parent=self.root)

    def on_close(self):
        """窗口关闭时自动保存"""
        self.auto_save_data()
        self.save_details()
        self.root.destroy()

    def clear_all_data(self):
        """清空所有数据"""
        confirm = messagebox.askyesno("确认清空", "你确定要清空所有数据吗？此操作不可恢复。")
        if confirm:
            self.grades = {}
            self.score_rules = {1: 7, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
            self.scores = defaultdict(lambda: defaultdict(lambda: {
                "total": 0,
                "manual": False
            }))
            self.details = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
            self.history = []
            self.redo_stack = []
            self.update_display()
            self.auto_save_data()
            self.save_details()
            messagebox.showinfo("成功", "所有数据已清空", parent=self.root)

    def show_grade_tab(self, grade):
        """显示指定年级的选项卡"""
        for i in range(self.notebook.index(tk.END)):
            frame = self.notebook.nametowidget(self.notebook.tabs()[i])
            if hasattr(frame, 'grade') and frame.grade == grade:
                self.notebook.select(i)
                break

    def export_to_excel(self):
        """将数据导出到 Excel 文件"""
        try:
            wb = Workbook()
            # 删除默认的工作表
            default_sheet = wb.active
            wb.remove(default_sheet)

            for grade in sorted(self.grades.keys()):
                # 创建一个新的工作表
                ws = wb.create_sheet(title=f"{grade}年级")
                # 写入总积分表格标题
                ws.append(["班级", "总积分"])
                class_scores = [(cls, data["total"]) for cls, data in self.scores[grade].items()]
                for cls, score in sorted(class_scores, key=lambda x: x[1], reverse=True):
                    ws.append([cls, score])

                # 写入单项成绩详情表格标题
                ws.append([])  # 空行分隔
                ws.append(["班级", "第1名", "第2名", "第3名", "第4名", "第5名", "第6名"])
                for cls in sorted(self.grades[grade]):
                    row_data = [cls]
                    for pos in range(1, 7):
                        row_data.append(self.details[grade][cls].get(pos, 0))
                    ws.append(row_data)

            # 手动选择保存位置和名称
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                # 保存工作簿
                wb.save(file_path)
                messagebox.showinfo("成功", f"数据已成功导出到 {file_path}", parent=self.root)
            else:
                messagebox.showinfo("提示", "未选择保存路径，导出取消", parent=self.root)
        except Exception as e:
            messagebox.showerror("导出错误", f"数据导出失败：{str(e)}", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 初始隐藏窗口
    app = SportsManagementSystem(root)
    root.mainloop()