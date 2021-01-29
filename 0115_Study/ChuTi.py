import xlsxwriter
import random

# """以下为可修改参数"""
# "出题数目--100题整个一页A4纸大小"
t = 100
# "出题列数"
m = 4
# "出题难度大小"
n = 10
# "出题规则
# 1、加法
# 2、减法
# 3、加减混合
# 4、乘法
# 5、除法
# 6、乘除混合
# 7、四则运算
# "
g = 7

# """以下为函数代码，修改可能会无法使用"""


# 运算符
def fu(x):
    sys = ['+', '-', '×', '÷']
    if x == 1:
        return sys[0]
    elif x == 2:
        return sys[1]
    elif x == 3:
        f = random.randint(0, 1)
        return sys[f]
    elif x == 4:
        return sys[2]
    elif x == 5:
        return sys[3]
    elif x == 6:
        f = random.randint(2, 3)
        return sys[f]
    elif x == 7:
        f = random.randint(0, 3)
        return sys[f]


# 随机数
def num(x):
    y = random.randint(1, x)
    return y


# 出题
def ti(x):
    n1 = num(x)
    n2 = num(x)
    f = fu(g)
    if f == '+':
        s = [n1, f, n2, n1 + n2]
        return s
    elif f == '-':
        n1, n2 = max(n1, n2), min(n1, n2)
        s = [n1, f, n2, n1 - n2]
        return s
    elif f == '×':
        s = [n1, f, n2, n1 * n2]
        return s
    elif f == '÷':
        n1, n2 = max(n1, n2), min(n1, n2)
        while n1 % n2 != 0:
            n1 = num(x)
            n2 = num(x)
            n1, n2 = max(n1, n2), min(n1, n2)
        s = [n1, f, n2, int(n1 / n2)]
        return s


# 四舍五入避免round(0.5)等于0
def sswr(x):
    return int(x + 0.5)


# Excel创建表格操作
workbook = xlsxwriter.Workbook('./口算.xlsx')
sheet1 = workbook.add_worksheet('试题')
sheet2 = workbook.add_worksheet('答案')
sheet1.set_column('A:D', 21.6)
sheet1.set_row(30)
sheet2.set_column('A:D', 21.6)
sheet2.set_row(30)

# 写入格式
font = workbook.add_format({
    'font_size': 20,
    'font_name': '微软雅黑',
    'bold': 1

})

# Excel写入操作
for h in range(sswr(t / m)):
    for l in range(m):
        s1 = ti(n)
        shiti = str(s1[0]) + str(s1[1]) + str(s1[2]) + '='
        daan = str(s1[0]) + str(s1[1]) + str(s1[2]) + '=' + str(s1[3])
        sheet1.write(h, l, shiti, font)
        sheet2.write(h, l, daan, font)
        t = t - 1
        if t == 0:
            break

workbook.close()