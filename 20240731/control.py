import configparser
import time
import psutil
import threading
import tkinter as tk
from tkinter.messagebox import showinfo


class Controller:
    ui: object

    def __init__(self):
        pass

    def init(self, ui):
        self.ui = ui
        self.loadInitialization()
        self.monitor_running = False  # 禁用标记

    def loadInitialization(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='GBK')
        ini_process_name = config.get('default', 'process_name')
        self.ui.tk_input_lz86i88e.insert(0, ini_process_name)

    def startMonitor(self, evt):
        if self.monitor_running:
            return  # 如果监控已经在运行，则不执行任何操作

        process_name = self.ui.tk_input_lz86i88e.get()
        if process_name == "":
            showinfo(title="提示", message="未输入进程！")
            return False
        process_name = process_name.replace("，", ",")
        self.configurationSave('default', 'process_name', process_name)
        process_name_list = process_name.split(",")
        # print("输入框中的值为：", process_name_list)
        # 创建一个线程来更新
        self.stop_event = threading.Event()  # 创建一个事件对象
        self.thread = threading.Thread(target=self.update_counter, args=(process_name_list, self.stop_event))
        self.thread.daemon = True
        self.thread.start()

        self.ui.tk_button_lz86i38f.config(state=tk.DISABLED)  # 禁用按钮
        self.monitor_running = True

    def update_counter(self, process_name_list, stop_event):
        while not stop_event.is_set():  # 检查是否收到停止信号
            time.sleep(3)
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in process_name_list:
                    proc.terminate()
                    self.ui.tk_text_lz86hgpy.insert(tk.END, f"{current_time}：已终止进程 {proc.pid}\r\n")
                    # print(f"已终止进程 {proc.pid}")
            self.ui.tk_text_lz86hgpy.insert(tk.END, f"{current_time}：持续监控中...\r\n")
            self.ui.tk_text_lz86hgpy.see(tk.END)  # 自动滚动到底部

    # 配置保存
    def configurationSave(self, section, key, value):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='GBK')
        if not config.has_section(section):  # 判断是否包含指定section
            config.add_section(section)  # 添加section到配置文件
        config.set(section, key, str(value))  # 添加section的key-value
        with open('config.ini', "w") as f:
            config.write(f)  # 将configparser对象写入.ini类型的文件