import tkinter as tk
from tkinter import filedialog, messagebox
import winreg
import os

# 获取当前用户的启动项注册表路径
startup_reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
startup_reg_key = winreg.HKEY_CURRENT_USER


def get_startup_items():
    try:
        key = winreg.OpenKey(startup_reg_key, startup_reg_path, 0, winreg.KEY_READ)
        startup_items = []
        index = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, index)
                startup_items.append(name)  # 存储启动项的名称而非值
                index += 1
            except OSError:
                break
        winreg.CloseKey(key)
        return startup_items
    except FileNotFoundError:
        return []


def add_startup_item(file_path):
    try:
        file_path = os.path.normpath(file_path)  # 规范化路径
        filename = os.path.basename(file_path)
        key = winreg.OpenKey(startup_reg_key, startup_reg_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, filename, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
        messagebox.showinfo("添加启动项", f"已成功添加启动项: {filename}")
    except Exception as e:
        messagebox.showerror("添加启动项失败", f"添加启动项时出错: {str(e)}")


def remove_startup_item(item_name):
    try:
        key = winreg.OpenKey(startup_reg_key, startup_reg_path, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(key, item_name)
        winreg.CloseKey(key)
        messagebox.showinfo("删除启动项", f"已成功删除启动项: {item_name}")
    except FileNotFoundError:
        messagebox.showwarning("删除启动项", f"启动项 '{item_name}' 不存在")
    except Exception as e:
        messagebox.showerror("删除启动项失败", f"删除启动项时出错: {str(e)}")


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
    if file_path:
        add_startup_item(file_path)
        update_listbox()


def update_listbox():
    startup_items = get_startup_items()
    listbox.delete(0, tk.END)
    for item in startup_items:
        listbox.insert(tk.END, item)


def refresh_listbox():
    update_listbox()


def delete_selected_item():
    selected_index = listbox.curselection()
    if selected_index:
        selected_item = listbox.get(selected_index)
        remove_startup_item(selected_item)
        update_listbox()


# 创建Tkinter界面
root = tk.Tk()
root.title("启动项管理程序")

frame_top = tk.Frame(root)
frame_top.pack(pady=10)

add_button = tk.Button(frame_top, text="添加启动项", command=select_file)
add_button.pack(side=tk.LEFT, padx=10)

remove_button = tk.Button(frame_top, text="删除选中启动项", command=delete_selected_item)
remove_button.pack(side=tk.LEFT)

refresh_button = tk.Button(frame_top, text="手动刷新", command=refresh_listbox)
refresh_button.pack(side=tk.LEFT, padx=10)

frame_bottom = tk.Frame(root)
frame_bottom.pack(pady=20)

listbox = tk.Listbox(frame_bottom, width=50)
listbox.pack()

update_listbox()

root.mainloop()