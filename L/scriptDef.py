import cv2,time,random,os, datetime
import os,sys,pyautogui, traceback
import numpy
import mss

#判断像素点 颜色是否吻合，若吻合 则点击
def is_color(x, y, color_x):
    pyautogui.moveTo(x, y)
    while not pyautogui.pixelMatchesColor(x, y, color_x):
        time.sleep(0.5)
        print(pyautogui.pixelMatchesColor(x, y, color_x))
        print(pyautogui.position())
        print(pyautogui.screenshot().getpixel((pyautogui.position())))

#自动助教
def autoZhuJiao(x, y):
    pyautogui.click(1560,760)
    pyautogui.click(580,240)
    pyautogui.click(x,y)
    pyautogui.click(1200,1000)
    pyautogui.click(1200,950)
    time.sleep(2)



# 在背景查找目标图片，并返回查找到的结果坐标列表，target是背景，want是要找目标
def locate(target, want, show=bool(0), msg=bool(0)):
    loc_pos = []
    want, treshold, c_name = want[0], want[1], want[2]
    result = cv2.matchTemplate(target, want, cv2.TM_CCOEFF_NORMED)
    location = numpy.where(result >= treshold)

    if msg:  # 显示正式寻找目标名称，调试时开启
        print(c_name, 'searching... ')

    h, w = want.shape[:-1]  # want.shape[:-1]

    n, ex, ey = 1, 0, 0
    for pt in zip(*location[::-1]):  # 其实这里经常是空的
        x, y = pt[0] + int(w / 2), pt[1] + int(h / 2)
        if (x - ex) + (y - ey) < 15:  # 去掉邻近重复的点
            continue
        ex, ey = x, y

        cv2.circle(target, (x, y), 10, (0, 0, 255), 3)

        if msg:
            print(c_name, 'we find it !!! ,at', x, y)
            x, y = int(x), int(y)

        loc_pos.append([x, y])

    if show:  # 在图上显示寻找的结果，调试时开启
        print('Debug: show locate')
        cv2.imshow('we get', target)
        cv2.waitKey(2300)
        cv2.destroyAllWindows()

    if len(loc_pos) == 0:
        print(c_name, 'not find')
    else:
        print("Got it, guys!")

    return loc_pos

# 读取羁绊 目标头像   批量
def load_imgs():
    mubiao = {}
    path = os.getcwd() + '\png'
    file_list = os.listdir(path)
    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '\\' + file
        print(file_path)
        a = [cv2.imread(file_path), 0.95, name]
        mubiao[name] = a
    print(a)
    return mubiao

# 进入命运之斐  扫荡命运1至命运3
def mingYun():
    pyautogui.click(1620, 660)

    pyautogui.click(1200, 540)
    pyautogui.click(1200, 725)
    pyautogui.click(1900, 540)

    pyautogui.moveTo(1200, 540)
    pyautogui.dragTo(x=1200, y=155, duration=2, button='left')
    pyautogui.click(1200, 540)
    pyautogui.click(1200, 725)
    pyautogui.click(1900, 540)

    pyautogui.moveTo(1200, 540)
    pyautogui.dragTo(x=1200, y=155, duration=2, button='left')
    pyautogui.click(1200, 540)
    pyautogui.click(1200, 725)
    pyautogui.click(1900, 540)

    pyautogui.click(158, 56)
    pyautogui.click(158, 56)
    time.sleep(2)
    pyautogui.click(158, 56)


#蜂鸣报警器，参数n为鸣叫次数
def alarm(n):
    frequency = 1500
    duration = 500

    if os.name=='nt':
        import winsound
        winsound.Beep(frequency, duration)

#随机偏移坐标，防止游戏的外挂检测。p是原坐标，w、n是目标图像宽高，返回目标范围内的一个随机坐标
def cheat(p, w, h):
    a,b = p
    w, h = int(w/3), int(h/3)
    c,d = random.randint(-w, w),random.randint(-h, h)
    e,f = a + c, b + d
    y = [e, f]
    return(y)
