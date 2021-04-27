# -*- coding: utf8 -*-
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 10:47:40 2020

@author: MJ
"""
import requests
import re
import datetime

res = []
url = 'http://www.xwlbo.com/txt.html'
tit = requests.get(url=url).text
# 打开新闻联播文字版主页
time = datetime.datetime.now().timetuple()
date_time = str(time.tm_year) + '年' + str(time.tm_mon) + '月' + str(time.tm_mday - 1) + "日新闻联播文字完整版内容"
# date_time = (datetime.date.today() + datetime.timedelta(-1)).strftime("%Y-%#m-%#d").replace('-', '{}').format('年','月') + "日新闻联播文字完整版内容"
# 获取时间
print(tit)
print(date_time)
id = re.findall(r'id="v(.*?)">%s' % (date_time), tit)
print(id)
id = id[len(id) - 1]
# 取得id
idurl = 'http://www.xwlbo.com/%s.html' % (id)
title = requests.get(url=idurl).text

# 获取对应id内容
b = re.findall(r'.html">(.*?)</a></strong></p><p>', title)

n = re.findall(r'</strong></p><p>(.*?)</p><p><strong>', title)

# 提出所需要内容
try:
    for i in range(0, len(b) - 1):
        res.append('标题：' + b[i] + '\n\n')
        res.append(n[i].replace('</p><p>', '') + '\n')
        res.append('\n')
except:
    pass
s = ''.join(res)
print("S 开始处")
print(s)
# 转换好要发送的内容
data = {
    'text': '新闻联播文字版',
    'desp': s, }
print(requests.post(url='https://sctapi.ftqq.com/SCT11567TbqhyKCJDvWUjsRA2jQ3gJoIn.send?title=messagetitle&desp=messagecontent', data=data))