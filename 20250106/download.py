import tkinter as tk
import parsel
import requests
from PIL import Image
import os
import re
from PyPDF2 import PdfMerger
import json


# 下载图片
def download_image(url, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # 创建目录
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)


# 删除文件夹下所有文件
def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


# 删除文件夹
def remove_folder(path):
    if os.path.exists(path):
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        else:
            for filename in os.listdir(path):
                remove_folder(os.path.join(path, filename))
            os.rmdir(path)


def trans_jpg2pdf(jpg_list: list, tmpdir: str) -> list:
    """jpg图片转换成pdf

    Args:
        jpg_list (list): 图片文件列表
        tmpdir (str): 临时目录路径

    Returns:
        list: 图片转换后的pdf文件列表
    """
    pdf_list = []
    for jpg in jpg_list:
        jpg_path = os.path.join(images_dir, jpg)
        pdf_file = jpg.replace('.png', '.pdf')
        pdf_path = os.path.join(tmpdir, pdf_file)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        pdf_list.append(pdf_path)
        im = Image.open(jpg_path)
        im.save(pdf_path, 'PDF', resolution=100.0)
    return pdf_list


def merge_pdf(pdf_list: list, result_pdf):
    """ 合并pdf文件
    Args:
        pdf_list (list): pdf文件列表
        result_pdf (str): 合并后的pdf文件名称
    """
    sorted_list = sorted(pdf_list, key=lambda x: int(re.search(r'\d+', x).group()))
    f_merger = PdfMerger()
    for pdf in sorted_list:
        f_merger.append(pdf)
    if os.path.exists(result_pdf):
        os.remove(result_pdf)
    with open(result_pdf, 'wb') as f:
        f_merger.write(f)
    f_merger.close()  # 将 close() 移动到写入操作之后


def getUrl(url):
    response = requests.get(url)
    return response


def getPage(current, key):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://hbba.sacinfo.org.cn/stdList",
    }
    url = "https://hbba.sacinfo.org.cn/stdQueryList"
    data = {
        "current": f"{current}",
        "size": "100",
        "key": f"{key}",
        "status": "现行"
    }
    response = requests.post(url, headers=headers, data=data)
    return response


def search():
    global records  # 声明records为全局变量
    keyword = entry_keyword.get()
    getJson = json.loads(getPage(1, keyword).text)
    pages = getJson["pages"]
    records = getJson["records"]
    listbox_results.delete(0, tk.END)
    for i, record in enumerate(records):
        chName = record["chName"]
        code = record["code"]
        listbox_results.insert(tk.END, f'{i + 1} 《{chName}》{code}')


def download_selected():
    selected_index = listbox_results.curselection()
    if selected_index:
        getNum = selected_index[0]
        getId = records[getNum]["pk"]
        chName = records[getNum]["chName"]
        code = records[getNum]["code"].replace('/', ' ')
        titleUrl = f'https://hbba.sacinfo.org.cn/stdDetail/{getId}'
        selector = parsel.Selector(getUrl(titleUrl).text)
        title = f'《{chName}》{code}'
        url = 'https://hbba.sacinfo.org.cn/' + selector.css('h4 a::attr(href)').get()
        if url:
            html = getUrl(url).text
            numbers = re.findall(r'parseInt\(\'\d+\'\),', html)[0]
            number = re.findall(r'\d+', numbers)[0]
            key = url.split('/')[-1]

            for i in range(int(number)):
                pngUrl = f'https://hbba.sacinfo.org.cn/hbba_onlineRead_page/{key}/{i}.png'
                # 下载并保存图片
                filename = os.path.basename(pngUrl)
                download_image(pngUrl, f'images/{filename}')
                print(f'已缓存第{i}页')
            tmpdir = "temp"
            if not os.path.exists(tmpdir):
                # 如果不存在，创建目录
                os.mkdir(tmpdir)
            jpg_list = [f for f in os.listdir(images_dir) if f.endswith(".png")]
            pdf_list = trans_jpg2pdf(jpg_list, tmpdir)
            merge_pdf(pdf_list, f"{title}.pdf")
            print(f'已保存{title}.pdf')
            remove_folder(images_dir)
            remove_folder(tmpdir)
            print(f'已清理缓存页面')
        else:
            print('版权原因不公开，无法下载！')


# Create main window
root = tk.Tk()
root.title("行业标准文件 PDF下载")

images_dir = "images"
if not os.path.exists(images_dir):
    # 如果不存在，创建目录
    os.mkdir(images_dir)

# Create search frame
frame_search = tk.Frame(root)
frame_search.pack(pady=10)

# Label and entry for keyword
label_keyword = tk.Label(frame_search, text="名称:")
label_keyword.grid(row=0, column=0)
entry_keyword = tk.Entry(frame_search, width=30)
entry_keyword.grid(row=0, column=1)

# Search button
button_search = tk.Button(frame_search, text="搜索", command=search)
button_search.grid(row=0, column=2, padx=10)

# Create results frame
frame_results = tk.Frame(root)
frame_results.pack(pady=10)

# Listbox to display search results
listbox_results = tk.Listbox(frame_results, width=50, height=10)
listbox_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for listbox
scrollbar_results = tk.Scrollbar(frame_results)
scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)

# Configure scrollbar and listbox
listbox_results.config(yscrollcommand=scrollbar_results.set)
scrollbar_results.config(command=listbox_results.yview)

# Create download button
button_download = tk.Button(root, text="下载PDF", command=download_selected)
button_download.pack(pady=10)

root.mainloop()