from bs4 import BeautifulSoup
#     运行会提示from bs4 import BeautifulSoup
# ModuleNotFoundError: No module named 'bs4'
# 报错是因为BeautifulSoup 的最新版本是 4.x 版本，之前的版本已经停止开发了，这里推荐使用 Pip 来安装，安装命令如下：
# pip3 install beautifulsoup4
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple beautifulsoup4


# 验证是否完成


# from bs4 import BeautifulSoup
# soup = BeautifulSoup('<p>cloudbility</p>', 'lxml')
# print(soup.p.string)
# 为什么？我们安装的是 beautifulsoup4 包，但是在引入的时是引入的 bs4？
# 因为这个包源代码本身的库文件夹名称就是 bs4，所以安装完成之后，这个库文件夹就被移入到我们 Python3 的 lib 库里，所以识别到的库文件名称就叫做 bs4，所以我们引入的时候就引入 bs4 这个包。
# 所以，包本身的名称和我们使用时导入的包的名称并不一定是一致的。
import re
import urllib.request, urllib.error
import xlwt
from fake_useragent import UserAgent

kaishi = int(input("请输入开始节点："))
jieshu = int(input("请输入结束节点："))
# 检测编号
number = re.compile(r'<span id="ctl00_ContentPlaceHolder1_Label1">(.*)</span>')
# 检测日期
date = re.compile(r'<spanid="ctl00_ContentPlaceHolder1_Label2">(.*)</span>')
# 检测名称
c_name = re.compile(r'<spanid="ctl00_ContentPlaceHolder1_Label3">(.*)</span>')
# 公司名称
client = re.compile(r'<spanid="ctl00_ContentPlaceHolder1_Label4">(.*)</span>')


def main():
    baseurl = "http://www.tcspbj.com/News/Report.aspx?id="
    datalist = getData(baseurl)
    name_ = str(kaishi) + str('-') + str(jieshu)
    file_name = str(name_ + ".xls")
    saveData(datalist, str(kaishi) + str('-') + str(jieshu) + ".xls")


def getData(baseurl):
    datalist = []
    for i in range(kaishi, jieshu):
        url = baseurl + str(i)
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("spanid", class_="time"):
            data = []
            item = str(item)
            one = re.findall(number, item)[0]
            data.append(one)
            tow = re.findall(date, item)[0]
            data.append(tow)
            seer = re.findall(c_name, item)
            data.append(seer)
            fors = re.findall(client, item)[0]
            data.append(fors)
            datalist.append(data)
    return datalist


def askURL(url):
    headers = {'User-Agent': str(UserAgent().random)}
    request = urllib.request.Request(url, headers=headers)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLErrorase:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


def saveData(datalist, savepath):
    print("save.......")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet(str(kaishi) + str('-') + str(jieshu), cell_overwrite_ok=True)
    col = ("报告编号", "报告日期", "产品型号名称", "送检单位")
    for i in range(0, 4):
        sheet.write(0, i, col)
    for i in range(0, ):
        print("第%d条" % (i + 1))
        data = datalist
        for j in range(0, 4):
            sheet.write(i + 1, j, data[j])
    book.save(str(kaishi) + str('-') + str(jieshu) + ".xls")


main()
print("结束")