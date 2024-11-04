import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

# 常见的 RAW 文件格式
RAW_EXTENSIONS = ['.raf', '.cr2', '.nef', '.arw', '.dng', '.orf', '.cr3', '.3fr', 'pef', '.rw2']


class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAW 文件下载器")

        # 下载链接输入框
        tk.Label(root, text="下载链接").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # 保存文件夹选择框
        tk.Label(root, text="保存文件夹").grid(row=1, column=0, padx=10, pady=10)
        self.folder_entry = tk.Entry(root, width=50)
        self.folder_entry.grid(row=1, column=1, padx=10, pady=10)
        self.folder_entry.insert(0, 'D:\\')  # 设置默认路径为D:\
        tk.Button(root, text="选择", command=self.select_folder).grid(row=1, column=2, padx=10, pady=10)

        # 下载按钮
        self.download_button = tk.Button(root, text="下载", command=self.start_download_thread)
        self.download_button.grid(row=2, column=1, pady=10)

        # 滚动日志框
        self.log_text = scrolledtext.ScrolledText(root, width=60, height=15)
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择保存文件的文件夹")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def sanitize_folder_name(self, name):
        # 替换不能作为文件夹名称的符号
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def fetch_raw_links(self, url):
        try:
            # 发送HTTP请求
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有链接
            links = soup.find_all('a')

            # 筛选出所有结尾为常见RAW格式的链接
            raw_links = [urljoin(url, link.get('href')) for link in links if
                         link.get('href') and any(link.get('href').lower().endswith(ext) for ext in RAW_EXTENSIONS)]

            # 查找页面中所有非id为logo的h1标签内容
            h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1') if h1.get('id') != 'logo']
            folder_name = h1_tags[0] if h1_tags else 'raw_files'
            folder_name = self.sanitize_folder_name(folder_name)

            return raw_links, folder_name
        except Exception as e:
            self.log(f'Error fetching links: {e}')
            return [], 'raw_files'

    def download_file(self, file_url, folder):
        try:
            # 获取文件名
            file_name = os.path.join(folder, os.path.basename(file_url))
            # 检查文件是否已经存在
            if os.path.exists(file_name):
                self.log(f'Skipping {file_name}, already exists.')
                return
            # 下载文件
            self.log(f'Downloading {file_url} to {file_name}')
            file_response = requests.get(file_url)
            file_response.raise_for_status()  # 确保请求成功
            # 保存文件
            with open(file_name, 'wb') as file:
                file.write(file_response.content)
            self.log(f'Successfully downloaded {file_name}')
        except Exception as e:
            self.log(f'Failed to download {file_url}: {e}')

    def start_download(self):
        url = self.url_entry.get()
        save_folder = self.folder_entry.get()

        if not url:
            messagebox.showerror("错误", "URL不能为空")
            return

        if not save_folder:
            messagebox.showerror("错误", "保存文件的文件夹不能为空")
            return

        raw_links, folder_name = self.fetch_raw_links(url)
        save_path = os.path.join(save_folder, folder_name)
        os.makedirs(save_path, exist_ok=True)

        # 使用ThreadPoolExecutor进行多线程下载
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有下载任务
            futures = [executor.submit(self.download_file, file_url, save_path) for file_url in raw_links]
            # 等待所有任务完成
            for future in as_completed(futures):
                future.result()  # 这将引发任何下载过程中发生的异常

        self.log('下载完成！')
        messagebox.showinfo("完成", "下载完成！")

    def start_download_thread(self):
        # 启动一个新线程来运行下载任务
        download_thread = threading.Thread(target=self.start_download)
        download_thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()