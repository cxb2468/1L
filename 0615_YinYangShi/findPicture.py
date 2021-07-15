import numpy,time,sys
import cv2,time,random,os, datetime
import sys,pyautogui, traceback
import numpy as np
import mss
import action



class findPicture:
    def __init__(self):
        self.imgs = {}
        self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        self.start = time.time()
        self.cishu = 0
        self.True_False = False
        self.True_False2 = False
        self.True_False3 = False

        def whatWindow():
            print('操作系统:', sys.platform)

        def readFile():
            imgs = action.load_imgs()
            # pyautogui.PAUSE = 0.05
            pyautogui.FAILSAFE = False
            return imgs

        self.imgs = readFile()


    def jiBan(self):   #御魂司机
        im = np.array(mss.mss().grab(self.monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
        want = self.imgs['jiBan']
        size = want[0].shape
        h, w, ___ = size
        pts = action.locate(screen, want, 1, 1)
        xy = action.cheat(pts[0], w, h - 10)
        print(xy)
        pyautogui.click(xy)




        # while not self.True_False:
        #     if self.True_False2 == True:
        #         return
        #     self.randomnumber = action.randomnumber()
        #     self.times = action.randtimis()
        #     # 截屏
        #     im = np.array(mss.mss().grab(self.monitor))
        #     screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
        #     t = 1
        #     # print('screen shot ok',time.ctime())
        #     # 体力不足
        #
        #
        #
        #     # 自动点击通关结束后的页面
        #     for i in ['challenge_true', 'victory', 'fail','information', 'victory_two']:
        #         want = self.imgs[i]
        #         size = want[0].shape
        #         h, w, ___ = size
        #         pts = action.locate(screen, want,1,1)
        #         if not len(pts) == 0:
        #             if i == 'challenge_true':
        #                 xy = action.cheat(pts[0], w, h - 10)
        #                 self.cishu += 1
        #                 print('挑战次数：', self.cishu)
        #                 for i in range(self.times):
        #                     pyautogui.click(xy)
        #                 t = random.randint(1, 2)
        #
        #             elif i == "victory":
        #                 xy = action.cheat(pts[0], w, h - 10)
        #                 for i in range(self.times):
        #                     pyautogui.click(xy)
        #                 t = random.randint(1, 2)
        #             elif i == "victory_two":
        #                 t = random.randint(1, 2)
        #                 xy = action.cheat(pts[0], w, h - 10)
        #                 for i in range(self.times):
        #                     pyautogui.click(xy)
        #             elif i == "fail":
        #                 t = random.randint(1, 3)
        #                 x = random.randint(130, 1100)
        #                 y = random.randint(124, 600)
        #                 xy = [x, y]
        #                 pyautogui.click(xy)
        #
        #             elif self.randomnumber == "7":
        #                 if i == "information":
        #                     xy = action.cheat(pts[0], w, h - 10)
        #                     t = random.randint(1, 4)
        #                     pyautogui.click(xy)
        #                     time.sleep(t)
        #                     for i in range(self.times):
        #                         pyautogui.click(xy)
        #             x = random.randint(-110, 110)
        #             y = random.randint(-110, 110)
        #             for i in range(t):
        #                 pyautogui.move(x, y, 0.5)
        #                 x = -(x)
        #                 y = -(y)
        #         else:
        #             im = np.array(mss.mss().grab(self.monitor))
        #             screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)




# self = findPicture()
# pyautogui.click(1805,15)
# time.sleep(1)
# pyautogui.click(1805,65)
# time.sleep(3)
# findPicture.jiBan(self)

# pyautogui.FAILSAFE = True  # 如果出错，将鼠标移至屏幕左上角可停止程序
#
# time.sleep(3)
# for i in range(1,12):
#     time.sleep(1)
#     pyautogui.click(1860, 800)
#     pyautogui.dragTo(x=1860, y=258, duration=3, button='left')
#     pyautogui.click(1860, 258)

# time.sleep(3)
# a = [cv2.imread(r"D:\1L\0615_YinYangShi\png2\25.png"), 0.95, 25]
#
#
#
# monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
# im = np.array(mss.mss().grab(monitor))
# screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
#
# pts = action.locate(screen,a,0)
# print("分隔线——————————————————————————————————————")
# print(pts)
# xy = pts[0]
# print(xy)
# pyautogui.click(xy)


time.sleep(3)
for i in range(1,12):
    a = [cv2.imread(r"D:\1L\0615_YinYangShi\png2\om.png"), 0.95, 25]
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    im = np.array(mss.mss().grab(monitor))
    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

    pts = action.locate(screen, a, 0)
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
