import cv2,time,random,os, datetime
import os,sys,pyautogui, traceback
import numpy as np
import mss
import action

class chushihua:
    def __init__(self):
        self.imgs = {}
        self.monitor = {"top": 0, "left": 0, "width": 1300, "height": 770}
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

    def yuhun(self):  # 御魂单刷
        while not self.True_False:
            if self.True_False == True:
                return

            self.times = action.randtimis()
            # 截屏
            im = np.array(mss.mss().grab(self.monitor))
            screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
            t = 0
            want = self.imgs['Stamina']
            print(want[0])
            size = want[0].shape
            print(size)
            h, w, ___ = size

            pts = action.locate(screen, want, 0)  # 判断体力是否充足
            if not len(pts) == 0:
                print('体力不足')

            else:
                print("体力充足")

            # 自动点击通关结束后的页面
            for i in ['challenge_one', 'prepare_one', 'prepare_two', 'prepare_three', 'continiu_one', 'fail']:
                want = self.imgs[i]
                size = want[0].shape
                h, w, ___ = size
                print(h, w)
                pts = action.locate(screen, want, 1,0)
                if not len(pts) == 0:
                    if i == 'challenge_one':
                        xy = action.cheat(pts[0], w, h - 10)
                        self.cishu += 1
                        print('挑战次数：', self.cishu)
                        for i in range(self.times):
                            pyautogui.click(xy)
                        t = random.randint(1, 2)
                    elif i == "prepare_one" or i == 'prepare_two' or i == "prepare_three":
                        t = random.randint(1, 3)
                        xy = action.cheat(pts[0], w, h - 10)
                        for i in range(self.times):
                            pyautogui.click(xy)
                    elif i == "continiu_one":
                        t = random.randint(1, 3)
                        xy = action.cheat(pts[0], w, h - 10)
                        for i in range(self.times):
                            pyautogui.click(xy)
                    elif i == "fail":
                        t = random.randint(1, 3)
                        x = random.randint(100, 1200)
                        y = random.randint(100, 480)
                        xy = [x, y]
                        pyautogui.click(xy)
                    x = random.randint(-110, 110)
                    y = random.randint(-110, 110)
                    for i in range(t):
                        pyautogui.move(x, y, 0.5)
                        x = -(x)
                        y = -(y)
                else:
                    im = np.array(mss.mss().grab(self.monitor))
                    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)



    def yuhun2(self):   #御魂司机
        while not self.True_False:
            if self.True_False2 == True:
                return
            self.randomnumber = action.randomnumber()
            self.times = action.randtimis()
            # 截屏
            im = np.array(mss.mss().grab(self.monitor))
            screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
            t = 1
            # print('screen shot ok',time.ctime())
            # 体力不足

            # 自动点击通关结束后的页面
            for i in ['challenge_true', 'victory', 'fail','information', 'victory_two']:
                want = self.imgs[i]
                size = want[0].shape
                h, w, ___ = size
                pts = action.locate(screen, want,1,1)
                if not len(pts) == 0:
                    if i == 'challenge_true':
                        xy = action.cheat(pts[0], w, h - 10)
                        self.cishu += 1
                        print('挑战次数：', self.cishu)
                        for i in range(self.times):
                            pyautogui.click(xy)
                        t = random.randint(1, 2)

                    elif i == "victory":
                        xy = action.cheat(pts[0], w, h - 10)
                        for i in range(self.times):
                            pyautogui.click(xy)
                        t = random.randint(1, 2)
                    elif i == "victory_two":
                        t = random.randint(1, 2)
                        xy = action.cheat(pts[0], w, h - 10)
                        for i in range(self.times):
                            pyautogui.click(xy)
                    elif i == "fail":
                        t = random.randint(1, 3)
                        x = random.randint(130, 1100)
                        y = random.randint(124, 600)
                        xy = [x, y]
                        pyautogui.click(xy)

                    elif self.randomnumber == "7":
                        if i == "information":
                            xy = action.cheat(pts[0], w, h - 10)
                            t = random.randint(1, 4)
                            pyautogui.click(xy)
                            time.sleep(t)
                            for i in range(self.times):
                                pyautogui.click(xy)
                    x = random.randint(-110, 110)
                    y = random.randint(-110, 110)
                    for i in range(t):
                        pyautogui.move(x, y, 0.5)
                        x = -(x)
                        y = -(y)
                else:
                    im = np.array(mss.mss().grab(self.monitor))
                    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)


    def yuhun3(self):   #御魂打手
        while not self.True_False:
            if self.True_False3 == True:
                return
            self.times = action.randtimis()
            # 截屏
            im = np.array(mss.mss().grab(self.monitor))
            screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
            t = 1
            # print('screen shot ok',time.ctime())
            # 体力不足

            # 自动点击通关结束后的页面
            for i in ['thugsVictory', 'thugsVictory2','fail']:
                want = self.imgs[i]
                size = want[0].shape
                h, w, ___ = size
                pts = action.locate(screen, want,1,0)
                if not len(pts) == 0:
                    if i == 'thugsVictory':
                        xy = action.cheat(pts[0], w, h - 10)
                        self.cishu += 1
                        print('挑战次数：', self.cishu)
                        for i in range(self.times):
                            pyautogui.click(xy)
                            t = random.randint(1, 2)
                    elif i == "thugsVictory2":
                        t = random.randint(1, 2)
                        xy = action.cheat(pts[0], w, h - 10)
                        for i in range(self.times):
                            pyautogui.click(xy)

                    elif i == "fail":
                        t = random.randint(1, 3)
                        x = random.randint(130, 1100)
                        y = random.randint(124, 600)
                        xy = [x, y]
                        pyautogui.click(xy)
                    x = random.randint(-110, 110)
                    y = random.randint(-110, 110)
                    for i in range(t):
                        pyautogui.move(x, y, 0.7)
                        x = -(x)
                        y = -(y)
                else:
                    im = np.array(mss.mss().grab(self.monitor))
                    screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)






