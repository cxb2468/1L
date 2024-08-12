import pymysql
from tkinter import ttk
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
import tkinter.messagebox as messagebox


class StartPage:
    def __init__(self, parent_window):
        parent_window.destroy()

        self.window = Tk()
        self.window.title('图书馆管理系统')
        self.window.geometry('450x450')
        self.window.configure(bg="SkyBlue")
        label = Label(self.window, text="欢迎使用图书馆管理系统", font=("Verdana", 22), bg='LightSeaGreen')
        label.pack(pady=50)

        Button(self.window, text="管理员登陆", font=tkFont.Font(size=16), command=lambda: Adminpage(self.window), width=30,
               height=2,
               fg='white', bg='green', activebackground='black', activeforeground='white').pack()
        Button(self.window, text='学生登陆', font=tkFont.Font(size=16), command=lambda: StudentPage(self.window), width=30,
               height=2,
               fg='white', bg='green', activebackground='black', activeforeground='white').pack()
        Button(self.window, text='使用说明', font=tkFont.Font(size=16), command=lambda: AboutPage(self.window), width=30,
               height=2,
               fg='white', bg='green', activebackground='black', activeforeground='white').pack()
        self.window.mainloop()


class AboutPage:
    def __init__(self, parent_window):
        parent_window.destroy()

        self.window = tk.Tk()  # 初始框的声明
        self.window.title('使用说明')
        self.window.geometry('450x450')  # 这里的乘是小x
        self.window.configure(bg="SkyBlue")

        label = tk.Label(self.window, text='图书馆管理系统使用说明', bg='green', font=('Verdana', 20), width=30, height=2)
        label.pack()

        Label(self.window, text='1.系统用户由学生和管理员组成，\n学生账号并不是注册的而是管理员\n添加。管理员只有一个初始账号和\n密码均为123.',
              font=('Verdana', 18)).pack(pady=30)
        Label(self.window, text='2.系统初步实现了借书还书，图书\n管理（管理员），学生管理功能.', font=('Verdana', 18)).pack(padx=1, pady=5)
        Label(self.window, text='3.待开发功能为获取借书，还书时\n间等详细记录.', font=('Verdana', 18)).pack(padx=1, pady=5)
        Label(self.window, text='4.系统使用Mysql数据库进行开发', font=('Verdana', 18)).pack(padx=1, pady=5)
        Button(self.window, text="返回首页", width=8, font=tkFont.Font(size=12), command=self.back).pack(padx=1, pady=100)

        self.window.protocol("WM_DELETE_WINDOW", self.back)  # 捕捉右上角关闭点击


class Adminpage:  # 一个类里千万不要定义两个一样的方法呀！!!!!!
    def __init__(self, parent_window):
        parent_window.destroy()
        print('执行到Adminpage的第一个方法了')
        self.window = tk.Tk()
        self.window.title('管理员登陆页面')
        self.window.geometry('450x450')
        self.window.configure(bg="SkyBlue")
        label = tk.Label(self.window, text='管理员登陆', bg='green', font=('Verdana', 20), width=30, height=2)
        label.pack()
        Label(self.window, text='管理员账号: ', font=tkFont.Font(size=14)).pack(pady=25)
        self.admin_id = tk.Entry(self.window, width=30, font=tkFont.Font(size=14), bg='Ivory')
        self.admin_id.pack()

        Label(self.window, text='管理员密码: ', font=tkFont.Font(size=14)).pack(pady=25)
        self.admin_pass = tk.Entry(self.window, show='*', width=30, font=tkFont.Font(size=14), bg='Ivory')
        self.admin_pass.pack()

        Button(self.window, text='登陆', width=8, font=tkFont.Font(size=12), command=self.login).pack(padx=30, pady=40)
        Button(self.window, text='返回首页', width=8, font=tkFont.Font(size=12), command=self.back).pack(padx=30, pady=5)
        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def login(self):

        id = str(self.admin_id.get())
        pas = str(self.admin_pass.get())
        print("执行到Adminage的login方法了")
        print(id)
        print('**')
        print(pas)
        db = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             passwd='Cxb871231@',
                             charset='utf8mb4'
                             )

        cursor = db.cursor()
        cursor.execute("use library")
        sql = "select * from admin_login_k"

        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            print(row[0], ' ', row[1])
        f = 0
        for row in results:
            if id == row[0]:
                f = 1
                if pas == row[1]:
                    AdminManage(self.window)
                else:
                    messagebox.showinfo("警告", "密码错误!")
                    self.admin_pass.delete(0, END)
        if f == 0:
            messagebox.showinfo("警告", "用户名不存在")
            self.admin_id.delete(0, END)
            self.admin_pass.delete(0, END)

        db.close()

    def back(self):
        StartPage(self.window)  # 回到主窗口


class AdminManage:
    def __init__(self, parent_window):
        parent_window.destroy()

        self.window = Tk()
        self.window.title('管理员操作界面')
        self.window.configure(bg="SkyBlue")
        self.window.geometry('450x450')
        Button(self.window, text='学生管理', width=20, bg='green', font=tkFont.Font(size=30), command=self.Stu_Manage).grid(
            row=10, column=40, padx=30, pady=30)
        Button(self.window, text='图书管理', width=20, bg='green', font=tkFont.Font(size=30),
               command=self.Book_Manage).grid(row=20, column=40, padx=30, pady=30)
        Button(self.window, text='返回首页', width=20, bg='green', font=tkFont.Font(size=30), command=self.back).grid(
            row=30, column=40, padx=30, pady=30)

    def Stu_Manage(self):

        self.frame_left_top = tk.Frame(width=300, height=200)
        self.frame_right_top = tk.Frame(width=200, height=200)
        self.frame_center = tk.Frame(width=500, height=400)
        self.frame_bottom = tk.Frame(width=650, height=50)

        self.columns = ("学号", "姓名", "密码", "借阅数量")
        self.tree = ttk.Treeview(self.frame_center, show="headings", height=18, columns=self.columns)
        self.vbar = ttk.Scrollbar(self.frame_center, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vbar.set)

        self.tree.column("学号", width=150, anchor='center')
        self.tree.column("姓名", width=150, anchor='center')
        self.tree.column("密码", width=100, anchor='center')
        self.tree.column("借阅数量", width=100, anchor='center')

        self.tree.grid(row=0, column=0, sticky=NSEW)
        self.vbar.grid(row=0, column=1, sticky=NS)

        self.id = []
        self.name = []
        self.author = []
        self.count = []
        db = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             passwd='Cxb871231@',
                             charset='utf8'
                             )

        cursor = db.cursor()
        cursor.execute("use library")
        sql = "SELECT * FROM stu_k"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                self.id.append(row[0])
                self.name.append(row[1])
                self.author.append(row[2])
                self.count.append(row[3])
        except:
            print("Error: unable to fetch data")
            messagebox.showinfo('警告！', '数据库连接失败！')
        db.close()

        for i in range(min(len(self.id), len(self.name), len(self.author), len(self.count))):  # 写入数据
            self.tree.insert('', i, values=(self.id[i], self.name[i], '******', self.count[i]))

        for col in self.columns:
            self.tree.heading(col, text=col,
                              command=lambda _col=col: self.tree_sort_column1(self.tree, _col, False))

        self.top_title = Label(self.frame_left_top, text="学生信息:", font=('Verdana', 20))
        self.top_title.grid(row=0, column=0, columnspan=2, sticky=NSEW, padx=50, pady=10)

        self.left_top_frame = tk.Frame(self.frame_left_top)
        self.var_id = StringVar()
        self.var_name = StringVar()
        self.var_author = StringVar()
        self.var_count = StringVar()
        # 图书号
        self.right_top_id_label = Label(self.frame_left_top, text="学号：", font=('Verdana', 15))
        self.right_top_id_entry = Entry(self.frame_left_top, textvariable=self.var_id, font=('Verdana', 15))
        self.right_top_id_label.grid(row=1, column=0)
        self.right_top_id_entry.grid(row=1, column=1)
        # 书名
        self.right_top_name_label = Label(self.frame_left_top, text="姓名：", font=('Verdana', 15))
        self.right_top_name_entry = Entry(self.frame_left_top, textvariable=self.var_name, font=('Verdana', 15))
        self.right_top_name_label.grid(row=2, column=0)
        self.right_top_name_entry.grid(row=2, column=1)
        # 作者
        self.right_top_gender_label = Label(self.frame_left_top, text="密码：", font=('Verdana', 15))
        self.right_top_gender_entry = Entry(self.frame_left_top, show='*', textvariable=self.var_author,
                                            font=('Verdana', 15))
        self.right_top_gender_label.grid(row=3, column=0)
        self.right_top_gender_entry.grid(row=3, column=1)
        # 数量
        self.right_top_gender_label = Label(self.frame_left_top, text="借阅数量：", font=('Verdana', 15))
        self.right_top_gender_entry = Entry(self.frame_left_top, textvariable=self.var_count,
                                            font=('Verdana', 15))
        self.right_top_gender_label.grid(row=4, column=0)
        self.right_top_gender_entry.grid(row=4, column=1)

        # 定义右上方区域
        self.right_top_title = Label(self.frame_right_top, text="操作：", font=('Verdana', 20))

        self.tree.bind('<Button-1>', self.click1)
        self.right_top_button1 = ttk.Button(self.frame_right_top, text='新建学生信息', width=20, command=self.new_row1)
        self.right_top_button2 = ttk.Button(self.frame_right_top, text='更新选中学生信息', width=20,
                                            command=self.updata_row1)
        self.right_top_button3 = ttk.Button(self.frame_right_top, text='删除选中学生信息', width=20,
                                            command=self.del_row1)

        self.right_top_title.grid(row=1, column=0, pady=10)
        self.right_top_button1.grid(row=2, column=0, padx=20, pady=10)
        self.right_top_button2.grid(row=3, column=0, padx=20, pady=10)
        self.right_top_button3.grid(row=4, column=0, padx=20, pady=10)

        self.frame_left_top.grid(row=0, column=0, padx=2, pady=5)
        self.frame_right_top.grid(row=0, column=1, padx=30, pady=30)
        self.frame_center.grid(row=1, column=0, columnspan=2, padx=4, pady=5)
        self.frame_bottom.grid(row=2, column=0, columnspan=2)

        self.frame_left_top.grid_propagate(0)
        self.frame_right_top.grid_propagate(0)
        self.frame_center.grid_propagate(0)
        self.frame_bottom.grid_propagate(0)

        self.frame_left_top.tkraise()
        self.frame_right_top.tkraise()
        self.frame_center.tkraise()
        self.frame_bottom.tkraise()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def click1(self, event):
        self.col = self.tree.identify_column(event.x)
        self.row = self.tree.identify_row(event.y)

        print(self.col)
        print(self.row)
        self.row_info = self.tree.item(self.row, "values")
        self.var_id.set(self.row_info[0])
        self.var_name.set(self.row_info[1])
        self.var_author.set(self.row_info[2])
        self.var_count.set(self.row_info[3])
        self.right_top_id_entry = Entry(self.frame_left_top, state='disabled', textvariable=self.var_id,
                                        font=('Verdana', 15))

        print('')

    def tree_sort_column1(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.tree_sort_column(tv, col, not reverse))

    def new_row1(self):
        print('执行到AdminManet的new_row方法了')
        idd = self.var_id.get()
        namee = self.var_name.get()
        authorr = self.var_author.get()
        countt = self.var_count.get()
        print(idd)
        print(authorr)
        print(countt)
        print(namee)
        print(self.id)

        if str(self.var_id.get()) in self.id:
            messagebox.showinfo('警告', '该学生已存在!')
        else:
            if self.var_id.get() != '' and self.var_name.get() != '' and self.var_count.get() != '' and self.var_author.get() != '':
                db = pymysql.connect(host='localhost',  # 地址 本机127.0.0.1或localhost
                                     port=3306,  # 数据库的端口号 Navicat是3306
                                     user='root',
                                     passwd='Cxb871231@',
                                     charset='utf8'
                                     )

                cursor = db.cursor()
                cursor.execute("use library")

                sql = "insert into stu_k(id,name,password,count)\
                    values('%s','%s','%s','%s')" % \
                      (self.var_id.get(), self.var_name.get(), self.var_author.get(), self.var_count.get())
                cursor.execute(sql)
                db.commit()
                # try:
                #    print('提交数据库执行')
                #    cursor.execute(sql)
                #    db.commit()
                # except:
                #    db.rollback()
                #    messagebox.showinfo('警告', '数据库连接失败')
                db.close()
                self.id.append(self.var_id.get())
                self.name.append(self.var_name.get())
                self.author.append(self.var_author.get())
                self.count.append(self.var_count.get())
                self.tree.insert('', len(self.id) - 1, value=(
                    self.id[len(self.id) - 1], self.name[len(self.id) - 1], self.author[len(self.id) - 1],
                    self.count[len(self.id) - 1]))

                self.tree.update()
                messagebox.showinfo('提示!', '插入成功')

            else:
                messagebox.showinfo('警告', '请填写图书信息')

    def updata_row1(self):
        res = messagebox.askyesnocancel('警告！', '是否更新所填数据？')
        if res == True:
            if self.var_id.get() == self.row_info[0]:
                db = pymysql.connect(host='localhost',
                                     port=3306,
                                     user='root',
                                     passwd='Cxb871231@',
                                     charset='utf8'
                                     )

                cursor = db.cursor()
                cursor.execute("use library")
                sql = "UPDATE stu_k SET name = '%s', password = '%s', count = '%s' \
                        			 WHERE id = '%s'" % (
                    self.var_name.get(), self.var_author.get(), self.var_count.get(), self.var_id.get())

                try:
                    cursor.execute(sql)
                    db.commit()
                    messagebox.showinfo('提示！', '更新成功！')
                except:
                    db.rollback()  # 发生错误时回滚
                    messagebox.showinfo('警告！', '更新失败，数据库连接失败！')
                db.close()  # 关闭数据库连接

                id_index = self.id.index(self.row_info[0])
                self.name[id_index] = self.var_name.get()
                self.author[id_index] = self.var_author.get()
                self.count[id_index] = self.var_count.get()

                self.tree.item(self.tree.selection()[0], values=(
                    self.var_id.get(), self.var_name.get(), self.var_author.get(),
                    self.var_count.get()))  # 修改对于行信息
            else:
                messagebox.showinfo('警告！', '不能修改学生学号！')

    def del_row1(self):
        res = messagebox.askyesnocancel('警告！', '是否删除所选数据？')
        if res == True:
            print(self.row_info[0])
            print(self.tree.selection()[0])
            print(self.tree.get_children())
            db = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 passwd='Cxb871231@',
                                 charset='utf8'
                                 )

            cursor = db.cursor()
            cursor.execute("use library")
            sql = "DELETE FROM stu_k WHERE id = '%s'" % (self.row_info[0])
            try:
                cursor.execute(sql)
                db.commit()
                messagebox.showinfo('提示！', '删除成功！')
            except:
                db.rollback()  # 发生错误时回滚
                messagebox.showinfo('警告！', '删除失败，数据库连接失败！')
            db.close()

            id_index = self.id.index(self.row_info[0])
            print(id_index)
            del self.id[id_index]
            del self.name[id_index]
            del self.author[id_index]
            del self.count[id_index]
            print(self.id)
            self.tree.delete(self.tree.selection()[0])
            print(self.tree.get_children())

    def Book_Manage(self):
        self.frame_left_top = tk.Frame(width=300, height=200)
        self.frame_right_top = tk.Frame(width=200, height=200)
        self.frame_center = tk.Frame(width=500, height=400)
        self.frame_bottom = tk.Frame(width=650, height=50)

        self.columns = ("图书号", "书名", "作者", "数量")
        self.tree = ttk.Treeview(self.frame_center, show="headings", height=18, columns=self.columns)
        self.vbar = ttk.Scrollbar(self.frame_center, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vbar.set)

        self.tree.column("图书号", width=150, anchor='center')
        self.tree.column("书名", width=150, anchor='center')
        self.tree.column("作者", width=100, anchor='center')
        self.tree.column("数量", width=100, anchor='center')

        self.tree.grid(row=0, column=0, sticky=NSEW)
        self.vbar.grid(row=0, column=1, sticky=NS)

        self.id = []
        self.name = []
        self.author = []
        self.count = []
        db = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             passwd='Cxb871231@',
                             charset='utf8'
                             )

        cursor = db.cursor()
        cursor.execute("use library")
        sql = "SELECT * FROM book_k"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                self.id.append(row[0])
                self.name.append(row[1])
                self.author.append(row[2])
                self.count.append(row[3])
        except:
            print("Error: unable to fetch data")
            messagebox.showinfo('警告！', '数据库连接失败！')
        db.close()
        for i in range(min(len(self.id), len(self.name), len(self.author), len(self.count))):  # 写入数据
            self.tree.insert('', i, values=(self.id[i], self.name[i], self.author[i], self.count[i]))

        for col in self.columns:
            self.tree.heading(col, text=col,
                              command=lambda _col=col: self.tree_sort_column(self.tree, _col, False))

        self.top_title = Label(self.frame_left_top, text="图书信息:", font=('Verdana', 20))
        self.top_title.grid(row=0, column=0, columnspan=2, sticky=NSEW, padx=50, pady=10)

        self.left_top_frame = tk.Frame(self.frame_left_top)
        self.var_id = StringVar()
        self.var_name = StringVar()
        self.var_author = StringVar()
        self.var_count = StringVar()
        # 图书号
        self.right_top_id_label = Label(self.frame_left_top, text="图书号：", font=('Verdana', 15))
        self.right_top_id_entry = Entry(self.frame_left_top, textvariable=self.var_id, font=('Verdana', 15))
        self.right_top_id_label.grid(row=1, column=0)
        self.right_top_id_entry.grid(row=1, column=1)
        # 书名
        self.right_top_name_label = Label(self.frame_left_top, text="书名：", font=('Verdana', 15))
        self.right_top_name_entry = Entry(self.frame_left_top, textvariable=self.var_name, font=('Verdana', 15))
        self.right_top_name_label.grid(row=2, column=0)
        self.right_top_name_entry.grid(row=2, column=1)
        # 作者
        self.right_top_gender_label = Label(self.frame_left_top, text="作者：", font=('Verdana', 15))
        self.right_top_gender_entry = Entry(self.frame_left_top, textvariable=self.var_author,
                                            font=('Verdana', 15))
        self.right_top_gender_label.grid(row=3, column=0)
        self.right_top_gender_entry.grid(row=3, column=1)
        # 数量
        self.right_top_gender_label = Label(self.frame_left_top, text="数量：", font=('Verdana', 15))
        self.right_top_gender_entry = Entry(self.frame_left_top, textvariable=self.var_count,
                                            font=('Verdana', 15))
        self.right_top_gender_label.grid(row=4, column=0)
        self.right_top_gender_entry.grid(row=4, column=1)

        # 定义右上方区域
        self.right_top_title = Label(self.frame_right_top, text="操作：", font=('Verdana', 20))

        self.tree.bind('<Button-1>', self.click)
        self.right_top_button1 = ttk.Button(self.frame_right_top, text='新建图书信息', width=20, command=self.new_row)
        self.right_top_button2 = ttk.Button(self.frame_right_top, text='更新选中图书信息', width=20,
                                            command=self.updata_row)
        self.right_top_button3 = ttk.Button(self.frame_right_top, text='删除选中图书信息', width=20,
                                            command=self.del_row)

        self.right_top_title.grid(row=1, column=0, pady=10)
        self.right_top_button1.grid(row=2, column=0, padx=20, pady=10)
        self.right_top_button2.grid(row=3, column=0, padx=20, pady=10)
        self.right_top_button3.grid(row=4, column=0, padx=20, pady=10)

        self.frame_left_top.grid(row=0, column=0, padx=2, pady=5)
        self.frame_right_top.grid(row=0, column=1, padx=30, pady=30)
        self.frame_center.grid(row=1, column=0, columnspan=2, padx=4, pady=5)
        self.frame_bottom.grid(row=2, column=0, columnspan=2)

        self.frame_left_top.grid_propagate(0)
        self.frame_right_top.grid_propagate(0)
        self.frame_center.grid_propagate(0)
        self.frame_bottom.grid_propagate(0)

        self.frame_left_top.tkraise()
        self.frame_right_top.tkraise()
        self.frame_center.tkraise()
        self.frame_bottom.tkraise()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def back(self):
        StartPage(self.window)

    def click(self, event):
        self.col = self.tree.identify_column(event.x)
        self.row = self.tree.identify_row(event.y)

        print(self.col)
        print(self.row)
        self.row_info = self.tree.item(self.row, "values")
        self.var_id.set(self.row_info[0])
        self.var_name.set(self.row_info[1])
        self.var_author.set(self.row_info[2])
        self.var_count.set(self.row_info[3])
        self.right_top_id_entry = Entry(self.frame_left_top, state='disabled', textvariable=self.var_id,
                                        font=('Verdana', 15))

        print('')

    def tree_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.tree_sort_column(tv, col, not reverse))

    def new_row(self):
        print('执行到AdminManet的new_row方法了')
        print(self.var_id.get())
        print(self.var_name.get())
        print(self.var_author.get())
        print(self.var_count.get())
        print(self.id)

        if str(self.var_id.get()) in self.id:
            messagebox.showinfo('警告', '该图书已存在!')
        else:
            if self.var_id.get() != '' and self.var_name.get() != '' and self.var_count.get() != '' and self.var_author.get() != '':
                db = pymysql.connect(host='localhost',  # 地址 本机127.0.0.1或localhost
                                     port=3306,  # 数据库的端口号 Navicat是3306
                                     user='root',  # 用户 root
                                     passwd='Cxb871231@',  # 密码
                                     charset='utf8'
                                     )

                cursor = db.cursor()
                cursor.execute("use library")
                sql = "insert into book_k(id,name,author,count)\
                    values('%s','%s','%s','%s')" % \
                      (self.var_id.get(), self.var_name.get(), self.var_author.get(), self.var_count.get())
                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                    messagebox.showinfo('警告', '数据库连接失败')
                db.close()
                self.id.append(self.var_id.get())
                self.name.append(self.var_name.get())
                self.author.append(self.var_author.get())
                self.count.append(self.var_count.get())
                self.tree.insert('', len(self.id) - 1, value=(
                    self.id[len(self.id) - 1], self.name[len(self.id) - 1], self.author[len(self.id) - 1],
                    self.count[len(self.id) - 1]))

                self.tree.update()
                messagebox.showinfo('提示!', '插入成功')

            else:
                messagebox.showinfo('警告', '请填写图书信息')

    def updata_row(self):
        res = messagebox.askyesnocancel('警告！', '是否更新所填数据？')
        if res == True:
            if self.var_id.get() == self.row_info[0]:
                db = pymysql.connect(host='localhost',
                                     port=3306,
                                     user='root',
                                     passwd='Cxb871231@',
                                     charset='utf8'
                                     )

                cursor = db.cursor()
                cursor.execute("use library")
                sql = "UPDATE book_k SET name = '%s', author = '%s', count = '%s' \
        			 WHERE id = '%s'" % (
                    self.var_name.get(), self.var_author.get(), self.var_count.get(), self.var_id.get())
                try:
                    cursor.execute(sql)
                    db.commit()
                    messagebox.showinfo('提示！', '更新成功！')
                except:
                    db.rollback()  # 发生错误时回滚
                    messagebox.showinfo('警告！', '更新失败，数据库连接失败！')
                db.close()  # 关闭数据库连接

                id_index = self.id.index(self.row_info[0])
                self.name[id_index] = self.var_name.get()
                self.author[id_index] = self.var_author.get()
                self.count[id_index] = self.var_count.get()

                self.tree.item(self.tree.selection()[0], values=(
                    self.var_id.get(), self.var_name.get(), self.var_author.get(),
                    self.var_count.get()))  # 修改对于行信息
            else:
                messagebox.showinfo('警告！', '不能修改图书书号！')

    def del_row(self):
        res = messagebox.askyesnocancel('警告！', '是否删除所选数据？')
        if res == True:
            print(self.row_info[0])
            print(self.tree.selection()[0])
            print(self.tree.get_children())
            db = pymysql.connect(host='localhost',
                                 port=3306,
                                 user='root',
                                 passwd='Cxb871231@',
                                 charset='utf8'
                                 )

            cursor = db.cursor()
            cursor.execute("use library")
            sql = "DELETE FROM book_k WHERE id = '%s'" % (self.row_info[0])
            try:
                cursor.execute(sql)
                db.commit()
                messagebox.showinfo('提示！', '删除成功！')
            except:
                db.rollback()  # 发生错误时回滚
                messagebox.showinfo('警告！', '删除失败，数据库连接失败！')
            db.close()

            id_index = self.id.index(self.row_info[0])
            print(id_index)
            del self.id[id_index]
            del self.name[id_index]
            del self.author[id_index]
            del self.count[id_index]
            print(self.id)
            self.tree.delete(self.tree.selection()[0])
            print(self.tree.get_children())


class StudentPage:
    def __init__(self, parent_window):
        parent_window.destroy()

        self.window = tk.Tk()
        self.window.title('学生登陆')
        self.window.geometry('500x500')  # 这里的乘是小x
        self.window.configure(bg="SkyBlue")

        label = tk.Label(self.window, text='学生登陆', bg='green', font=('Verdana', 20), width=30, height=2)
        label.pack()

        Label(self.window, text='学生账号：', font=tkFont.Font(size=14)).pack(pady=25)
        self.student_id = tk.Entry(self.window, width=30, font=tkFont.Font(size=14), bg='Ivory')
        self.student_id.pack()

        Label(self.window, text='学生密码：', font=tkFont.Font(size=14)).pack(pady=25)
        self.student_pass = tk.Entry(self.window, width=30, font=tkFont.Font(size=14), bg='Ivory', show='*')
        self.student_pass.pack()

        Button(self.window, text="登陆", width=8, font=tkFont.Font(size=12), command=self.login).pack(pady=40)
        Button(self.window, text="返回首页", width=8, font=tkFont.Font(size=12), command=self.back).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def login(self):
        print(str(self.student_id.get()))
        print(str(self.student_pass.get()))
        id = str(self.student_id.get())
        pas = str(self.student_pass.get())

        db = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             passwd='Cxb871231@',
                             charset='utf8'
                             )
        cursor = db.cursor()
        cursor.execute("use library")
        sql = "SELECT * FROM stu_k "
        cursor.execute(sql)
        results = cursor.fetchall()
        student__id = self.student_id.get()
        f = 0
        for row in results:
            if id == row[0]:
                f = 1
                if pas == row[2]:
                    StudentView(self.window, self.student_id, student__id)
                else:
                    messagebox.showinfo("警告", "密码错误!")
                    self.admin_pass.delete(0, END)
        if f == 0:
            messagebox.showinfo("警告", "用户名不存在")
            self.admin_id.delete(0, END)
            self.admin_pass.delete(0, END)

    def back(self):
        StartPage(self.window)  # 显示主窗口 销毁本窗口


class StudentView:  # 实现借阅
    def __init__(self, parent_window, student_id, student__id):
        parent_window.destroy()
        print('获取一下账号：')
        print(student__id)
        self.student__id = student__id
        self.window = tk.Tk()
        self.window.configure(bg="SkyBlue")
        self.window.title('学生登陆界面')

        self.frame_left_top = tk.Frame(width=300, height=200)
        self.frame_right_top = tk.Frame(width=200, height=200)
        self.frame_center = tk.Frame(width=500, height=400)
        self.frame_bottom = tk.Frame(width=650, height=50)

        self.columns = ("图书号", "书名", "作者", "数量")
        self.tree = ttk.Treeview(self.frame_center, show="headings", height=18, columns=self.columns)
        self.vbar = ttk.Scrollbar(self.frame_center, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vbar.set)

        self.tree.column("图书号", width=150, anchor='center')
        self.tree.column("书名", width=150, anchor='center')
        self.tree.column("作者", width=100, anchor='center')
        self.tree.column("数量", width=100, anchor='center')

        self.tree.grid(row=0, column=0, sticky=NSEW)
        self.vbar.grid(row=0, column=1, sticky=NS)

        self.id = []
        self.name = []
        self.author = []
        self.count = []
        db = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             passwd='Cxb871231@',
                             charset='utf8'
                             )

        cursor = db.cursor()
        cursor.execute("use library")
        sql = "SELECT * FROM book_k"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                self.id.append(row[0])
                self.name.append(row[1])
                self.author.append(row[2])
                self.count.append(row[3])
        except:
            print("Error: unable to fetch data")
            messagebox.showinfo('警告！', '数据库连接失败！')
        db.close()
        for i in range(min(len(self.id), len(self.name), len(self.author), len(self.count))):  # 写入数据
            self.tree.insert('', i, values=(self.id[i], self.name[i], self.author[i], self.count[i]))

        for col in self.columns:
            self.tree.heading(col, text=col,
                              command=lambda _col=col: self.tree_sort_column(self.tree, _col, False))

        self.top_title = Label(self.frame_left_top, text="图书信息:", font=('Verdana', 20))
        self.top_title.grid(row=0, column=0, columnspan=2, sticky=NSEW, padx=50, pady=10)

        self.left_top_frame = tk.Frame(self.frame_left_top)
        self.var_id = StringVar()
        self.var_name = StringVar()
        self.var_author = StringVar()
        self.var_count = StringVar()
        # 图书号
        self.right_top_id_label = Label(self.frame_left_top, text="图书号：", font=('Verdana', 15))
        self.right_top_id_entry = Entry(self.frame_left_top, textvariable=self.var_id, font=('Verdana', 15))
        self.right_top_id_label.grid(row=1, column=0)
        self.right_top_id_entry.grid(row=1, column=1)
        # 书名
        self.right_top_name_label = Label(self.frame_left_top, text="书名：", font=('Verdana', 15))
        self.right_top_name_entry = Entry(self.frame_left_top, textvariable=self.var_name, font=('Verdana', 15))
        self.right_top_name_label.grid(row=2, column=0)
        self.right_top_name_entry.grid(row=2, column=1)
        # 作者
        self.right_top_gender_label = Label(self.frame_left_top, text="作者：", font=('Verdana', 15))
        self.right_top_gender_entry = Entry(self.frame_left_top, textvariable=self.var_author,
                                            font=('Verdana', 15))
        self.right_top_gender_label.grid(row=3, column=0)
        self.right_top_gender_entry.grid(row=3, column=1)
        # 数量
        self.right_top_gender_label = Label(self.frame_left_top, text="数量：", font=('Verdana', 15))
        self.right_top_gender_entry = Entry(self.frame_left_top, textvariable=self.var_count,
                                            font=('Verdana', 15))
        self.right_top_gender_label.grid(row=4, column=0)
        self.right_top_gender_entry.grid(row=4, column=1)

        # 定义右上方区域
        self.right_top_title = Label(self.frame_right_top, text="操作：", font=('Verdana', 20))

        self.tree.bind('<Button-1>', self.click)
        self.right_top_button1 = ttk.Button(self.frame_right_top, text='借书', width=20, command=self.borrow_row)
        self.right_top_button2 = ttk.Button(self.frame_right_top, text='还书', width=20,
                                            command=self.return_row)
        self.right_top_button3 = ttk.Button(self.frame_right_top, text='退出', width=20,
                                            command=self.del_row)

        self.right_top_title.grid(row=1, column=0, pady=10)
        self.right_top_button1.grid(row=2, column=0, padx=20, pady=10)
        self.right_top_button2.grid(row=3, column=0, padx=20, pady=10)
        self.right_top_button3.grid(row=4, column=0, padx=20, pady=10)

        self.frame_left_top.grid(row=0, column=0, padx=2, pady=5)
        self.frame_right_top.grid(row=0, column=1, padx=30, pady=30)
        self.frame_center.grid(row=1, column=0, columnspan=2, padx=4, pady=5)
        self.frame_bottom.grid(row=2, column=0, columnspan=2)

        self.frame_left_top.grid_propagate(0)
        self.frame_right_top.grid_propagate(0)
        self.frame_center.grid_propagate(0)
        self.frame_bottom.grid_propagate(0)

        self.frame_left_top.tkraise()
        self.frame_right_top.tkraise()
        self.frame_center.tkraise()
        self.frame_bottom.tkraise()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def back(self):
        StartPage(self.window)

    def del_row(self):
        StudentPage(self.window)

    def click(self, event):
        self.col = self.tree.identify_column(event.x)
        self.row = self.tree.identify_row(event.y)

        print(self.col)
        print(self.row)
        self.row_info = self.tree.item(self.row, "values")
        self.var_id.set(self.row_info[0])
        self.var_name.set(self.row_info[1])
        self.var_author.set(self.row_info[2])
        self.var_count.set(self.row_info[3])
        self.right_top_id_entry = Entry(self.frame_left_top, state='disabled', textvariable=self.var_id,
                                        font=('Verdana', 15))

        print('')

    def tree_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.tree_sort_column(tv, col, not reverse))

    def borrow_row(self):
        print(self.var_id.get())
        print(self.var_name.get())
        print(self.var_author.get())

        print(self.id)
        count = float(self.var_count.get())
        if count <= 0:
            messagebox.showinfo('抱歉', '这本书已经被借光了哦!')

        else:
            if self.var_id.get() != '' and self.var_name.get() != '' and self.var_count.get() != '' and self.var_author.get() != '':
                db = pymysql.connect(host='localhost',  # 地址 本机127.0.0.1或localhost
                                     port=3306,  # 数据库的端口号 Navicat是3306
                                     user='root',  # 用户 root
                                     passwd='Cxb871231@',  # 密码
                                     charset='utf8'
                                     )

                cursor = db.cursor()
                cursor.execute("use library")
                sql = "UPDATE book_k SET  count = '%s' \
                            			 WHERE id = '%s'" % (
                    count - 1, self.var_id.get())

                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                    messagebox.showinfo('警告', '数据库连接失败')
                cursor = db.cursor()
                cursor.execute("use library")
                sql = "UPDATE stu_k SET  count = count+1 \
                            			 WHERE id = '%s'" % (
                    self.student__id)
                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                    messagebox.showinfo('警告', '数据库连接失败')

                db.close()

                id_index = self.id.index(self.row_info[0])
                count_index = int(self.var_count.get()) - 1
                self.name[id_index] = self.var_name.get()
                self.author[id_index] = self.var_author.get()
                self.count[id_index] = str(count_index)

                self.tree.item(self.tree.selection()[0], values=(
                    self.var_id.get(), self.var_name.get(), self.var_author.get(),
                    str(count_index)))  # 修改对于行信息

                self.tree.update()
                messagebox.showinfo('提示!', '借书成功，请按时归还')

            else:
                messagebox.showinfo('警告', '请填写图书信息')

    def return_row(self):
        print(self.var_id.get())
        print(self.var_name.get())
        print(self.var_author.get())

        print(self.id)
        count = float(self.var_count.get())
        if count <= 0:
            messagebox.showinfo('抱歉', '这本书已经被借光了哦!')

        else:
            if self.var_id.get() != '' and self.var_name.get() != '' and self.var_count.get() != '' and self.var_author.get() != '':
                db = pymysql.connect(host='localhost',  # 地址 本机127.0.0.1或localhost
                                     port=3306,  # 数据库的端口号 Navicat是3306
                                     user='root',  # 用户 root
                                     passwd='Cxb871231@',  # 密码
                                     charset='utf8'
                                     )

                cursor = db.cursor()
                cursor.execute("use library")
                sql = "UPDATE book_k SET  count = '%s' \
                            			 WHERE id = '%s'" % (
                    count + 1, self.var_id.get())

                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                    messagebox.showinfo('警告', '数据库连接失败')
                cursor = db.cursor()
                cursor.execute("use library")
                sql = "UPDATE stu_k SET  count = count-1 \
                            			 WHERE id = '%s'" % (
                    self.student__id)
                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                    messagebox.showinfo('警告', '数据库连接失败')

                db.close()

                id_index = self.id.index(self.row_info[0])
                count_index = int(self.var_count.get()) + 1
                self.name[id_index] = self.var_name.get()
                self.author[id_index] = self.var_author.get()
                self.count[id_index] = str(count_index)

                self.tree.item(self.tree.selection()[0], values=(
                    self.var_id.get(), self.var_name.get(), self.var_author.get(),
                    str(count_index)))  # 修改对于行信息

                self.tree.update()
                messagebox.showinfo('提示!', '还书成功了呦')

            else:
                messagebox.showinfo('警告', '请填写图书信息')


# 还差借书还书，借书时间的功能
if __name__ == '__main__':
    try:
        print('开始执行')
        db = pymysql.connect(host='localhost',  # 地址 本机127.0.0.1或localhost
                             port=3306,  # 数据库的端口号 Navicat是3306
                             user='root',  # 用户 root
                             passwd='Cxb871231@',  # 密码
                             charset='utf8'
                             )

        cursor = db.cursor()
        sql = "CREATE SCHEMA if not exists `library` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
        cursor.execute(sql)
        cursor.execute("use library")
        sql = """CREATE TABLE IF NOT EXISTS book_k(
        		id char(20) NOT NULL,
        		name char(20) default NULL,
        		author char(5) default NULL,  
        		count int default NULL,
        		PRIMARY KEY (id)

        		) """
        cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS admin_login_k(
        					admin_id char(20) NOT NULL,
        					admin_pass char(20) default NULL,
        					PRIMARY KEY (admin_id)
        					) ENGINE = InnoDB 
        					DEFAULT	CHARSET = utf8
        					"""
        cursor.execute(sql)

        sql = """CREATE TABLE IF NOT EXISTS stu_k(
        				id char(20) NOT NULL,
        				name char(20) NOT NULL,
        				password char(20) default NULL,
        				count int not NULl,
        				PRIMARY KEY (id)
        				) ENGINE = InnoDB 
        				DEFAULT	CHARSET = utf8
        				"""
        cursor.execute(sql)

        try:
            sql = "INSERT INTO `library`.`admin_login_k` (`admin_id`, `admin_pass`) VALUES ('123', '123');"

            cursor.execute(sql)
            db.commit()
        except:
            print('已存在')
        try:
            sql = "INSERT INTO `library`.`book_k` (`id`, `name`, `author`, `count`) VALUES ('1001', '《python》', '于孟林', '10');"

            cursor.execute(sql)
            db.commit()
        except:
            print('已存在')
        try:
            sql = "INSERT INTO `library`.`stu_k` (`id`, `name`, `password`, `count`) VALUES ('123', '于孟林', '123', '0');"

            cursor.execute(sql)
            db.commit()
        except:
            print('已存在')

        db.close()
        window = tk.Tk()
        StartPage(window)

        window.mainloop()




    except:
        messagebox.showinfo('错误', '连接数据库失败')
