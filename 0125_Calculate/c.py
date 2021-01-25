import tkinter
import tkinter.messagebox
import re
import math


#1、先定义一个面板  minsize 、 resizable、title

panel = tkinter.Tk()
panel.minsize(500,700)
panel.resizable(0,0)     # 00窗口最大化 禁用  True,True启用
panel.title("陈仙博的计算器")

#2、设置button 并放置到指定坐标上
# 第一行 ac  ← ^ + 按钮 格式，并放置到指定坐标
# bt = tkinter.Button(panel,text="",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "": buttonClick(x))
# bt.place(x=0,y=0,width=125,height=110)
btAc = tkinter.Button(panel,text="AC",font=("黑体",40),fg="orange",bd=0.5,command=lambda x = "AC": buttonClick(x))
btAc.place(x=0,y=150,width=125,height=110)

btBack = tkinter.Button(panel,text="←",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "←": buttonClick(x))
btBack.place(x=125,y=150,width=125,height=110)

btSquare = tkinter.Button(panel,text="^",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "^": buttonClick(x))
btSquare.place(x=250,y=150,width=125,height=110)

btPlus = tkinter.Button(panel,text="+",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "+": buttonClick(x))
btPlus.place(x=375,y=150,width=125,height=110)

#第二行
bt7 = tkinter.Button(panel,text="7",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "7": buttonClick(x))
bt7.place(x=0,y=260,width=125,height=110)
bt8 = tkinter.Button(panel,text="8",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "8": buttonClick(x))
bt8.place(x=125,y=260,width=125,height=110)
bt9 = tkinter.Button(panel,text="9",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "9": buttonClick(x))
bt9.place(x=250,y=260,width=125,height=110)
btMinus = tkinter.Button(panel,text="-",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "-": buttonClick(x))
btMinus.place(x=375,y=260,width=125,height=110)

# 第三行
bt4 = tkinter.Button(panel,text="4",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "4": buttonClick(x))
bt4.place(x=0,y=370,width=125,height=110)
bt5 = tkinter.Button(panel,text="5",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "5": buttonClick(x))
bt5.place(x=125,y=370,width=125,height=110)
bt6 = tkinter.Button(panel,text="6",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "6": buttonClick(x))
bt6.place(x=250,y=370,width=125,height=110)
btx = tkinter.Button(panel,text="x",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "x": buttonClick(x))
btx.place(x=375,y=370,width=125,height=110)

#第四行
bt1 = tkinter.Button(panel,text="1",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "1": buttonClick(x))
bt1.place(x=0,y=480,width=125,height=110)
bt2 = tkinter.Button(panel,text="2",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "2": buttonClick(x))
bt2.place(x=125,y=480,width=125,height=110)
bt3 = tkinter.Button(panel,text="3",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "3": buttonClick(x))
bt3.place(x=250,y=480,width=125,height=110)
btDivide = tkinter.Button(panel,text="÷",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "÷": buttonClick(x))
btDivide.place(x=375,y=480,width=125,height=110)

#第五行
btJin = tkinter.Button(panel,text="#",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "#": buttonClick(x))
btJin.place(x=0,y=590,width=125,height=110)
bt0 = tkinter.Button(panel,text="0",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "0": buttonClick(x))
bt0.place(x=125,y=590,width=125,height=110)
btDian = tkinter.Button(panel,text=".",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = ".": buttonClick(x))
btDian.place(x=250,y=590,width=125,height=110)
btEqual = tkinter.Button(panel,text="=",font=("微软雅黑",40),fg='#4F4F4F',bd=0.5,command=lambda x = "=": buttonClick(x))
btEqual.place(x=375,y=590,width=125,height=110)

#显示框
displayVar = tkinter.StringVar(panel,"")
displayEntry = tkinter.Entry(panel,textvariable=displayVar,state="readonly",font=("Arial",48))
displayEntry.place(x=0,y=20,width=500,height=100)




def buttonClick(bt):
    content = displayVar.get()
    operators = ("÷", "x", '-', '+', '=', '.')

    if bt in '01213456789':
        content += bt
    elif bt == ".":
        content += bt

    elif bt == "AC":
        content=""
    elif bt == "=":
        try:
            for operat in content:
                if operat == "÷":
                    content = content.replace("÷","/")
                elif operat == "x":
                    content = content.replace("x","*")
            value = eval(content)
            content = str(round(value,10))
        except:
            tkinter.messagebox("错误","VALUE ERROR!")
            return
    elif bt in operators:
        if content.endswith(operators):
            tkinter.messagebox("错误","FORMAT ERROR!")
            return
        content +=bt
    elif bt == "^":
        n = content.split(".")
        if  all(map(lambda x:x.isdigit(),n)):
            content = eval(content) * eval(content)
        else:
            tkinter.messagebox("错误","Input ERROR!")
            return

    elif bt == "←":
        content = content[0:-1]
    displayVar.set(content)











panel.mainloop()