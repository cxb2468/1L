from typing import List
import argparse
import requests
import time
import random
import os
from bs4 import BeautifulSoup
from article import Article
from to_different_outputs import articles2txt, articles2csv, articles2csv_pandas, \
    articles2xls, articles2xlsx

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}
proxies = {
    'http': None,
    'https': None
}


def get_articles_from_html(html_txt: str) -> List[Article]:
    bs = BeautifulSoup(html_txt, 'html.parser')
    ul = bs.find(id='pagelist')
    a_links = ul.find_all('a')
    res = []
    for a_link in a_links:
        link = a_link['href']
        span_title = a_link.find(class_='one-line')
        title = span_title.text.strip()
        span_date = a_link.find_all('span')[-1]
        date = span_date.text.strip('() \n\t')
        article = Article(date, link, title)
        res.append(article)
    return res


def fetch_data_from_website():
    all_articles: List[Article] = []
    for i in range(1, 21):
        if i > 1:
            rest_time = random.uniform(0.5, 1)
            print('Have a rest for %.2fs' % (rest_time))
            time.sleep(rest_time)
        url = f'http://www.lottery.gx.cn/sylm_171188/jdzx/index_{i}.html'
        response = requests.get(url, headers=headers, proxies=proxies)
        print('dbg', i, response.text[:50])
        articles = get_articles_from_html(response.text)
        all_articles.extend(articles)
    return all_articles


def load_data_from_local():
    local_txt_name = 'lottery_gx_mid.txt'
    if not os.path.exists(local_txt_name):
        raise FileNotFoundError(f'unable to load article info because {local_txt_name} doesn\'t exist')
    with open(local_txt_name, 'r', encoding='utf-8') as f:
        lns = f.read().splitlines()
    all_articles: List[Article] = []
    for ln in lns:
        items = ln.split(' ')
        if not items:
            continue
        date = items[0]
        link = items[1] if len(items) >= 2 else ''
        title = ' '.join(items[2:]) if len(items) >= 3 else ''
        article = Article(date, link, title)
        all_articles.append(article)
    return all_articles


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Bool expected')


def main():
    arg_parser = argparse.ArgumentParser(description='lottery gx articles fetch')
    arg_parser.add_argument(
        '-out', '-o', default='txt', choices=('txt', 'csv', 'xls', 'xlsx', 'p.csv'),
        help='output file format. p.csv means using pandas to write to csv file'
    )
    arg_parser.add_argument(
        '-local', '-l', type=str2bool, default=True, help='load data from local'
    )
    cmd_args = arg_parser.parse_args()
    out_opt = cmd_args.out
    load_from_local = cmd_args.local
    all_articles = load_data_from_local() if load_from_local else fetch_data_from_website()
    if out_opt == 'txt':
        articles2txt(all_articles)
    if out_opt == 'csv':
        articles2csv(all_articles)
    if out_opt == 'p.csv':
        articles2csv_pandas(all_articles)
    if out_opt == 'xls':
        articles2xls(all_articles)
    if out_opt == 'xlsx':
        articles2xlsx(all_articles)


if __name__ == '__main__':
    main()
