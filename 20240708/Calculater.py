import tkinter as tk


class Calculator(tk.Tk):
    """计算器窗体类"""

    def __init__(self):
        """初始化实例"""
        tk.Tk.__init__(self)
        self.title("我的计算器")
        self.memory = 0  # 暂存数值
        self.Demo()

    def Demo(self):
        """Create the Demo"""
        btn_list = ["C", "(", ")", "/",
                    "7", "8", "9", "*",
                    "4", "5", "6", "-",
                    "1", "2", "3", "+",
                    "+/-", "0", ".", "="]
        r = 1
        c = 0
        for b in btn_list:
            self.button = tk.Button(self, text=b, width=5,
                                    command=(lambda x=b: self.operate(x)))
            self.button.grid(row=r, column=c, padx=3, pady=6)
            c += 1
            if c > 3:
                c = 0
                r += 1
        self.entry = tk.Entry(self, width=21, borderwidth=3,
                              bg="light blue", font=("黑体", 11))
        self.entry.grid(row=0, column=0, columnspan=4, padx=8, pady=6)

    def operate(self, key):
        """press the button"""
        if key == "=":  # 输出结果
            result = eval(self.entry.get())  # 获取文本框输入的值（值为=)
            self.entry.insert(tk.END, " = " + str(result))  # 在’=‘后输出计算结果
        elif key == "C":  # 清空输入框
            self.entry.delete(0, tk.END)  # 将结果清零
        elif key == "+/-":  # 取相反数
            if "=" in self.entry.get():
                self.entry.delete(0, tk.END)
            elif self.entry.get()[0] == "-":
                self.entry.delete(0)
            else:
                self.entry.insert(0, "-")
        else:  # 其他键
            if "=" in self.entry.get():
                self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, key)


if __name__ == "__main__":
    Calculator().mainloop()
