'''
更新了界面
使用了Python标准库内的tkinter库、random库
使用了pyperclip库
'''

import tkinter  # 界面
import tkinter.ttk  # 加强界面
import tkinter.messagebox  # 弹窗库
import random  # 生成随机密码
import pyperclip  # 密码复制到剪切板

import pandas as pd
from tkinter import filedialog  # 显式导入filedialog以避免后续问题

'''
通用函数
'''


def 清空字符串空格(字符串):
    新字符串 = 字符串.replace(" ", "")
    return 新字符串


def 生成随机密码():
    小写字母 = "abcdefghijklmnopqrstuvwxyz"  # #密码组合
    大写字母 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    数字 = "0123456789"
    下划线 = "_"
    其他符号 = "~!@#$%^&*()-+=,."

    密码长度 = 8  # #密码长度
    密码组合 = 小写字母 + 大写字母 + 数字 + 下划线 + 其他符号  # #密码组合

    随机密码 = "".join(random.sample(密码组合, 密码长度))  # #生成随机密码

    # print(随机密码)    # #打印结果
    return 随机密码


def 表格数据清空(表格):
    表格 = 表格
    表格.delete(*表格.get_children())


def 表格数据加载(表格, 数据):
    表格 = 表格
    数据 = 数据
    表格数据清空(表格)
    for 行号, 数据行 in enumerate(数据):
        数据行.append("【复制密码】")
        数据行.append("【删除】")
        表格.insert("", 行号, text=str(行号 + 1), values=数据行)  # #给第0行添加数据，索引值可重复


'''
初始化变量
'''
密码本 = ""
列名 = ["平台", "账号", "密码", "备注", "复制密码", "删除"]

'''
选择密码本
'''
密码本 = r"密码本"
with open(密码本, "a", encoding='utf-8') as 文件:  # #读取密码本
    pass


def 读取密码本():
    数据 = []
    单行数据 = []
    with open(密码本, "r", encoding='utf-8') as 文件:  # #读取密码本
        for 行 in 文件:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            单行数据.append(平台)
            单行数据.append(账号)
            单行数据.append(密码)
            单行数据.append(备注)
            数据.append(单行数据)
            单行数据 = []
    return 数据


'''
模拟数据

数据 = [
    ["QQ", "123456789", "123456", "11155557777"],
    ["微信", "wuaipojie", "234567", "11155557777"],
    ["360", "wuaipojie", "345678", "无"],
    ["百度", "吾爱破解", "456789", "xxxxaaaa@qq.com"],
    ["抖音", "wuaidouyin", "douyin123", "无"],
    ["快手", "wuaikuaishou", "kuaishou123", "无"],
    ]
'''

'''
密码本界面
'''
密码本界面 = tkinter.Tk()
密码本界面.title("Python密码记录管理工具")  # #窗口标题
# 密码本界面.geometry("600x500+200+20")   # #窗口位置500后面是字母x

'''
占位标签
'''
占位标签1 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签1.grid(row=0, column=0)  # #格子布局(0,0)
占位标签2 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签2.grid(row=1, column=0)  # #格子布局(1,0)
占位标签3 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签3.grid(row=2, column=0)  # #格子布局(2,0)
占位标签4 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签4.grid(row=3, column=0)  # #格子布局(3,0)
占位标签5 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签5.grid(row=4, column=0)  # #格子布局(4,0)
占位标签6 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签6.grid(row=6, column=8)  # #格子布局(6,0)
占位标签7 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
占位标签7.grid(row=7, column=8)  # #格子布局(7,0)

右占位标签1 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签1.grid(row=0, column=9)  # #格子布局(0,9)
右占位标签2 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签2.grid(row=1, column=9)  # #格子布局(1,9)
右占位标签3 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签3.grid(row=2, column=9)  # #格子布局(2,9)
右占位标签4 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签4.grid(row=3, column=9)  # #格子布局(3,9)
右占位标签5 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签5.grid(row=4, column=9)  # #格子布局(4,9)
右占位标签6 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签6.grid(row=6, column=9)  # #格子布局(6,9)
右占位标签7 = tkinter.ttk.Label(密码本界面, text='        ')  # #占位
右占位标签7.grid(row=7, column=9)  # #格子布局(7,9)

'''
提示标签
'''
提示标签标题 = tkinter.ttk.Label(密码本界面, text="信息提示 : ", anchor='e')  # #创建
提示标签标题.grid(row=1, column=1, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)  # #格子布局(1,1)
提示标签 = tkinter.ttk.Label(密码本界面, text="欢迎使用Python密码记录管理工具!", anchor='w')  # #创建
提示标签.grid(row=1, column=2, columnspan=3, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)  # #格子布局(1,2)(1,3)(1,4)

'''
菜单
'''
平台标签 = tkinter.ttk.Label(密码本界面, text='平台')  # #创建
账号标签 = tkinter.ttk.Label(密码本界面, text='账号')  # #创建
密码标签 = tkinter.ttk.Label(密码本界面, text='密码(点击随机生成)')  # #创建
备注标签 = tkinter.ttk.Label(密码本界面, text='备注')  # #创建
平台输入框 = tkinter.ttk.Entry(密码本界面)  # #创建
账号输入框 = tkinter.ttk.Entry(密码本界面)  # #创建
密码输入框 = tkinter.ttk.Entry(密码本界面)  # #创建
备注输入框 = tkinter.ttk.Entry(密码本界面)  # #创建
查询输入框 = tkinter.ttk.Entry(密码本界面)  # #创建
查询按钮 = tkinter.ttk.Button(密码本界面, text="查询", width=8)  # #创建
添加按钮 = tkinter.ttk.Button(密码本界面, text="添加", width=8)  # #创建
修改按钮 = tkinter.ttk.Button(密码本界面, text="修改", width=8)  # #创建
重置按钮 = tkinter.ttk.Button(密码本界面, text="重置", width=8)  # #创建

平台标签.grid(row=2, column=1)  # #格子布局(2,1)
账号标签.grid(row=2, column=2)  # #格子布局(2,2)
密码标签.grid(row=2, column=3)  # #格子布局(2,3)
备注标签.grid(row=2, column=4)  # #格子布局(2,4)
平台输入框.grid(row=3, column=1)  # #格子布局(2,1)
账号输入框.grid(row=3, column=2)  # #格子布局(2,2)
密码输入框.grid(row=3, column=3)  # #格子布局(2,3)
备注输入框.grid(row=3, column=4)  # #格子布局(2,4)
查询输入框.grid(row=1, column=4)  # #格子布局(1,4)
添加按钮.grid(row=3, column=5)  # #格子布局(3,5)
修改按钮.grid(row=3, column=6)  # #格子布局(3,6)
重置按钮.grid(row=1, column=6)  # #格子布局(1,6)
查询按钮.grid(row=1, column=5)  # #格子布局(1,5)
'''
导出按钮
'''
导出按钮 = tkinter.ttk.Button(密码本界面, text="导出", width=8)  # #创建
导出按钮.grid(row=1, column=7)  # #格子布局(1,7)
'''
导入按钮
'''
导入按钮 = tkinter.ttk.Button(密码本界面, text="导入", width=8)
导入按钮.grid(row=1, column=8)

'''
表格
'''
密码表格滚动条 = tkinter.ttk.Scrollbar(密码本界面, orient='vertical')  # #创建表格滚动条对象
密码表格 = tkinter.ttk.Treeview(密码本界面, show='headings', yscrollcommand=密码表格滚动条.set)  # #创建表格对象
密码表格滚动条['command'] = 密码表格.yview
密码表格['show'] = 'headings'  # #消除第一行第一列空列
密码表格["columns"] = 列名  # #定义列
密码表格.column("平台", width=145, anchor='w')  # #设置列
密码表格.column("账号", width=145, anchor='w')
密码表格.column("密码", width=145, anchor='w')
密码表格.column("备注", width=145, anchor='w')
密码表格.column("复制密码", width=80, anchor='center')
密码表格.column("删除", width=60, anchor='center')
密码表格.heading("平台", text="平台")  # #设置当前列显示的表头名
密码表格.heading("账号", text="账号")
密码表格.heading("密码", text="密码")
密码表格.heading("备注", text="备注")
密码表格.heading("复制密码", text="")
密码表格.heading("删除", text="")
表格数据加载(密码表格, 读取密码本())
密码表格.grid(row=5, column=1, columnspan=7)  # #格子布局(5,0)(5,1)(5,2)(5,3)(5,4)(5,5)(5,7)
密码表格滚动条.grid(row=5, column=8, sticky='ns')  # #格子布局(5,8)
'''
执行动作
'''


def 重加载表格(event):
    数据 = []
    单行数据 = []
    with open(密码本, "r", encoding='utf-8') as 文件:  # #读取密码本
        for 行 in 文件:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            单行数据.append(平台)
            单行数据.append(账号)
            单行数据.append(密码)
            单行数据.append(备注)
            数据.append(单行数据)
            单行数据 = []
    表格数据加载(密码表格, 数据)
    数据 = []


def 查询操作(event):  # #当用户按下回车键时，打印输入框的内容
    print("查询操作!")
    查询的平台 = 清空字符串空格(查询输入框.get())  # #查询的平台
    数据 = []
    单行数据 = []
    with open(密码本, "r", encoding='utf-8') as 文件:  # #读取密码本
        for 行 in 文件:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            if 查询的平台.lower() in 平台.lower():  # #查询匹配成功
                单行数据.append(平台)
                单行数据.append(账号)
                单行数据.append(密码)
                单行数据.append(备注)
                数据.append(单行数据)
            单行数据 = []
    表格数据加载(密码表格, 数据)
    数据 = []
    提示标签.configure(text="查询成功!")  # #查询成功


def 查询重加载(event):  # #查询重加载
    print("查询操作!")
    查询的平台 = 清空字符串空格(查询输入框.get())  # #查询的平台
    数据 = []
    单行数据 = []
    with open(密码本, "r", encoding='utf-8') as 文件:  # #读取密码本
        for 行 in 文件:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            if 查询的平台.lower() in 平台.lower():  # #查询匹配成功
                单行数据.append(平台)
                单行数据.append(账号)
                单行数据.append(密码)
                单行数据.append(备注)
                数据.append(单行数据)
            单行数据 = []
    表格数据加载(密码表格, 数据)
    数据 = []


def 添加密码(event):
    # print("添加密码!")

    ''' 读取输入框 '''
    平台输入框内容 = 清空字符串空格(平台输入框.get())  # #获取输入框的内容,并格式化
    账号输入框内容 = 清空字符串空格(账号输入框.get())  # #获取输入框的内容,并格式化
    密码输入框内容 = 清空字符串空格(密码输入框.get())  # #获取输入框的内容,并格式化
    备注输入框内容 = 清空字符串空格(备注输入框.get())  # #获取输入框的内容,并格式化
    if 备注输入框内容 == "":
        备注输入框内容 = "无"
    输入的平台账号 = str(平台输入框内容) + "x" + str(账号输入框内容)

    ''' 写入内容 '''
    if 平台输入框内容 != "" and 账号输入框内容 != "" and 密码输入框内容 != "" and 备注输入框内容 != "":
        数据 = 读取密码本()  # #读取密码本数据并检查是否有相同平台账号
        for 单行数据 in 数据:
            平台, 账号, 密码, 备注 = 单行数据[0], 单行数据[1], 单行数据[2], 单行数据[3]
            平台账号唯一性标志 = str(str(平台) + "x" + str(账号))
            if 输入的平台账号 == 平台账号唯一性标志:
                # print("添加失败,已存在相同的平台账号!")
                提示标签.configure(text="添加失败,已存在相同的平台账号!")
                return  # #有相同的直接退出

        with open(密码本, "a", encoding='utf-8') as 文件:  # #新平台账号直接添加
            文件.write(f"{平台输入框内容} {账号输入框内容} {密码输入框内容} {备注输入框内容}\n")
        # print("添加成功!")
        提示标签.configure(text="添加成功!")
        平台输入框.delete(0, tkinter.END)  # #清空
        账号输入框.delete(0, tkinter.END)  # #清空
        密码输入框.delete(0, tkinter.END)  # #清空
        备注输入框.delete(0, tkinter.END)  # #清空
    else:
        # print("添加失败,有输入框未填写!")
        提示标签.configure(text="添加失败,有输入框未填写!")


def 重置输入框(event):
    print("重置输入框!")
    查询输入框.delete(0, tkinter.END)
    平台输入框.delete(0, tkinter.END)
    账号输入框.delete(0, tkinter.END)
    密码输入框.delete(0, tkinter.END)
    备注输入框.delete(0, tkinter.END)
    查询的平台 = 清空字符串空格(查询输入框.get())  # #查询的平台
    数据 = []
    单行数据 = []
    with open(密码本, "r", encoding='utf-8') as 文件:  # #读取密码本
        for 行 in 文件:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            if 查询的平台.lower() in 平台.lower():  # #查询匹配成功
                单行数据.append(平台)
                单行数据.append(账号)
                单行数据.append(密码)
                单行数据.append(备注)
                数据.append(单行数据)
            单行数据 = []
    表格数据加载(密码表格, 数据)
    数据 = []
    提示标签.configure(text="重置成功!")


def 修改操作(event):
    print("修改操作!")
    选定行 = 密码表格.item(密码表格.focus())  # #当用户单击左键并弹起时，获得选中行全部内容
    if 选定行['values'] == '':
        return
    选定行标志 = str(选定行['values'][0]) + "x" + str(选定行['values'][1])

    平台输入框内容 = 清空字符串空格(平台输入框.get())  # 获取文本输入框的内容
    账号输入框内容 = 清空字符串空格(账号输入框.get())  # 获取文本输入框的内容
    密码输入框内容 = 清空字符串空格(密码输入框.get())  # 获取文本输入框的内容
    备注输入框内容 = 清空字符串空格(备注输入框.get())  # 获取文本输入框的内容

    if 备注输入框内容 == "":
        备注输入框内容 = "无"
    修改后的内容 = str(平台输入框内容) + " " + str(账号输入框内容) + " " + str(密码输入框内容) + " " + str(备注输入框内容) + "\n"

    if 平台输入框内容 != "" and 账号输入框内容 != "" and 密码输入框内容 != "":
        pass
    else:
        提示标签.configure(text="平台、账号或密码未填写!")
        return

    全部内容 = []
    with open(密码本, "r", encoding='utf-8') as 文件:
        for 行 in 文件:
            全部内容.append(行)

    for 行 in 全部内容:
        平台, 账号, 密码, 备注 = 行.strip().split(' ')
        if 选定行标志 == str(平台 + "x" + 账号):
            信息确认 = tkinter.messagebox.askquestion(title='注意!', message='确定修改吗!')  # 信息确认弹窗 是 yes或 否 no

    if 信息确认 == "yes":
        pass
    elif 信息确认 == "no":
        提示标签.configure(text="取消修改!")
        return

    with open(密码本, "w", encoding='utf-8') as 文件:
        for 行 in 全部内容:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            if 选定行标志 == str(平台 + "x" + 账号):
                文件.write(修改后的内容)
            else:
                文件.write(行)
    提示标签.configure(text="修改成功!")
    平台输入框.delete(0, tkinter.END)
    账号输入框.delete(0, tkinter.END)
    密码输入框.delete(0, tkinter.END)
    备注输入框.delete(0, tkinter.END)
    查询重加载(True)


def 操作密码表格(event):  # # #1平台 #2账号 #3密码 #4备注 #5复制密码 #6删除（以平台+分隔符"x"+账号合并起来为唯一标志）
    选定行 = 密码表格.item(密码表格.focus())  # #当用户单击左键并弹起时，获得选中行全部内容
    选定列号 = 密码表格.identify_column(event.x)  # #获得列号格式为字符串，例如 #1 #2 #3，第一列是#1
    if 选定行['values'] == '':
        return
    选定单元格内容 = 选定行['values'][int(选定列号[1:]) - 1]  # #获得选定单元格内容
    选定行标志 = str(选定行['values'][0]) + "x" + str(选定行['values'][1])

    # print(选定行['values'])        # #这个指的是选定行的内容
    # print(选定列号)        # #这个指的是选定列序号，从#1开始
    # print(选定单元格内容)        # #选定哪个单元格是哪个单元格内容
    # print(选定行标志)        # #这个指的是 平台x账号

    平台输入框.delete(0, tkinter.END)  # #清空
    账号输入框.delete(0, tkinter.END)  # #清空
    密码输入框.delete(0, tkinter.END)  # #清空
    备注输入框.delete(0, tkinter.END)  # #清空

    if 选定列号 == "#1" or 选定列号 == "#2" or 选定列号 == "#3" or 选定列号 == "#4":  # #第1234列是表格内容
        平台输入框.insert(0, str(选定行['values'][0]))  # #写入
        账号输入框.insert(0, str(选定行['values'][1]))  # #写入
        密码输入框.insert(0, str(选定行['values'][2]))  # #写入
        备注输入框.insert(0, str(选定行['values'][3]))  # #写入
        提示标签.configure(text="内容已读取!")


    elif 选定列号 == "#5":  # #第5列是复制
        print("复制密码!")
        pyperclip.copy(str(选定行['values'][2]))  # #密码放到剪切板
        提示标签.configure(text="密码已复制!")

    elif 选定列号 == "#6":  # #第6列是删除
        print("删除密码!")

        全部内容 = []
        with open(密码本, "r", encoding='utf-8') as 文件:
            for 行 in 文件:
                全部内容.append(行)

        查询的平台 = str(选定行['values'][0]) + "x" + str(选定行['values'][1])
        for 行 in 全部内容:
            平台, 账号, 密码, 备注 = 行.strip().split(' ')
            if 查询的平台 == str(平台 + "x" + 账号):
                print("有待删除的平台账号,确定删除吗!")
                信息确认 = tkinter.messagebox.askquestion(title='注意!', message='确定删除吗!')  # 信息确认弹窗 是 yes或 否 no

        if 信息确认 == "yes":
            pass
        elif 信息确认 == "no":
            提示标签.configure(text="取消删除!")
            return
        with open(密码本, "w", encoding='utf-8') as 文件:
            for 行 in 全部内容:
                平台, 账号, 密码, 备注 = 行.strip().split(' ')
                if 查询的平台 == str(平台 + "x" + 账号):
                    pass
                else:
                    文件.write(行)

        提示标签.configure(text="密码已删除!")
        查询重加载(True)


def 写入随机密码(event):
    随机密码 = 生成随机密码()
    提示标签.configure(text="随机密码已写入!")

    # 写入输入框
    密码输入框.delete(0, tkinter.END)
    密码输入框.insert(0, 随机密码)


def 导出到excel(event):
    # 读取表格中的数据
    数据 = []
    for 子 in 密码表格.get_children():
        行数据 = 密码表格.item(子)['values']
        数据.append(行数据)

    # 创建DataFrame
    df = pd.DataFrame(数据, columns=列名)

    # 导出到Excel文件
    try:
        df.to_excel("密码本.xlsx", index=False)
        提示标签.configure(text="导出成功!")
    except Exception as e:
        tkinter.messagebox.showerror("错误", f"导出失败: {str(e)}")


def 导入excel(event):
    try:
        # 读取Excel文件
        file_path = tkinter.filedialog.askopenfilename(title="选择Excel文件", filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        df = pd.read_excel(file_path)

        # 检查列名是否一致
        if list(df.columns) != 列名[:-2]:
            tkinter.messagebox.showerror("错误", "Excel文件的列名与程序要求不符！")
            return

        # 读取现有的密码本数据
        现有数据 = 读取密码本()

        # 检查并保存数据
        新增数据 = []  # 用于存储新的数据行
        for _, 行 in df.iterrows():
            平台, 账号, 密码, 备注 = 行[0], 行[1], 行[2], 行[3]
            平台账号唯一性标志 = str(平台) + "x" + str(账号)

            # 检查是否已存在相同的平台账号
            if any(平台账号唯一性标志 == str(平台) + "x" + str(账号) for 平台, 账号, _, _ in 现有数据):
                tkinter.messagebox.showwarning("警告", f"存在重复的平台账号: {平台} - {账号}")
                continue

            # 将数据添加到新增数据列表中
            新增数据.append(f"{平台} {账号} {密码} {备注}\n")

        # 如果有新增数据，则写入密码本
        if 新增数据:
            with open(密码本, "a", encoding='utf-8') as 文件:
                文件.writelines(新增数据)

        # 清空现有数据
        表格数据清空(密码表格)

        # 加载新数据
        表格数据加载(密码表格, df.values.tolist())

        提示标签.configure(text="导入成功!")
    except Exception as e:
        tkinter.messagebox.showerror("错误", f"导入失败: {str(e)}")


'''
动作绑定
'''
查询输入框.bind('<Return>', 查询操作)  # #绑定一个函数到回车键，当用户在输入框中按下回车键时触发

查询按钮.bind('<Button-1>', 查询操作)  # #绑定一个函数到左键，当用户在单击左键时触发

添加按钮.bind('<Button-1>', 添加密码)  # #绑定一个函数到左键，当用户在单击左键时触发

添加按钮.bind('<ButtonRelease-1>', 查询重加载)  # #绑定一个函数到左键，当用户在单击左键时触发

重置按钮.bind('<Button-1>', 重置输入框)  # #绑定一个函数到左键，当用户在单击左键时触发

修改按钮.bind('<Button-1>', 修改操作)  # #绑定一个函数到左键，当用户在单击左键时触发

密码表格.bind('<ButtonRelease-1>', 操作密码表格)  # #绑定一个函数到左键，当用户在单击左键后松开时触发

密码标签.bind('<ButtonRelease-1>', 写入随机密码)  # #绑定一个函数到左键，当用户在单击左键后松开时触发

导出按钮.bind('<Button-1>', 导出到excel)

导入按钮.bind('<Button-1>', 导入excel)

密码本界面.mainloop()  # #窗口持久化
