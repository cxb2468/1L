import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

# 自动下载并安装 ChromeDriver
chromedriver_autoinstaller.install()

# 设置 ChromeDriver 服务
service = ChromeService()

# 创建一个新的 Chrome 浏览器实例
driver = webdriver.Chrome(service=service)

try:
    # 打开一个网页
    driver.get('https://www.example.com')

    # 打印出网页标题
    print(driver.title)

    # 这里可以添加更多的 Selenium 代码来与网页交互

finally:
    # 关闭浏览器
    driver.quit()