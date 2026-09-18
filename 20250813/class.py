import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# 创建数据库和表结构
def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    # 创建表
    c.execute('''CREATE TABLE IF NOT EXISTS Classes 
                 (classID INTEGER PRIMARY KEY, className TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Courses 
                 (courseID INTEGER PRIMARY KEY, courseName TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Students 
                 (studentID INTEGER PRIMARY KEY, 
                  studentName TEXT, 
                  classID INTEGER,
                  FOREIGN KEY(classID) REFERENCES Classes(classID))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Teachers 
                 (teacherID INTEGER PRIMARY KEY, teacherName TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Schedules 
                 (scheduleID INTEGER PRIMARY KEY,
                  teacherID INTEGER,
                  courseID INTEGER,
                  classID INTEGER,
                  weekDay TEXT,
                  classTime TEXT,
                  remark TEXT,
                  FOREIGN KEY(teacherID) REFERENCES Teachers(teacherID),
                  FOREIGN KEY(courseID) REFERENCES Courses(courseID),
                  FOREIGN KEY(classID) REFERENCES Classes(classID))''')

    # 插入示例数据
    c.execute("INSERT OR IGNORE INTO Classes VALUES (1, '三年二班'), (2, '四年一班')")
    c.execute("INSERT OR IGNORE INTO Courses VALUES (1, '数学'), (2, '语文'), (3, '英语')")
    c.execute("INSERT OR IGNORE INTO Teachers VALUES (1, '张老师'), (2, '李老师')")
    c.execute("INSERT OR IGNORE INTO Students VALUES (1, '小明', 1), (2, '小红', 2)")
    c.execute("INSERT OR IGNORE INTO Schedules VALUES (1, 1, 1, 1, '星期一', '第1节', '重点讲解')")

    # 创建视图
    c.execute('''CREATE VIEW IF NOT EXISTS StudentCourseView AS
                 SELECT s.studentID, s.studentName, c.courseName, t.teacherName, cl.className,
                        sc.weekDay, sc.classTime, sc.remark
                 FROM Students s
                 JOIN Schedules sc ON s.classID = sc.classID
                 JOIN Courses c ON sc.courseID = c.courseID
                 JOIN Teachers t ON sc.teacherID = t.teacherID
                 JOIN Classes cl ON s.classID = cl.classID''')

    conn.commit()
    return conn


# 主界面
class SchoolApp:
    def __init__(self, root):
        self.conn = init_db()
        self.root = root
        self.root.title("教学管理系统")
        self.root.geometry("800x600")

        # 创建选项卡
        self.tabControl = ttk.Notebook(root)

        # 课程信息管理
        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='课程管理')
        self.create_course_management(self.tab1)

        # 学生信息管理
        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text='学生管理')
        self.create_student_management(self.tab2)

        # 教师信息管理
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='教师管理')
        self.create_teacher_management(self.tab3)

        # 排课管理
        self.tab4 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab4, text='排课管理')
        self.create_schedule_management(self.tab4)

        # 其他功能
        self.tab5 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab5, text='其他功能')
        self.create_other_functions(self.tab5)

        self.tabControl.pack(expand=1, fill="both")

    # 课程管理
    def create_course_management(self, parent):
        # 课程信息显示
        tk.Label(parent, text="课程信息").pack()
        self.course_tree = ttk.Treeview(parent, columns=("courseID", "courseName"), show="headings")
        self.course_tree.heading("courseID", text="课程ID")
        self.course_tree.heading("courseName", text="课程名称")
        self.course_tree.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 课程操作按钮框架
        course_btn_frame = tk.Frame(parent)
        course_btn_frame.pack(pady=5)
        
        tk.Button(course_btn_frame, text="查询全部", command=self.refresh_courses).grid(row=0, column=0, padx=5)
        tk.Button(course_btn_frame, text="新增", command=self.add_course).grid(row=0, column=1, padx=5)
        tk.Button(course_btn_frame, text="修改", command=self.update_course).grid(row=0, column=2, padx=5)
        tk.Button(course_btn_frame, text="删除", command=self.delete_course).grid(row=0, column=3, padx=5)
        
        # 课程输入框架
        course_input_frame = tk.Frame(parent)
        course_input_frame.pack(pady=5)
        
        tk.Label(course_input_frame, text="课程ID:").grid(row=0, column=0, padx=5)
        self.course_id_entry = tk.Entry(course_input_frame, width=10)
        self.course_id_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(course_input_frame, text="课程名称:").grid(row=0, column=2, padx=5)
        self.course_name_entry = tk.Entry(course_input_frame, width=20)
        self.course_name_entry.grid(row=0, column=3, padx=5)
        
        # 初始化显示课程信息
        self.refresh_courses()
        
        # 绑定选中事件
        self.course_tree.bind("<<TreeviewSelect>>", self.on_course_select)

    def on_course_select(self, event):
        selection = self.course_tree.selection()
        if selection:
            item = self.course_tree.item(selection[0])
            values = item["values"]
            self.course_id_entry.delete(0, tk.END)
            self.course_id_entry.insert(0, values[0])
            self.course_name_entry.delete(0, tk.END)
            self.course_name_entry.insert(0, values[1])

    def refresh_courses(self):
        for row in self.course_tree.get_children():
            self.course_tree.delete(row)
        c = self.conn.cursor()
        c.execute("SELECT * FROM Courses")
        for row in c.fetchall():
            self.course_tree.insert("", "end", values=row)

    def add_course(self):
        course_name = self.course_name_entry.get()
        if not course_name:
            messagebox.showerror("错误", "请输入课程名称")
            return

        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO Courses (courseName) VALUES (?)", (course_name,))
            self.conn.commit()
            self.refresh_courses()
            messagebox.showinfo("成功", "课程添加成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def update_course(self):
        course_id = self.course_id_entry.get()
        course_name = self.course_name_entry.get()
        
        if not course_id or not course_name:
            messagebox.showerror("错误", "请输入课程ID和课程名称")
            return

        try:
            c = self.conn.cursor()
            c.execute("UPDATE Courses SET courseName=? WHERE courseID=?", (course_name, course_id))
            self.conn.commit()
            self.refresh_courses()
            messagebox.showinfo("成功", "课程信息已更新")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_course(self):
        course_id = self.course_id_entry.get()
        if not course_id:
            messagebox.showerror("错误", "请输入要删除的课程ID")
            return

        try:
            c = self.conn.cursor()
            # 检查是否有排课关联此课程
            c.execute("SELECT COUNT(*) FROM Schedules WHERE courseID=?", (course_id,))
            count = c.fetchone()[0]
            if count > 0:
                messagebox.showwarning("警告", "该课程有关联的排课信息，不能删除")
                return
                
            c.execute("DELETE FROM Courses WHERE courseID=?", (course_id,))
            self.conn.commit()
            self.refresh_courses()
            # 清空输入框
            self.course_id_entry.delete(0, tk.END)
            self.course_name_entry.delete(0, tk.END)
            messagebox.showinfo("成功", "课程信息已删除")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 学生管理
    def create_student_management(self, parent):
        # 学生信息显示
        tk.Label(parent, text="学生信息").pack()
        self.student_tree = ttk.Treeview(parent,
                                         columns=("studentID", "studentName", "classID", "className"),
                                         show="headings")
        self.student_tree.heading("studentID", text="学生ID")
        self.student_tree.heading("studentName", text="学生姓名")
        self.student_tree.heading("classID", text="班级ID")
        self.student_tree.heading("className", text="班级名称")
        self.student_tree.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 学生操作按钮框架
        student_btn_frame = tk.Frame(parent)
        student_btn_frame.pack(pady=5)
        
        tk.Button(student_btn_frame, text="查询全部", command=self.refresh_students).grid(row=0, column=0, padx=5)
        tk.Button(student_btn_frame, text="新增", command=self.add_student).grid(row=0, column=1, padx=5)
        tk.Button(student_btn_frame, text="修改", command=self.update_student).grid(row=0, column=2, padx=5)
        tk.Button(student_btn_frame, text="删除", command=self.delete_student).grid(row=0, column=3, padx=5)
        
        # 学生输入框架
        student_input_frame = tk.Frame(parent)
        student_input_frame.pack(pady=5)
        
        tk.Label(student_input_frame, text="学生ID:").grid(row=0, column=0, padx=5)
        self.student_id_entry = tk.Entry(student_input_frame, width=10)
        self.student_id_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(student_input_frame, text="学生姓名:").grid(row=0, column=2, padx=5)
        self.student_name_entry = tk.Entry(student_input_frame, width=15)
        self.student_name_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(student_input_frame, text="班级ID:").grid(row=0, column=4, padx=5)
        self.student_class_id_entry = tk.Entry(student_input_frame, width=10)
        self.student_class_id_entry.grid(row=0, column=5, padx=5)
        
        # 初始化显示学生信息
        self.refresh_students()
        
        # 绑定选中事件
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)

    def on_student_select(self, event):
        selection = self.student_tree.selection()
        if selection:
            item = self.student_tree.item(selection[0])
            values = item["values"]
            self.student_id_entry.delete(0, tk.END)
            self.student_id_entry.insert(0, values[0])
            self.student_name_entry.delete(0, tk.END)
            self.student_name_entry.insert(0, values[1])
            self.student_class_id_entry.delete(0, tk.END)
            self.student_class_id_entry.insert(0, values[2])

    def refresh_students(self):
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        c = self.conn.cursor()
        c.execute('''SELECT s.studentID, s.studentName, s.classID, c.className 
                     FROM Students s LEFT JOIN Classes c ON s.classID = c.classID''')
        for row in c.fetchall():
            self.student_tree.insert("", "end", values=row)

    def add_student(self):
        student_name = self.student_name_entry.get()
        class_id = self.student_class_id_entry.get()
        
        if not student_name:
            messagebox.showerror("错误", "请输入学生姓名")
            return
            
        try:
            class_id = int(class_id) if class_id else None
        except ValueError:
            messagebox.showerror("错误", "班级ID必须是数字")
            return

        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO Students (studentName, classID) VALUES (?, ?)", (student_name, class_id))
            self.conn.commit()
            self.refresh_students()
            messagebox.showinfo("成功", "学生添加成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def update_student(self):
        student_id = self.student_id_entry.get()
        student_name = self.student_name_entry.get()
        class_id = self.student_class_id_entry.get()
        
        if not student_id or not student_name:
            messagebox.showerror("错误", "请输入学生ID和学生姓名")
            return
            
        try:
            class_id = int(class_id) if class_id else None
        except ValueError:
            messagebox.showerror("错误", "班级ID必须是数字")
            return

        try:
            c = self.conn.cursor()
            c.execute("UPDATE Students SET studentName=?, classID=? WHERE studentID=?", 
                      (student_name, class_id, student_id))
            self.conn.commit()
            self.refresh_students()
            messagebox.showinfo("成功", "学生信息已更新")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_student(self):
        student_id = self.student_id_entry.get()
        if not student_id:
            messagebox.showerror("错误", "请输入要删除的学生ID")
            return

        try:
            c = self.conn.cursor()
            c.execute("DELETE FROM Students WHERE studentID=?", (student_id,))
            self.conn.commit()
            self.refresh_students()
            # 清空输入框
            self.student_id_entry.delete(0, tk.END)
            self.student_name_entry.delete(0, tk.END)
            self.student_class_id_entry.delete(0, tk.END)
            messagebox.showinfo("成功", "学生信息已删除")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 教师管理
    def create_teacher_management(self, parent):
        # 教师信息显示
        tk.Label(parent, text="教师信息").pack()
        self.teacher_tree = ttk.Treeview(parent, columns=("teacherID", "teacherName"), show="headings")
        self.teacher_tree.heading("teacherID", text="教师ID")
        self.teacher_tree.heading("teacherName", text="教师姓名")
        self.teacher_tree.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 教师操作按钮框架
        teacher_btn_frame = tk.Frame(parent)
        teacher_btn_frame.pack(pady=5)
        
        tk.Button(teacher_btn_frame, text="查询全部", command=self.refresh_teachers).grid(row=0, column=0, padx=5)
        tk.Button(teacher_btn_frame, text="新增", command=self.add_teacher).grid(row=0, column=1, padx=5)
        tk.Button(teacher_btn_frame, text="修改", command=self.update_teacher).grid(row=0, column=2, padx=5)
        tk.Button(teacher_btn_frame, text="删除", command=self.delete_teacher).grid(row=0, column=3, padx=5)
        
        # 教师输入框架
        teacher_input_frame = tk.Frame(parent)
        teacher_input_frame.pack(pady=5)
        
        tk.Label(teacher_input_frame, text="教师ID:").grid(row=0, column=0, padx=5)
        self.teacher_id_entry = tk.Entry(teacher_input_frame, width=10)
        self.teacher_id_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(teacher_input_frame, text="教师姓名:").grid(row=0, column=2, padx=5)
        self.teacher_name_entry = tk.Entry(teacher_input_frame, width=20)
        self.teacher_name_entry.grid(row=0, column=3, padx=5)
        
        # 初始化显示教师信息
        self.refresh_teachers()
        
        # 绑定选中事件
        self.teacher_tree.bind("<<TreeviewSelect>>", self.on_teacher_select)

    def on_teacher_select(self, event):
        selection = self.teacher_tree.selection()
        if selection:
            item = self.teacher_tree.item(selection[0])
            values = item["values"]
            self.teacher_id_entry.delete(0, tk.END)
            self.teacher_id_entry.insert(0, values[0])
            self.teacher_name_entry.delete(0, tk.END)
            self.teacher_name_entry.insert(0, values[1])

    def refresh_teachers(self):
        for row in self.teacher_tree.get_children():
            self.teacher_tree.delete(row)
        c = self.conn.cursor()
        c.execute("SELECT * FROM Teachers")
        for row in c.fetchall():
            self.teacher_tree.insert("", "end", values=row)

    def add_teacher(self):
        teacher_name = self.teacher_name_entry.get()
        if not teacher_name:
            messagebox.showerror("错误", "请输入教师姓名")
            return

        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO Teachers (teacherName) VALUES (?)", (teacher_name,))
            self.conn.commit()
            self.refresh_teachers()
            messagebox.showinfo("成功", "教师添加成功")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def update_teacher(self):
        teacher_id = self.teacher_id_entry.get()
        teacher_name = self.teacher_name_entry.get()
        
        if not teacher_id or not teacher_name:
            messagebox.showerror("错误", "请输入教师ID和教师姓名")
            return

        try:
            c = self.conn.cursor()
            c.execute("UPDATE Teachers SET teacherName=? WHERE teacherID=?", (teacher_name, teacher_id))
            self.conn.commit()
            self.refresh_teachers()
            messagebox.showinfo("成功", "教师信息已更新")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_teacher(self):
        teacher_id = self.teacher_id_entry.get()
        if not teacher_id:
            messagebox.showerror("错误", "请输入要删除的教师ID")
            return

        try:
            c = self.conn.cursor()
            # 检查是否有排课关联此教师
            c.execute("SELECT COUNT(*) FROM Schedules WHERE teacherID=?", (teacher_id,))
            count = c.fetchone()[0]
            if count > 0:
                messagebox.showwarning("警告", "该教师有关联的排课信息，不能删除")
                return
                
            c.execute("DELETE FROM Teachers WHERE teacherID=?", (teacher_id,))
            self.conn.commit()
            self.refresh_teachers()
            # 清空输入框
            self.teacher_id_entry.delete(0, tk.END)
            self.teacher_name_entry.delete(0, tk.END)
            messagebox.showinfo("成功", "教师信息已删除")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 排课管理
    def create_schedule_management(self, parent):
        # 排课信息显示
        tk.Label(parent, text="排课信息").pack()
        self.schedule_tree = ttk.Treeview(parent,
                                          columns=(
                                          "scheduleID", "teacherName", "courseName", "className", "weekDay", "classTime",
                                          "remark"),
                                          show="headings")
        self.schedule_tree.heading("scheduleID", text="排课ID")
        self.schedule_tree.heading("teacherName", text="教师姓名")
        self.schedule_tree.heading("courseName", text="课程名称")
        self.schedule_tree.heading("className", text="班级名称")
        self.schedule_tree.heading("weekDay", text="星期")
        self.schedule_tree.heading("classTime", text="节次")
        self.schedule_tree.heading("remark", text="备注")
        self.schedule_tree.pack(padx=10, pady=10, fill="both", expand=True)

        # 排课操作按钮框架
        schedule_btn_frame = tk.Frame(parent)
        schedule_btn_frame.pack(pady=5)
        
        tk.Button(schedule_btn_frame, text="查询全部", command=self.refresh_schedules).grid(row=0, column=0, padx=5)
        tk.Button(schedule_btn_frame, text="新增", command=self.add_schedule).grid(row=0, column=1, padx=5)
        tk.Button(schedule_btn_frame, text="修改", command=self.update_schedule).grid(row=0, column=2, padx=5)
        tk.Button(schedule_btn_frame, text="删除", command=self.delete_schedule).grid(row=0, column=3, padx=5)

        # 排课输入框架
        schedule_input_frame = tk.Frame(parent)
        schedule_input_frame.pack(pady=5)

        tk.Label(schedule_input_frame, text="排课ID:").grid(row=0, column=0, padx=5)
        self.schedule_id_entry = tk.Entry(schedule_input_frame, width=10)
        self.schedule_id_entry.grid(row=0, column=1, padx=5)

        tk.Label(schedule_input_frame, text="教师ID:").grid(row=0, column=2, padx=5)
        self.schedule_teacher_id_entry = tk.Entry(schedule_input_frame, width=10)
        self.schedule_teacher_id_entry.grid(row=0, column=3, padx=5)

        tk.Label(schedule_input_frame, text="课程ID:").grid(row=0, column=4, padx=5)
        self.schedule_course_id_entry = tk.Entry(schedule_input_frame, width=10)
        self.schedule_course_id_entry.grid(row=0, column=5, padx=5)

        tk.Label(schedule_input_frame, text="班级ID:").grid(row=1, column=0, padx=5)
        self.schedule_class_id_entry = tk.Entry(schedule_input_frame, width=10)
        self.schedule_class_id_entry.grid(row=1, column=1, padx=5)

        tk.Label(schedule_input_frame, text="星期:").grid(row=1, column=2, padx=5)
        self.schedule_week_entry = tk.Entry(schedule_input_frame, width=10)
        self.schedule_week_entry.grid(row=1, column=3, padx=5)

        tk.Label(schedule_input_frame, text="节次:").grid(row=1, column=4, padx=5)
        self.schedule_time_entry = tk.Entry(schedule_input_frame, width=10)
        self.schedule_time_entry.grid(row=1, column=5, padx=5)

        tk.Label(schedule_input_frame, text="备注:").grid(row=2, column=0, padx=5)
        self.schedule_remark_entry = tk.Entry(schedule_input_frame, width=30)
        self.schedule_remark_entry.grid(row=2, column=1, columnspan=5, padx=5, sticky="w")
        
        # 初始化显示排课信息
        self.refresh_schedules()
        
        # 绑定选中事件
        self.schedule_tree.bind("<<TreeviewSelect>>", self.on_schedule_select)

    def on_schedule_select(self, event):
        selection = self.schedule_tree.selection()
        if selection:
            item = self.schedule_tree.item(selection[0])
            values = item["values"]
            self.schedule_id_entry.delete(0, tk.END)
            self.schedule_id_entry.insert(0, values[0])
            # 注意：显示的是名称，但数据库中存储的是ID
            # 这里仅用于显示基本信息，修改时仍需输入ID

    def refresh_schedules(self):
        for row in self.schedule_tree.get_children():
            self.schedule_tree.delete(row)
        c = self.conn.cursor()
        c.execute('''SELECT sc.scheduleID, t.teacherName, c.courseName, cl.className, 
                     sc.weekDay, sc.classTime, sc.remark
                     FROM Schedules sc
                     JOIN Teachers t ON sc.teacherID = t.teacherID
                     JOIN Courses c ON sc.courseID = c.courseID
                     JOIN Classes cl ON sc.classID = cl.classID''')
        for row in c.fetchall():
            self.schedule_tree.insert("", "end", values=row)

    def add_schedule(self):
        teacher_id = self.schedule_teacher_id_entry.get()
        course_id = self.schedule_course_id_entry.get()
        class_id = self.schedule_class_id_entry.get()
        week = self.schedule_week_entry.get()
        time = self.schedule_time_entry.get()
        remark = self.schedule_remark_entry.get()

        if not all([teacher_id, course_id, class_id, week, time]):
            messagebox.showerror("错误", "请填写所有必填字段")
            return

        try:
            # 检查外键是否存在
            c = self.conn.cursor()
            c.execute("SELECT COUNT(*) FROM Teachers WHERE teacherID=?", (teacher_id,))
            if c.fetchone()[0] == 0:
                messagebox.showerror("错误", "教师ID不存在")
                return
                
            c.execute("SELECT COUNT(*) FROM Courses WHERE courseID=?", (course_id,))
            if c.fetchone()[0] == 0:
                messagebox.showerror("错误", "课程ID不存在")
                return
                
            c.execute("SELECT COUNT(*) FROM Classes WHERE classID=?", (class_id,))
            if c.fetchone()[0] == 0:
                messagebox.showerror("错误", "班级ID不存在")
                return

            c.execute('''INSERT INTO Schedules 
                         (teacherID, courseID, classID, weekDay, classTime, remark)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (teacher_id, course_id, class_id, week, time, remark))
            self.conn.commit()
            self.refresh_schedules()
            messagebox.showinfo("成功", "排课信息已添加")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def update_schedule(self):
        schedule_id = self.schedule_id_entry.get()
        teacher_id = self.schedule_teacher_id_entry.get()
        course_id = self.schedule_course_id_entry.get()
        class_id = self.schedule_class_id_entry.get()
        week = self.schedule_week_entry.get()
        time = self.schedule_time_entry.get()
        remark = self.schedule_remark_entry.get()

        if not all([schedule_id, teacher_id, course_id, class_id, week, time]):
            messagebox.showerror("错误", "请填写所有字段")
            return

        try:
            c = self.conn.cursor()
            c.execute('''UPDATE Schedules SET 
                         teacherID=?, courseID=?, classID=?, weekDay=?, classTime=?, remark=?
                         WHERE scheduleID=?''',
                      (teacher_id, course_id, class_id, week, time, remark, schedule_id))
            self.conn.commit()
            self.refresh_schedules()
            messagebox.showinfo("成功", "排课信息已更新")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_schedule(self):
        schedule_id = self.schedule_id_entry.get()
        if not schedule_id:
            messagebox.showerror("错误", "请输入排课ID")
            return

        try:
            c = self.conn.cursor()
            c.execute("DELETE FROM Schedules WHERE scheduleID=?", (schedule_id,))
            self.conn.commit()
            self.refresh_schedules()
            # 清空输入框
            self.schedule_id_entry.delete(0, tk.END)
            self.schedule_teacher_id_entry.delete(0, tk.END)
            self.schedule_course_id_entry.delete(0, tk.END)
            self.schedule_class_id_entry.delete(0, tk.END)
            self.schedule_week_entry.delete(0, tk.END)
            self.schedule_time_entry.delete(0, tk.END)
            self.schedule_remark_entry.delete(0, tk.END)
            messagebox.showinfo("成功", "排课信息已删除")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    # 其他功能
    def create_other_functions(self, parent):
        # 计算班级课程数
        tk.Label(parent, text="计算班级课程数").pack()
        self.class_count_frame = tk.Frame(parent)
        self.class_count_frame.pack()

        tk.Label(self.class_count_frame, text="班级ID:").grid(row=0, column=0)
        self.class_count_id = tk.Entry(self.class_count_frame)
        self.class_count_id.grid(row=0, column=1)

        tk.Button(self.class_count_frame, text="计算", command=self.count_class_courses).grid(row=1, column=0, columnspan=2, pady=5)

        # 检查教师是否有课
        tk.Label(parent, text="检查教师节次").pack()
        self.teacher_time_frame = tk.Frame(parent)
        self.teacher_time_frame.pack()

        tk.Label(self.teacher_time_frame, text="教师ID:").grid(row=0, column=0)
        self.teacher_time_id = tk.Entry(self.teacher_time_frame)
        self.teacher_time_id.grid(row=0, column=1)

        tk.Label(self.teacher_time_frame, text="节次:").grid(row=1, column=0)
        self.teacher_time_slot = tk.Entry(self.teacher_time_frame)
        self.teacher_time_slot.grid(row=1, column=1)

        tk.Button(self.teacher_time_frame, text="检查", command=self.check_teacher_time).grid(row=2, column=0, columnspan=2, pady=5)

        # 生成课程表
        tk.Label(parent, text="生成课程表").pack()
        self.schedule_gen_frame = tk.Frame(parent)
        self.schedule_gen_frame.pack()

        tk.Label(self.schedule_gen_frame, text="类型:").grid(row=0, column=0)
        self.schedule_type = ttk.Combobox(self.schedule_gen_frame,
                                          values=["班级", "教师", "学生"])
        self.schedule_type.grid(row=0, column=1)

        tk.Label(self.schedule_gen_frame, text="ID:").grid(row=1, column=0)
        self.schedule_id = tk.Entry(self.schedule_gen_frame)
        self.schedule_id.grid(row=1, column=1)

        tk.Button(self.schedule_gen_frame, text="生成", command=self.generate_schedule).grid(row=2, column=0, columnspan=2, pady=5)

        self.schedule_result = ttk.Treeview(parent,
                                            columns=("scheduleID", "teacherName", "courseName", "className", "weekDay",
                                                     "classTime", "remark"),
                                            show="headings")
        self.schedule_result.heading("scheduleID", text="排课ID")
        self.schedule_result.heading("teacherName", text="教师姓名")
        self.schedule_result.heading("courseName", text="课程名称")
        self.schedule_result.heading("className", text="班级名称")
        self.schedule_result.heading("weekDay", text="星期")
        self.schedule_result.heading("classTime", text="节次")
        self.schedule_result.heading("remark", text="备注")
        self.schedule_result.pack(padx=10, pady=10, fill="both", expand=True)

    def count_class_courses(self):
        clid = self.class_count_id.get()
        if not clid:
            messagebox.showerror("错误", "请输入班级ID")
            return

        try:
            c = self.conn.cursor()
            c.execute("SELECT COUNT(*) FROM Schedules WHERE classID=?", (clid,))
            count = c.fetchone()[0]
            messagebox.showinfo("结果", f"该班级共有 {count} 门课程")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def check_teacher_time(self):
        tid = self.teacher_time_id.get()
        time = self.teacher_time_slot.get()
        if not all([tid, time]):
            messagebox.showerror("错误", "请输入完整信息")
            return

        try:
            c = self.conn.cursor()
            c.execute("SELECT COUNT(*) FROM Schedules WHERE teacherID=? AND classTime=?", (tid, time))
            result = c.fetchone()[0]
            if result > 0:
                messagebox.showwarning("警告", "该教师在该节次已有课程")
            else:
                messagebox.showinfo("结果", "该节次可用")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def generate_schedule(self):
        schedule_type = self.schedule_type.get()
        sid = self.schedule_id.get()

        if not all([schedule_type, sid]):
            messagebox.showerror("错误", "请选择类型并输入ID")
            return

        for row in self.schedule_result.get_children():
            self.schedule_result.delete(row)

        try:
            c = self.conn.cursor()

            if schedule_type == "班级":
                c.execute('''SELECT sc.scheduleID, t.teacherName, c.courseName, cl.className, 
                            sc.weekDay, sc.classTime, sc.remark
                            FROM Schedules sc
                            JOIN Teachers t ON sc.teacherID = t.teacherID
                            JOIN Courses c ON sc.courseID = c.courseID
                            JOIN Classes cl ON sc.classID = cl.classID
                            WHERE sc.classID = ?''', (sid,))
            elif schedule_type == "教师":
                c.execute('''SELECT sc.scheduleID, t.teacherName, c.courseName, cl.className, 
                            sc.weekDay, sc.classTime, sc.remark
                            FROM Schedules sc
                            JOIN Teachers t ON sc.teacherID = t.teacherID
                            JOIN Courses c ON sc.courseID = c.courseID
                            JOIN Classes cl ON sc.classID = cl.classID
                            WHERE sc.teacherID = ?''', (sid,))
            elif schedule_type == "学生":
                c.execute('''SELECT sc.scheduleID, t.teacherName, c.courseName, cl.className, 
                            sc.weekDay, sc.classTime, sc.remark
                            FROM Schedules sc
                            JOIN Teachers t ON sc.teacherID = t.teacherID
                            JOIN Courses c ON sc.courseID = c.courseID
                            JOIN Classes cl ON sc.classID = cl.classID
                            WHERE sc.classID = (SELECT classID FROM Students WHERE studentID = ?)''', (sid,))

            results = c.fetchall()

            for row in results:
                self.schedule_result.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("错误", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolApp(root)
    root.mainloop()