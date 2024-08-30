# -*- coding: utf-8 -*-
# @Time :  16:34
# @File : 豆瓣电影TOP250数据提取并存储数据库.py
# @Software : PyCharm


from bs4 import BeautifulSoup
import requests
import re
import pymysql

data_list = list()


class Spider_Douban_Movie:
    def Get_html(self):
        self.headers = {
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
        self.url = "https://movie.douban.com/top250"
        for page in range(0, 250, 25):
            self.params = {
                "start": str(page),
                "filter": ""
            }
            response = requests.get(self.url, headers=self.headers, params=self.params).text
            # print(response)

            # 生成器，每次生成一个response
            yield response

    # 使用BeautifulSoup库解析网页内容，提取电影信息。
    def Parse_html_beautifulsoup(self, response_generator):
        for response in response_generator:
            soup = BeautifulSoup(response, 'lxml')
            movie_list = soup.find('ol', class_='grid_view').find_all('li')
            # 提取电影信息
            # 遍历电影列表，提取电影名称、评分、链接等信息。

            for movie in movie_list:
                item = dict()
                # 电影名称
                item['title'] = movie.find('span', class_='title').text
                # 电影链接
                item['href'] = movie.select('a')[0]['href']
                # 电影导演主演信息
                item['info'] = ' '.join(movie.find('div', class_='bd').p.text.strip().split())
                # 电影评分
                item['rating_num'] = movie.find('span', class_='rating_num').text
                # 电影评价人数
                item['evaluators_num'] = movie.find('div', class_='star').find_all('span')[-1].text
                # 电影语录
                item['quote'] = movie.find('span', class_='inq').text if movie.find('span', class_='inq') else '无电影语录'
                data_list.append(item)

                # print(item)


class Douban_Movie_Save_Database:
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='root', password='你的数据库密码', db='你的数据库名称')
        self.cursor = self.db.cursor()

    def create_table(self):
        sql = """
            create table if not exists movie(
                id int primary key auto_increment,
                title varchar(100) not null,
                href varchar(100),
                info varchar(500),
                rating_num varchar(100),
                evaluators_num varchar(100),
                quote varchar(100)
            );
        """

        try:
            self.cursor.execute(sql)
            print('表创建成功...')
        except Exception as e:
            print('表创建失败:', e)

    # 关闭数据库
    def __del__(self):
        self.cursor.close()
        self.db.close()

    def Insert_movie_info(self, *args):
        """
        :param args:
        :return:
            title
            info
            href
            rating_num
            evaluators
            quote
        """
        sql = """
            insert into movie() values (%s, %s, %s, %s, %s, %s, %s);
        """

        try:

            self.cursor.execute(sql, args)
            self.db.commit()  # 需要手动提交后数据库才会保存数据: 事务
            print('数据插入成功:', args)
        except Exception as e:
            print('数据插入失败:', e)
            self.db.rollback()  # 回滚

    def main(self):
        self.create_table()
        for data in data_list:
            title = data['title']
            href = data['href']
            info = data['info']
            rating_num = data['rating_num']
            evaluators_num = data['evaluators_num']
            quote = data['quote']
            self.Insert_movie_info(0, title, href, info, rating_num, evaluators_num, quote)


if __name__ == '__main__':
    spider = Spider_Douban_Movie()
    res_generator = spider.Get_html()
    spider.Parse_html_beautifulsoup(res_generator)
    # print(data_list)
    douban_movie = Douban_Movie_Save_Database()
    douban_movie.main()