
# 自动计算器输入
import pyautogui
import time

time.sleep(1)
pyautogui.moveTo(400,200)
pyautogui.click(400,200)


x = [0]*4
x[0] = pyautogui.locateCenterOnScreen('7.png')


x[1] = pyautogui.locateCenterOnScreen('+.png')

x[2] = pyautogui.locateCenterOnScreen('5.png')

x[3] = pyautogui.locateCenterOnScreen('=.png')


for i in range(4):
    pyautogui.click(x[i])
    time.sleep(1)
    print(i)
