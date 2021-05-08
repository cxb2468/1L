# from ip_proxy import ips
import requests, os, re, random
from lxml import etree

# ip_add = random.choice(ips())
if not os.path.exists('./zhifu'):
    os.mkdir('./zhifu')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}
for i in range(1, 4):
    url = 'https://www.ikmjx.com/index.php?g=portal&m=list&a=index&id=3&p=' + str(i)
    r = requests.get(url=url, headers=headers).text
    tree = etree.HTML(r)
    div_list = tree.xpath('/html/body/main/div/div[2]/div')[1:-1]
    for li in div_list:
        a = 0
        src = 'https://www.ikmjx.com' + li.xpath('./div[2]/a/@href')[0]
        titles = li.xpath('./div[2]/a/@title')[0]
        title = titles.replace('?', '')
        req = requests.get(url=src, headers=headers).text
        tree1 = etree.HTML(req)
        div1_list = tree1.xpath('/html/body/main/div/div/div/div[3]/p[2]')
        for p in div1_list:
            src_path = p.xpath('./img/@src')
            # print(src_path)
            for img in src_path:
                a = a + 1
                img_data = requests.get(url=img, headers=headers).content
                img_path = './zhifu/' + title + '_' + str(a) + '.jpg'
                with open(img_path, 'wb') as fp:
                    fp.write(img_data)
                    print(img_data, '下载完成！！！')