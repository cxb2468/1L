# -*- coding: utf-8 -*-
# @Time    : 2022/8/19 13:17
# @AuThor  : lzc
# @Email   : hybpjx@163.com
# @file    : __init__.py
# @Software: PyCharm

import asyncio
from pyppeteer import launch

from collections import namedtuple

def screen_size():
    """使用tkinter获取屏幕大小"""
    # 导入gui编程的模块
    import tkinter
    # 创建一个空间界面
    tk = tkinter.Tk()
    # 获得宽高
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    # 得到返回值
    return width, height

async def main():
    # 默认无头浏览器  沙盒模式
    browser = await launch({'headless': False, 'args': ['--no-sandbox'], })
    # 新开一个page对象
    page = await browser.newPage()
    # 拿到一个尺寸 作为你的谷歌浏览器大小
    width, height = screen_size()
    # 也可以自定义
    await page.setViewport(viewport={"width": width, "height": height})
    # 开启js
    await page.setJavaScriptEnabled(enabled=True)
    # 设置请求头
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    )
    # 开启 隐藏 是selenium 让网站检测不到
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    # 访问url
    await page.goto(website.url)

    now_page = 0

    while True:

        now_page += 1
        # 滑动js  动态加载
        await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        # 优雅的等待1秒 不会造成 资源阻塞
        await asyncio.sleep(1)
        # xpath
        li_list = await page.querySelectorAll(website.list_query)
        # 可将返回值返回到列表中 可省略
        # item_list = []
        for li in li_list:
            # 防止有些网站 第一条数据获取不到 第二条数据获取的到 故加个try
            try:
                # 找寻下面所有的a标签 详情页链接地址
                title_obj = await li.querySelector("a ")
                # 找到 其 链接地址和链接标题
                title_url = await page.evaluate('(element) => element.href', title_obj)
                title_name = await page.evaluate('(element) => element.textContent', title_obj)
                # 由于网站的时间 千奇百怪 有的在td 有的在p 有的在div  所有还是不要写死了
                date_obj = await li.querySelector(website.title_date_query)
                title_date = await page.evaluate('(element) => element.textContent', date_obj)
                # 开一个新的对象
                detail_page = await browser.newPage()
                # 访问详情页
                await detail_page.goto(url=str(title_url))
                # 拿到源码
                await detail_page.content()
                # 拿到 详情页的selector 对象
                element = await detail_page.querySelector(website.content_query)
                # 拿到详情页
                content_html = await detail_page.evaluate('(element) => element.outerHTML', element)
                print(title_url, title_name, title_date, len(content_html))
                await detail_page.close()
            except Exception as e:
                print(e)
        print(f"第{now_page}页访问>>>>>")
        # 点击下一页
        next_page_link = website.next_page_query

        if next_page_link:
            await page.click(next_page_link)
        else:
            raise Exception("already Crawl complete Exit coming soon....")

        await asyncio.sleep(2)

    # return item_list

async def page_close(browser):
    for _page in await browser.pages():
        await _page.close()
    await browser.close()

if __name__ == '__main__':
    Websites = namedtuple('websites', ['url', 'list_query', 'title_date_query', 'content_query', 'next_page_query'])

    websites = [
        (
            'http://www.cqzbtb.cn/_jiaoyixinxi/',
            '.listbox ul',
            '.ys',
            '.article-wrap',
            "body > section > div > div.list-wrap.row > div.listpa > ul > li:nth-child(7)"
        ),

    ]
    for i in websites:
        website = Websites._make(i)

        a = main()
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(asyncio.gather(a))
