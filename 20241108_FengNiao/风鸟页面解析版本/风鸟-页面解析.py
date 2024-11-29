# -*- coding: utf-8 -*-

"""
@File       : 风鸟.py
@Project    : pythonToolsProject
@Author     : Aura Service
@Time       : 2024/4/14 22:46
@Description:
"""
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from ChromeDriver import Driver

driver = Driver()
driver.OVER_TIME = 10


def getCompanyPageTableHtml(company):
    # 查找，进入查找列表
    search_base_url = "https://www.riskbird.com/ent/"
    search_url = search_base_url + company + ".html"
    # print(search_url)
    driver.navigate_to(search_url)
    # time.sleep(10)
    # html_source = driver.driver.page_source
    resultMap = {}
    resultMap["COMPANY"] = driver.driver.execute_script("""
                const headerDivs = document.querySelectorAll('.xs-data-module-header');
                let tableHtml = '';

                for (let i = 0; i < headerDivs.length; i++) {
                    const headerDiv = headerDivs[i];
                    const childNodes = headerDiv.childNodes;
                    let flag = false;
                    for (let j = 0; j < childNodes.length; j++) {
                        const node = childNodes[j];
                        if (node.textContent.includes('工商信息')) {
                            flag = true;
                            const gsxxDiv = node.parentNode;
                            const nextDiv = gsxxDiv.nextElementSibling;
                            const tableElement = nextDiv.querySelector('table');
                            if (tableElement) {  // 检查是否找到了 table 元素
                                tableHtml = tableElement.outerHTML;
                            } else {
                                tableHtml = '';  // 可以根据需要设定一个默认的消息或者返回空字符串等
                            }
                            break;
                        }
                    }
                    if (flag) break;
                }

                return tableHtml;
                """)
    # 逐帧滑动到最底部
    for i in range(15):
        time.sleep(0.2)
        driver.driver.execute_script(f'document.documentElement.scrollTop={(i + 1) * 300}')
    resultMap["FATHERCOMPANY"] = driver.driver.execute_script("""
                    const headerDivs = document.querySelectorAll('.xs-data-module-header');
                    let tableHtml = '';

                    for (let i = 0; i < headerDivs.length; i++) {
                        const headerDiv = headerDivs[i];
                        const childNodes = headerDiv.childNodes;
                        let flag = false;
                        for (let j = 0; j < childNodes.length; j++) {
                            const node = childNodes[j];
                            if (node.textContent.includes('股东信息')) {
                                flag = true;
                                const gsxxDiv = node.parentNode;
                                const nextDiv = gsxxDiv.nextElementSibling;
                                const tableElement = nextDiv.querySelector('table');
                                if (tableElement) {  // 检查是否找到了 table 元素
                                    tableHtml = tableElement.outerHTML;
                                } else {
                                    tableHtml = '';  // 可以根据需要设定一个默认的消息或者返回空字符串等
                                }
                                break;
                            }
                        }
                        if (flag) break;
                    }

                    return tableHtml;
                    """)
    resultMap["SONCOMPANY"] = driver.driver.execute_script("""
                        const headerDivs = document.querySelectorAll('.xs-data-module-header');
                        let tableHtml = '';

                        for (let i = 0; i < headerDivs.length; i++) {
                            const headerDiv = headerDivs[i];
                            const childNodes = headerDiv.childNodes;
                            let flag = false;
                            for (let j = 0; j < childNodes.length; j++) {
                                const node = childNodes[j];
                                if (node.textContent.includes('对外投资')) {
                                    flag = true;
                                    const gsxxDiv = node.parentNode;
                                    const nextDiv = gsxxDiv.nextElementSibling;
                                    const tableElement = nextDiv.querySelector('table');
                                    if (tableElement) {  // 检查是否找到了 table 元素
                                        tableHtml = tableElement.outerHTML;
                                    } else {
                                        tableHtml = '';  // 可以根据需要设定一个默认的消息或者返回空字符串等
                                    }
                                    break;
                                }
                            }
                            if (flag) break;
                        }

                        return tableHtml;
                        """)
    resultMap["BRANCHCOMPANY"] = driver.driver.execute_script("""
                        const headerDivs = document.querySelectorAll('.xs-data-module-header');
                        let tableHtml = '';

                        for (let i = 0; i < headerDivs.length; i++) {
                            const headerDiv = headerDivs[i];
                            const childNodes = headerDiv.childNodes;
                            let flag = false;
                            for (let j = 0; j < childNodes.length; j++) {
                                const node = childNodes[j];
                                if (node.textContent.includes('分支机构')) {
                                    flag = true;
                                    const gsxxDiv = node.parentNode;
                                    const nextDiv = gsxxDiv.nextElementSibling;
                                    const tableElement = nextDiv.querySelector('table');
                                    if (tableElement) {  // 检查是否找到了 table 元素
                                        tableHtml = tableElement.outerHTML;
                                    } else {
                                        tableHtml = '';  // 可以根据需要设定一个默认的消息或者返回空字符串等
                                    }
                                    break;
                                }
                            }
                            if (flag) break;
                        }

                        return tableHtml;
                        """)
    return resultMap


def resolveTable(html_source):
    # 使用Beautiful Soup解析HTML
    soup = BeautifulSoup(html_source, 'html.parser')

    # 找到所有的表格行（tr）
    table_rows = soup.find_all('tr', class_='xs-descriptions-tr-box')

    # 初始化一个空字典来存储表格数据
    table_data = {}

    # 遍历每一行
    for row in table_rows:
        # 找到当前行中所有的表头单元格（th）
        headers = row.find_all('th', class_='xs-descriptions-th-box')
        # 找到当前行中所有的数据单元格（td）
        data_cells = row.find_all('td', class_='xs-descriptions-td-box')

        # 判断是否包含法定代表人信息
        for header, data_cell in zip(headers, data_cells):
            header_text = header.get_text(strip=True)
            data_text = data_cell.get_text(strip=True).replace("复制点击复制", "").replace("点击复制", "")

            # 如果当前单元格包含法定代表人信息
            if header_text == "法定代表人":
                # 找到法定代表人姓名
                legal_representative_name = data_cell.find('span', class_='text left').get_text(strip=True)
                # 找到法人关联企业页面链接
                related_company_link = data_cell.find('a')['href']

                # 输出提取的法定代表人信息
                # print("法定代表人姓名:", legal_representative_name)
                # print("法人关联企业页面链接:", related_company_link)
                table_data["法定代表人"] = legal_representative_name

                # table_data["法人关联企业页面链接"] = "https://www.riskbird.com" + related_company_link
            elif header_text == "企业名称":
                table_data[header_text] = data_text.replace("曾用名", "\n曾用名")
            else:

                # 将表头作为键，数据作为值，添加到字典中
                table_data[header_text] = data_text

    # 输出解析后的表格数据
    return table_data


def resolveTableOther(html_source):
    soup = BeautifulSoup(html_source, 'html.parser')
    table = soup.find('table', class_='table-box')
    if not table:
        return "No table found."

    # Get headers as text directly
    headers = [th.get_text(strip=True) for th in table.find_all('th', class_='th-box')]

    rows = table.find_all('tr', class_='tr-box')
    table_data = []  # this should be a list of dictionaries if multiple rows are expected

    for row in rows:
        cells = row.find_all('td')
        if len(cells) == len(headers):
            row_data = {}  # initialize dictionary to store data of each row
            for header, data_cell in zip(headers, cells):
                data_text = data_cell.get_text(strip=True).replace("复制点击复制", "")

                if "法定代表人" in header:
                    legal_representative_name = data_cell.find('a')['href'].split('=')[-1]
                    row_data["法定代表人"] = legal_representative_name
                elif "股东名称" in header:
                    legal_representative_name = data_cell.find('a')['href'].split('=')[-1]
                    row_data["股东名称"] = legal_representative_name
                else:
                    row_data[header] = data_text

            table_data.append(row_data)

    return table_data


def wait_login():
    print("等待手动登录......")
    while True:
        user_input = input("登录完成后，请输入 'OK' 并按回车键继续程序: ")
        if user_input.upper() == "OK":
            return True
        else:
            print("输入错误，请重新输入。")


def doLogin(username, password):
    print("自动密码登录操作......")
    # 发送POST请求
    headers = {
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9",
        "app-device": "WEB",
        "content-type": "application/json",
        "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://www.riskbird.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    data = {
        "mobile": username,
        "smsCode": "",
        "password": password,
        "type": "password"
    }
    response = requests.post("https://www.riskbird.com/api/auth/login", json=data, headers=headers)

    # 将请求返回的cookie添加到WebDriver中
    for cookie in response.cookies:
        driver.driver.add_cookie({'name': cookie.name, 'value': cookie.value})

    driver.navigate_to("https://www.riskbird.com/")
    soup = BeautifulSoup(driver.driver.page_source, 'html.parser')
    # 查找所有符合条件的a标签
    matching_links = soup.find_all('a', href="/center/account")
    # 遍历所有匹配的链接
    loginResult = False
    for link in matching_links:
        if username in link.get_text():
            print("逻辑判断登录成功！")
            loginResult = True
            break
        else:
            print("逻辑判断登录失败！")
    return loginResult


def getCompanyBaseInfo(companyName):
    driver.navigate_to("https://www.riskbird.com/ent/" + companyName + ".html")
    # elist = driver.find_elements(By.CLASS_NAME, "xs-clip-text xs-clip-on info-basic-grow-bold")
    try:
        info = driver.driver.execute_script("""
            var elements = document.querySelectorAll('.xs-clip-text.xs-clip-on.info-basic-grow-bold');
            var combinedText = ""
            // 检查是否有至少两个这样的元素
            if (elements.length > 0) {
                for (let i = 0; i < elements.length; i++) {
                    if (i > 0) {
                        combinedText += "|";
                    }
                    combinedText += elements[i].textContent;
                }
            }
            return combinedText;
        """)

    except Exception as e:
        print(f"【{companyName}】 解析基本信息为,信息获取失败！{e}")
    info = info.replace("复制点击复制", "").replace("在营", "").replace("吊销", "")
    return info


if __name__ == '__main__':
    login_url = "https://www.riskbird.com/auth/login"
    driver.url = "https://www.riskbird.com/"
    driver.start()
    phone = '123333'
    password = 'passwd'
    #if (not doLogin(phone, password)):
    #    wait_login()

    companys = open(f"company.txt", "r", encoding="utf-8").read().split("\n")

    companyInfoList = []
    for company in companys:
        print(f"Start----开始解析【{company}】......")
        tableDataMap = getCompanyPageTableHtml(company)
        # print(tableDataMap)
        companyJson = resolveTable(tableDataMap["COMPANY"])
        relationInfo = ""
        if not tableDataMap["FATHERCOMPANY"] == "":
            relationInfo = "————————股东信息————————\n"
            fatrherCompanyJson = resolveTableOther(tableDataMap["FATHERCOMPANY"])
            print(f"fatrherCompanyJson :{fatrherCompanyJson}")
            for i in fatrherCompanyJson:
                if i["股东类型"] == "企业法人":
                    cbaseinfo = getCompanyBaseInfo(i["股东名称"])
                    cbaseinfofather = f"{cbaseinfo}"
                else:
                    cbaseinfofather = i["股东名称"]
                relationInfo += f"{cbaseinfofather}|{i['出资日期']}出资{i['认缴出资额']}({i['出资比例']})\n"
        if not tableDataMap["SONCOMPANY"] == "":
            relationInfo += "————————投资信息————————\n"
            sonCompanyJson = resolveTableOther(tableDataMap["SONCOMPANY"])
            print(f"sonCompanyJson :{sonCompanyJson}")
            for i in sonCompanyJson:
                cbaseinfo = getCompanyBaseInfo(i["被投资企业名称"])
                relationInfo += f"{cbaseinfo}({i['成立日期']})({i['状态']})|法人:{i['法定代表人']}|{i['投资数额']}({i['投资比例']})\n "
        brandInfo = ""
        if not tableDataMap["BRANCHCOMPANY"] == "":
            # brandInfo += "分支公司：\n"
            brandCompanyJson = resolveTableOther(tableDataMap["BRANCHCOMPANY"])
            print(f"brandCompanyJson :{brandCompanyJson}")
            for i in brandCompanyJson:
                cbaseinfo = getCompanyBaseInfo(i['分支机构名称'])
                brandInfo += f"{cbaseinfo}({i['成立日期']})({i['状态']})|法人:{i['负责人']}\n"
        if not relationInfo == "":
            companyJson["股权关系企业"] = relationInfo.rstrip('\n')
        if not brandInfo == "":
            companyJson["分支机构"] = brandInfo.rstrip('\n')
        print(f"公司名称:{company}|公司基本信息：{companyJson}")
        companyInfoList.append(companyJson)

    print(f"End----结果解析完成：\n{companyInfoList}")
    # https://www.qcc.com/web/search?key=
    df = pd.DataFrame(companyInfoList)
    # 将DataFrame写入Excel文件
    df.to_excel("output.xlsx", index=False)

    driver.close()
