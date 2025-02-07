from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from typing import Optional, List
from datetime import datetime


def find_doctor_and_nextpage(driver, doctor_name, hospital_name, department_name):
    page_index = 0
    while True:
        page_index += 1
        doctors = driver.find_elements(By.XPATH, '//*[@id="expert_div_1"]/div[*]/div[1]/div[2]')

        for doctor in doctors:
            text = doctor.text
            if doctor_name in text and hospital_name in text and department_name in text:
                try:
                    # 在当前医生元素中查找链接
                    link_element = doctor.find_element(By.XPATH, './ul/li[1]/span[1]/a')  # 相对 XPath
                    href = link_element.get_attribute("href")  # 获取链接的 href 属性
                    print(f"Found the link to the doctor at page {page_index}. href={href}")
                    return href
                except Exception as e:
                    print(f"Do not find the doctor link, doctor.text={text}. {e}")

        # 搜索下一页
        try:
            switch_page_bar = driver.find_element(By.XPATH, '//*[@id="page1"]')
            next_page_btn = switch_page_bar.find_element(By.XPATH, './/*[contains(text(), "下一页")]')
            href = next_page_btn.get_attribute('href')
            if href:
                print(
                    f"Page {page_index} has been searched completely with no matches found, proceeding to the next page.")
                time.sleep(random.randint(2, 5))
                next_page_btn.click()
            else:
                print(f"The search has reached the last page {page_index} and no matches found.")
                return False
        except Exception as e:
            print(f"find_doctor_and_nextpage Error. {e}")
            return False


def search_doctor(driver, base_url, doctor_name, hospital_name, department_name):
    try:
        # 打开搜索页面（基网址传入）
        driver.get(base_url)

        # 定位搜索框并输入医生
        doctor_input = driver.find_element(By.XPATH, "//*[@id='txtSearch']")

        doctor_input.clear()
        doctor_input.send_keys(doctor_name)

        # 点击搜索按钮
        search_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[3]/div/input[3]")
        search_button.click()

        try:
            # 等待跳转到结果页面
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@id='expert_div_1']/div[1]"))
            )
        except Exception as e:
            print(f"Search the doctor timeout, name={doctor_name}. {e}")
            return False

        doctor_link = find_doctor_and_nextpage(driver, doctor_name, hospital_name, department_name)
        # print(f"doctor_link={doctor_link}")
        return doctor_link

    except Exception as e:
        print(f":Search the doctor failed, name={doctor_name}. {e}")
        return False


def convert_to_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%m-%d")
    except ValueError:
        return None


def parse_target_date(target_date) -> List[datetime]:
    """
    解析入参 target_date，支持单个日期、多个日期和日期范围。
    '01-05'
    '01-05, 01-07, 01-19'
    '01-05~02-02'
    返回日期对象列表。
    """
    if isinstance(target_date, str):
        if '~' in target_date:  # 日期范围
            start_date_str, end_date_str = target_date.split('~')
            start_date = convert_to_datetime(start_date_str)
            end_date = convert_to_datetime(end_date_str)
            return [start_date, end_date] if start_date and end_date else []

        elif ',' in target_date:  # 多个日期
            date_str_list = [date.strip() for date in target_date.split(',')]
            converted_dates = [convert_to_datetime(date_str) for date_str in date_str_list]
            return [date for date in converted_dates if date]

        else:  # 单个日期
            single_date = convert_to_datetime(target_date)
            return [single_date] if single_date else []

    return []


def check_availability(driver, doctor_link, target_date, target_time: Optional[str]):
    """在网页中检查是否有目标日期时间的号源"""
    can_be_appointments = False

    try:
        driver.get(doctor_link)

        try:
            # 等待跳转到结果页面
            doctor_subscribe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="doctorsubscribe"]'))
            )
        except Exception as e:
            print(f"Open link {doctor_link} timeout. {e}")
            return False

        # 匹配日期
        date_items = doctor_subscribe.find_elements(By.XPATH, './div[1]/ul/li/span[1]')

        parsed_dates = parse_target_date(target_date.strip())

        matched_indices = []

        if '~' in target_date:  # 日期范围
            if len(parsed_dates) == 2 and isinstance(parsed_dates[0], datetime) and isinstance(parsed_dates[1],
                                                                                               datetime):  # 日期范围
                start_date, end_date = parsed_dates
                for idx, item in enumerate(date_items):
                    item_date = convert_to_datetime(item.text)
                    if item_date and start_date <= item_date <= end_date:
                        matched_indices.append(idx)
        elif len(parsed_dates) > 1:  # 多个日期
            for idx, item in enumerate(date_items):
                item_date = convert_to_datetime(item.text)
                if item_date and item.text in [date.strftime("%m-%d") for date in parsed_dates]:
                    matched_indices.append(idx)
        elif len(parsed_dates) == 1:  # 单个日期
            for idx, item in enumerate(date_items):
                item_date = convert_to_datetime(item.text)
                if item_date and item.text == parsed_dates[0].strftime("%m-%d"):
                    matched_indices.append(idx)

        if len(matched_indices) > 0:
            print(f"Found the matched date index {matched_indices}")
        else:
            print(f"No matched date can be found.")
            return False

        whliesubscribe = doctor_subscribe.find_elements(By.XPATH, './div[2]/ul/li')
        for index in matched_indices:
            if index < len(whliesubscribe):
                element = whliesubscribe[index]
                if "预约" in element.text:
                    can_be_appointments = True
                    print(f"There are available slots on  {date_items[index].text}, and appointments can be made.")
                    return True

        # 匹配时间
        print(f"can_be_appointments={can_be_appointments}")

    except Exception as e:
        print(f"check_availability Error. {e}")
        return False


def book_appointment(driver):
    """执行挂号流程"""
    try:
        # 点击预约按钮
        book_button = driver.find_element(By.ID, "book_button")  # 替换为实际 ID
        book_button.click()

        # 填写必要的预约信息
        patient_name = driver.find_element(By.ID, "patient_name_input")  # 替换为实际 ID
        patient_phone = driver.find_element(By.ID, "patient_phone_input")  # 替换为实际 ID

        patient_name.send_keys("测试患者")  # 替换为实际患者姓名
        patient_phone.send_keys("12345678901")  # 替换为实际联系电话

        # 确认预约
        confirm_button = driver.find_element(By.ID, "confirm_button")  # 替换为实际 ID
        confirm_button.click()

        print("挂号成功！")
    except Exception as e:
        print(f"挂号出错: {e}")


def main(base_url, doctor_name, hospital, department, target_date, target_time):
    """主程序入口"""
    driver = webdriver.Chrome()  # 浏览器驱动

    try:
        # 步骤 1：搜索医生
        doctor_link = search_doctor(driver, base_url, doctor_name, hospital, department)
        if not doctor_link:
            print("Search doctor failed.")
            return

        # doctor_link = 'https://www.xxx.com/UrpOnline/Home/Doctor/2439FC00A213861E30C599CDDD0833B8'

        # 步骤 2：检查是否有目标日期的号源
        if check_availability(driver, doctor_link, target_date, target_time):
            print(f"找到 {target_date} 的号源，开始预约...")
        else:
            print(f"没有找到 {target_date} 的号源。")

    finally:
        # 关闭浏览器
        driver.quit()


# 示例调用
if __name__ == "__main__":
    main(
        base_url="https://www.xxx.com/UrpOnline/Home/DoctorList/",
        doctor_name="医师",
        # doctor_name="张三",
        hospital="中山医院",
        department="皮肤科",
        # department="便民门诊2",
        # department="消化内科asdf午间门诊", # 第4页
        # target_date="01-05~01-06",
        target_date="01-05~02-01",
        target_time=None
    )