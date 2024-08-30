import  tkinter as tk
import requests
from tkinter import Menu, messagebox


class GUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('中英翻译v0.1')
        self.root.geometry("380x160+600+300")
        # 创建主菜单实例
        self.root.resizable(False, False)  # 禁止最大化
        self.menubar = Menu(self.root)
        # 显示菜单,将root根窗口的主菜单设置为menu
        self.root.config(menu=self.menubar)
        self.interface()

    def interface(self):
        """"界面编写位置"""

        self.lab1 = tk.Label(self.root, text="输入：", font=("黑体", 12, "bold"))
        self.lab1.place(x=5, y=3)

        self.lab2 = tk.Label(self.root, text="结果：", font=("黑体", 12, "bold"))
        self.lab2.place(x=200, y=3)

        self.lab3 = tk.Label(self.root, text="----->", )
        self.lab3.place(x=155, y=45)

        self.lab4 = tk.Label(self.root, text="<-----", )
        self.lab4.place(x=155, y=125)

        self.Button0 = tk.Button(self.root, text="翻译", command=self.fanyi)
        self.Button0.place(x=158, y=65, relwidth=0.1, relheight=0.35)

        self.w1 = tk.Text(self.root, width=20, height=10)
        self.w1.place(x=5, y=30)

        self.w2 = tk.Text(self.root, width=20, height=10)
        self.w2.place(x=200, y=30)

    def fanyi(self):
        zh = 'zh'
        en = 'en'
        if self.w1.get('1.0', 'end-1c') == '':
            messagebox.showinfo("内容", "翻译内容不能为空！")
        else:
            for c in self.w1.get('1.0', 'end-1c'):
                if ('\u4e00' <= c <= '\u9fa5'):  # 判断是否为中文
                    zh = 'en'
                    en = 'zh'
            try:
                url = "https://fy.httpcn.com/bdaify/?s1=%s&t1=%s&q=%s" % (en, zh, self.w1.get('1.0', 'end-1c'))
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
                }
                fanhui = requests.get(url, headers=headers, timeout=30)
                jieguo = fanhui.json()
                self.w2.delete(1.0, tk.END)
                self.w2.insert("insert", jieguo['result']['trans_result'][0]['dst'])
            except:
                self.w2.insert("insert", 'error')


if __name__ == '__main__':
    a = GUI()
    a.root.mainloop()