import pickle
import random
import time

import settings
from services.common.base_service import BaseService
from selenium.webdriver.common.action_chains import ActionChains
import scrapy
from selenium import webdriver
import requests
import settings
from PIL import Image
from io import BytesIO


class BLoginService(BaseService):
    name = "zhihu"
    login_url = "https://passport.bilibili.com/login"

    # 截取你需要的图片 有缺口和无缺口的
    def crop_image(self, img_file_name):
        time.sleep(2)
        img = self.browser.find_element_by_css_selector('.geetest_canvas_img.geetest_absolute')

        location = img.location
        print("图片的位置：", location)

        size = img.size
        print("图片的大小：", size)

        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        print("验证码截图的位置：", left, top, bottom, right)

        screen_shot = self.browser.get_screenshot_as_png()
        screen_shot = Image.open(BytesIO(screen_shot))
        capt = screen_shot.crop((int(left), int(top), int(right), int(bottom)))
        capt.save(img_file_name)
        return capt

    # 初始化
    def __init__(self, settings):
        self.user_name = settings.Accounts[self.name]["username"]
        self.pass_word = settings.Accounts[self.name]["password"]
        # self.browser = webdriver.Chrome(executable_path="yourself driver path")
        self.browser = webdriver.Chrome(executable_path=r"D:\copy\chrome60\chromedriver.exe")

    # 验证是否登录成功
    def check_login(self):
        try:
            self.browser.find_element_by_xpath('//class[contains(text(), "我的收藏夹")]')
            return True
        except Exception as e:
            return False

    # 像素比对 找到缺口位置像素，到时候直接滑动
    def compare_pixel(self, img1, img2, i, j):
        pixel1 = img1.load()[i, j]
        pixel2 = img2.load()[i, j]
        # 允许的偏差值
        dif = 60
        # RGB
        # 如果很相似的话应该不是缺口 false  否则差异很大的话就是True
        if abs(pixel1[0] - pixel2[0]) < dif and abs(pixel1[1] - pixel2[2]) < dif and abs(pixel1[2] - pixel2[2]) < dif:
            return False
        return True

    def login(self):
        try:
            # max window, because we need to slider captcha.  get position
            self.browser.maximize_window()
        except Exception as e:
            pass
        while not self.check_login():

            self.browser.get(self.login_url)
            name_ele = self.browser.find_element_by_css_selector("#login-username")
            pass_ele = self.browser.find_element_by_css_selector("#login-passwd")
            name_ele.send_keys(self.user_name)
            pass_ele.send_keys(self.pass_word)

            # 调出滑动验证码
            login_btn = self.browser.find_element_by_css_selector("a.btn.btn-login")
            login_btn.click()
            time.sleep(2)

            # 还原没有缺口的图片
            self.browser.execute_script('document.querySelectorAll("canvas")[3].style=""')
            # 截取验证码
            img1 = self.crop_image("cap1.png")
            # 显示有缺口的图片
            self.browser.execute_script('document.querySelectorAll("canvas")[3].style="display: none; opacity: 1;"')
            img2 = self.crop_image("cap2.png")

            # image1 = Image.open("cap1.png")
            # image2 = Image.open("cap2.png")

            # 拿到缺口图片的位置
            left = 60
            find = False
            # 60....width
            for i in range(60, img1.size[0]):
                if find:
                    break
                # j...height
                for j in range(img1.size[1]):
                    # 如果是True left = i
                    if self.compare_pixel(img1, img2, i, j):
                        left = i
                        find = True
                        break

            left -= 5
            print(left)

            # 滑动轨迹
            track = []
            # 当前位移
            current = 0
            # 减速阈值
            mid = left * 3 / 4
            # 间隔时间
            t = 0.1
            v = 0
            while current < left:
                if current < mid:
                    a = random.randint(2, 3)
                else:
                    a = - random.randint(6, 7)
                v0 = v
                # 当前速度
                v = v0 + a * t
                # 移动距离
                move = v0 * t + 1 / 2 * a * t * t
                # 当前位移
                current += move
                track.append(round(move))

            # 事件链去执行
            slider = self.browser.find_element_by_css_selector(".geetest_slider_button")
            ActionChains(self.browser).click_and_hold(slider).perform()
            for x in track:
                ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()

            time.sleep(0.5)
            ActionChains(self.browser).release().perform()
            time.sleep(5)

        # 保存cookie 下次直接登录，可以添加判断
        cookies = self.browser.get_cookies()
        print(cookies)
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        self.browser.close()
        return cookie_dict

    def check_ck(self, cookie_dict):
        pass


if __name__ == '__main__':
    import settings

    bb = BLoginService(settings)
    bb.login()