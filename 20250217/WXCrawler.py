from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# 校验地址
def invalid_url(url):
    result = urlparse(url)
    try:
        return all([result.scheme, result.netloc])
    except:
        return False


# 动态生成请求头
def random_head():
    ua = UserAgent()
    random_headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    try:
        return random_headers
    except:
        return False


# 接收选择榜单，拼接对应url，调用对应方法
def switch_bangdan(case, headers, base_url):
    # print("传过来的榜单参数：",case)
    # print("传过来的随机请求头：",headers)
    # print("传过来的经过校验后的url地址",base_url)
    zongbang_url = base_url + "category/all"
    biaosheng_url = base_url + "category/rising"
    newbook_url = base_url + "category/newbook"
    xiaoshuo_url = base_url + "category/general_novel_rising"
    shenzuo_url = base_url + "category/newrating_publish"
    shenzuo_qianli_url = base_url + "category/newrating_potential_publish"
    resou_url = base_url + "category/hot_search"
    if case == '总榜':
        get_book_textfile(zongbang_url, headers)
    elif case == '飙升榜':
        get_book_textfile(biaosheng_url, headers)
    elif case == '新书榜':
        get_book_textfile(newbook_url, headers)
    elif case == '小说榜':
        get_book_textfile(xiaoshuo_url, headers)
    elif case == '神作榜':
        get_book_textfile(shenzuo_url, headers)
    elif case == '神作/潜力榜':
        get_book_textfile(shenzuo_qianli_url, headers)
    elif case == '热搜榜':
        get_book_textfile(resou_url, headers)
    else:
        get_book_textfile(zongbang_url, headers)


def get_book_textfile(target_url, headers):
    # print("完整的总榜url", target_url)
    res = requests.get(target_url, headers=headers)
    # print("总榜Requests请求状态码", res.status_code)
    soup = BeautifulSoup(res.content, 'lxml')
    # print(soup)
    ul = soup.find('ul', class_='ranking_content_bookList')
    # print(ul)
    # print(ul.text)
    # 数字排名
    book_paiming = ul.find_all('p', class_='wr_bookList_item_index')
    # 书籍封面图
    book_img = ul.find_all('img', class_='wr_bookCover_img', src=True)
    # 书名
    book_name = ul.find_all('p', class_='wr_bookList_item_title')
    # 作者
    book_author = ul.find_all('p', class_='wr_bookList_item_author')
    # 今日阅读人数
    book_read_num = ul.find_all('span', class_='wr_bookList_item_reading_number')
    # 本书推荐值
    book_tuijian_num = ul.find_all('span', class_='wr_bookList_item_reading_percent')
    # 作者序
    book_author_xu = ul.find_all('p', class_='wr_bookList_item_desc')

    min_length = min(len(book_paiming), len(book_img), len(book_name), len(book_author),
                     len(book_read_num), len(book_tuijian_num), len(book_author_xu))
    # print("最小标签数量", min_length)

    # for index, (
    # book_paiming, book_img, book_name, book_author, book_read_num, book_tuijian_num, book_author_xu) in enumerate(
    #         zip(book_paiming, book_img, book_name, book_author, book_read_num, book_tuijian_num, book_author_xu)):
    #     book_paiming_value = book_paiming.get_text(strip=True)
    #     book_img_value = book_img[index]['src']
    #     book_name_value = book_name.get_text(strip=True)
    #     book_author_value = book_author.get_text(strip=True)
    #     book_read_num_value = book_read_num.get_text(strip=True)
    #     book_tuijian_num_value = book_tuijian_num.get_text(strip=True)
    #     book_author_xu_value = book_author_xu.get_text(strip=True)
    #
    #     print(f'排行:{book_paiming_value}\n'
    #           f'书籍封面图:{book_img_value}\n'
    #           f'书名:《{book_name_value}》\n'
    #           f'作者:{book_author_value}\n'
    #           f'今日阅读人数:{book_read_num_value}\n'
    #           f'本书推荐值:{book_tuijian_num_value}\n'
    #           f'序:{book_author_xu_value}\n')

    desktop_path = Path.home() / 'Desktop'
    file_path = desktop_path / 'book_rankings.txt'

    with open(file_path, 'w', encoding='utf-8') as file:
        for index in range(min_length):
            book_paiming_value = book_paiming[index].get_text(strip=True)
            book_img_value = book_img[index]['src']
            book_name_value = book_name[index].get_text(strip=True)
            book_author_value = book_author[index].get_text(strip=True)
            book_read_num_value = book_read_num[index].get_text(strip=True)
            book_tuijian_num_value = book_tuijian_num[index].get_text(strip=True)
            book_author_xu_value = book_author_xu[index].get_text(strip=True)

            line = (
                f'排行:{book_paiming_value}\n'
                f'书籍封面图:{book_img_value}\n'
                f'书名:《{book_name_value}》\n'
                f'作者:{book_author_value}\n'
                f'今日阅读人数:{book_read_num_value}\n'
                f'本书推荐值:{book_tuijian_num_value}\n'
                f'序:{book_author_xu_value}\n\n\n\n'
            )

            file.write(line)
        print(f"书籍信息已保存到 {file_path}")


def main():
    base_url = "https://weread.qq.com/web/"
    #     校验地址合法性
    if not invalid_url(base_url):
        print("地址不合法")
    else:
        print(base_url)
        print("请输入要获取的榜单:")
        bangdan = input()
        # print("需要获取的榜单：",bangdan)
        headers = random_head()
        # print("生成的随机请求头：",headers)
        switch_bangdan(bangdan, headers, base_url)


if __name__ == '__main__':
    main()