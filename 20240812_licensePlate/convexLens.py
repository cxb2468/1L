import tkinter as tk


class Axis:  # 主光轴
    def __init__(self):  # 创建主光轴
        self.line = cv_display.create_line(0, 0, 1000, 0, width=2, arrow="none", dash=(2, 1, 2, 1))  # dash参数设置为虚线

    def move(self, y):  # 根据坐标移动
        self.rel_y = get_relpos(y=y)[1]  # 转换为画布坐标
        cv_display.coords(self.line, (0, self.rel_y, 1000, self.rel_y))  # 重置位置


class Obj:  # 物体
    def __init__(self, h):  # 创建物体，h为高度
        self.h = round(h)
        self.pic = cv_display.create_line((0, 0, 0, self.h), width=3, arrow="last", arrowshape=(20, 30, 10),
                                          fill="black", state="normal")

    def move(self, x, y):  # 根据坐标移动
        self.x = x
        self.rel_x, self.rel_y = get_relpos(x, y)  # 转换为画布坐标
        cv_display.coords(self.pic, (self.rel_x, self.rel_y, self.rel_x, self.rel_y - self.h))  # 重置位置


class Len:  # 透镜
    def __init__(self, h):  # 创建透镜，h为高度
        self.h = round(h)
        self.convex = cv_display.create_line((0, 0, 0, self.h), width=1, arrow="both", arrowshape=(10, 30, 5))  # 创建凸透镜
        self.concave = cv_display.create_line((0, 0, 0, self.h), width=1, arrow="both",
                                              arrowshape=(-10, -30, 5))  # 创建凹透镜
        self.flat = cv_display.create_line((0, 0, 0, self.h), width=1, arrow="none")  # 创建f=0的透镜替代品

    def status_process(self):  # 根据焦距选择合适的透镜状态， 隐藏其他状态
        if f > 0:
            cv_display.itemconfigure(self.convex, state="normal")
            cv_display.itemconfigure(self.concave, state="hidden")
            cv_display.itemconfigure(self.flat, state="hidden")
            self.pic = self.convex
        elif f < 0:
            cv_display.itemconfigure(self.concave, state="normal")
            cv_display.itemconfigure(self.convex, state="hidden")
            cv_display.itemconfigure(self.flat, state="hidden")
            self.pic = self.concave
        else:
            cv_display.itemconfigure(self.flat, state="normal")
            cv_display.itemconfigure(self.convex, state="hidden")
            cv_display.itemconfigure(self.concave, state="hidden")
            self.pic = self.flat

    def move(self, x, y):  # 根据坐标移动
        self.x = x
        self.rel_x, self.rel_y = get_relpos(x, y)  # 转换为画布坐标
        self.status_process()
        cv_display.coords(self.pic, (self.rel_x, self.rel_y - self.h / 2, self.rel_x, self.rel_y + self.h / 2))  # 重置位置


class Img:  # 像
    def __init__(self, h):  # 创建像，h为高度
        self.h = round(h)
        self.pic = cv_display.create_line((0, 0, 0, self.h), width=3, arrow="last", arrowshape=(20, 30, 10),
                                          fill="black", state="normal")

    def check_reality(self):  # 检查像的虚实与否
        if f > 0:
            if abs(u) > f:
                self.real = True
            elif 0 < abs(u) < f:
                self.real = False
            else:
                self.real = None
        elif f < 0:
            if u != 0:
                self.real = False
            else:
                self.real = None
        else:
            self.real = None

    def status_process(self):  # 设置状态
        if self.real == True:
            cv_display.itemconfigure(self.pic, fill="black")  # 实像为黑色
        elif self.real == False:
            cv_display.itemconfigure(self.pic, fill="#c0c0c0")  # 虚像为灰色

        if self.real == None:
            cv_display.itemconfigure(self.pic, state="hidden")  # 成像时显示，不成像时隐藏
        else:
            cv_display.itemconfigure(self.pic, state="normal")

    def move(self, h, x, y):  # 根据坐标移动
        self.x = x
        if h != None:
            self.h = round(h)
        self.rel_x, self.rel_y = get_relpos(x, y)  # 转换为画布坐标
        self.check_reality()
        self.status_process()
        if self.real != None:
            cv_display.coords(self.pic, (self.rel_x, self.rel_y, self.rel_x, self.rel_y + self.h))  # 重置位置


class Point():
    def __init__(self, x, y, text):  # 创建点
        self.rel_x, self.rel_y = get_relpos(x, y)
        self.mark = cv_display.create_text(self.rel_x, self.rel_y - 20, text=text, font=("Arial", 15))  # 标注
        self.pic = cv_display.create_oval(self.rel_x - 3, self.rel_y - 3, self.rel_x + 3, self.rel_y + 3,
                                          fill="blue")  # 用小圆表示点

    def get_status(self):  # 根据状态显示
        if Point_Mode == True:
            cv_display.itemconfigure(self.pic, state="normal")
            cv_display.itemconfigure(self.mark, state="normal")
        else:
            cv_display.itemconfigure(self.pic, state="hidden")
            cv_display.itemconfigure(self.mark, state="hidden")

    def move(self, x, y):  # 根据坐标移动
        self.get_status()
        self.rel_x, self.rel_y = get_relpos(x, y)
        cv_display.coords(self.pic, (self.rel_x - 3, self.rel_y - 3, self.rel_x + 3, self.rel_y + 3))  # 重置位置
        cv_display.coords(self.mark, (self.rel_x, self.rel_y - 20))  # 重置标注位置


class Point_group:
    def __init__(self, x, y):  # 创建透镜的关键点
        self.O = Point(x, y, "O")
        self.F1 = Point(x - abs(f), y, "F₁")
        self.F2 = Point(x + abs(f), y, "F₂")
        self.P1 = Point(x - 2 * abs(f), y, "P₁")
        self.P2 = Point(x + 2 * abs(f), y, "P₂")

    def move_points(self, x, y):  # 根据坐标移动
        self.O.move(x, y)
        self.F1.move(x - abs(f), y)
        self.F2.move(x + abs(f), y)
        self.P1.move(x - 2 * abs(f), y)
        self.P2.move(x + 2 * abs(f), y)


class Light:
    def __init__(self, start, end, inc, axis_y):  # 创建光线，start起点坐标，end终点坐标，inc入射点坐标，axis_y主光轴位置
        self.get_points(start, end, inc, axis_y)
        self.reverse_ext = cv_display.create_line((self.rel_inc[0], self.rel_inc[1], self.mid2[0], self.mid2[1]),
                                                  width=3, arrow="none", fill="pink", dash=(2, 1, 2, 1),
                                                  state="hidden")  # 反向延长线
        self.line_in = cv_display.create_line((self.rel_start[0], self.rel_start[1], self.rel_inc[0], self.rel_inc[1]),
                                              width=3, arrow="none", fill="red")  # 入射光线
        self.line_out = cv_display.create_line((self.rel_inc[0], self.rel_inc[1], self.rel_end[0], self.rel_end[1]),
                                               width=3, arrow="none", fill="red")  # 折射光线
        self.mark_in = cv_display.create_line((self.rel_start[0], self.rel_start[1], self.mid1[0], self.mid1[1]),
                                              width=3, arrow="last", arrowshape=(5, 5, 5), fill="red")  # 入射光线标注箭头
        self.mark_out = cv_display.create_line((self.rel_inc[0], self.rel_inc[1], self.mid2[0], self.mid2[1]), width=3,
                                               arrow="last", arrowshape=(5, 5, 5), fill="red")  # 折射光线标注箭头

    def get_points(self, start, end, inc, axis_y):  # 确定光线关键点位置
        self.rel_start = get_relpos(start[0], start[1])
        self.rel_inc = get_relpos(inc[0], inc[1])

        if f == 0 or v == None:  # 不成像时折射光无终点
            self.rel_end = (None, None)
        else:
            self.rel_end = get_relpos(end[0], end[1])

        if f == 0 or u == 0:  # 透镜f或物距u被调整为0时，指定折射光终点与入射点重合（即无折射光）
            x_out, y_out = inc
        else:
            if v == None or (v != None and u * v < 0):  # 成虚像或不成像时折射光无终点，指定折射光终点位置
                k_out = self.get_k(start, inc, axis_y)  # 确定折射光线所在直线斜率
                x_out = 2 * abs(f) * sgn(u) + inc[0]
                y_out = k_out * (x_out - inc[0]) + inc[1]
            else:  # 成实像时折射光有终点（像所在点）
                x_out, y_out = end
        self.out = get_relpos(x_out, y_out)

        self.mid1 = (
        (self.rel_start[0] + self.rel_inc[0]) / 2, (self.rel_start[1] + self.rel_inc[1]) / 2)  # 标注箭头位置为光线中部
        self.mid2 = ((self.rel_inc[0] + self.out[0]) / 2, (self.rel_inc[1] + self.out[1]) / 2)

    def get_k(self, start, inc, axis_y):  # 确定折射光线所在直线斜率
        if u > 0:
            k1 = (inc[1] - start[1]) / u
            k2 = k1 - (inc[1] - axis_y) / f
            return k2
        elif u < 0:
            k2 = (inc[1] - start[1]) / u
            k1 = k2 + (inc[1] - axis_y) / f
            return k1

    def get_status(self):  # 根据状态显示
        if Light_Mode == True:
            if u != 0 and v != None and u * v < 0:
                cv_display.itemconfigure(self.reverse_ext, state="normal")
            else:
                cv_display.itemconfigure(self.reverse_ext, state="hidden")

            for i in [self.line_in, self.line_out, self.mark_in, self.mark_out]:
                if u == 0:
                    cv_display.itemconfigure(i, state="hidden")
                else:
                    cv_display.itemconfigure(i, state="normal")
        else:
            for i in [self.line_in, self.line_out, self.mark_in, self.mark_out, self.reverse_ext]:
                cv_display.itemconfigure(i, state="hidden")

    def move(self, start, end, inc, axis_y):  # 根据坐标移动
        self.get_points(start, end, inc, axis_y)
        self.get_status()

        cv_display.coords(self.line_in, (self.rel_start[0], self.rel_start[1], self.rel_inc[0], self.rel_inc[1]))
        cv_display.coords(self.line_out, (self.rel_inc[0], self.rel_inc[1], self.out[0], self.out[1]))
        cv_display.coords(self.mark_in, (self.rel_start[0], self.rel_start[1], self.mid1[0], self.mid1[1]))
        cv_display.coords(self.mark_out, (self.rel_inc[0], self.rel_inc[1], self.mid2[0], self.mid2[1]))
        if f != 0 and v != None:
            cv_display.coords(self.reverse_ext, (self.rel_inc[0], self.rel_inc[1], self.rel_end[0], self.rel_end[1]))


class Modifier(tk.Scale):  # 创建标尺
    def __init__(self, x, y, from_, to, length, orient, label, value):
        super().__init__(win, from_=from_, to=to, length=length, tickinterval=50,
                         orient=orient, digits=1, label=label)
        self.place(x=x, y=y)
        self.set(value)


class Win(tk.Tk):  # 创建主窗口
    def __init__(self):
        super().__init__()
        self.geometry("1400x780+50+0")
        self.title("透镜成像实验")


class Cv_display(tk.Canvas):  # 创建演示画布
    def __init__(self):
        super().__init__(win, width=1000, height=500, bg="white")
        self.place(x=18, y=20)


class Data_board(tk.Frame):  # 创建框架用于显示数据
    def __init__(self):
        super().__init__(win, width=150, height=90)
        self.place(x=1130, y=50)
        self.f_label = tk.Label(self, font=("Arial", 20))
        self.u_label = tk.Label(self, font=("Arial", 20))
        self.v_label = tk.Label(self, font=("Arial", 20))
        self.LEN_label = tk.Label(self, font=("Arial", 20))
        self.OBJ_label = tk.Label(self, font=("Arial", 20))
        self.IMG_label = tk.Label(self, font=("Arial", 20))

        labels = [self.f_label, self.u_label, self.v_label, self.LEN_label, self.OBJ_label, self.IMG_label]
        for i in labels:
            i.pack(anchor="w")

    def refresh(self):  # 更新显示数据
        try:
            self.f_label["text"] = "焦距f={} cm".format(f)
            self.u_label["text"] = "物距u={} cm".format(u)
            self.LEN_label["text"] = "透镜位置：{} cm".format(LEN.x)
            self.OBJ_label["text"] = "物体位置：{} cm".format(OBJ.x)
            if v == None or f == 0:
                self.v_label["text"] = "像距：无"
                self.IMG_label["text"] = "成像位置：无"
            else:
                self.v_label["text"] = "像距v={:.0f} cm".format(v)
                self.IMG_label["text"] = "成像位置：{:.0f} cm".format(IMG.x)
        except:
            pass


class Cbtn_Mode(tk.Checkbutton):  # 创建复选框，控制光线、焦点的显示与否
    def __init__(self, x, y, text):
        self.var = tk.BooleanVar()
        super().__init__(win, text=text, font=("Arial", 20), variable=self.var)
        self.place(x=x, y=y)
        self.invoke()


class Btn_start(tk.Button):  # 开始按钮
    def __init__(self):
        super().__init__(win, text="开始实验", font=("Simsun", 20), width=10, height=5, command=self.start)
        self.pack(anchor="c", pady=300)

    def start(self):
        global u, v, f, from_, to, Light_Mode, Point_Mode, \
            cv_display, axis, p_group, OBJ, LEN, IMG, light1, light2, \
            Axis_scale, LEN_scale, OBJ_scale, f_scale, \
            data_board, cbtn_Light_Mode, cbtn_Point_Mode
        self.destroy()

        Light_Mode = True  # 光线的显示
        Point_Mode = True  # 焦点的显示
        from_ = -500  # from_和to为标尺量程
        to = 500
        f = 100  # 初始焦距
        OBJ_x = -200  # 物体初始横坐标
        OBJ_h = 100  # 指定物体高度
        LEN_x = 0  # 透镜初始横坐标
        LEN_h = 300  # 指定透镜高度
        axis_y = 0  # 主光轴初始纵坐标
        u, v, OBJ_y, IMG_x, IMG_h, IMG_y = analyse(OBJ_x, LEN_x, OBJ_h, axis_y)  # 计算
        # OBJ_y IMG_y 物体、像的纵坐标     IMG_h像的高度

        # 初始化各个部件
        cv_display = Cv_display()
        axis = Axis()
        p_group = Point_group(LEN_x, axis_y)
        LEN = Len(LEN_h)
        IMG = Img(IMG_h)
        OBJ = Obj(OBJ_h)
        light1 = Light((OBJ_x, OBJ_y), (IMG_x, IMG_y), (LEN_x, OBJ_y), axis_y)
        light2 = Light((OBJ_x, OBJ_y), (IMG_x, IMG_y), (LEN_x, axis_y), axis_y)

        Axis_scale = Modifier(1030, 0, 250, -250, 535, "vertical", "主光轴位置/cm", axis_y)
        OBJ_scale = Modifier(0, 520, from_, to, 1033, "horizontal", "物体位置/cm", OBJ_x)
        LEN_scale = Modifier(0, 600, from_, to, 1033, "horizontal", "透镜位置/cm", LEN_x)
        f_scale = Modifier(0, 680, from_, to, 1033, "horizontal", "焦距f/cm", f)

        data_board = Data_board()
        cbtn_Light_Mode = Cbtn_Mode(1120, 290, "显示光路")
        cbtn_Point_Mode = Cbtn_Mode(1120, 330, "显示焦点和二倍焦点")

        # 刷新数据以及画布上的图形
        Refresh()


def sgn(x):  # 符号函数
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def get_relpos(x=None, y=None):  # 坐标转换
    rel_x = None
    rel_y = None
    if x != None:
        rel_x = (x - from_) / (to - from_) * 1000
    if y != None:
        rel_y = 250 - y
    return rel_x, rel_y


def analyse(OBJ_x, LEN_x, OBJ_h, axis_y):  # 计算
    u = LEN_x - OBJ_x
    OBJ_y = axis_y + OBJ_h
    if u != 0 and abs(u) != f:
        v = u * f / (abs(u) - f)
        IMG_x = round(LEN_x + v)
        IMG_h = round(OBJ_h * v / u)
        IMG_y = axis_y - IMG_h
    else:
        v, IMG_x, IMG_h, IMG_y = None, None, None, None
    return u, v, OBJ_y, IMG_x, IMG_h, IMG_y


def Refresh():
    global Light_Mode, Point_Mode, f, u, v
    # 更新各种参数
    Light_Mode = cbtn_Light_Mode.var.get()
    Point_Mode = cbtn_Point_Mode.var.get()
    f = f_scale.get()
    axis_y = Axis_scale.get()
    OBJ_x = OBJ_scale.get()
    LEN_x = LEN_scale.get()
    OBJ_h = OBJ.h
    u, v, OBJ_y, IMG_x, IMG_h, IMG_y = analyse(OBJ_x, LEN_x, OBJ_h, axis_y)

    # 刷新画布上的图形
    axis.move(axis_y)
    p_group.move_points(LEN_x, axis_y)
    LEN.move(LEN_x, axis_y)
    IMG.move(IMG_h, IMG_x, axis_y)
    OBJ.move(OBJ_x, axis_y)
    light1.move((OBJ_x, OBJ_y), (IMG_x, IMG_y), (LEN_x, OBJ_y), axis_y)
    light2.move((OBJ_x, OBJ_y), (IMG_x, IMG_y), (LEN_x, axis_y), axis_y)

    # 更新面板数据
    data_board.refresh()

    # 使用tkinter自带的after方法，每1毫秒循环一次
    win.after(1, Refresh)


def main():  # 主函数
    global win, btn_start
    win = Win()
    btn_start = Btn_start()
    win.mainloop()


if __name__ == "__main__":
    main()
