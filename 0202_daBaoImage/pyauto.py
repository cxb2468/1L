# 例 1：使用 pyautogui打开计算器界面，点击计算器上的按键 5：
import pyautogui
import time
import memory_pic
import base64
import os


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



# image = open("search_button.png","wb")
# image.write((base64.b64decode(search_button_png)))
# print(image)
# image.close()


# 先把图片弄出来
# tmp = open('search_button.png', 'wb')        #创建临时的文件, 这里把后缀改成了gif，因为tk只认识gif格式图片
# tmp.write(base64.b64decode(search_button_png))    ##把这个one图片解码出来，写入文件中去。
# print(tmp)
# tmp.close()
# x,y=pyautogui.locateCenterOnScreen(image='search_button.png')
# print(x,y)
#
# window = tk.Tk()

# # 第2步，给窗口的可视化起名字
# window.title('My Window')
#
# # 第3步，设定窗口的大小(长 * 宽)
# window.geometry('500x300')  # 这里的乘是小x
#
# # 第4步，在图形界面上创建 500 * 200 大小的画布并放置各种元素
# canvas = tk.Canvas(window, bg='green', height=200, width=500)
# # 说明图片位置，并导入图片到画布上
# image_file = tk.PhotoImage(file='search_button.png')  # 图片位置（相对路径，与.py文件同一文件夹下，也可以用绝对路径，需要给定图片具体绝对路径）
#
#
# image = canvas.create_image(150, 0, anchor='n', image=image_file)  # 图片锚定点（n图片顶端的中间点位置）放在画布（0,0）坐标处
#
# canvas.pack()
#
# # 第5步，主窗口循环显示
# window.mainloop()
#
# # 删除生成的临时图片
# os.remove('search_button.png')



def get_pic(pic_code, pic_name):
    image = open(pic_name, 'wb')
    image.write(base64.b64decode(pic_code))
    image.close()

get_pic(memory_pic.search_button_png , 'search_button.png')
get_pic(memory_pic.search_input_png , 'search_input.png')
get_pic(memory_pic.calculator_open_png , "calculator_open.png")
get_pic(memory_pic.cal_5_png , "cal_5.png")
# 在这里使用图片 icon.ico



for i in range(0,2):
    # 第一步：定位并点击【搜索】图标：


    x,y=pyautogui.locateCenterOnScreen(image="search_button.png")
    print(x,y)
    pyautogui.click(x=x,y=y,clicks=1,button='left')


    # 第二步：定位【输入框】并输入"calculator"：
    # x,y=100,1024
    # 或：
    # location=pyautogui.locateCenterOnScreen(image=r"C:\Users\XuYunPeng\Desktop\Pyautogui_test\search_input.png")
    # x,y=pyautogui.center(location)
    # 或：
    x,y=pyautogui.locateCenterOnScreen(image="search_input.png")
    pyautogui.moveTo(x,y)
    pyautogui.typewrite('calculator', interval=0.5)

    # 第三步：定位并点击计算器 【open】 按钮：
    x,y=pyautogui.locateCenterOnScreen(image="calculator_open.png")
    pyautogui.click(x=x,y=y,clicks=1,button='left')
    time.sleep(2)

# 第四步：拖拽第2个计算器窗口至指定位置：
pyautogui.moveTo(295,255)
pyautogui.dragTo(700, 165, button='left')

# 第五步：在两个计算器窗口中分别输入按键 5：
for location in pyautogui.locateAllOnScreen(image="cal_5.png"):
    print(location)
    x,y=pyautogui.center(location)
    pyautogui.click(x=x,y=y,clicks=1,button='left')

os.remove('search_button.png')
os.remove('search_input.png')
os.remove("calculator_open.png")
os.remove("cal_5.png")
