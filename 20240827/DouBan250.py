import requests
from lxml import etree
from bs4 import BeautifulSoup
import os
import csv
import json

item_dict = {'info': []}
item_list = list()


# 获取网页内容
def get_html():
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "^cookie": "bid=gCNMDIxLN2o; ap_v=0,6.0; __utma=30149280.427624870.1724377017.1724377017.1724377017.1; __utmb=30149280.0.10.1724377017; __utmc=30149280; __utmz=30149280.1724377017.1.1.utmcsr=(direct)^|utmccn=(direct)^|utmcmd=(none)^",
        "pragma": "no-cache",
        "referer": "https://movie.douban.com/top250?start=25&filter=",
        "^sec-ch-ua": "^\\^Google",
        "sec-ch-ua-mobile": "?1",
        "^sec-ch-ua-platform": "^\\^Android^^^",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://movie.douban.com/top250?start=25&filter=",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
        "Referer;": "",
        "origin": "https://movie.douban.com",
        "Upgrade-Insecure-Requests": "1"
    }
    url = "https://movie.douban.com/top250"
    for page in range(0, 250, 25):
        params = {
            "start": str(page),
            "filter": ""
        }
        response = requests.get(url, headers=headers, params=params)

        # print(response.text)
        # print(response)
        parse_html_xpath(response.text)


# xpath提取数据
def parse_html_xpath(html):
    if html:
        et = etree.HTML(html)
        li_list = et.xpath('//ol[@class="grid_view"]/li')
        # print(li_list)
        for li in li_list:
            # 电影名字
            movie_name = li.xpath('.//img/@alt')[0]
            # 电影详情链接
            movie_href = li.xpath('.//a/@href')[0]
            # 电影导演和主演
            movie_info = " ".join(li.xpath('.//p[@class=""]/text()')[0].strip().split())
            # 电影评分
            movie_rating = li.xpath('.//span[@class="rating_num"]/text()')[0]
            # 电影评价人数
            movie_rating_num = li.xpath('.//div[@class="star"]/span[4]/text()')[0]

            # 保存字典格式方式一，用来保存json格式
            item = {}
            item['movie_name'] = movie_name
            item['movie_href'] = movie_href
            item['move_info'] = movie_info
            item['movie_rating'] = movie_rating
            item['movie_rating_num'] = movie_rating_num
            item_dict['info'].append(item)

            # 保存字典格式方式二，用来保存json格式
            # item = {
            #     "movie_name": movie_name,
            #     "movie_href": movie_href,
            #     "movie_info": movie_info,
            #     "movie_rating": movie_rating,
            #     "movie_rating_num": movie_rating_num}
            # item_dict['info'].append(item)
            # print(item_dict)

            # 保存列表
            item_list.append((movie_name, movie_href, movie_info, movie_rating, movie_rating_num))

            # print(item)
            # print(movie_name,movie_href,movie_info,movie_rating,movie_rating_num)
            # print(item_list)


# 创建表格和表头
def Creat_table_title():
    if not os.path.exists('douban.csv'):
        table_title = ['movie_name', 'movie_href', 'move_info', 'movie_rating', 'movie_rating_num']
        with open('douban.csv', 'w', encoding='utf-8', newline='') as f:
            # 方式一
            # writer = csv.writer(f)
            # writer.writerow(table_title)

            # 方式二
            # 定义表头
            writer = csv.DictWriter(f, table_title)
            # 写入表头
            writer.writeheader()


# csv保存列表格式
def csv_list_save(data):
    with open('douban.csv', 'a', encoding='utf-8', newline='') as f:
        # 定义表头
        # writer = csv.DictWriter(f, ['movie_name','movie_href', 'move_info', 'movie_rating', 'movie_rating_num'])
        # #写入表头
        # writer.writeheader()
        writer = csv.writer(f)
        # 写入数据
        writer.writerows(data)


# 字典保存json格式
def json_save(data_dic):
    # json.dumps 把字典格式转换成字符串格式
    data_json = json.dumps(data_dic, indent=2, ensure_ascii=False)
    with open('douban.json', 'w', encoding='utf-8') as f:
        f.write(data_json)


if __name__ == '__main__':
    Creat_table_title()
    html = get_html()
    print(html)
    csv_list_save(item_list)
    json_save(item_dict)
