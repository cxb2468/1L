# -*- coding: utf-8 -*-

"""
@File       : 风鸟.py
@Project    : pythonToolsProject
@Author     : Aura Service
@Time       : 2024/4/14 22:46
@Description:
"""
import datetime
import json
import os
import re
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
from logger import log

cookie_path = 'cookie.txt'
outputpath = f"./output/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"


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
            if header_text == "执行事务合伙人":
                table_data["法定代表人"] = data_cell.find('a')["href"].split('=')[-1]
            elif header_text == "经营者":
                table_data["法定代表人"] = data_cell.find('a')["href"].split('=')[-1]
            elif header_text == "法定代表人":
                # 找到法定代表人姓名
                legal_representative_name = data_cell.find('span', class_='text left').get_text(strip=True)
                # 找到法人关联企业页面链接
                related_company_link = data_cell.find('a')['href']

                # 输出提取的法定代表人信息
                # log.info("法定代表人姓名:", legal_representative_name)
                # log.info("法人关联企业页面链接:", related_company_link)
                table_data["法定代表人"] = legal_representative_name

                # table_data["法人关联企业页面链接"] = "https://www.riskbird.com" + related_company_link
            elif header_text == "企业名称":
                table_data[header_text] = data_text.replace("曾用名", "\n曾用名")
            else:

                # 将表头作为键，数据作为值，添加到字典中
                table_data[header_text] = data_text

    # 获取 WEB111111  orderNo
    orderNoElement = soup.find(id="__NUXT_DATA__")
    orderNo = ""
    if orderNoElement is not None:
        jlist = json.loads(orderNoElement.string)
        for i in jlist:
            if "WEB" in str(i) and re.match(r"^WEB\d+$", i):
                orderNo = i
                break
    # 输出解析后的表格数据
    return {"tableData": table_data, "orderNo": orderNo}


def doLogin(username, password):
    r = False
    log.info("自动密码登录操作......")
    url = "https://www.riskbird.com/auth/login"

    # Set up the headers based on the fetch call
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    # Prepare the session to manage cookies
    session = requests.Session()

    # Send a GET request
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        log.info("Request successful.")
        cookies = '; '.join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
        url = "https://www.riskbird.com/api/auth/login"

        headers = {
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9",
            "app-device": "WEB",
            "content-type": "application/json",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "cookie": cookies,
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "Referer": "https://www.riskbird.com/auth/login",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        data = {
            "mobile": username,
            "smsCode": "",
            "password": password,
            "type": "password"
        }
        session = requests.Session()
        response = session.post(url, headers=headers, json=data)
        if response.status_code == 200 and response.json().get("code") == 20000:
            log.info("Login successful.")
            log.info(response.json())
            cookies = '; '.join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
            open(cookie_path, "w").write(cookies)
            log.info("update cookie:", cookies)
            r = True
        else:
            log.info("Failed to login")
            log.info("Status code:", response.status_code)
            log.info("Response body:", response.text)
    else:
        log.info("Failed to fetch data")
        log.info("Status code:", response.status_code)
        log.info("Response body:", response.text)

    return r


def getCookie():
    phone = '123'
    password = 'pwd'

    r = False
    if os.path.exists(cookie_path) and checkLogin():
        r = open(cookie_path, "r").read()

    else:
        doLogin(phone, password)
        if os.path.exists(cookie_path) and checkLogin():
            r = open(cookie_path, "r").read()
    if not r:
        sys.exit()
    return r


def getCompanyPageTableHtml(company):
    url = f"https://www.riskbird.com/ent/{company}.html"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "cookie": getCookie()
    }
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            r = response.text
    except Exception as e:
        log.error(f"An error occurred: {e}")
        r = False
    return r


def getCompanyBaseInfo(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.select('.xs-clip-text.xs-clip-on.info-basic-grow-bold')
        if len(elements) > 1:
            # Combine text content from elements, separated by '|'
            info = "|".join(element.get_text(strip=True) for element in elements)
            # Replace specific substrings in the fetched text
            info = info.replace("复制点击复制", "").replace("在营", "").replace("吊销", "")
            r = info
        else:
            log.error("Not enough info elements found")
    except Exception as e:
        log.error(f"An error occurred: {e}")
        r = False
    return r


def checkLogin():
    r = False

    url = "https://www.riskbird.com/riskbird-api/user/checkIsVip"

    # Set up the headers as per the original fetch request
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "app-device": "WEB",
        "content-type": "application/json",
        "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": open(cookie_path).read(),
        "Referer": "https://www.riskbird.com/center/account",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    # Send a GET request
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json()["code"] == 20000:
        r = True
    return r


def getRequest(company, orderno, extractType):
    session = requests.Session()
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "App-Device": "WEB",
        "Content-Type": "application/json",
        "Sec-CH-UA": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": getCookie(),
        "Referer": f"https://www.riskbird.com/ent/{company}.html",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    # URL encode the Referer header
    headers['Referer'] = requests.utils.quote(headers['Referer'], safe=':/')

    # URL for the GET request
    url = f"https://www.riskbird.com/riskbird-api/query/company/searchCompanyPageByWeb?page=1&size=200&orderNo={orderno}&extractType={extractType}"
    r = False
    try:
        # Make the GET request
        response = session.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200 and response.json()["code"] == 20000:
            log.info(
                f" {company}--{orderno}--{extractType}---info:{response.text}")  # Or process the response in a way that fits your needs
            r = response.json()["data"]["apiData"]
            if len(r) < 1:
                log.info(f" {company}--{orderno}--{extractType}--- 无相关数据")
            r = False
        else:
            log.info(f" {company}--{orderno}--{extractType}---error:{response.status_code} {response.text}")
    except Exception as e:
        log.error(f" {company}--{orderno}--{extractType}---error:{e}")
    return r


def create_file_with_path(file_path):
    # 提取目录路径
    directory = os.path.dirname(file_path)

    try:
        # 如果目录不存在，则创建它
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as e:
        log.error(f"发生了一个意外错误: {e}")


if __name__ == '__main__':

    companys = open(f"company.txt", "r", encoding="utf-8").read().split("\n")
    i = 0
    companyInfoList = []
    for company in companys:
        log.info(f"Start----开始解析【{company}】({i + 1}/{len(companys)})......")
        html = getCompanyPageTableHtml(company)
        log.info(f"原始html:{html}")
        # 公司基本信息
        companyJson = resolveTable(html)

        compayInfo = companyJson["tableData"]
        orderNo = companyJson["orderNo"]

        # 股东信息
        gdczinfo = getRequest(company, orderNo, "gdcz")
        if not gdczinfo:
            log.error(f"股东信息获取失败...")
        else:
            gdinfo = ""
            for i in gdczinfo:
                conDate = i["conDate"]
                fundedRatio = i["fundedRatio"]
                invType = i["invType"]
                shaName = i["shaName"]
                subConAm = i["subConAm"]
                gdinfo += f"{shaName}--{invType}--{fundedRatio}--{subConAm}--{conDate}\n"
                log.info(gdinfo.rstrip("\n"))
            compayInfo["股东信息\n股东名称--股东类型--出资比例--认缴出资额--出资日期"] = gdinfo.rstrip('\n')

        # 对外投资
        qydwtzinfo = getRequest(company, orderNo, "qydwtz")
        if not qydwtzinfo:
            log.error(f"企业对外投资信息获取失败...")
        else:
            dwtzinfo = ""
            for i in qydwtzinfo:
                entJgName = i["entJgName"]
                name = i["name"]
                subConAm = i["subConAm"]
                fundedRatio = i["fundedRatio"]
                esDate = i["esDate"]
                entStatus = i["entStatus"]
                personid = i["personid"]
                dwtzinfo += f"{entJgName}[{entStatus}]--{name}--{subConAm}--{fundedRatio}--{esDate}\n"
                log.info(dwtzinfo.rstrip("\n"))
            compayInfo["对外投资\n被投资企业名称--法定代表人--投资数额--投资比例--成立日期"] = dwtzinfo.rstrip('\n')

        # 分支机构
        fzjginfo = getRequest(company, orderNo, "fzjg")
        if not fzjginfo:
            log.error(f"分支机构信息获取失败...")
        else:
            fzinfo = ""
            for i in fzjginfo:
                brName = i["brName"]
                brPrincipal = i["brPrincipal"]
                esDate = i["esDate"]
                ent_status = i["ent_status"]
                personId = i["personId"]
                fzinfo += f"{brName}[{ent_status}]--{brPrincipal}--{esDate}\n"
                log.info(fzinfo.rstrip("\n"))
            compayInfo["分支机构\n分支机构名称--负责人--成立日期"] = fzinfo.rstrip('\n')

        targetlist = ["执行事务合伙人"]
        x = [value for value in map(lambda index: compayInfo.pop(index) if compayInfo.get(index) else None, targetlist)]

        log.info(f"compan json: {compayInfo}")
        companyInfoList.append(compayInfo)

    log.info(f"End----结果解析完成：\n{companyInfoList}")
    # https://www.qcc.com/web/search?key=
    df = pd.DataFrame(companyInfoList)
    # 将DataFrame写入Excel文件

    create_file_with_path(outputpath)
    df.to_excel(outputpath, index=False)