# -*- coding: UTF-8 -*-
'''
@Project ：网络爬虫
@file    ：kfz_demo2.py
@IDE     ：PyCharm
@AuThor  ：慕逸
@date    ：02/12/2024 15:21
@Description :  爬取孔夫子旧书网信息
'''

# TODO: 注意:在保存到MySQL数据库时,需要先创建一个名为spider的数据库

import json
import os
import pandas as pd
import pymysql
from tqdm import tqdm
import requests

class KfzDemo2():
    def __init__(self, url):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

        self.url = url

    def get_html(self):
        response = requests.get(url=self.url, headers=self.headers)
        context = response.content
        return context

    def get_data(self):
        context = self.get_html()
        data = json.loads(context)['data']['itemResponse']['list']
        data_lis = []

        for d in data:
            data_dic = {}
            data_dic['type'] = d['type']
            data_dic['书籍名称'] = d['bookName']
            # data_dic['bigImgUrl'] = d['imgUrlEntity']['bigImgUrl']
            # data_dic['smallImgUrl'] = d['imgUrlEntity']['smallImgUrl']
            data_dic['新书价格'] = d['newBookMinPrice']
            data_dic['新书余量'] = d['newBookOnSaleNum']
            data_dic['旧书价格'] = d['oldBookMinPrice']
            data_dic['旧书余量'] = d['oldBookOnSaleNum']
            data_dic['书籍信息'] = d['bookShowInfo']
            data_lis.append(data_dic)
        # print(data_lis)
        return data_lis

    def save_data(self, data):
        df = pd.DataFrame(data)

        # 保存到Excel文件
        df.to_excel('output.xlsx', index=True)

        save_path = os.path.abspath('output.xlsx')
        print("数据已成功保存到 Excel 文件,保存位置为: ", save_path)

    def save_data_to_mysql(self, data: list):
        # 连接到mysql数据库
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Cxb871231@',
            'database': 'spider',
        }

        # 连接到数据库
        connection = pymysql.connect(**db_config)

        try:
            with connection.cursor() as cursor:
                create_table = '''
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type VARCHAR(50),
                    `书籍名称` VARCHAR(255),
                    `新书价格` DECIMAL(10, 2),  -- 假设价格有小数点，使用DECIMAL更合适
                    `新书余量` INT,            -- 假设余量是整数
                    `旧书价格` DECIMAL(10, 2),
                    `旧书余量` INT,
                    `书籍信息` JSON 
                )
                '''
                cursor.execute(create_table)

                # 插入数据
                for d in tqdm(data, desc='正在存储数据'):
                    insert_sql = '''
                            INSERT INTO books (type, `书籍名称`, `新书价格`, `新书余量`, `旧书价格`, `旧书余量`, `书籍信息`)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            '''
                    val = (d['type'], d['书籍名称'], d['新书价格'], d['新书余量'], d['旧书价格'], d['旧书余量'],
                           json.dumps(d['书籍信息']))
                    cursor.execute(insert_sql, val)

                # 提交事务
                connection.commit()
                print("数据已成功插入到 MySQL 数据库")

        finally:
            connection.close()

def main():
    while True:
        data = []
        kfz = KfzDemo2(None)
        # 请输入需要数据需要保存的类型
        category_save = input(
            "**********************\n"
            "     【1】Excel(.xlsx)\n"
            "     【2】MySQL\n"
            "     【3】退出程序\n"
            "**********************\n"
            "请输入需要数据需要保存的类型的数字:"
        )
        print("**********************")
        if category_save == '3':
            print("程序已退出")
            break
        elif category_save not in ['1', '2']:
            print("输入错误，请重新输入!!!!")
            continue

        for i in tqdm(range(1, 101), desc='正在爬取数据'):  # 101
            url = "https://search.kongfz.com/pc-gw/search-web/client/pc/bookLib/category/list?catId=31&actionPath=catId&page={}".format(i)
            kfz.url = url
            data_lis = kfz.get_data()
            data.extend(data_lis)
        print("共获取{}条数据".format(len(data)))
        if category_save == '1':
            kfz.save_data(data)
        elif category_save == '2':
            try:
                kfz.save_data_to_mysql(data)
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1049:  # 错误码 1049 表示数据库不存在
                    print(
                        "****************************\n数据库不存在,请创建数据库后重新尝试\n****************************")
                else:
                    print(f"An error occurred: {e}")
        # 当数据库不存在时,会抛出数据库不存在异常

if __name__ == '__main__':
    main()
