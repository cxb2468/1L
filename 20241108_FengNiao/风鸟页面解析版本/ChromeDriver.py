# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File       : Chrome.py
@Project    : Scripts
@Time       : 2021/12/21 17:08
@Author     : Aura Service
@Software   : PyCharm
@Description :
"""
# -*- coding:utf-8 -*-

import time
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from selenium import webdriver


class Driver(object):
    """
        driver : 选择驱动
        OVER_TIME : 隐式等待时间 单位秒      查找元素的超时次数
        url : 启动网页
        browser_type : max 全屏 | diy 自定义
        browser_width browser_heigth :分辨率长宽

    """
    print("初始化浏览器选项......")
    option = webdriver.ChromeOptions()
    option.add_experimental_option('useAutomationExtension', False)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option("detach", True)
    # option.add_argument("--disable-dev-shm-usage")
    # option.add_argument("--no-sandbox")
    # option.add_argument("--disable-gpu")
    # option.add_argument(f'--user-data-dir=./chrome_data')  # 设置数据路径为调用文件同路径/chrome_data
    # option.headless = True  # 隐藏chrome窗口
    option.add_argument("--incognito") # 无痕
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(service=Service(), options=option)
    OVER_TIME = 0
    url = ""
    browser_type = ""
    browser_width = 1200
    browser_height = 768
    print("初始化完毕")

    def __new__(cls, *args, **kw):
        """
        使用单例模式将类设置为运行时只有一个实例，在其他Python类中使用基类时，
        可以创建多个对象，保证所有的对象都是基于一个浏览器
        """
        if not hasattr(cls, '_instance'):
            orig = super(Driver, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def start(self):
        """
        启动浏览器
        :param url: 测试地址
        :param driver_name: 在启动时设置浏览器的类型
        :return:
        """
        self.driver.get(self.url)
        self.driver.implicitly_wait(self.OVER_TIME)
        if self.browser_type == "max":
            self.driver.maximize_window()
        elif self.browser_type == "diy":
            self.driver.set_window_size(self.browser_width, self.browser_height)

        # def get_url(self):
        #     """返回浏览器的地址"""
        #     return BASE_URL

    def find_element(self, by, value):
        """
        这里添加了一个OVER_TIME作为查找元素的超时次数，根据系统的实际情况设置OVER_TIME的大小
        driver.find_element(By.ID,'kw').clear()
        driver.find_element(By.NAME,'wd').send_keys("Selenium ")
        driver.find_element(By.CLASS_NAME,'s_ipt').send_keys(" ")
        driver.find_element(By.CSS_SELECTOR,"#kw").send_keys("")
        """
        for i in range(self.OVER_TIME):
            try:
                return self.driver.find_element(by=by, value=value)
            except Exception as e:
                print(e)

    def find_elements(self, by, value):
        """与find_element一致"""
        for i in range(self.OVER_TIME):
            try:
                return self.driver.find_elements(by=by, value=value)
            except Exception as e:
                print(e)

    def find_display_elements(self, by, value):
        """
        查找状态为displayed的元素集合，当查找一类元素时，
        经常出现有些元素是不可见的情况，此函数屏蔽那些不可见的元素
        """
        for i in range(self.OVER_TIME):
            try:
                elements = self.driver.find_elements(by=by, value=value)
                num = elements.__len__()
            except Exception as e:
                print(e)
                time.sleep(1)
            if num >= 1:
                break
        display_element = []
        # 将可见的元素放到列表中， 并返回
        for j in range(num):
            element = elements.__getitem__(j)
            if element.is_displayed():
                display_element.append(element)
        return display_element

    def is_element_present(self, by, value):
        """判断元素是否存在"""
        try:
            self.driver.find_element(by=by, value=value)
            return True
        except Exception as e:
            print(e)
            return False

    def navigate_to(self, url):
        """
        导航到指定的 URL
        """
        self.quit()  # 先完全退出当前的浏览器
        self.url = url  # 更新URL
        self.driver = webdriver.Chrome(service=Service(), options=self.option)  # 重新初始化webdriver
        self.start()

    def close(self):
        self.driver.close()

    def quit(self):
        """退出浏览器"""
        self.driver.quit()


if __name__ == "__main__":
    page = Driver()
    page.start()
