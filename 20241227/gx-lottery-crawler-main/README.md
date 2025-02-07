[TOC]

# Python入门项目：一个简单的办公自动化需求

## 引言

前段时间，我npy说有一个很烦人的需求：有一个文章列表页面，总共10页，每页有30篇文章的标题、链接和日期。她领导希望把这些数据汇总进一个excel表格。她们公司有后台，由技术部的人负责维护，但技术部的后端可能是因为不想加班，并不想帮她干这个活。她在某个周二接的需求，跟领导说这事很麻烦，而且还有其他并行需求，需要到周五才能交付。我听后，笑道：“在你们公司摸鱼也太容易了。”

[样本地址](http://www.lottery.gx.cn/sylm_171188/jdzx/index.html)。值得注意的是，页面上显示只有10页数据，但实际上这10页数据仅包含了2024年的大部分文章，还有一小部分文章在第10页之后。经测试，翻到第21页时才会返回“页面地址已失效”。

面对办公自动化问题，需要考虑什么工具是你用得最趁手的。如果上述需求的数据量很小，比如10条，那就不必写代码了，可以直接手动解决，或者粘贴给LLM，让LLM处理。如果可以接受JS的数据结构格式，那么可以直接在控制台写一小段JS来解决，也不需要开IDE写Python代码。

获取某一页的文章数据：

```js
const res = [...document.getElementById('pagelist').querySelectorAll('a')].map((a) => {
    const title = a.querySelector('.one-line')?.innerText
    const link = a.href
    return [title, link]
});

// 使用方式：开两个页面，一个页面在当前页，另一个页面在下一页。当前页输出了到当前页为止的所有文章组成的数组，记为arr。进入另一个页面，执行上述代码，然后把arr粘贴到这个页面，然后输入“.push(...res)”，按回车，拿到下一页的文章数组。重复若干次
```

获取所有数据后，找出疑似重复的文章：

```js
let dat = 300 lines data;
let tmp = new Set();
let duplicate = [];
dat.reduce((res, v) => {
    if (tmp.has(v[0])) {
        duplicate.push(v);
        return res;
    }
    tmp.add(v[0]);
    res.push(v);
    return res;
}, [])
```

好了，接下来聊聊怎么用Python做这个需求。

**作者：[hans774882968](https://blog.csdn.net/hans774882968)以及[hans774882968](https://juejin.cn/user/1464964842528888)以及[hans774882968](https://www.52pojie.cn/home.php?mod=space&uid=1906177)**

本文52pojie：https://www.52pojie.cn/thread-1994769-1-1.html

本文juejin：https://juejin.cn/post/7452610281720184832

本文CSDN：https://blog.csdn.net/hans774882968/article/details/144750109

环境：

- Python 3.7.6
- pytest 7.4.4
- pandas 1.3.5, xlwt 1.3.0, styleframe 4.2

## 项目介绍

[项目传送门](https://github.com/Hans774882968/gx-lottery-crawler.git)。这个项目是麻雀虽小五脏俱全，展示了爬取前的数据准备、爬取后如何存储数据、如何进行数据处理等方面的技巧。项目结构：

```
GX-LOTTERY-CRAWLER
│  .gitignore
│  article.py to_different_outputs.py也用到Article类，所以拆分出来
│  lottery_gx_mid.txt 内容和lottery_gx_out.txt一样。样本页面数据大约每天多一条，没必要每次运行都爬取，因此产生了这个文件作为桥梁。将数据写入数据库有点小题大做，用txt存即可
│  lottery_gx_out.csv 爬到的数据输出为csv。这个csv是用csv标准库生成的
│  lottery_gx_out.p.csv 爬到的数据输出为csv。这个csv是用pandas生成的，所以加了个.p作为区分
│  lottery_gx_out.txt 爬到的数据输出为txt
│  lottery_gx_out.xls 爬到的数据输出为xls
│  lottery_gx_out.xlsx 爬到的数据输出为xlsx
│  main.py 一开始只有这个文件，后面拆分出了to_different_outputs.py
│  test_main.py 单测
│  to_different_outputs.py 爬到的数据输出为多种格式
│
├─coverage 单测输出
  │  report.html
  │
  └─assets
          style.css
```

单测命令：`pytest --html=coverage/report.html`。

我们将是否发HTTP请求获取数据，以及输出形式的决定权交给用户。所以要用到`argparse`标准库，[documentation](https://docs.python.org/zh-cn/3/howto/argparse.html)。相关代码：

```python
import argparse

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
```

## 爬取数据：BeautifulSoup

样本网站很粗糙，需要的数据在HTML里就能拿到。之前已经知道，总共有20页有效数据，不妨将这个总页码在代码里写死。

```python
proxies = {
    'http': None,
    'https': None
}

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
```

数据格式示例：

```html
<ul class="news-list" id="pagelist">
    <li>
        <a href="http://www.lottery.gx.cn/sylm_171188/jdzx/376174.html">
            <span class="one-line">
                奥运冠军盛李豪、黄雨婷、谢瑜走进“广西体彩大讲堂”分享夺金背后的故事
            </span>
            <span>
                (
                2024-12-12)
            </span>
        </a>
    </li>
    <li>
        <a href="http://www.lottery.gx.cn/sylm_171188/jdzx/376035.html">
            <span class="one-line">
                在逆境中绽放，体彩点亮我的人生希望——一名特殊体彩人的自述
            </span>
            <span>
                (
                2024-12-10)
            </span>
        </a>
    </li>
</ul>
```

用bs4解析即可。直接看代码吧：

```python
def get_articles_from_html(html_txt: str) -> List[Article]:
    bs = BeautifulSoup(html_txt, 'html.parser')
    ul = bs.find(id='pagelist')
    a_links = ul.find_all('a')
    res = []
    for a_link in a_links:
        link = a_link['href']
        span_title = a_link.find(class_='one-line')
        title = span_title.text.strip()
        span_date = a_link.find_all('span')[-1] # 取a标签下的最后一个span
        date = span_date.text.strip('() \n\t')
        article = Article(date, link, title)
        res.append(article)
    return res
```

## 写入csv：csv标准库或`pandas`

用csv标准库写入相对麻烦些：

```python
def articles2csv(articles: List[Article]):
    with open('lottery_gx_out.csv', 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(('date', 'link', 'title'))
        csv_rows = articles_to_2d_array(articles)
        csv_writer.writerows(csv_rows)
```

用`pandas`写入则相当简单：

```python
import pandas as pd

def articles2csv_pandas(articles: List[Article]):
    df = pd.DataFrame(articles)
    df.to_csv('lottery_gx_out.p.csv', index=False)
```

安装`pandas`很简单，直接`pip install pandas`。大约占10MB磁盘空间。

根据[pandas DataFrame documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)，`pd.DataFrame`可以接受`dataclass`数组，所以我们将`Article`改造为`dataclass`即可直接传入。

```python
from dataclasses import dataclass


@dataclass
class Article:
    date: str
    link: str
    title: str

    def __str__(self) -> str:
        return f'{self.date} {self.link} {self.title}'

    def __eq__(self, value: object) -> bool:
        return self.date == value.date and self.link == value.link and self.title == value.title
```

pandas默认输出的csv的编码为utf-8。如果想用Excel查看，建议点击Excel的“数据”tab→“自文本”按钮来加载数据。

## 写入xlsx

### 用`pandas`写入

我们写下这段代码，运行看看效果：

```python
def get_duplicate_and_unique(articles: List[Article]):
    st = set()
    duplicate: List[Article] = []
    unq: List[Article] = []
    for article in articles:
        title = article.title
        if title in st:
            duplicate.append(article)
            continue
        st.add(title)
        unq.append(article)
    return duplicate, unq

def articles2xlsx(articles: List[Article]):
    df_all = pd.DataFrame(articles)
    duplicate, unq = get_duplicate_and_unique(articles)
    df_unq = pd.DataFrame(unq)
    df_duplicate = pd.DataFrame(duplicate)
    df_arr = (df_all, df_unq, df_duplicate)
    with pd.ExcelWriter('lottery_gx_out.xlsx') as writer:
        for df, sheet_name in zip(df_arr, XLS_SHEET_NAMES):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
```

数据是成功写入了，但默认的列宽都太小了，需要想办法调大些。

### 用`styleframe`完成样式美化

问了下doubao AI，在用`pandas`写入Excel的场景下，调整列宽是比较麻烦的。之前可用的`set_column`方法已经废弃了（`'Worksheet' object has no attribute 'set_column'`），而现在需要直接导入`openpyxl`：

```python
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from openpyxl import load_workbook

# 创建一个示例DataFrame
data = {'姓名': ['张三', '李四', '王五'],
        '年龄': [20, 25, 30],
        '成绩': [80, 90, 95]}
df = pd.DataFrame(data)

# 将DataFrame写入Excel文件
writer = pd.ExcelWriter('example.xlsx', engine='openpyxl')
df.to_excel(writer, sheet_name='Sheet1', index=False)
workbook = writer.book
worksheet = writer.sheets['Sheet1']

# 设置列宽
for column in df:
    column_width = max(df[column].astype(str).map(len).max(), len(column))
    col_letter = get_column_letter(df.columns.get_loc(column) + 1)
    worksheet.column_dimensions[col_letter].width = column_width * 1.2
writer.save()
```

因此打算用`styleframe`调整列宽。既然用`styleframe`可以方便地完成样式美化的工作，那么不妨多做点事情。安装`styleframe`很简单，只需要`pip install styleframe`。

问了AI（Prompt：“有一个学生列表和一个老师列表。希望生成一个excel文件，将它们分别写入不同的sheet。需要使用Python的pandas和styleframe，且要使用styleframe调整列宽、设置表头样式”），注意到`styleframe.StyleFrame`也有一个`to_excel()`方法，在此和`pandas`的`to_excel`一样地调用即可。

```python
from styleframe import StyleFrame

def articles2xlsx(articles: List[Article]):
    # ...
    with pd.ExcelWriter('lottery_gx_out.xlsx') as writer:
        for df, sheet_name in zip(df_arr, XLS_SHEET_NAMES):
            sf = StyleFrame(df)
            sf.set_column_width_dict(
                {
                    'date': 15,
                    'link': 20,
                    'title': 40,
                }
            )
            sf.to_excel(writer, sheet_name=sheet_name, index=False)
```

再次打开Excel文档可以看到，虽然列宽仍然不够大，但每个单元格的内容都是完整显示的，每一行的文本都居中。这是因为源码里：

```python
# StyleFrame 构造函数有：
self._default_style = styler_obj or Styler()
# 而 Styler 构造函数有：
horizontal_alignment: str = utils.horizontal_alignments.center,
vertical_alignment: str = utils.vertical_alignments.center, # 顺便说下，默认垂直也居中
shrink_to_fit: bool = True
```

接下来我们参考[参考链接2](https://www.cnblogs.com/wang_yb/p/18070891)，给表格多加点样式。

```python
from styleframe import StyleFrame, Styler, utils

def articles2xlsx(articles: List[Article]):
    df_all = pd.DataFrame(articles)
    duplicate, unq = get_duplicate_and_unique(articles)
    df_unq = pd.DataFrame(unq)
    df_duplicate = pd.DataFrame(duplicate)
    df_arr = (df_all, df_unq, df_duplicate)
    with pd.ExcelWriter('lottery_gx_out.xlsx') as writer:
        for df, sheet_name in zip(df_arr, XLS_SHEET_NAMES):
            sf = StyleFrame(df)
            header_style = Styler(
                font_color='#2980b9',
                bold=True,
                font_size=14,
                horizontal_alignment=utils.horizontal_alignments.center,
                vertical_alignment=utils.vertical_alignments.center,
            )
            content_style = Styler(
                font_size=12,
                horizontal_alignment=utils.horizontal_alignments.left,
            )
            sf.apply_headers_style(header_style)
            sf.apply_column_style(sf.columns, content_style)

            # it's a pity that we have to set font_size and horizontal_alignment again
            row_bg_style = Styler(
                bg_color='#bdc3c7',
                font_size=12,
                horizontal_alignment=utils.horizontal_alignments.left,
            )
            indexes = list(range(1, len(sf), 2))
            sf.apply_style_by_indexes(indexes, styler_obj=row_bg_style)

            sf.set_column_width_dict(
                {
                    'date': 15,
                    'link': 20,
                    'title': 40,
                }
            )
            sf.to_excel(writer, sheet_name=sheet_name, index=False)
```

酷！

## 参考资料

1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
2. https://www.cnblogs.com/wang_yb/p/18070891