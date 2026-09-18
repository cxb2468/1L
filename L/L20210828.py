import pyautogui
import cv2
import time
import random
import os
import datetime
import numpy
import mss

pyautogui.FAILSAFE = True  # 如果出错，将鼠标移至屏幕左上角可停止程序

# 读取坐标信息
def read_coordinates():
    with open('坐标信息.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    coordinates = {}
    for i, line in enumerate(lines):
        name = f'point_{i}'
        x = int(line.split("=")[-1].strip().split(",")[0])
        y = int(line.split("=")[-1].strip().split(",")[1])
        coordinates[name] = (x, y)
    return coordinates

# 初始化坐标常量
COORDINATES = read_coordinates()

# 常量定义
app = COORDINATES['point_0']
gongGao = COORDINATES['point_1']
quFu = COORDINATES['point_2']
touxiang = COORDINATES['point_3']
miJing = COORDINATES['point_4']
xiongGui = COORDINATES['point_5']
anDong = COORDINATES['point_6']
luoJi = COORDINATES['point_7']
niMu = COORDINATES['point_8']
xgQiu = COORDINATES['point_9']
saoDang = COORDINATES['point_10']
queRenX = COORDINATES['point_11']
fanHuiX = COORDINATES['point_12']
saoDangXG = COORDINATES['point_13']
nvShen = COORDINATES['point_14']
qiuX = COORDINATES['point_15']
saoDangX = COORDINATES['point_16']
jiBan = COORDINATES['point_17']
shenDian = COORDINATES['point_18']
qiuSD = COORDINATES['point_19']
mo = COORDINATES['point_20']
fu = COORDINATES['point_21']
qiZhi = COORDINATES['point_22']
qianDaoX = COORDINATES['point_23']
mianBao = COORDINATES['point_24']
lianBing = COORDINATES['point_25']
zhuJiao = COORDINATES['point_26']
weiTuo1 = COORDINATES['point_27']
xiaoShi = COORDINATES['point_28']
xuanZe = COORDINATES['point_29']
yingXiong1 = COORDINATES['point_30']
queDing = COORDINATES['point_31']
queRen = COORDINATES['point_32']
weiTuo2 = COORDINATES['point_33']
yingXiong2 = COORDINATES['point_34']
weiTuo3 = COORDINATES['point_35']
yingXiong3 = COORDINATES['point_36']

color_weiTuo1_red = (174, 70, 95)
color_weiTuo1_blue = (86, 195, 230)

# 在背景查找目标图片，并返回查找到的结果坐标列表
def locate(target, want, show=False, msg=False):
    loc_pos = []
    template, threshold, name = want
    
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    locations = numpy.where(result >= threshold)

    if msg:
        print(f'{name} searching...')

    height, width = template.shape[:-1]
    last_x, last_y = 0, 0
    
    for pt in zip(*locations[::-1]):
        x, y = pt[0] + int(width/2), pt[1] + int(height/2)
        
        # 去掉邻近重复的点
        if (x - last_x) + (y - last_y) < 15:
            continue
            
        last_x, last_y = x, y
        cv2.circle(target, (x, y), 10, (0, 0, 255), 3)

        if msg:
            print(f'{name} found at {x}, {y}')

        loc_pos.append([int(x), int(y)])

    if show:
        print('Debug: show locate')
        cv2.imshow('Detection Result', target)
        cv2.waitKey(2300)
        cv2.destroyAllWindows()

    if not loc_pos:
        print(f'{name} not found')
    else:
        print("Got it, guys!")

    return loc_pos

# 按文件内容、匹配精度、名称格式批量加载目标图片
def load_images():
    target = {}
    path = os.path.join(os.getcwd(), 'png')
    
    for filename in os.listdir(path):
        name = os.path.splitext(filename)[0]
        file_path = os.path.join(path, filename)
        print(f'Loading {file_path}')
        target[name] = [cv2.imread(file_path), 0.95, name]
    
    return target

# 读取图片库并初始化设置
def initialize():
    imgs = load_images()
    pyautogui.PAUSE = 0.05
    pyautogui.FAILSAFE = False
    return imgs

# 屏幕截图捕获函数
def capture(want):
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    im = numpy.array(mss.mss().grab(monitor))
    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
    pts = locate(screen, want, True, True)
    
    while not pts:
        time.sleep(0.5)
        im = numpy.array(mss.mss().grab(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
        pts = locate(screen, want, True, True)
    
    if pts:
        xy = pts[0]
        print(xy)
        pyautogui.click(xy)

# 自动执行战斗任务
def auto_battle(position):
    pyautogui.click(position)
    pyautogui.click(COORDINATES['point_31'])  # 确定按钮
    pyautogui.click(COORDINATES['point_32'])  # 确认按钮
    time.sleep(2)

# 进入命运之斐并执行任务
def fate_mission():
    pyautogui.click(1760, 660)  # 主界面某个位置

    # 执行命运1-3
    for _ in range(3):
        pyautogui.click(1200, 540)
        pyautogui.click(1200, 725)
        pyautogui.click(1900, 540)
        
        pyautogui.moveTo(1200, 540)
        pyautogui.dragTo(x=1200, y=155, duration=2, button='left')

    pyautogui.click(85, 50)
    pyautogui.click(85, 50)
    time.sleep(2)
    pyautogui.click(85, 50)

# 主函数
def main():
    starttime = datetime.datetime.now()
    time.sleep(2)
    pyautogui.PAUSE = 1.3

    # 读取png目录图片库
    imgs = initialize()

    # 开启程序 根据logo 定位 点击
    want = imgs['logo']
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    im = numpy.array(mss.mss().grab(monitor))
    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
    pts = locate(screen, want, 0)
    print(pts)
    if not len(pts) == 0:
        xy = pts[0]
        print(xy)
    pyautogui.doubleClick(xy)

    # 循环截图  找到X 图片 点击
    want = imgs['x']
    capture(want)

    # 登录界面
    want = imgs['mhmnz']
    capture(want)

    # 每日签到
    time.sleep(4)
    pyautogui.click(1830, 75)
    time.sleep(1)
    pyautogui.click(1830, 75)
    time.sleep(1)
    pyautogui.click(1830, 75)

    # 世界
    want = imgs['shiJie']
    capture(want)

    # 秘境
    want = imgs['miJing']
    capture(want)
    # 兄贵健身房
    # 兄贵
    pyautogui.click(xiongGui)
    # 周1、4、7 andong  周2、5 luoji  周3、6 nimu
    day = datetime.datetime.now().isoweekday()
    if day == 2 or day == 5:
        pyautogui.click(luoJi)
    elif day == 3 or day == 6:
        pyautogui.click(niMu)
    else:
        pyautogui.click(anDong)

    time.sleep(1)
    pyautogui.click(xgQiu)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)  # 第一次扫荡
    time.sleep(1)
    pyautogui.click(saoDangXG)  # 第二次扫荡
    time.sleep(1)
    # pyautogui.click(800,690) #取消按钮
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 女神
    pyautogui.click(nvShen)
    pyautogui.click(qiuX)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)  # 第一次扫荡
    time.sleep(1)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 拖动秘境 进入羁绊
    pyautogui.click(220, 1055)  # (返回后起点)
    pyautogui.dragTo(x=220, y=100, duration=4, button='left')
    # 羁绊
    pyautogui.click(jiBan)
    pyautogui.click(qiuX)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 拖动秘境 进入神殿
    pyautogui.click(220, 1055)  # (返回后起点)
    pyautogui.dragTo(x=220, y=100, duration=4, button='left')
    # 神殿
    pyautogui.click(shenDian)
    pyautogui.click(qiuSD)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 神契
    pyautogui.click(220, 1055)  # (返回后起点)
    pyautogui.dragTo(x=220, y=100, duration=4, button='left')
    pyautogui.click(220, 1055)  # (返回后起点)
    pyautogui.dragTo(x=220, y=100, duration=2, button='left')
    time.sleep(1)
    pyautogui.click(900, 900)
    pyautogui.click(1800, 950)
    time.sleep(1.5)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 判断下是否回到主界面
    # 任务
    time.sleep(1)
    want = imgs['renWu']
    capture(want)
    time.sleep(2)
    pyautogui.click(1700, 925)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 好友
    want = imgs['haoYou']
    capture(want)
    time.sleep(1.5)
    pyautogui.click(380, 970)
    pyautogui.click(700, 970)
    pyautogui.click(fanHuiX)
    time.sleep(2)

    # 练兵
    want = imgs['lianBing']
    capture(want)
    time.sleep(1)
    want = imgs['zhuJiao']
    capture(want)
    time.sleep(1)

    # 如果委托颜色为红色，返回主界面；否则 开始委托1、委托2、委托3
    #   蓝色 未执行  0
    #   红色 执行中  0.5
    #   黄色 已执行完成 1
    pyautogui.moveTo(weiTuo1)
    if pyautogui.pixelMatchesColor(weiTuo1[0], weiTuo1[1], color_weiTuo1_red):
        pyautogui.click(fanHuiX)
    elif pyautogui.pixelMatchesColor(weiTuo1[0], weiTuo1[1], color_weiTuo1_blue):
        pyautogui.click(weiTuo1)
        auto_battle(yingXiong1)
        pyautogui.click(weiTuo2)
        auto_battle(yingXiong2)
        pyautogui.click(weiTuo3)
        auto_battle(yingXiong3)
        pyautogui.click(fanHuiX)
    else:
        pyautogui.click(weiTuo1)
        time.sleep(1)
        pyautogui.click(zhuJiao)
        pyautogui.click(weiTuo1)
        auto_battle(yingXiong1)
        pyautogui.click(weiTuo2)
        time.sleep(1)
        pyautogui.click(zhuJiao)
        pyautogui.click(weiTuo2)
        auto_battle(yingXiong2)
        pyautogui.click(weiTuo3)
        time.sleep(1)
        pyautogui.click(zhuJiao)
        pyautogui.click(weiTuo3)
        auto_battle(yingXiong3)
        pyautogui.click(fanHuiX)

    # 官方特权 版本更新 需变更

    # 邮件
    want = imgs['youJian']
    capture(want)
    pyautogui.click(1830, 930)
    pyautogui.click(1750, 120)
    pyautogui.click(1750, 120)

    # 羁绊
    time.sleep(3)
    want = imgs['jiBan']
    capture(want)

    for i in range(1, 12):

        a = imgs['1']
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        im = numpy.array(mss.mss().grab(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
        pts = locate(screen, a, 0)
        print(pts)
        if not len(pts) == 0:
            xy = pts[0]
            print(xy)
            break
        time.sleep(1)
        pyautogui.click(1870, 775)
        pyautogui.dragTo(x=1870, y=230, duration=2, button='left')
        pyautogui.click(x=1870, y=230, interval=0.0, duration=0.0)
    pyautogui.click(xy)
    fate_mission()

    time.sleep(3)
    want = imgs['jiBan']
    capture(want)
    for i in range(1, 12):
        a = imgs['2']
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        im = numpy.array(mss.mss().grab(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

        pts = locate(screen, a, 0)
        print(pts)
        if not len(pts) == 0:
            xy = pts[0]
            print(xy)
            break
        time.sleep(1)
        pyautogui.click(1870, 775)
        pyautogui.dragTo(x=1870, y=230, duration=2, button='left')
        pyautogui.click(x=1870, y=230, interval=0.0, duration=0.0)
    pyautogui.click(xy)
    fate_mission()
    print("第二次羁绊结束")

    time.sleep(3)
    want = imgs['jiBan']
    capture(want)

    for i in range(1, 12):
        imgs['3']
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        im = numpy.array(mss.mss().grab(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

        pts = locate(screen, a, 0)
        print(pts)
        if not len(pts) == 0:
            xy = pts[0]
            print(xy)
            break
        time.sleep(1)
        pyautogui.click(1870, 775)
        pyautogui.dragTo(x=1870, y=230, duration=2, button='left')
        pyautogui.click(x=1870, y=230, interval=0.0, duration=0.0)
    pyautogui.click(xy)
    fate_mission()

    # 程序结束时间
    endtime = datetime.datetime.now()
    duration = str(endtime - starttime)
    print(duration)
    pyautogui.alert(f"程序总用时：{duration} s", title="Test")

if __name__ == "__main__":
    main()
