import requests
import os
import re
from lxml import etree
from multiprocessing import Pool

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'
}
DETAIL_URLS_LIST = []
URL_END = 5  # 抓取几页


def get_url():
    for i in range(1, URL_END + 1):
        url = 'http://www.52guzhuang.com/forum-59-%d.html' % i
        yield url


def get_detail_url():
    urls = get_url()
    for url in urls:
        response = requests.get(url, headers=HEADERS).content.decode('gbk')
        html = etree.HTML(response)
        detail_url_list = html.xpath('//*[@id="threadlist"]/div[3]/div/div/div/div[3]/div[1]/a[2]/@href')
        for detail_url in detail_url_list:
            for i in range(1, 4):
                detail_urls = detail_url[0:-8] + str(i) + '-1.html'
                DETAIL_URLS_LIST.append(detail_urls)


def parse_url():
    try:
        for detail_url in DETAIL_URLS_LIST:
            response = requests.get(detail_url, headers=HEADERS)
            html = etree.HTML(response.content.decode('gbk'))
            imgs_title = html.xpath('//*[@id="thread_subject"]/text()')[0]
            img_title = re.sub('。，？\?,\.《》', ' ', imgs_title)
            img_urls = html.xpath(
                '//td[@class="plc"]/div[@class="pct"]//div[@align="center"]/ignore_js_op/img[@class="zoom"]/@zoomfile')
            yield img_title, img_urls
    except Exception as e:
        print(e)


def save_images(title, urls):
    for url in urls:
        try:
            image_url = 'http://www.52guzhuang.com/' + url
            image = requests.get(image_url, headers=HEADERS).content
            file_path = 'img' + os.path.sep + title
            if os.path.exists(file_path) is False:
                os.makedirs(file_path)
            img_path = file_path + os.path.sep + url[-25:]
            if os.path.exists(img_path) is True:
                print('已经下载' + img_path)
            if os.path.exists(img_path) is False:
                print('正在下载' + img_path)
                with open(img_path, 'wb') as f:
                    f.write(image)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    pool = Pool()
    get_detail_url()
    for title, urls in parse_url():
        pool.apply_async(save_images(title, urls))
    pool.close()
    pool.join()