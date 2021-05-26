import requests
from bs4 import BeautifulSoup
import os
import datetime

now = str(datetime.datetime.today().date())
# 获取当前日期

headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F'}

num = 0
url_list = []
for page in range(1, 6):
    html1 = "https://wallhaven.cc/latest?page=" + str(page)
    html2 = "https://wallhaven.cc/hot?page=" + str(page)
    html_list = [html1, html2]
    for html in html_list:
        requests_html = requests.get(html, headers=headers)

        bs_html = BeautifulSoup(requests_html.text, "lxml")

        for link in bs_html.find_all('a', class_="preview"):
            image_link = link['href']
            url_list.append(image_link)
            num += 1
            print("已获取第" + str(num) + "个链接")

a = os.path.exists("D:/1L/0526/壁纸/" + now)
if a:
    print("文件夹已存在，PASS")
else:
    os.makedirs("D:/1L/0526/壁纸/" + now)
    print("文件夹建立成功")
# 建立文件夹存放图片
num = 0
for link in url_list:
    requests_html = requests.get(link, headers=headers)
    bs_html = BeautifulSoup(requests_html.text, "lxml")
    img = bs_html.find('img', id='wallpaper')
    r = requests.get(img['src'])
    num += 1
    with open("D:/1L/0526/壁纸/" + now + "/" + str(num) + ".jpg", 'wb') as f:
        f.write(r.content)
        print("第" + str(num) + "张写入成功")
