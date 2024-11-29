from selenium import webdriver
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()  # 检查当前版本的chromedriver是否存在
                                      # 如果不存在，则自动下载，
                                      # 然后将chromedriver添加到路径中

driver = webdriver.Chrome()
driver.get("http://www.python.org")
assert "Python" in driver.title