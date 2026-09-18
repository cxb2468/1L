import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog


class AdmissionQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高考录取查询系统")
        self.root.geometry("500x520")

        # 初始化文件路径变量
        self.scores_file = ""
        self.choices_file = ""

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 标题
        tk.Label(self.root, text="高考录取查询系统", font=('微软雅黑', 16)).pack(pady=10)

        # 文件选择部分
        tk.Label(self.root, text="1. 选择投档分数线表:").pack(anchor='w', padx=20, pady=5)
        self.scores_frame = tk.Frame(self.root)
        self.scores_frame.pack(fill=tk.X, padx=20)
        self.scores_entry = tk.Entry(self.scores_frame, width=40)
        self.scores_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(
            self.scores_frame,
            text="浏览...",
            command=lambda: self.select_file(self.scores_entry, "选择投档分数线表")
        ).pack(side=tk.LEFT)

        tk.Label(self.root, text="2. 选择考生志愿表:").pack(anchor='w', padx=20, pady=5)
        self.choices_frame = tk.Frame(self.root)
        self.choices_frame.pack(fill=tk.X, padx=20)
        self.choices_entry = tk.Entry(self.choices_frame, width=40)
        self.choices_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(
            self.choices_frame,
            text="浏览...",
            command=lambda: self.select_file(self.choices_entry, "选择考生志愿表")
        ).pack(side=tk.LEFT)

        # 分数和位次输入
        tk.Label(self.root, text="3. 输入考生总分:").pack(anchor='w', padx=20, pady=5)
        self.score_entry = tk.Entry(self.root, width=20)
        self.score_entry.pack(anchor='w', padx=20)

        tk.Label(self.root, text="4. 输入考生位次:").pack(anchor='w', padx=20, pady=5)
        self.rank_entry = tk.Entry(self.root, width=20)
        self.rank_entry.pack(anchor='w', padx=20)

        # 查询按钮
        self.query_btn = tk.Button(
            self.root,
            text="查询录取结果",
            command=self.query_admission,
            bg="#4CAF50",
            fg="white",
            font=('微软雅黑', 12),
            padx=20,
            pady=5
        )
        self.query_btn.pack(pady=20)

        # 结果显示
        self.result_label = tk.Label(
            self.root,
            text="请按步骤操作后查询",
            font=('微软雅黑', 12),
            wraplength=450,
            justify=tk.LEFT
        )
        self.result_label.pack(pady=20)

    def select_file(self, entry_widget, title):
        """选择文件并更新输入框"""
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[("Excel文件", "*.xls *.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def load_data(self):
        """加载Excel数据，支持.xls和.xlsx格式"""
        try:
            scores_path = self.scores_entry.get()
            choices_path = self.choices_entry.get()

            if not scores_path or not choices_path:
                messagebox.showwarning("警告", "请先选择投档分数线表和考生志愿表")
                return None, None

            # 自动检测文件格式并选择合适的引擎
            def read_excel_auto(path):
                if path.endswith('.xls'):
                    return pd.read_excel(path, engine='xlrd')
                else:
                    return pd.read_excel(path, engine='openpyxl')

            df_scores = read_excel_auto(scores_path)
            df_choices = read_excel_auto(choices_path).sort_values('序号')

            return df_scores, df_choices

        except Exception as e:
            messagebox.showerror("错误",
                                 f"加载数据失败:\n{str(e)}\n\n"
                                 "可能原因:\n"
                                 "1. 文件不是有效的Excel文件\n"
                                 "2. 文件已被其他程序打开\n"
                                 "3. 文件已损坏\n\n"
                                 "解决方案:\n"
                                 "1. 确认文件能正常用Excel打开\n"
                                 "2. 关闭已打开的文件\n"
                                 "3. 尝试另存为新Excel文件")
            return None, None

    def query_admission(self):
        """查询录取结果"""
        try:
            total_score = float(self.score_entry.get())
            rank = int(self.rank_entry.get())

            df_scores, df_choices = self.load_data()
            if df_scores is None or df_choices is None:
                return

            # 检查必要列是否存在
            required_columns = {
                'df_scores': ['学校代号', '专业代号', '分数线', '位次'],
                'df_choices': ['序号', '学校代码', '专业代码']
            }

            for df_name, cols in required_columns.items():
                df = locals()[df_name]
                for col in cols:
                    if col not in df.columns:
                        messagebox.showerror("错误", f"{df_name}中缺少必要列: {col}")
                        return

            # 遍历考生志愿表
            for _, choice in df_choices.iterrows():
                match = df_scores[
                    (df_scores['学校代号'] == choice['学校代码']) &
                    (df_scores['专业代号'] == choice['专业代码']) &
                    (df_scores['分数线'] <= total_score) &
                    (df_scores['位次'] >= rank)
                    ]

                if not match.empty:
                    school = match.iloc[0]['学校名称']
                    major = match.iloc[0]['专业名称']
                    self.result_label.config(
                        text=f"录取院校: {school}\n录取专业: {major}",
                        fg="green"
                    )
                    return

            self.result_label.config(
                text="很遗憾，您未被任何志愿录取\n\n"
                     "可能原因:\n"
                     "1. 分数未达到要求\n"
                     "2. 位次不符合要求\n"
                     "3. 志愿填报顺序问题",
                fg="red"
            )

        except ValueError:
            messagebox.showerror("错误", "请输入有效的分数和位次(数字)")
        except Exception as e:
            messagebox.showerror("错误", f"查询出错: {str(e)}")


if __name__ == "__main__":
    # 检查必要库是否安装
    required = {'xlrd': '1.2.0', 'openpyxl': '3.0.0', 'pandas': '1.0.0'}
    missing = []
    for lib, ver in required.items():
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)

    if missing:
        print(f"缺少依赖库: {', '.join(missing)}")
        print("请运行以下命令安装:")
        print("pip install xlrd openpyxl pandas")
        input("按Enter键退出...")
    else:
        root = tk.Tk()
        app = AdmissionQueryApp(root)
        root.mainloop()