from tkinter import ttk
import tkinter  as tk
import time, re
import parsel
import requests
import urllib.parse
from tkinter.filedialog import askdirectory
import threading

headers = {
    'Referer': 'https://www.9ku.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}


def start_music():
    for i in range(5):
        name = ui.path1.get()
        ui.t.insert('insert', "正在搜索歌曲：" + name)
        ui.t.insert('insert', "\n")
        name1 = urllib.parse.quote(name)
        url = f"https://baidu.9ku.com/song/?key={name1}"
        try:
            rep1 = requests.get(url=url, headers=headers).text
            music_nums = re.findall(r'<li><input\s+style="display:none"\sclass="check"\stype="checkbox"\svalue="(.*?)@',
                                    rep1)
            selector = parsel.Selector(rep1)
            songNames = selector.xpath('//ul[@class="clearfix"]/li/a[@class="songName"]/text()').extract()
            singerNames = selector.xpath('//ul[@class="clearfix"]/li/a[@class="singerName"]/text()').extract()
            for music_num, songname, singerName in zip(music_nums, songNames, singerNames):
                dowm_url = f'https://www.9ku.com/down/{music_num}.htm'
                resp = requests.get(url=dowm_url, headers=headers)
                music_url = re.findall('a\shref="(.*?)" style="display', resp.text)[0]
                print(music_url, songname, singerName)
                ui.t.insert('insert', music_url, songname, singerName)
                ui.t.insert('insert', "\n")
                music_down(music_url, songname, name)
            print('所有歌曲下载完毕')
            ui.t.insert('insert', '所有歌曲下载完毕')
            break
        except:
            print('没有找到，请输入正确的歌曲名称')
            ui.t.insert('insert', '没有找到，请输入正确的歌曲名称')
            ui.t.insert('insert', "\n")
            continue


def music_down(music_url, songname, name):
    pat = ui.vv.get()
    print(pat)
    path = pat + "\\" + name + songname + ".mp3"
    resp = requests.get(url=music_url, headers=headers).content
    with open(path, "wb")  as  f:
        f.write(resp)
        ui.t.insert('insert', f"歌曲{name} 歌手{songname}下载完成")
        ui.t.insert('insert', "\n")


def main():
    ui.t.delete('1.0', 'end')
    start = time.time()
    thread = threading.Thread(target=start_music)
    thread.start()
    tim = time.time() - start
    tim = round(tim, 2)
    print("一共耗时", tim)
    ui.t.insert('insert', f"一共耗时{tim}秒")
    ui.t.insert('insert', "\n")


class music_ui():
    def __init__(self, root):
        self.root = root
        self.vv = tk.StringVar()
        self.path1 = tk.StringVar()

    def ui_cuaw(self):
        # 标题
        self.root.title("音乐下载")
        # 画布大小
        self.root.geometry("600x480")
        # 标签
        tk.Label(self.root, text="九酷歌曲下载", font="楷体").place(x=250, y=10)
        # 备注
        tk.Label(self.root, text="可以搜索歌曲名或者歌手名支持模糊搜索").place(x=40, y=30)
        # 搜索按钮
        ttk.Button(self.root, text="搜索", command=start_music).place(x=40, y=50)
        # 输入框
        ttk.Entry(self.root, width=60, textvariable=self.path1).place(x=140, y=52)
        # 选择存放地址
        ttk.Button(self.root, text="选择存放地址", command=self.storage).place(x=40, y=80)
        ttk.Entry(self.root, width=60, textvariable=self.vv).place(x=140, y=82)
        # 状态文本框
        tk.Label(self.root, text="下载状态").place(x=240, y=110)
        ttk.Button(self.root, text="歌曲下载", command=main).place(x=40, y=110)
        self.t = tk.Text(self.root, width=75, height=24)
        self.t.place(x=40, y=140)

    def storage(self):
        path = askdirectory()
        music_down_path = path.replace("/", "\\\\")
        print(music_down_path)
        self.vv1 = self.vv.set(music_down_path)


if __name__ == '__main__':
    # 画布
    root = tk.Tk()
    # ui类
    ui = music_ui(root)
    ui.ui_cuaw()
    # 循环
    root.mainloop()