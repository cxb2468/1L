import pyautogui
import cv2,time,random,os, datetime
import numpy
import mss

pyautogui.FAILSAFE = True  # 如果出错，将鼠标移至屏幕左上角可停止程序

with open('坐标信息.txt', 'r', encoding='utf-8') as t:
    txt = t.readlines()
    def zb(i):
        x = txt[i].split("=")[-1].strip().split(",")[0]
        y = txt[i].split("=")[-1].strip().split(",")[1]
        a = (int(x), int(y))
        return a
app=zb(0)
gongGao=zb(1)
quFu=zb(2)
touxiang=zb(3)
miJing=zb(4)
xiongGui=zb(5)
anDong=zb(6)
luoJi=zb(7)
niMu=zb(8)
xgQiu=zb(9)
saoDang=zb(10)
queRenX=zb(11)
fanHuiX=zb(12)
saoDangXG=zb(13)
nvShen=zb(14)
qiuX=zb(15)
saoDangX=zb(16)
jiBan=zb(17)
shenDian=zb(18)
qiuSD=zb(19)
mo=zb(20)
fu=zb(21)
qiZhi=zb(22)
qianDaoX=zb(23)
mianBao=zb(24)
lianBing =zb(25)
zhuJiao = zb(26)
weiTuo1 = zb(27)
xiaoShi = zb(28)
xuanZe = zb(29)
yingXiong1=zb(30)
queDing=zb(31)
queRen = zb(32)
weiTuo2 = zb(33)
yingXiong2 = zb(34)
weiTuo3 = zb(35)
yingXiong3 = zb(36)

color_weiTuo1_red = (174,70,95)
color_weiTuo1_blue = (86,195,230)

#在背景查找目标图片，并返回查找到的结果坐标列表，target是背景，want是要找目标
def locate(target,want, show=bool(0), msg=bool(0)):
    loc_pos=[]
    want,treshold,c_name=want[0],want[1],want[2]
    result=cv2.matchTemplate(target,want,cv2.TM_CCOEFF_NORMED)
    location=numpy.where(result>=treshold)

    if msg:  #显示正式寻找目标名称，调试时开启
        print(c_name,'searching... ')

    h,w=want.shape[:-1] #want.shape[:-1]

    n,ex,ey=1,0,0
    for pt in zip(*location[::-1]):    #其实这里经常是空的
        x,y=pt[0]+int(w/2),pt[1]+int(h/2)
        if (x-ex)+(y-ey)<15:  #去掉邻近重复的点
            continue
        ex,ey=x,y

        cv2.circle(target,(x,y),10,(0,0,255),3)

        if msg:
            print(c_name,'we find it !!! ,at',x,y)
            x,y=int(x),int(y)

        loc_pos.append([x,y])

    if show:  #在图上显示寻找的结果，调试时开启
        print('Debug: show locate')
        cv2.imshow('we get',target)
        cv2.waitKey(2300)
        cv2.destroyAllWindows()


    if len(loc_pos)==0:
        print(c_name,'not find')
    else:
        print("Got it, guys!")

    return loc_pos


#按【文件内容，匹配精度，名称】格式批量聚聚要查找的目标图片，精度统一为0.95，名称为文件名
def load_imgs():
    target = {}
    path = os.getcwd() + '\png'
    file_list = os.listdir(path)
    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '\\' + file
        print(file_path)
        a = [cv2.imread(file_path), 0.95, name]
        target[name] = a
    print(a)
    return target


def readFile():
    imgs = load_imgs()
    # pyautogui.PAUSE = 0.05
    pyautogui.FAILSAFE = False
    return imgs


def capture(want):
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    im = numpy.array(mss.mss().grab(monitor))
    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
    pts = locate(screen, want, 1, 1)
    while len(pts) == 0:
        time.sleep(0.5)
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        im = numpy.array(mss.mss().grab(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
        pts = locate(screen, want, 1, 1)
    if not len(pts) == 0:
        xy = pts[0]
        print(xy)
    pyautogui.click(xy)


def autoZhuJiao(x,y):
    pyautogui.click(xiaoShi)
    pyautogui.click(xuanZe)
    pyautogui.click(x,y)
    pyautogui.click(queDing)
    pyautogui.click(queRen)
    time.sleep(2)


# 进入命运之斐  扫荡命运1至命运3
def mingYun():
    pyautogui.click(1760,660)

    pyautogui.click(1200,540)
    pyautogui.click(1200,725)
    pyautogui.click(1900,540)

    pyautogui.moveTo(1200,540)
    pyautogui.dragTo(x=1200, y=155, duration=2, button='left')
    pyautogui.click(1200,540)
    pyautogui.click(1200,725)
    pyautogui.click(1900,540)

    pyautogui.moveTo(1200,540)
    pyautogui.dragTo(x=1200, y=155, duration=2, button='left')
    pyautogui.click(1200,540)
    pyautogui.click(1200,725)
    pyautogui.click(1900,540)

    pyautogui.click(85,50)
    pyautogui.click(85,50)
    time.sleep(2)
    pyautogui.click(85,50)


def main():

    starttime = datetime.datetime.now()
    time.sleep(2)
    pyautogui.PAUSE = 1.3

    # 读取png目录图片库
    imgs = readFile()

    #开启程序 根据logo 定位 点击
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

    #登录界面
    want = imgs['mhmnz']
    capture(want)

    #每日签到
    pyautogui.click(1830,75)
    time.sleep(1)
    pyautogui.click(1830,75)

    #世界
    want = imgs['shiJie']
    capture(want)



    #秘境
    want = imgs['miJing']
    capture(want)
    #兄贵健身房
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
        autoZhuJiao(yingXiong1[0], yingXiong1[1])
        pyautogui.click(weiTuo2)
        autoZhuJiao(yingXiong2[0], yingXiong2[1])
        pyautogui.click(weiTuo3)
        autoZhuJiao(yingXiong3[0], yingXiong3[1])
        pyautogui.click(fanHuiX)
    else:
        pyautogui.click(weiTuo1)
        time.sleep(1)
        pyautogui.click(zhuJiao)
        pyautogui.click(weiTuo1)
        autoZhuJiao(yingXiong1[0], yingXiong1[1])
        pyautogui.click(weiTuo2)
        time.sleep(1)
        pyautogui.click(zhuJiao)
        pyautogui.click(weiTuo2)
        autoZhuJiao(yingXiong2[0], yingXiong2[1])
        pyautogui.click(weiTuo3)
        time.sleep(1)
        pyautogui.click(zhuJiao)
        pyautogui.click(weiTuo3)
        autoZhuJiao(yingXiong3[0], yingXiong3[1])
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
        a = [cv2.imread(r"D:\1L\L\png\1.png"), 0.95, '1']
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
    mingYun()

    time.sleep(3)
    want = imgs['jiBan']
    capture(want)
    for i in range(1, 12):
        a = [cv2.imread(r"D:\1L\L\png\2.png"), 0.95, '2']
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
    mingYun()

    time.sleep(3)
    want = imgs['jiBan']
    capture(want)
    for i in range(1, 12):
        a = [cv2.imread(r"D:\1L\L\png\3.png"), 0.95, '3']
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
    mingYun()

    #程序结束时间
    endtime = datetime.datetime.now()
    time1 =str(endtime - starttime)
    print(time1)
    pyautogui.alert("程序总用时： "+time1+" s", title="Test")


if __name__ == "__main__":
    main()


