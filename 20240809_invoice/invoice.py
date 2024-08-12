import pdfplumber
import re
import tkinter as tk
from tkinter import filedialog
import threading
import shutil
import os
import configparser


# 新线程的工作函数
def worker(arg):
    # 创建ConfigParser对象
    config = configparser.ConfigParser()
    # 读取INI文件
    config.read('config.ini')
    xuhao = config.get('RunCount1', 'count1')
    oldfile = config.get('RunCount2', 'count2')
    oldfile_data = os.path.dirname(oldfile)
    money = config.get('RunCount2', '金额')
    newfile = oldfile_data + '/重命名文件/' + money + '(' + xuhao + ').pdf'
    # 检查重命名文件文件夹是否存在
    if not os.path.exists(os.path.join(oldfile_data, '重命名文件')):
        # 如果不存在，就创建重命名文件文件夹
        os.makedirs(os.path.join(oldfile_data, '重命名文件'))
        print('重命名文件夹创建成功')

    shutil.move(oldfile, newfile)  # move是移动，如果只想复制可以更换为copy


def main():
    filetypes = (
        ('pdf文件', '*.pdf'),
        ('所有文件', '*.*')
    )

    filename = filedialog.askopenfilename(
        title='选择要打开的文件',
        initialdir='D:/',
        filetypes=filetypes)

    if filename:

        # 读取PDF文档
        with pdfplumber.open(filename) as pdf:
            # 获取文档的总页数
            total_pages = len(pdf.pages)

            # 遍历每一页
            for page_number in range(total_pages):
                # 获取当前页
                page = pdf.pages[page_number]

                # 提取文本内容
                text = page.extract_text()

                # pattern = r'（小写）&#165;\d+\.\d+'
                # pattern = r'（小写）￥\s*\d+\.\d+'
                pattern = r'（小写）[\uFFE5¥]\S*\d+(\.\d+)?'
                # 使用re.search 方法提取匹配的内容
                match = re.search(pattern, text)
                money = match.group()
                text = money
                pattern = r"(\d+(\.\d+)?)"
                result = re.search(pattern, text)
                extracted_amount = result.group()
                money = extracted_amount

                # 检查是否找到匹配项并打印结果
                if match:
                    # 要写入的新内容
                    new_lines = [filename, money]

                    # 创建配置文件对象
                    config = configparser.ConfigParser()

                    # 设置运行次数的节和键
                    run_count_section = 'RunCount1'
                    run_count_key = 'count1'

                    run_count_section_1 = 'RunCount2'
                    run_count_key_1 = 'count2'

                    # 检查配置文件是否存在，如果不存在则创建
                    config_file = 'config.ini'
                    if not config.read(config_file, encoding='ANSI'):
                        config[run_count_section] = {run_count_key: '0'}

                        with open(config_file, 'w', encoding='ANSI') as configfile:
                            config.write(configfile)

                    config[run_count_section_1] = {run_count_key_1: filename,
                                                   '金额': money
                                                   }

                    # 读取运行次数
                    current_count = config.getint(run_count_section, run_count_key)

                    # 递增运行次数
                    new_count = current_count + 1
                    config.set(run_count_section, run_count_key, str(new_count))

                    # 保存配置文件
                    with open(config_file, 'w', encoding='ANSI') as configfile:
                        config.write(configfile)

                    print(f"重命名的第: {new_count}张发票", '金额：', money)

                    section1_values_1 = config['RunCount1']

                    section1_values_2 = config['RunCount2']

                    list_data = ['发票信息',
                                 section1_values_2['count2'],
                                 os.path.dirname(section1_values_2['count2']),
                                 '/',
                                 section1_values_2['金额'],
                                 '(',
                                 section1_values_1['count1'],
                                 ').pdf']

                    # 主线程中创建新线程，并传递参数
                    t = threading.Thread(target=worker, args=(list_data,))
                    t.start()
                else:
                    print("未找到匹配项")


# 程序入口
if __name__ == "__main__":
    root = tk.Tk()
    root.title("文件上传")
    root.geometry('300x150')

    upload_button = tk.Button(root, text='选择PDF文档', command=main)
    upload_button.pack(expand=True)

    root.mainloop()
