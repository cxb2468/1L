import os

import requests
import time

from PIL import Image


# 行业标准信息服务平台pdf下载
# https://hbba.sacinfo.org.cn/
# 利用图片一张一张加载
# 爬取页面从0开始，到最后一页
# https://hbba.sacinfo.org.cn/attachment/onlineRead/f3a1351c7ea9f4b0914dfe8daf2a7f9ef92ef400f2c83212e6abbc3a7f04705f
# https://hbba.sacinfo.org.cn/attachment/onlineRead/186b15530a0e4b4d130cb58fc1513f5f2d024312779b844832bfb687484899f0
# name 是url的onlineRead最后面的一串数字
name = 'f4db4bd28bb3dbb35e86cd2fd569a454ae0fe4cce70507d252bf7cd755b05761'
# 文件夹以name命名，避免重复
folder = r"./" + name + "/"
# 转换的pdf名字为1
pdfFile = r"./" + name + "/1.pdf"
os.mkdir(name)
# 开始的页面
star_num =0
def get_data(name,page):
    cookies = {
        'Hm_lvt_bc6f61eace617162b31b982f796830e6': '1718068419',
        'Hm_lpvt_bc6f61eace617162b31b982f796830e6': '1718069627',
    }
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://hbba.sacinfo.org.cn/attachment/onlineRead/856ccf5d84f60ac91cef2c665d307f4b844384554af755502cb6e1bf6a2dc457',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        'https://hbba.sacinfo.org.cn/hbba_onlineRead_page/'+name+'/'+str(page)+'.png?t=1',
        cookies=cookies,
        headers=headers,
    )
    print(response.text)
    if '404 Not Found' in response.text:
        print("已经到最后一页\n下载结束，等待转换成pdf")
        return False
    save_png(response.content,page)

def save_png(content,num):
    if(num<10):
        num= '00'+str(num)
    elif(10<=num<100):
        num='0'+str(num)
    elif(num>=100):
        num=str(num)
    time.sleep(1)
    with open('./'+name+'/'+str(num) + '.jpg', 'wb') as file:
            file.write(content)
            file.close()
            print("第" + str(num) + "页保存成功")

def combine_imgs_pdf(folder_path, pdf_file_path):
    """
    合成文件夹下的所有图片为pdf
    Args:
        folder_path (str): 源文件夹
        pdf_file_path (str): 输出路径
    """
    files = os.listdir(folder_path)
    png_files = []
    sources = []
    # 筛选出图片格式
    for file in files:
        if 'png' in file or 'jpg' in file:
            png_files.append(folder_path + file)
    #排序
    png_files.sort()
    output = Image.open(png_files[0])
    png_files.pop(0)
    for file in png_files:
        png_file = Image.open(file)
        if png_file.mode == "RGB":
            png_file = png_file.convert("RGB")
        sources.append(png_file)
    output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)

while True:
    try:
        cz = get_data(name, star_num)
        star_num = star_num+1
        if cz==False:
            break

    except Exception as e:
        print(e)
combine_imgs_pdf(folder,pdfFile)
print("转换成功，在文件夹里面找名字为1.pdf的文件")