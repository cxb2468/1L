from tkinter import *
from tkinter.ttk import *


class Win:
    def __init__(self):
        self.root = self.__win()
        self.tk_label_l61k2rxh = self.__tk_label_l61k2rxh()
        self.tk_input_l61k35ee = self.__tk_input_l61k35ee()
        self.tk_label_l61k3i5r = self.__tk_label_l61k3i5r()
        self.tk_check_button_l61k3rgq = self.__tk_check_button_l61k3rgq()
        self.tk_check_button_l61k449f = self.__tk_check_button_l61k449f()
        self.tk_check_button_l61k4hdx = self.__tk_check_button_l61k4hdx()
        self.tk_check_button_l61k4pw1 = self.__tk_check_button_l61k4pw1()
        self.tk_label_l61k56rj = self.__tk_label_l61k56rj()
        self.tk_radio_button_l61k5gk4 = self.__tk_radio_button_l61k5gk4()
        self.tk_radio_button_l61k5r4p = self.__tk_radio_button_l61k5r4p()
        self.tk_select_box_l61k6jik = self.__tk_select_box_l61k6jik()
        self.tk_label_l61k6ngn = self.__tk_label_l61k6ngn()
        self.tk_button_l61k71gi = self.__tk_button_l61k71gi()
        self.tk_button_l61k7gt7 = self.__tk_button_l61k7gt7()

    def __win(self):
        root = Tk()
        root.title("tk与ttk对比 ~ Tkinter布局助手")
        # 设置大小 居中展示
        width = 600
        height = 500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(geometry)
        root.resizable(width=False, height=False)
        return root

    def show(self):
        self.root.mainloop()

    def __tk_label_l61k2rxh(self):
        label = Label(self.root, text="姓名")
        label.place(x=50, y=60, width=50, height=24)
        return label

    def __tk_input_l61k35ee(self):
        ipt = Entry(self.root)
        ipt.place(x=120, y=60, width=150, height=24)
        return ipt

    def __tk_label_l61k3i5r(self):
        label = Label(self.root, text="爱好")
        label.place(x=50, y=100, width=50, height=24)
        return label

    def __tk_check_button_l61k3rgq(self):
        cb = Checkbutton(self.root, text="唱")
        cb.place(x=120, y=100, width=54, height=24)
        return cb

    def __tk_check_button_l61k449f(self):
        cb = Checkbutton(self.root, text="跳")
        cb.place(x=190, y=100, width=54, height=24)
        return cb

    def __tk_check_button_l61k4hdx(self):
        cb = Checkbutton(self.root, text="rap")
        cb.place(x=260, y=100, width=54, height=24)
        return cb

    def __tk_check_button_l61k4pw1(self):
        cb = Checkbutton(self.root, text="篮球")
        cb.place(x=330, y=100, width=54, height=24)
        return cb

    def __tk_label_l61k56rj(self):
        label = Label(self.root, text="性别")
        label.place(x=50, y=142, width=50, height=24)
        return label

    def __tk_radio_button_l61k5gk4(self):
        rb = Radiobutton(self.root, text="男")
        rb.place(x=120, y=140, width=57, height=24)
        return rb

    def __tk_radio_button_l61k5r4p(self):
        rb = Radiobutton(self.root, text="女")
        rb.place(x=190, y=140, width=57, height=24)
        return rb

    def __tk_select_box_l61k6jik(self):
        cb = Combobox(self.root, state="readonly")
        cb['values'] = ("本科", "专科", "高中")
        cb.place(x=120, y=180, width=150, height=24)
        return cb

    def __tk_label_l61k6ngn(self):
        label = Label(self.root, text="学历")
        label.place(x=50, y=180, width=50, height=24)
        return label

    def __tk_button_l61k71gi(self):
        btn = Button(self.root, text="登记")
        btn.place(x=100, y=410, width=143, height=40)
        return btn

    def __tk_button_l61k7gt7(self):
        btn = Button(self.root, text="清空")
        btn.place(x=340, y=410, width=143, height=40)
        return btn


if __name__ == "__main__":
    win = Win()
    # TODO 绑定点击事件或其他逻辑处理
    win.show()