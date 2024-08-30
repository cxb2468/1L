import requests
from lxml import etree
import os
import csv
import json

item_dict = {'info': []}
item_list = []

# 获取网页内容
def get_html():
    headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://movie.douban.com/top250?start=25&filter=",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
        "upgrade-insecure-requests": "1"
    }
    url = "https://movie.douban.com/top250"
    for page in range(0, 250, 25):
        params = {
            "start": str(page),
            "filter": ""
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # 检查响应状态码是否为200
            parse_html_xpath(response.text)
        except requests.RequestException as e:
            print(f"请求失败: {e}")


# xpath提取数据
def parse_html_xpath(html):
    if html:
        et = etree.HTML(html)
        li_list = et.xpath('//ol[@class="grid_view"]/li')
        for li in li_list:
            movie_name = li.xpath('.//img/@alt')
            movie_href = li.xpath('.//a/@href')
            movie_info = " ".join(li.xpath('.//p[@class=""]/text()')[0].strip().split()) if li.xpath('.//p[@class=""]/text()') else ''
            movie_rating = li.xpath('.//span[@class="rating_num"]/text()')
            movie_rating_num = li.xpath('.//div[@class="star"]/span[4]/text()')

            if movie_name and movie_href and movie_rating and movie_rating_num:
                movie_name = movie_name[0]
                movie_href = movie_href[0]
                movie_rating = movie_rating[0]
                movie_rating_num = movie_rating_num[0]

                item = {
                    "movie_name": movie_name,
                    "movie_href": movie_href,
                    "movie_info": movie_info,
                    "movie_rating": movie_rating,
                    "movie_rating_num": movie_rating_num
                }
                item_dict['info'].append(item)
                item_list.append((movie_name, movie_href, movie_info, movie_rating, movie_rating_num))


# 创建表格和表头
def create_table_title():
    if not os.path.exists('douban.csv'):
        table_title = ['movie_name', 'movie_href', 'movie_info', 'movie_rating', 'movie_rating_num']
        try:
            with open('douban.csv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, table_title)
                writer.writeheader()
        except IOError as e:
            print(f"文件写入失败: {e}")


# CSV保存列表格式
def csv_list_save(data):
    try:
        with open('douban.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    except IOError as e:
        print(f"文件写入失败: {e}")


# JSON保存字典格式
def json_save(data_dic):
    try:
        data_json = json.dumps(data_dic, indent=2, ensure_ascii=False)
        with open('douban.json', 'w', encoding='utf-8') as f:
            f.write(data_json)
    except IOError as e:
        print(f"文件写入失败: {e}")


if __name__ == '__main__':
    create_table_title()
    get_html()
    csv_list_save(item_list)
    json_save(item_dict)
