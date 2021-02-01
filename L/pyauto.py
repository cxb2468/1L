# 例 1：使用 pyautogui打开计算器界面，点击计算器上的按键 5：
import pyautogui
import time
#
# # 第一步：定位并点击【搜索】图标：
# x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\search_button.png")
# print(x,y)
# pyautogui.click(x=x,y=y,clicks=1,button='left')
#
# # 第二步：定位【输入框】并输入"calculator"：
# # x,y=100,1024
# # 或：
# # location=pyautogui.locateCenterOnScreen(image=r"C:\Users\XuYunPeng\Desktop\Pyautogui_test\search_input.png")
# # x,y=pyautogui.center(location)
# # 或：
# x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\search_input.png")
# pyautogui.moveTo(x,y)
# print(x,y)
# pyautogui.typewrite('calculator', interval=0.5)
#
# # 第三步：定位并点击计算器 【open】 按钮：
# x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\calculator_open.png")
# print(x,y)
# pyautogui.click(x=x,y=y,clicks=1,button='left')
#
# # 定位并点击按钮 【5】：
# time.sleep(1.5)
# x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\cal_5.png")
# print(x,y)
# pyautogui.click(x=x,y=y,clicks=6,button='left')


# 例 2：使用 pyautogui打开两个计算器界面，拖拽其中一个，使两个窗口并列，分别点击两个计算器上的相同按键 5：

for i in range(0,2):
    # 第一步：定位并点击【搜索】图标：
    x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\search_button.png")
    pyautogui.click(x=x,y=y,clicks=1,button='left')

    # 第二步：定位【输入框】并输入"calculator"：
    # x,y=100,1024
    # 或：
    # location=pyautogui.locateCenterOnScreen(image=r"C:\Users\XuYunPeng\Desktop\Pyautogui_test\search_input.png")
    # x,y=pyautogui.center(location)
    # 或：
    x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\search_input.png")
    pyautogui.moveTo(x,y)
    pyautogui.typewrite('calculator', interval=0.5)

    # 第三步：定位并点击计算器 【open】 按钮：
    x,y=pyautogui.locateCenterOnScreen(image=r"D:\2\calculator_open.png")
    pyautogui.click(x=x,y=y,clicks=1,button='left')
    time.sleep(2)

# 第四步：拖拽第2个计算器窗口至指定位置：
pyautogui.moveTo(295,255)
pyautogui.dragTo(700, 165, button='left')

# 第五步：在两个计算器窗口中分别输入按键 5：
for location in pyautogui.locateAllOnScreen(image=r"D:\2\cal_5.png"):
    print(location)
    x,y=pyautogui.center(location)
    pyautogui.click(x=x,y=y,clicks=1,button='left')