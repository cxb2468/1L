import turtle


def draw_love():
    turtle.speed(3)  # 设置画笔速度
    turtle.color('red')  # 设置画笔颜色为红色

    # 开始绘制
    turtle.begin_fill()  # 开始填充颜色
    turtle.left(140)  # 向左旋转140度
    turtle.forward(224)  # 向前移动224个单位

    # 绘制爱心的上半部分，即两个圆弧
    for i in range(200):
        turtle.right(1)
        turtle.forward(2)
    turtle.left(120)  # 向左旋转120度

    for i in range(200):
        turtle.right(1)
        turtle.forward(2)
    turtle.forward(224)  # 向前移动224个单位
    turtle.end_fill()  # 结束填充颜色

    # 隐藏画笔的箭头
    turtle.hideturtle()

    # 保持窗口
    turtle.done()


if __name__ == "__main__":
    draw_love()
