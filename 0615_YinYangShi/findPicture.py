import cv2,time,random,os, datetime
import sys,pyautogui, traceback
import numpy as np
import mss
import action

def load_imgs():
    mubiao = {}
    path = os.getcwd() + '\png2'
    file_list = os.listdir(path)
    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '\\' + file
        print(file_path)
        a = [cv2.imread(file_path), 0.95, name]
        mubiao[name] = a
    print(a)
    return mubiao


#读取羁绊头像图片
imgs = load_imgs()
#根据头像位置，执行羁绊
for i in ['25', 'bobo', 'laNa', 'le']:
    want = imgs[i]
    print(want)
    size = want[0].shape
    h, w, ___ = size
    print(h, w)
    time.sleep(3)
    for j in range(1, 12):
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        im = np.array(mss.mss().grab(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

        a = want

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


