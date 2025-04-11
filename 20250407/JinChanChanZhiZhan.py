# coding = utf-8
import traceback
import numpy as np
from paddleocr import PaddleOCR
from pyautogui import *
import win32gui
import win32api
import logging
import pynput, time
import keyboard
import loguru
import pathlib
import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, ALL_COMPLETED, wait

##https://hbba.sacinfo.org.cn/


# 创建日志目录
log_dir = pathlib.Path('./logs')
log_dir.mkdir(exist_ok=True)
if not os.path.exists(f"/logs/"):
    os.mkdir(f"/logs/")
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
if not os.path.exists(f"/logs/{current_date}/"):
    os.mkdir(f"/logs/{current_date}/")
log_file = log_dir.joinpath(f'./logs/{current_date}/' + "log_{time: YYYY_MM_DD}.log")
log = loguru.logger

# 只允许一条线程同时识别,解决CPU占用
pool = ThreadPoolExecutor(max_workers=1)

# 关闭paddleocr的打印功能,不需要关闭的话去掉下面两行代码
logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印


# 主要识别并且购买函数
def ocr_hero_buy(heroname, windowTitle="腾讯手游助手(64位)", isClick=True):
    time.sleep(0.25)  # 键盘或鼠标按下后0.3秒后触发
    """
    自动截图模拟器窗口并且OCR指定英雄然后点击购买
    :param heroname:英雄名称,多个请直接传入数组
    :param windowName:模拟器窗口名称
    :param isClick:识别到了是否自动点击
    :return:
    """
    if type(heroname) == str:
        # 如果传入的是单个英雄或者不为数组就转换为数组
        heroname = [heroname]

    # 获取指定窗口在屏幕的位置大小函数
    def get_window_rect(window_title):
        # 获取指定窗口标题的窗口在系统中的位置
        hwnd = win32gui.FindWindow(0, window_title)
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            return rect
        return None

    rect = get_window_rect(windowTitle)
    if rect:
        # 计算模拟器窗口在桌面的起始位置和终点位置 启动StartLeft,StartTop这两个参数是窗口在桌面的坐标位置,后面OCR识别到指定英雄的位置的时候必须要加回去
        StartLeft, StartTop, right, bottom = rect
        width = right - StartLeft
        height = bottom - StartTop
    else:
        StartLeft, StartTop, right, bottom = 0, 0, 1, 1
        width = right - StartLeft
        height = bottom - StartTop
    # 调用 pyautogui 进行窗口截图
    image = screenshot(region=(StartLeft, StartTop, width, height))

    # 这里是处理裁剪掉模拟器窗口图片的上面80%的图片面积,因为图片越小识别越快,0.8代表80%。如果识别不准确请少截取一点,但是我个人测试只留下20%下方图片即可
    heroBoxheight = image.height * 0.95
    # 这里是处理裁剪掉模拟器窗口图片的左边10%的图片面积,因为图片越小识别越快
    heroBoxwidth = image.width * 0.2

    # 记录一下截取掉的位置,后期识别到了点击的时候要架上,因为这部分位置被裁剪掉了
    StartLeft = StartLeft + heroBoxwidth
    StartTop = StartTop + heroBoxheight
    # 裁剪图片到适合识别的大小
    image = image.crop((int(heroBoxwidth), int(heroBoxheight), image.width, image.height))
    oimage = image
    # 下面开始OCR
    image = np.array(image)
    result = ocr.ocr(image, cls=False)
    # 一堆if是在检查是否ocr成功,for是遍历识别结果
    point = win32api.GetCursorPos()
    if result is not None:
        for line in result:
            if line is not None:
                for word in line:
                    # 遍历识别结果
                    log.error(word)
                    for hero in heroname:

                        if str(word).find(hero) > -1 or heroname == "":
                            log.success(
                                f"发现英雄牌:{hero},坐标位置,x:{word[0][0][0] + StartLeft},y:{word[0][0][1] + StartTop}")
                            if isClick:
                                moveTo(word[0][0][0] + StartLeft, word[0][0][1] + StartTop)
                                click()

    return ""


if __name__ == '__main__':
    # 要截图的窗口标题,目前是腾讯手游模拟器,可以改成别的模拟器的标题一样通用
    windowName = "腾讯手游助手(64位)"
    # 要购买的卡牌名称
    heros = ['雷克顿', '莎弥拉', '卡西奥佩娅', '崔丝塔娜', '烬']


    # 监听键盘按键,如果是在手游模拟器里面按下的指定按键就启动识别
    def keyboardDown():
        currentWindow(windowName)


    # 监听鼠标按键,如果是在手游模拟器里面按下的按键就启动识别
    def on_click(x, y, button, pressed):
        if not pressed:
            currentWindow(windowName)
            return True


    # 判断当前鼠标所在窗口是否是指定模拟器窗口
    def currentWindow(windowTitle):
        point = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint(point)  # 请填写 x 和 y 坐标
        hwnd = win32gui.GetParent(hwnd)
        if hwnd == 0:
            hwnd = win32gui.WindowFromPoint(point)  # 请填写 x 和 y 坐标
        title = win32gui.GetWindowText(hwnd)
        if title == windowTitle:
            pool.submit(lambda cxp: ocr_hero_buy(*cxp),
                        (heros, windowTitle, True))


    log.success("正在载入OCR金铲铲自动识别选牌工具,正在初始化PaddleOCR模块")
    # 初始化 PaddleOCR
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", use_gpu=False, debug=False, show_log=False)
    log.success("PaddleOCR模块初始化成功,您可以在游戏里按下D键或者鼠标任意键来触发自动选牌")
    # 监听D键 按一次d键启动一次卡牌识别功能并且购买
    keyboard.add_hotkey('d', keyboardDown)
    # 监听鼠标键 按一次启动一次卡牌识别功能并且购买解决死循环D牌导致的CPU占用问题。但是这样也很高,这里还能优化
    with pynput.mouse.Listener(
            on_click=on_click) as listener:
        listener.join()