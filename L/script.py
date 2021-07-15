import cv2,time,random,os, datetime
import os,sys,pyautogui, traceback
import numpy
import mss
import scriptDef

class script:
    def __init__(self):
        self.imgs = {}
        self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        self.start = time.time()
        self.counter = 0
        self.True_False = False
        self.True_False2 = False
        self.True_False3 = False
        

        def whatWindow():
            print('操作系统:', sys.platform)
        def readFile():
            imgs = scriptDef.scriptDef.load_imgs()
            # pyautogui.PAUSE = 0.05
            pyautogui.FAILSAFE = False
            return imgs
        self.imgs = readFile()

    def saoDang(self):
        starttime = datetime.datetime.now()
        time.sleep(2)
        pyautogui.PAUSE = 1.3
        pyautogui.doubleClick(app)

        # 1715,120点像素 不等于 该点像素时 sleep 0.5,如果等于，则跳出while 循环。
        scriptDef.is_color(gongGao[0], gongGao[1], color_gongGao)
        pyautogui.click(gongGao)

        # 有个 账号登录中画面，需要判断像素点
        scriptDef.is_color(mo[0], mo[1], color_mo)
        pyautogui.click(quFu)
        time.sleep(3)

        # 1需 先选中区服后 再 点击头像
        scriptDef.is_color(fu[0], fu[1], color_fu)

        pyautogui.click(touxiang)

        # 选完区服中角色后，判断像素点是否等于 1000,580像素
        scriptDef.is_color(mo[0], mo[1], color_mo)
        pyautogui.click(touxiang)
        # 进入签到奖励界面  判断面包的像素 ，while 非面包像素，则一直点击 叉叉 标记！

        pyautogui.moveTo(mianBao[0], mianBao[1])
        while not pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao):
            pyautogui.click(qianDaoX)
            pyautogui.moveTo(mianBao[0], mianBao[1])
            time.sleep(0.3)
            print(pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao))
            print(pyautogui.position())
            print(pyautogui.screenshot().getpixel((pyautogui.position())))

        # 判断 勇气的旗帜像素 ，确定有没有买月卡
        pyautogui.moveTo(qiZhi)

        # 秘境
        # 判断是否在秘境像素的上
        # scriptDef.is_color(miJing[0], miJing[1], color_miJing)
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
        pyautogui.click(900, 1000)
        time.sleep(2)
        pyautogui.click(1700, 925)
        time.sleep(2)
        pyautogui.click(fanHuiX)
        pyautogui.click(fanHuiX)

        # 好友
        pyautogui.click(60, 615)
        time.sleep(1.5)
        pyautogui.click(380, 970)
        pyautogui.click(700, 970)
        pyautogui.click(fanHuiX)
        time.sleep(2)

        # 练兵
        # scriptDef.is_color(lianBing[0], lianBing[1], color_lianBing)
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
            scriptDef.autoZhuJiao(yingXiong1[0], yingXiong1[1])
            pyautogui.click(weiTuo2)
            scriptDef.autoZhuJiao(yingXiong2[0], yingXiong2[1])
            pyautogui.click(weiTuo3)
            scriptDef.autoZhuJiao(yingXiong3[0], yingXiong3[1])
            pyautogui.click(fanHuiX)
        else:
            pyautogui.click(weiTuo1)
            time.sleep(1)
            pyautogui.click(zhuJiao)
            pyautogui.click(weiTuo1)
            scriptDef.autoZhuJiao(yingXiong1[0], yingXiong1[1])
            pyautogui.click(weiTuo2)
            time.sleep(1)
            pyautogui.click(zhuJiao)
            pyautogui.click(weiTuo2)
            scriptDef.autoZhuJiao(yingXiong2[0], yingXiong2[1])
            pyautogui.click(weiTuo3)
            time.sleep(1)
            pyautogui.click(zhuJiao)
            pyautogui.click(weiTuo3)
            scriptDef.autoZhuJiao(yingXiong3[0], yingXiong3[1])
            pyautogui.click(fanHuiX)

        # 官方特权
        pyautogui.click(88, 95)
        pyautogui.click(1330, 760)
        pyautogui.click(1260, 600)
        pyautogui.click(1030, 440)
        pyautogui.click(1030, 580)
        pyautogui.click(960, 550)
        pyautogui.click(1470, 262)
        pyautogui.click(1470, 262)
        pyautogui.click(1540, 210)

        # 邮件
        pyautogui.click(60, 400)
        pyautogui.click(1830, 930)
        pyautogui.click(1750, 120)
        pyautogui.click(1750, 120)

        # 羁绊
        # 读取羁绊头像图片
        # imgs = scriptDef.load_imgs()
        # 根据头像位置，执行羁绊
        for i in ['omiga', 'jszg', 'lisi']:
            want = self.imgs[i]
            size = want[0].shape
            h, w, ___ = size
            print(h, w)
            time.sleep(3)
            for j in range(1, 12):
                # monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
                im = numpy.array(mss.mss().grab(self.monitor))
                screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
                pts = scriptDef.locate(screen, want, 0)
                print("分隔线——————————————————————————————————————")
                print(pts)
                if not len(pts) == 0:
                    xy = pts[0]
                    print(xy)
                    break
                time.sleep(1)
                pyautogui.click(1860, 800)
                pyautogui.dragTo(x=1860, y=258, duration=3, button='left')
                pyautogui.click(1860, 258)
            pyautogui.click(xy)

        # 程序结束时间
        endtime = datetime.datetime.now()
        time1 = str(endtime - starttime)
        print(time1)

with open('坐标信息.txt', 'r', encoding='utf-8') as t:
    txt = t.readlines()

    def zb(i):
        x = txt[i].split("=")[-1].strip().split(",")[0]
        y = txt[i].split("=")[-1].strip().split(",")[1]
        a = (int(x), int(y))
        return a
app = zb(0)
gongGao = zb(1)
quFu = zb(2)
touxiang = zb(3)
miJing = zb(4)
xiongGui = zb(5)
anDong = zb(6)
luoJi = zb(7)
niMu = zb(8)
xgQiu = zb(9)
saoDang = zb(10)
queRenX = zb(11)
fanHuiX = zb(12)
saoDangXG = zb(13)
nvShen = zb(14)
qiuX = zb(15)
saoDangX = zb(16)
jiBan = zb(17)
shenDian = zb(18)
qiuSD = zb(19)
mo = zb(20)
fu = zb(21)
qiZhi = zb(22)
qianDaoX = zb(23)
mianBao = zb(24)
lianBing = zb(25)
zhuJiao = zb(26)
weiTuo1 = zb(27)
xiaoShi = zb(28)
xuanZe = zb(29)
yingXiong1 = zb(30)
queDing = zb(31)
queRen = zb(32)
weiTuo2 = zb(33)
yingXiong2 = zb(34)
weiTuo3 = zb(35)
yingXiong3 = zb(36)

print(app)
print(gongGao)

# 颜色值
color_gongGao = (176, 158, 137)
color_mo = (8, 4, 5)
color_fu = (255, 255, 123)
color_miJing = (184, 182, 168)
color_qiZhi = (109, 117, 72)
color_mianBao = (247, 240, 219)
color_lianBing = (41, 28, 8)
color_weiTuo1_red = (174, 70, 95)
color_weiTuo1_blue = (86, 195, 230)

