import pyautogui
import cv2,time,random,os, datetime
import numpy
import mss



pyautogui.FAILSAFE = True  # 如果出错，将鼠标移至屏幕左上角可停止程序




# --------------------------------------选择文件,并清洗数据（因为示例文件的数据相对简单，谈不上清洗）
# path = eg.fileopenbox(msg='')
# data = pd.read_excel(path, header=0)
# data = data.iloc[:, 1:5]  # 选择2-5列
# [m, n] = data.shape
# print(data)
# --------------------------------------设置各项目在屏幕上的坐标数值（x,y）
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



print(app)
print(gongGao)

#颜色值
color_gongGao = (177,162,137)
color_mo =(8, 4, 5)
color_fu=(255, 255, 123)
color_miJing=(184, 182, 168)
color_qiZhi=(109, 117, 72)
color_mianBao=(247, 242, 220)
color_lianBing = (41,28,8)
color_weiTuo1_red = (174,70,95)
color_weiTuo1_blue = (86,195,230)

#while当颜色 非  match时 ，一直sleep 0.5s，match则执行下一步
def  is_color(x,y,color_x):
     pyautogui.moveTo(x, y)
     while not pyautogui.pixelMatchesColor(x, y,color_x):
        time.sleep(0.5)
        print(pyautogui.pixelMatchesColor(x, y,color_x))
        print(pyautogui.position())
        print(pyautogui.screenshot().getpixel((pyautogui.position())))

def autoZhuJiao(x,y):
    pyautogui.click(xiaoShi)
    pyautogui.click(xuanZe)
    pyautogui.click(x,y)
    pyautogui.click(queDing)
    pyautogui.click(queRen)
    time.sleep(2)

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


# 进入命运之斐  扫荡命运1至命运3
def mingYun():
    pyautogui.click(1620,660)

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

    pyautogui.click(158,56)
    pyautogui.click(158,56)
    time.sleep(2)
    pyautogui.click(158,56)



def main():
    starttime = datetime.datetime.now()
    time.sleep(2)
    pyautogui.PAUSE = 1.3
    pyautogui.doubleClick(app)

    # 1715,120点像素 不等于 该点像素时 sleep 0.5,如果等于，则跳出while 循环。
    is_color(gongGao[0],gongGao[1],color_gongGao)
    pyautogui.click(gongGao)

    #有个 账号登录中画面，需要判断像素点
    is_color(mo[0],mo[1],color_mo)
    pyautogui.click(quFu)
    time.sleep(3)



    # 1需 先选中区服后 再 点击头像
    is_color(fu[0],fu[1],color_fu)

    pyautogui.click(touxiang)

    #选完区服中角色后，判断像素点是否等于 1000,580像素
    is_color(mo[0], mo[1], color_mo)
    pyautogui.click(touxiang)
    #进入签到奖励界面  判断面包的像素 ，while 非面包像素，则一直点击 叉叉 标记！

    pyautogui.moveTo(mianBao[0], mianBao[1])
    while not pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao):
        pyautogui.click(qianDaoX)
        pyautogui.moveTo(mianBao[0], mianBao[1])
        time.sleep(0.3)
        print(pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao))
        print(pyautogui.position())
        print(pyautogui.screenshot().getpixel((pyautogui.position())))



    #判断 勇气的旗帜像素 ，确定有没有买月卡
    pyautogui.moveTo(qiZhi)

    # 秘境
    # 判断是否在秘境像素的上
    # is_color(miJing[0], miJing[1], color_miJing)
    pyautogui.click(miJing)

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

    #拖动秘境 进入羁绊
    pyautogui.click(220,1055)#(返回后起点)
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
    #神殿
    pyautogui.click(shenDian)
    pyautogui.click(qiuSD)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    #神契
    pyautogui.click(220, 1055)  # (返回后起点)
    pyautogui.dragTo(x=220, y=100, duration=4, button='left')
    pyautogui.click(220, 1055)  # (返回后起点)
    pyautogui.dragTo(x=220, y=100, duration=2, button='left')
    time.sleep(1)
    pyautogui.click(900,900)
    pyautogui.click(1800, 950)
    time.sleep(1.5)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    #判断下是否回到主界面
    #任务
    time.sleep(1)
    pyautogui.click(900,1000)
    time.sleep(2)
    pyautogui.click(1700,925)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)



    #好友
    pyautogui.click(60, 615)
    time.sleep(1.5)
    pyautogui.click(380, 970)
    pyautogui.click(700, 970)
    pyautogui.click(fanHuiX)
    time.sleep(2)


    # 练兵
    # is_color(lianBing[0], lianBing[1], color_lianBing)
    pyautogui.click(lianBing)
    pyautogui.click(zhuJiao)
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


   #官方特权
    pyautogui.click(88,95)
    pyautogui.click(1330, 760)
    pyautogui.click(1260, 600)
    pyautogui.click(1030,440)
    pyautogui.click(1030,580)
    pyautogui.click(960,550)
    pyautogui.click(1470,262)
    pyautogui.click(1470,262)
    pyautogui.click(1540,210)

    #邮件
    pyautogui.click(60, 400)
    pyautogui.click(1830, 930)
    pyautogui.click(1750, 120)
    pyautogui.click(1750, 120)

    #羁绊
    time.sleep(3)
    pyautogui.click(1260, 1000)
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
        pyautogui.click(1854, 775)
        pyautogui.dragTo(x=1854, y=250, duration=2, button='left')
        pyautogui.click(x=1854, y=250, interval=0.0, duration=0.0)
    pyautogui.click(xy)
    mingYun()

    time.sleep(3)
    pyautogui.click(1260, 1000)
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
        pyautogui.click(1854, 775)
        pyautogui.dragTo(x=1854, y=250, duration=2, button='left')
        pyautogui.click(x=1854, y=250, interval=0.0, duration=0.0)
    pyautogui.click(xy)
    mingYun()

    time.sleep(3)
    pyautogui.click(1260, 1000)
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
        pyautogui.click(1854, 775)
        pyautogui.dragTo(x=1854, y=250, duration=2, button='left')
        pyautogui.click(x=1854, y=250, interval=0.0, duration=0.0)
    pyautogui.click(xy)
    mingYun()

    # 羁绊
    # 读取羁绊头像图片
    # imgs = load_imgs()
    # # 根据头像位置，执行羁绊
    # time.sleep(3)
    # pyautogui.click(1260, 1000)
    # for i in ['omiga','jszg','lisi']:
    #     want = imgs[i]
    #     print(want)
    #     size = want[0].shape
    #     h, w, ___ = size
    #     print(h, w)
    #     time.sleep(3)
    #     for j in range(1, 12):
    #         monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    #         im = numpy.array(mss.mss().grab(monitor))
    #         screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
    #
    #         a = want
    #
    #         pts = locate(screen, a, 0)
    #         print("分隔线——————————————————————————————————————")
    #         print(pts)
    #         if not len(pts) == 0:
    #             xy = pts[0]
    #             print(xy)
    #             break
    #         time.sleep(1)
    #         pyautogui.click(1860, 800)
    #         pyautogui.dragTo(x=1860, y=258, duration=3, button='left')
    #         pyautogui.click(1860, 258)
    #     pyautogui.click(xy)
    #     mingYun()
    # 羁绊

    #程序结束时间
    endtime = datetime.datetime.now()
    time1 =str(endtime - starttime)
    print(time1)
    pyautogui.alert("程序总用时： "+time1+" s", title="Test")
# main()
# def tick():
#     print("Tick! time is : "+ str(datetime.now()))
#     print("Tick! time is : %s" % datetime.now())
#     print()


if __name__ == "__main__":
    main()

    # 加入定时执行程序
    # sch = BlockingScheduler()
    # sch.add_job(main, 'cron', day_of_week='0-6', hour=14, minute=10, second=20)
    # print("Ctrl+0  to exit".format(("Break" if os.name == "nt" else "C  ")))
    #
    # try:
    #     sch.start()
    # except (KeyboardInterrupt,SystemExit):
    #     pass


