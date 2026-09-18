import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

chrome_driver_path = r"C:Users\zocchenxb\.cache\selenium\chromedriver\win64\131.0.6778.204chromedriver.exe"  # 这个需要你自己下载。浏览器内核不同这个也不一样。
download_dir = r"C:星球资源\知识星球下载文件"  # 你自己想放哪这个文件就指定哪
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

driver.get("https://wx.zsxq.com/login")
input("&#9989; 请扫码登录完成后按 Enter 继续...")  # 你得是会员不然没效果

group_url = "https://wx.zsxq.com/group/15552288522142"  # 这个看你的星球链接替换下就好了
driver.get(group_url)
time.sleep(5)


def hide_overlay():
    driver.execute_script("""
        let el = document.querySelector('.rank-tips');
        if (el) el.style.display = 'none';
    """)


def wait_download_button_disappear(timeout=20):
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".download-wrapper .download")))
    except TimeoutException:
        pass


def click_outside_popup():
    driver.execute_script("""
        document.elementFromPoint(10, 10).click();
    """)
    time.sleep(1)


def get_and_download_all_files():
    seen_file_names = set()
    prev_count = -1

    while True:
        try:
            hide_overlay()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "app-file-gallery")))
            file_items = driver.find_elements(By.CSS_SELECTOR, "app-file-gallery .item")
            print(f"&#128196; 发现文件数量：{len(file_items)}")

            for index in range(len(file_items)):
                file_items = driver.find_elements(By.CSS_SELECTOR, "app-file-gallery .item")
                item = file_items[index]

                try:
                    file_name_elem = item.find_element(By.CLASS_NAME, "file-name")
                    file_name = file_name_elem.text.strip()

                    if file_name in seen_file_names:
                        continue
                    seen_file_names.add(file_name)

                    print(f"&#10145;&#65039; 处理文件：{file_name}")

                    file_path = os.path.join(download_dir, file_name)
                    if os.path.exists(file_path):
                        print(f"&#9197;&#65039; 文件已存在，跳过")
                        continue

                    driver.execute_script("arguments[0].click();", item)
                    time.sleep(1)

                    download_btns = wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".download-wrapper .download")
                    ))
                    download_btn = download_btns[-1]
                    driver.execute_script("arguments[0].click();", download_btn)
                    print(f"&#9989; 点击下载：{file_name}")

                    wait_download_button_disappear()

                    click_outside_popup()

                    time.sleep(1)

                except Exception as e:
                    print(f"&#9888;&#65039; 处理失败: {e}")
                    continue

            print("&#128260; 下拉加载更多...")
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(3)

            new_count = len(driver.find_elements(By.CSS_SELECTOR, "app-file-gallery .item"))
            if new_count == prev_count:
                print("&#9989; 全部文件处理完成")
                break
            prev_count = new_count

        except Exception as e:
            print(f"&#10060; 异常终止: {e}")
            break


get_and_download_all_files()