import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

column_name = 'Website'
email_column = 'Email'
visited_links = set()  # 保存已访问的链接，避免重复访问


def extract_email_from_text(text):
    """从文本中提取邮箱地址，并处理常见的反爬虫技巧"""
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    text = text.replace('[at]', '@').replace('[dot]', '.').replace('(at)', '@').replace('(dot)', '.')
    return email_pattern.findall(text)


def get_all_links(soup, base_url):
    """获取页面中的所有链接，转换为绝对路径"""
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if base_url in full_url and full_url not in visited_links:
            links.add(full_url)
    return links


def find_impressum_link(soup, base_url):
    """查找包含 'Impressum' 或 'Kontakt' 的链接"""
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if any(keyword in href.lower() for keyword in ['impressum', 'kontakt', 'contact', 'about']):
            return urljoin(base_url, href)
    return None


def find_email_near_keywords(soup):
    """通过关键字在页面文本中查找邮箱"""
    keywords = ['email', 'e-mail', 'contact']
    text = soup.get_text().lower()
    for keyword in keywords:
        if keyword in text:
            emails = extract_email_from_text(text)
            if emails:
                return emails
    return None


def get_email_from_url(url, depth=0):
    """从指定 URL 及其链接中提取邮箱地址"""
    if url in visited_links or depth > 2:  # 限制递归深度
        return None
    visited_links.add(url)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')

            # 1. 先尝试从页面文本中直接提取邮箱
            emails = extract_email_from_text(soup.get_text())
            if emails:
                return emails

            # 2. 尝试查找可能的 Impressum 或 Contact 链接
            impressum_link = find_impressum_link(soup, url)
            if impressum_link:
                logging.info(f"找到 Impressum 链接: {impressum_link}")
                email = get_email_from_url(impressum_link, depth + 1)  # 递归访问 Impressum 链接
                if email:
                    return email

            # 3. 在页面中关键字附近查找邮箱
            emails = find_email_near_keywords(soup)
            if emails:
                return emails

            # 4. 遍历页面中的所有链接，递归访问这些链接
            links = get_all_links(soup, url)
            for link in links:
                email = get_email_from_url(link, depth + 1)
                if email:
                    return email
    except RequestException as e:
        logging.error(f"请求 URL 时发生错误: {e}")

    return None


def process_url(url):
    """处理单个 URL，提取邮箱地址"""
    if pd.notna(url) and url.strip() != '':
        url = 'https://' + url.strip()
        logging.info(f"访问: {url}")
        emails = get_email_from_url(url)
        if emails:
            email = emails[0]  # 如果找到多个邮箱，可以调整为选择最合适的
            logging.info(f"找到邮箱: {email}")
            return url, email
        else:
            logging.info("没有找到邮箱")
            return url, ''
    else:
        logging.info(f"跳过空 URL 或无效 URL: {url}")
        return url, ''


# 使用上下文管理器来处理 Excel 文件
input_file = 'out3.xlsx'
output_file = 'out3_updated.xlsx'

try:
    # 读取 Excel 文件
    df = pd.read_excel(input_file, engine='openpyxl')

    # 添加邮箱列
    if email_column not in df.columns:
        df[email_column] = ''

    # 使用线程池处理 URL
    with ThreadPoolExecutor(max_workers=1000) as executor:
        future_to_url = {executor.submit(process_url, row[column_name]): index for index, row in df.iterrows()}

        for future in as_completed(future_to_url):
            index = future_to_url[future]
            try:
                url, email = future.result()
                df.at[index, email_column] = email
            except Exception as e:
                logging.error(f"处理 URL 时发生错误: {e}")

    # 使用上下文管理器来写入 Excel 文件
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as excel_writer:
        df.to_excel(excel_writer, index=False)
        logging.info(f"处理完成，结果已保存到 {output_file}")

except Exception as e:
    logging.error(f"处理 Excel 文件时发生错误: {e}")