from tkinter import Button, END, Text, Checkbutton, Tk, IntVar
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import requests
from bs4 import BeautifulSoup
import re, pyperclip


class Application():
    def __init__(self, master=None):
        self.master = master
        self.master.wm_attributes('-topmost', 1)  # 设置窗口前段显示
        self.createWidget()
        self.master.title('每日一句发送器2.0|By pythonfun')
        self.master.geometry()

    def createWidget(self):
        Font = ("微软雅黑", 12, 'bold')

        # 定义复选框
        self.checkVar1 = IntVar()
        self.checkVar2 = IntVar()
        self.checkVar3 = IntVar()
        self.checkVar1.set(1)
        self.c1 = Checkbutton(self.master, text="金山词霸", font=("微软雅黑", 11), variable=self.checkVar1, onvalue=1,
                              offvalue=0, height=1, width=8)
        self.c1.grid(row=2, column=0)
        self.c2 = Checkbutton(self.master, text="海词", font=("微软雅黑", 11), variable=self.checkVar2, onvalue=1, offvalue=0,
                              height=1, width=8)
        self.c2.grid(row=2, column=1)
        self.c3 = Checkbutton(self.master, text="欧路", font=("微软雅黑", 11), variable=self.checkVar3, onvalue=1, offvalue=0,
                              height=1, width=8)
        self.c3.grid(row=2, column=2)

        # 设置搜索框
        self.t_read = Text(self.master, width=50, height=10, font=("微软雅黑", 12))
        self.t_read.grid(row=3, column=0, columnspan=4, padx=5)

        self.b1 = Button(self.master, text="获取句子", width=8, height=1, font=("微软雅黑", 12), command=self.send_message)
        self.b1.grid(row=2, column=5)

        self.b2 = Button(self.master, text="复制句子", width=8, height=1, font=("微软雅黑", 12), command=self.copy_text)
        self.b2.grid(row=3, column=5)

    def get_txt(self, filepath):
        ls = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                ls = [line.strip() for line in f.readlines() if line.strip() != ""]
        except Exception as exc:
            messagebox.showwarning('Warning', f'{exc}')
        return ls

    def jinshan(self):
        url = 'http://open.iciba.com/dsapi/'
        res = requests.get(url)
        content = res.json()['content'] + res.json()['note']
        return content

    def haici(self):
        url2 = r"http://dict.cn"
        resp = requests.get(url2)
        soup = BeautifulSoup(resp.text, "html.parser")
        htm = soup.find("div", class_="daily_sentence")
        sen = htm.text.strip().split("\t\t\t")[2]  # split("\n\t")[2].strip()
        return sen

    def oulu(self):
        url = f"https://dict.eudic.net/home/dailysentence/"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }
        resp = requests.get(url, headers=headers)
        quotes = re.search(r'<p class="sect sect_en">(.*)</p>', resp.text)  # lst['alt']) <span style=
        quotetrans = re.search(r'<p class="sect-trans">(.*)</p>', resp.text)
        if quotes and quotetrans:
            return quotes.group(1) + quotetrans.group(1)
        else:
            return "Failed to retrieve quotes or translation."

    def get_sentence(self):
        self.t_read.delete("1.0", "end")
        msg = "每日一句:"
        sources = [
            (self.checkVar1, self.jinshan),
            (self.checkVar2, self.haici),
            (self.checkVar3, self.oulu),
        ]

        sentences = []
        for check_var, source_func in sources:
            if check_var.get() == 1:
                sentences.append(source_func())

        if sentences:
            msg += "\n".join(sentences) + "\n"
        else:
            messagebox.showwarning("错误信息", "请选中金山词霸或者海词或insight")

        return msg

    def send_message(self):
        msgs = self.get_sentence()
        for m in msgs:
            self.t_read.insert('insert', m)

    def copy_text(self):
        pyperclip.copy(self.t_read.get("1.0", END))

    def translate_txt(self, txt):
        # 定义请求的 URL 和数据
        url = 'https://fanyi.so.com/index/search'
        data = {'eng': '1', 'validate': '', 'ignore_trans': '0', 'query': txt}
        # 伪装
        headers = {
            'useragent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36 Edg/128.0.0.0',
            'pro': 'fanyi'
        }
        # 发送 POST 请求并获取响应
        response = requests.post(url=url, headers=headers, data=data).json()
        # 提取翻译文本
        translated_text = response['data']['fanyi']
        return translated_text


if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    root.mainloop()