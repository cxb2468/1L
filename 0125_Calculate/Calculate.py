import tkinter as tk
import tkinter.messagebox
import re
import math
from functions import *


root = tk.Tk()
root.minsize(300, 400)      # 窗口大小300*400
root.resizable(0, 0)
root.title('Jhze的计算器')    # 计算器名字


# 运算符号按钮
# 第一行
btnac = tkinter.Button(root, text='AC', bd=0.5, font=('黑体', 20), fg='orange', command=lambda x='AC': buttonClick(x))
btnac.place(x=0, y=150, width=75, height=50)

btnback = tkinter.Button(root, text='←', font=('微软雅黑', 20), fg='#4F4F4F', bd=0.5, command=lambda \
        x='←': buttonClick(x))
btnback.place(x=75, y=150, width=75, height=50)
btndivi = tkinter.Button(root, text='^', font=('微软雅黑', 20), fg='#4F4F4F', bd=0.5, command=lambda \
        x='^': buttonClick(x))
btndivi.place(x=150, y=150, width=75, height=50)
btnmul = tkinter.Button(root, text='+', font=('微软雅黑', 20), fg="#4F4F4F", bd=0.5, command=lambda \
        x='+': buttonClick(x))
btnmul.place(x=225, y=150, width=75, height=50)
# 第二行
btn7 = tkinter.Button(root, text='7', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='7': buttonClick(x))
btn7.place(x=0, y=200, width=75, height=50)
btn8 = tkinter.Button(root, text='8', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='8': buttonClick(x))
btn8.place(x=75, y=200, width=75, height=50)
btn9 = tkinter.Button(root, text='9', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='9': buttonClick(x))
btn9.place(x=150, y=200, width=75, height=50)
btnsub = tkinter.Button(root, text='-', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='-': buttonClick(x))
btnsub.place(x=225, y=200, width=75, height=50)
# 第三行
btn4 = tkinter.Button(root, text='4', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='4': buttonClick(x))
btn4.place(x=0, y=250, width=75, height=50)
btn5 = tkinter.Button(root, text='5', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='5': buttonClick(x))
btn5.place(x=75, y=250, width=75, height=50)
btn6 = tkinter.Button(root, text='6', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='6': buttonClick(x))
btn6.place(x=150, y=250, width=75, height=50)
btnadd = tkinter.Button(root, text='×', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='×': buttonClick(x))
btnadd.place(x=225, y=250, width=75, height=50)
# 第四行
btn1 = tkinter.Button(root, text='1', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='1': buttonClick(x))
btn1.place(x=0, y=300, width=75, height=50)
btn2 = tkinter.Button(root, text='2', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='2': buttonClick(x))
btn2.place(x=75, y=300, width=75, height=50)
btn3 = tkinter.Button(root, text='3', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='3': buttonClick(x))
btn3.place(x=150, y=300, width=75, height=50)
btnechu = tkinter.Button(root, text='÷', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='÷': buttonClick(x))
btnechu.place(x=225, y=300, width=75, height=50)
# 第五行
btnper = tkinter.Button(root, text='高级', font=('微软雅黑', 20), fg='orange', bd=0.5,
                        command=lambda x='高级': buttonClick(x))
btnper.place(x=0, y=350, width=75, height=50)
btn0 = tkinter.Button(root, text='0', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='0': buttonClick(x))
btn0.place(x=75, y=350, width=75, height=50)
btnpoint = tkinter.Button(root, text='.', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
        x='.': buttonClick(x))
btnpoint.place(x=150, y=350, width=75, height=50)
btnequ = tkinter.Button(root, text='=', bg='orange', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5,
                        command=lambda x='=': buttonClick(x))
btnequ.place(x=225, y=350, width=75, height=50)


contentVar = tkinter.StringVar(root, '')
contentEntry = tkinter.Entry(root, textvariable=contentVar, state='readonly', font=("Arial", 12))
contentEntry.place(x=0, y=110, width=300, height=40)


def buttonClick(btn):
    content = contentVar.get()
    if content.startswith('.'):  # 小数点前加0
        content = '0' + content
    if btn in '0123456789':
        content += btn
    elif btn == '.':
        # lastPart = re.split(r'\+|-|\*|/', content)[-1]
        # if '.' in lastPart:
        #     tk.messagebox.showerror('错误', 'Input Error')
        #     return
        # else:
            content += btn

    elif btn == 'AC':
        content = ''
    elif btn == '=':
        try:
            for operat in content:
                if operat == '÷':
                    content = content.replace('÷', '/')
                elif operat == '×':
                    content = content.replace('×', '*')
            value = eval(content)
            content = str(round(value, 10))
        except:
            tk.messagebox.showerror('错误', 'VALUE ERROR')
            return
    elif btn in operators:
        if content.endswith(operators):
            tk.messagebox.showerror('错误', 'FORMAT ERROR')
            return
        content += btn
    elif btn == '^':
        n = content.split('.')
        if all(map(lambda x: x.isdigit(), n)):
            content = eval(content)*eval(content)
        else:
            tk.messagebox.showerror('错误', 'Input Error')
            return
    elif btn == '←':  # 如果按下的是退格‘’，则选取当前数字第一位到倒数第二位
        content = content[0:-1]
    elif btn == '高级':
        contentEntry.place(x=0, y=45, width=300, height=40) # 重新绘制输出框
        # 运算符号按钮
        # 第一行
        btncsc = tkinter.Button(root, text='csc', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='csc': buttonClick1(x))
        btncsc.place(x=0, y=85, width=60, height=45)
        btnrad = tkinter.Button(root, text='rad', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='rad': buttonClick1(x))
        btnrad.place(x=60, y=85, width=60, height=45)
        btnsin = tkinter.Button(root, text='sin', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='sin': buttonClick1(x))
        btnsin.place(x=120, y=85, width=60, height=45)
        btncos = tkinter.Button(root, text='cos', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='cos': buttonClick1(x))
        btncos.place(x=180, y=85, width=60, height=45)
        btntan = tkinter.Button(root, text='tan', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='tan': buttonClick1(x))
        btntan.place(x=240, y=85, width=60, height=45)
        # 第二行
        btnxsec = tkinter.Button(root, text='sec', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                 command=lambda x='sec': buttonClick1(x))
        btnxsec.place(x=0, y=130, width=60, height=45)
        btnlog = tkinter.Button(root, text='lg', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='lg': buttonClick1(x))
        btnlog.place(x=60, y=130, width=60, height=45)
        btnln = tkinter.Button(root, text='ln', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                               command=lambda x='ln': buttonClick1(x))
        btnln.place(x=120, y=130, width=60, height=45)
        btnleft = tkinter.Button(root, text='(', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                 command=lambda x='(': buttonClick1(x))
        btnleft.place(x=180, y=130, width=60, height=45)
        btnrigh = tkinter.Button(root, text=')', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5,
                                 command=lambda x=')': buttonClick1(x))
        btnrigh.place(x=240, y=130, width=60, height=45)
        # 第三行
        btnaxy = tkinter.Button(root, text='x^y', bd=0.5, font=('黑体', 20), bg=('#96CDCD'), command=lambda \
                x='x^y': buttonClick1(x))
        btnaxy.place(x=0, y=175, width=60, height=45)
        btnac.destroy()
        btnac1 = tkinter.Button(root, text='AC', bd=0.5, font=('黑体', 20), fg='orange', command=lambda \
                x='AC': buttonClick1(x))
        btnac1.place(x=60, y=175, width=60, height=45)
        btnback.destroy()
        btnback1 = tkinter.Button(root, text='←', font=('微软雅黑', 20), fg='#4F4F4F', bd=0.5, command=lambda \
                x='←': buttonClick1(x))
        btnback1.place(x=120, y=175, width=60, height=45)
        btndivi.destroy()
        btndivi1 = tkinter.Button(root, text='^', font=('微软雅黑', 20), fg='#4F4F4F', bd=0.5, command=lambda \
                x='^': buttonClick1(x))
        btndivi1.place(x=180, y=175, width=60, height=45)
        btnmul.destroy()
        btnmul1 = tkinter.Button(root, text='+', font=('微软雅黑', 20), fg="#4F4F4F", bd=0.5, command=lambda \
                x='+': buttonClick1(x))
        btnmul1.place(x=240, y=175, width=60, height=45)
        # 第四行
        btnx = tkinter.Button(root, text='X!', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5, command=lambda \
                 x='X!': buttonClick1(x))
        btnx.place(x=0, y=220, width=60, height=45)
        btn7.destroy()
        btn71 = tkinter.Button(root, text='7', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='7': buttonClick1(x))
        btn71.place(x=60, y=220, width=60, height=45)
        btn8.destroy()
        btn81 = tkinter.Button(root, text='8', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='8': buttonClick1(x))
        btn81.place(x=120, y=220, width=60, height=45)
        btn9.destroy()
        btn91 = tkinter.Button(root, text='9', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='9': buttonClick1(x))
        btn91.place(x=180, y=220, width=60, height=45)
        btnsub.destroy()
        btnsub1 = tkinter.Button(root, text='-', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='-': buttonClick1(x))
        btnsub1.place(x=240, y=220, width=60, height=45)
        # 第五行
        btn4x = tkinter.Button(root, text='1/X', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='1/X': buttonClick1(x))
        btn4x.place(x=0, y=265, width=60, height=45)
        btn4.destroy()
        btn41 = tkinter.Button(root, text='4', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='4': buttonClick1(x))
        btn41.place(x=60, y=265, width=60, height=45)
        btn5.destroy()
        btn51 = tkinter.Button(root, text='5', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='5': buttonClick1(x))
        btn51.place(x=120, y=265, width=60, height=45)
        btn6.destroy()
        btn61 = tkinter.Button(root, text='6', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='6': buttonClick1(x))
        btn61.place(x=180, y=265, width=60, height=45)
        btnadd.destroy()
        btnadd1 = tkinter.Button(root, text='×', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='×': buttonClick1(x))
        btnadd1.place(x=240, y=265, width=60, height=45)
        # 第六行
        btnpi = tkinter.Button(root, text='π', font=('微软雅黑', 20), bg=('#96CDCD'), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='π': buttonClick1(x))
        btnpi.place(x=0, y=310, width=60, height=45)
        btnpi.flash()
        btn1.destroy()
        btn11 = tkinter.Button(root, text='1', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='1': buttonClick1(x))
        btn11.place(x=60, y=310, width=60, height=45)
        btn2.destroy()
        btn21 = tkinter.Button(root, text='2', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='2': buttonClick1(x))
        btn21.place(x=120, y=310, width=60, height=45)
        btn3.destroy()
        btn31 = tkinter.Button(root, text='3', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='3': buttonClick1(x))
        btn31.place(x=180, y=310, width=60, height=45)
        btnechu.destroy()
        btnechu1 = tkinter.Button(root, text='÷', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='÷': buttonClick1(x))
        btnechu1.place(x=240, y=310, width=60, height=45)
        # 第七行
        btnperr = tkinter.Button(root, text='低级', font=('微软雅黑', 20), fg='orange', bd=0.5,
                                command=lambda x='低级': buttonClick1(x))
        btnperr.place(x=0, y=355, width=60, height=45)
        btnper.destroy()
        btnper1 = tkinter.Button(root, text='e', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='e': buttonClick1(x))
        btnper1.place(x=60, y=355, width=60, height=45)
        btn0.destroy()
        btn01 = tkinter.Button(root, text='0', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='0': buttonClick1(x))
        btn01.place(x=120, y=355, width=60, height=45)
        btnpoint.destroy()
        btnpoint1 = tkinter.Button(root, text='.', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                x='.': buttonClick1(x))
        btnpoint1.place(x=180, y=355, width=60, height=45)
        btnequ.destroy()
        btnequ1 = tkinter.Button(root, text='=', bg='orange', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5,
                                command=lambda x='=': buttonClick1(x))
        btnequ1.place(x=240, y=355, width=60, height=45)



        def buttonClick1(btn):
            content = contentVar.get()
            if content.startswith('.'):  # 小数点前加0
                content = '0' + content
            if btn in '0123456789()':
                content += btn
            elif btn == '.':
                lastPart = re.split(r'\+|-|\*|/', content)[-1]
                if '.' in lastPart:
                    tk.messagebox.showerror('错误', 'Input Error')
                    return
                else:
                    content += btn
            elif btn == '^':
                n = content.split('.')
                if all(map(lambda x: x.isdigit(), n)):
                    content = eval(content) * eval(content)
                else:
                    tk.messagebox.showerror('错误', 'Input Error')
                    return
            elif btn == 'AC':
                content = ''
            elif btn == '=':
                try:
                    for operat in content:
                        if operat == '÷':
                            content = content.replace('÷', '/')
                        elif operat == '×':
                            content = content.replace('×', '*')
                        elif operat == '^':
                            content = content.replace('^', '**')
                    strsin = r'sin\(\d+\)|sin\(\-?\d+\.\d+\)'
                    if 'sin' in content:
                        m = re.search(strsin, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                value = str(sin_t(float(value)))
                                content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                value = str(sin_t(float(value)))
                                content = content.replace(exchange1, value)
                    strcos = r'cos\(\d+\)|cos\(\-?\d+\.\d+\)'
                    if 'cos' in content:
                        m = re.search(strcos, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                value = str(cos_t(float(value)))
                                content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                value = str(cos_t(float(value)))
                                content = content.replace(exchange1, value)
                    strtan = r'tan\(\d+\)|tan\(\-?\d+\.\d+\)'
                    if 'tan' in content:
                        m = re.search(strtan, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                value = str(tan_t(float(value)))
                                content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                value = str(tan_t(float(value)))
                                content = content.replace(exchange1, value)
                    strsec = r'sec\(\-?\d+\)|sec\(\-?\d+\.\d+\)'
                    if 'sec' in content:
                        m = re.search(strsec, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                value = str(sec_t(float(value)))
                                content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                value = str(sec_t(float(value)))
                                content = content.replace(exchange1, value)
                    strcsc = r'csc\(\d+\)'
                    if 'csc' in content:
                        m = re.search(strcsc, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                value = str(csc_t(float(value)))
                                content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                value = str(csc_t(float(value)))
                                content = content.replace(exchange1, value)
                    strlg = r'lg\(\-?\d+\)|lg\(\-?\d+\.\d+\)'
                    if 'lg' in content:
                        m = re.search(strlg, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                if float(value) <= 0:
                                    tk.messagebox.showerror('错误', 'FORMAT ERROR')
                                else:
                                    value = str(lg_t(float(value)))
                                    content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                if int(value)<=0 :
                                    tk.messagebox.showerror('错误', 'FORMAT ERROR')
                                else:
                                    value = str(lg_t(float(value)))
                                    content = content.replace(exchange1, value)
                    strln = r'ln\(\-?\d+\)|ln\(\-?\d+\.\d+\)'
                    if 'ln' in content:
                        m = re.search(strln, content)
                        if m is not None:
                            exchange = m.group()
                            exchange1 = exchange
                            if '.' in exchange:
                                exchange = re.search("\-?\d+\.\d+", exchange)
                                value = exchange.group()
                                if float(value) <= 0:
                                    tk.messagebox.showerror('错误', 'FORMAT ERROR')
                                else:
                                    value = str(ln_t(float(value)))
                                    content = content.replace(exchange1, value)
                            else:
                                exchange = re.search("\-?\d+", exchange)
                                value = exchange.group()
                                if int(value) <= 0:
                                    tk.messagebox.showerror('错误', 'FORMAT ERROR')
                                else:
                                    value = str(ln_t(float(value)))
                                    content = content.replace(exchange1, value)
                    value = eval(content)
                    content = str(round(value, 10))
                except ZeroDivisionError:
                    tk.messagebox.showerror('错误', 'VALUE ERROR')
                    return
            elif btn in operators:
                if content.endswith(operators):
                    tk.messagebox.showerror('错误', 'FORMAT ERROR')
                    return
                content += btn
            elif btn == 'e':
                content = 2.7182818284
            elif btn == 'π':
                content = 3.1415926535
            elif btn == '1/X':
                content = reciprocal(float(content))
            elif btn == 'X!':
                content = factorial(int(content))
            elif btn == 'x^y':
                content += '^'
            elif btn == 'sin':
                content += 'sin('
            elif btn == 'cos':
                content += 'cos('
            elif btn == 'tan':
                content += 'tan('
            elif btn == 'sec':
                content += 'sec('
            elif btn == 'csc':
                content += 'csc('
            elif btn == 'lg':
                content += 'lg('
            elif btn == 'ln':
                content += 'ln('
            elif btn == '←':  # 如果按下的是退格‘’，则选取当前数字第一位到倒数第二位
                content = content[0:-1]

            elif btn == '低级':
                contentEntry.place(x=0, y=110, width=300, height=40)
                #第一行
                btncsc.destroy()
                btncsc.destroy()
                btnrad.destroy()
                btnsin.destroy()
                btncos.destroy()
                btntan.destroy()
                # 第二行
                btnxsec.destroy()
                btnlog.destroy()
                btnln.destroy()
                btnleft.destroy()
                btnrigh.destroy()
                # 第三行
                btnaxy.destroy()
                btnac1.destroy()
                btnback1.destroy()
                btndivi1.destroy()
                btnmul1.destroy()
                # 第四行
                btnx.destroy()
                btn71.destroy()
                btn81.destroy()
                btn91.destroy()
                btnsub1.destroy()
                # 第五行
                btn4x.destroy()
                btn41.destroy()
                btn51.destroy()
                btn61.destroy()
                btnadd1.destroy()
                # 第六行
                btnpi.destroy()
                btn11.destroy()
                btn21.destroy()
                btn31.destroy()
                btnechu1.destroy()
                # 第七行
                btnperr.destroy()
                btnper1.destroy()
                btn01.destroy()
                btnpoint1.destroy()
                btnequ1.destroy()
                # 第一行
                btnac = tkinter.Button(root, text='AC', bd=0.5, font=('黑体', 20), fg='orange', command=lambda \
                        x='AC': buttonClick(x))
                btnac.flash()
                btnac.place(x=0, y=150, width=75, height=50)
                btnback = tkinter.Button(root, text='←', font=('微软雅黑', 20), fg='#4F4F4F', bd=0.5, command=lambda \
                        x='←': buttonClick(x))
                btnback.place(x=75, y=150, width=75, height=50)
                btndivi = tkinter.Button(root, text='^', font=('微软雅黑', 20), fg='#4F4F4F', bd=0.5, command=lambda \
                        x='^': buttonClick(x))
                btndivi.place(x=150, y=150, width=75, height=50)
                btnmul = tkinter.Button(root, text='+', font=('微软雅黑', 20), fg="#4F4F4F", bd=0.5, command=lambda \
                        x='+': buttonClick(x))
                btnmul.place(x=225, y=150, width=75, height=50)
                # 第二行
                btn7 = tkinter.Button(root, text='7', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='7': buttonClick(x))
                btn7.place(x=0, y=200, width=75, height=50)
                btn8 = tkinter.Button(root, text='8', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='8': buttonClick(x))
                btn8.place(x=75, y=200, width=75, height=50)
                btn9 = tkinter.Button(root, text='9', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='9': buttonClick(x))
                btn9.place(x=150, y=200, width=75, height=50)
                btnsub = tkinter.Button(root, text='-', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='-': buttonClick(x))
                btnsub.place(x=225, y=200, width=75, height=50)
                # 第三行
                btn4 = tkinter.Button(root, text='4', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='4': buttonClick(x))
                btn4.place(x=0, y=250, width=75, height=50)
                btn5 = tkinter.Button(root, text='5', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='5': buttonClick(x))
                btn5.place(x=75, y=250, width=75, height=50)
                btn6 = tkinter.Button(root, text='6', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='6': buttonClick(x))
                btn6.place(x=150, y=250, width=75, height=50)
                btnadd = tkinter.Button(root, text='×', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='×': buttonClick(x))
                btnadd.place(x=225, y=250, width=75, height=50)
                # 第四行
                btn1 = tkinter.Button(root, text='1', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='1': buttonClick(x))
                btn1.place(x=0, y=300, width=75, height=50)
                btn2 = tkinter.Button(root, text='2', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='2': buttonClick(x))
                btn2.place(x=75, y=300, width=75, height=50)
                btn3 = tkinter.Button(root, text='3', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='3': buttonClick(x))
                btn3.place(x=150, y=300, width=75, height=50)
                btnechu = tkinter.Button(root, text='÷', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='÷': buttonClick(x))
                btnechu.place(x=225, y=300, width=75, height=50)
                # 第五行
                btnper = tkinter.Button(root, text='高级', font=('微软雅黑', 20), fg='orange', bd=0.5,
                                        command=lambda x='高级': buttonClick(x))
                btnper.place(x=0, y=350, width=75, height=50)
                btn0 = tkinter.Button(root, text='0', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='0': buttonClick(x))
                btn0.place(x=75, y=350, width=75, height=50)
                btnpoint = tkinter.Button(root, text='.', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5, command=lambda \
                        x='.': buttonClick(x))
                btnpoint.place(x=150, y=350, width=75, height=50)
                btnequ = tkinter.Button(root, text='=', bg='orange', font=('微软雅黑', 20), fg=('#4F4F4F'), bd=0.5,
                                        command=lambda x='=': buttonClick(x))
                btnequ.place(x=225, y=350, width=75, height=50)
            contentVar.set(content)
    contentVar.set(content)


operators = ('÷', '×', '-', '+', '=', '.')
root.mainloop()


