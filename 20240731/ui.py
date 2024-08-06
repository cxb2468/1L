from tkinter import *
from tkinter.ttk import *


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_label_lz86gwum = self.__tk_label_lz86gwum(self)
        self.tk_text_lz86hgpy = self.__tk_text_lz86hgpy(self)
        self.tk_button_lz86i38f = self.__tk_button_lz86i38f(self)
        self.tk_input_lz86i88e = self.__tk_input_lz86i88e(self)
        self.tk_label_lz86ipc7 = self.__tk_label_lz86ipc7(self)
        self.tk_label_lz86k0fr = self.__tk_label_lz86k0fr(self)

    def __win(self):
        self.title("检测指定进程后关闭_v1.0.0")
        # 设置窗口大小、居中
        width = 598
        height = 415
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_label_lz86gwum(self, parent):
        label = Label(parent, text="检测指定进程后关闭_v1.0.0", anchor="center", )
        label.place(x=0, y=0, width=596, height=34)
        return label

    def __tk_text_lz86hgpy(self, parent):
        text = Text(parent)
        text.place(x=0, y=175, width=597, height=234)
        self.create_bar(parent, text, True, False, 0, 175, 597, 234, 598, 415)
        return text

    def __tk_button_lz86i38f(self, parent):
        btn = Button(parent, text="开始监控", takefocus=False, )
        btn.place(x=498, y=101, width=99, height=31)
        return btn

    def __tk_input_lz86i88e(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=0, y=101, width=486, height=30)
        return ipt

    def __tk_label_lz86ipc7(self, parent):
        label = Label(parent, text="输入进程名称，多个进程用英文输入状态下的,分隔：", anchor="center", )
        label.place(x=0, y=62, width=289, height=30)
        return label

    def __tk_label_lz86k0fr(self, parent):
        label = Label(parent, text="监控记录：", anchor="center", )
        label.place(x=0, y=141, width=88, height=30)
        return label


class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)

    def __event_bind(self):
        self.tk_button_lz86i38f.bind('<Button-1>', self.ctl.startMonitor)
        pass

    def __style_config(self):
        pass


if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()