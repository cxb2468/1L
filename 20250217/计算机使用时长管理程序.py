import tkinter as tk
import time
import os
import logging
import datetime
import comtypes.client
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import psutil
import threading



# 全局标志位，用于控制 monitor_and_terminate 线程的终止
stop_monitor_thread = threading.Event()


# 倒计时完成验证窗口
class Yanzheng:  # 休息窗口
    def __init__(self, shi, fen, miao):
        # 调用函数，将 config.txt 作为参数传入
        self.modify_second_line('config.txt')
        toggle_mute()
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Countdown Timer")
        # 使窗口最大化
        self.root.state('zoomed')
        # 设置窗口背景为黑色
        self.root.configure(bg='black')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 为关闭窗口协议指定处理函数 on_close
        # 隐藏最小化、最大化和关闭按钮
        self.root.overrideredirect(True)
        # 让窗口可以拖动
        self.root.bind('<B1-Motion>', self.move_window)
        self.root.attributes('-topmost', True)
        # 初始倒计时时间为 2 小时（秒）
        self.shi = shi * 60 * 60
        self.fen = fen * 60
        self.miao = miao
        self.remaining_time = shi * 60 * 60 + fen * 60 + miao
        self.password_attempts = 5  # 记录密码输入尝试次数，初始为 5 次
        # 创建一个标签用于显示倒计时
        self.label = tk.Label(self.root, text="休息中...", bg='black', fg='white', font=("Arial", 34))
        self.label.pack(expand=True)
        # 创建一个标签用于显示剩余尝试次数
        self.attempts_label = tk.Label(self.root, text=f"剩余尝试次数: {self.password_attempts}", bg='black', fg='white', font=("Arial", 18))
        self.attempts_label.pack()
        self.update_countdown()
        # 创建密码输入框
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        self.password_entry.bind("<Return>", self.check_password)
        # 进入主事件循环
        self.root.mainloop()

    def modify_second_line(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            if len(lines) >= 2:
                lines[1] = '000001\n'
            with open(filename, 'w') as file:
                file.writelines(lines)
        except FileNotFoundError:
            print(f"文件 {filename} 未找到")
        except Exception as e:
            print(f"发生错误: {e}")

    def on_close(self):
        return  # 此函数直接返回，不执行任何关闭操作，从而阻止窗口关闭

    def update_countdown(self):
        if self.remaining_time > 0:
            # 将剩余时间转换为 hh:mm:ss 格式
            countdown_text = time.strftime('%H:%M:%S', time.gmtime(self.remaining_time))
            self.label.config(text=countdown_text)
            self.remaining_time -= 1
            self.root.after(1000, self.update_countdown)  # 每秒更新一次
        else:
            self.shutdown()

    def move_window(self, event):
        self.root.geometry(f'+{event.x_root}+{event.y_root}')

    def check_password(self, event):
        password = self.password_entry.get()
        correct_password = mima  # 在此处设置正确的密码
        if password == correct_password:
            toggle_mute()
            self.root.destroy()  # 关闭窗口，结束程序
            stop_monitor_thread.set()  # 设置标志位，通知 monitor_and_terminate 线程终止
            thread1.join()  # 等待 monitor_and_terminate 线程终止
        else:
            self.password_attempts -= 1
            self.attempts_label.config(text=f"剩余尝试次数: {self.password_attempts}")  # 更新剩余尝试次数的显示
            if self.password_attempts <= 0:
                self.shutdown()
            else:
                self.password_entry.delete(0, tk.END)  # 清空密码输入框

    def shutdown(self):
        toggle_mute()
        os.system("shutdown /s /t 0")


class Daojishi:  # 倒计时窗口
    def __init__(self, shi, fen, miao):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("倒计时")
        self.root.geometry("240x100")  # 设置窗口大小为 240x100
        # 设置窗口背景为黑色
        self.root.configure(bg='black')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 为关闭窗口协议指定处理函数 on_close
        # 隐藏最小化、最大化和关闭按钮
        self.root.overrideredirect(True)
        # 让窗口可以拖动
        self.root.bind('<B1-Motion>', self.move_window)
        # 获取屏幕的宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 计算窗口在屏幕中心的位置
        x = (screen_width - 240) // 2
        y = (screen_height - 100) // 2
        # 设置窗口的位置
        self.root.geometry(f"+{x}+{y}")
        self.root.attributes('-topmost', True)
        # 初始倒计时时间为 2 小时（秒）
        self.shi = shi * 60 * 60
        self.fen = fen * 60
        self.miao = miao
        self.remaining_time = shi * 60 * 60 + fen * 60 + miao
        # 创建一个标签用于显示倒计时
        self.label = tk.Label(self.root, text="", bg='black', fg='white', font=('Helvetica', 28))
        self.label.pack(expand=True)
        # 开始倒计时
        self.start_time = time.time()  # 记录开始时间
        self.update_countdown()
        # 进入主事件循环
        self.root.mainloop()

    def on_close(self):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.overrideredirect(True)
        # 此函数直接返回，不执行任何关闭操作，从而阻止窗口关闭
    def update_countdown(self):
        if self.remaining_time > 0:
            # 将剩余时间转换为 hh:mm:ss 格式
            countdown_text = time.strftime('%H:%M:%S', time.gmtime(self.remaining_time))
            self.label.config(text=countdown_text)
            self.remaining_time -= 1
            elapsed_time = time.time() - self.start_time  # 计算经过的时间
            if elapsed_time >= 5:  # 每过 5 秒
                self.write_remaining_time_to_file()
                self.start_time = time.time()  # 重置开始时间
            self.root.after(1000, self.update_countdown)  # 每秒更新一次
        else:
            self.root.destroy()
            d = Yanzheng(0, 0, yanzhengshijian)

    def move_window(self, event):
        self.root.geometry(f'+{event.x_root}+{event.y_root}')

    def write_remaining_time_to_file(self):
        try:
            with open('config.txt', 'r+') as config_file:
                lines = config_file.readlines()
                # 将剩余时间转换为 hhmmss 格式
                remaining_time_hhmmss = time.strftime('%H%M%S', time.gmtime(self.remaining_time))
                lines[1] = remaining_time_hhmmss + '\n'
                config_file.seek(0)
                config_file.writelines(lines)
        except FileNotFoundError:
            logging.error("config.txt 文件未找到，请检查文件路径。")
            print("config.txt 文件未找到，请检查文件路径。")


# 文件读取部分
try:
    with open('config.txt', 'r',encoding='utf-8') as config_file:  # 以只读模式打开 config.txt 文件
        morenshijian = config_file.readline().strip()  # 读取文件的第一行，默认时间，并去除换行符
        shengyushijian = config_file.readline().strip()  # 读取文件的第二行，剩余时间，并去除换行符
        shi = int(shengyushijian[0:2])
        fen = int(shengyushijian[2:4])
        miao = int(shengyushijian[4:6])
        riqi = config_file.readline().strip()  # 读取文件的第三行，日期，并去除换行符
        yue = int(riqi[0:2])
        ri = int(riqi[2:4])
        yanzhengshijian = int(config_file.readline().strip())  # 读取文件的第四行，验证时间，并去除换行符
        mima = config_file.readline().strip()  # 读取文件的第五行，密码，并去除换行符
except FileNotFoundError:
    logging.error("config.txt 文件未找到，请检查文件路径。")
    print("config.txt 文件未找到，请检查文件路径。")


def xiugai():
    try:
        with open('config.txt', 'r') as config_file:  # 以只读模式打开 config.txt 文件
            # 跳过第一行，如果不需要使用第一行的信息
            config_file.readline()
            gengxinshengyushijian = config_file.readline().strip()  # 读取文件的第二行，剩余时间，并去除换行符
            global gengxinshi, gengxinfen, gengxinmiao
            gengxinshi = int(gengxinshengyushijian[0:2])
            gengxinfen = int(gengxinshengyushijian[2:4])
            gengxinmiao = int(gengxinshengyushijian[4:6])
    except FileNotFoundError:
        print("config.txt 文件未找到")
        return


# 静音部分
def toggle_mute():
    # 获取系统默认音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
    volume = comtypes.cast(interface, comtypes.POINTER(IAudioEndpointVolume))
    # 检查当前是否静音
    is_muted = volume.GetMute()
    if is_muted:
        # 如果当前是静音，取消静音
        volume.SetMute(0, None)
    else:
        # 如果当前不是静音，设置为静音
        volume.SetMute(1, None)


# 任务管理器监测部分
def monitor_and_terminate():
    target_processes = ["Taskmgr.exe", "perfmon.exe"]
    while not stop_monitor_thread.is_set():  # 检查标志位是否被设置
        # 遍历系统中所有正在运行的进程
        for proc in psutil.process_iter():
            try:
                # 获取进程名称
                proc_name = proc.name()
                # 如果进程名称在目标进程列表中
                if proc_name in target_processes:
                    # 终止进程
                    proc.terminate()
                    print(f"Terminated process: {proc_name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 处理可能出现的异常
                pass
        # 休眠 1 秒，避免过度占用 CPU 资源
        time.sleep(1)


# 主程序
def main():
    print("主线程启动")
    now = datetime.datetime.now()
    # 获取当前月份
    month = now.month
    # 获取当前日期
    day = now.day
    huoqvriqi = str(month).zfill(2) + str(day).zfill(2)
    if month == yue and day == ri:
        print("未重置数据")  # 不更新日期
        q = Daojishi(shi, fen, miao)
    else:
        # 更新日期，更新剩余时间
        # 调用函数，将 'config.txt' 文件中的第二行替换为变量morenshijian
        # 读取文件内容
        with open('config.txt', 'r') as file:
            lines = file.readlines()
        # 检查文件是否有至少三行
        if len(lines) >= 3:
            # 修改第二行和第三行
            lines[1] = morenshijian + '\n'  # 替换第二行内容，添加换行符保持格式
            lines[2] = huoqvriqi + '\n'  # 替换第三行内容，添加换行符保持格式
        # 将修改后的内容写回文件
        with open('config.txt', 'w') as file:
            file.writelines(lines)
        print("已重置数据")
        xiugai()
        q = Daojishi(gengxinshi, gengxinfen, gengxinmiao)


if __name__ == '__main__':
    # 创建线程
    thread1 = threading.Thread(target=monitor_and_terminate)
    thread3 = threading.Thread(target=main)

    # 启动线程
    thread1.start()
    thread3.start()

    # 等待所有线程执行完毕
    thread1.join()
    thread3.join()