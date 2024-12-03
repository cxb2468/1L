import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
from PIL import Image, ImageGrab
import cv2
import numpy as np
import pyautogui
import time
import random
import threading


class ImageRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图像识别与点击")
        self.image_list = []  # 存储 (图像路径, 等待时间)
        self.default_wait_time = 100  # 默认等待时间 100 毫秒
        self.screenshot_area = None  # 用于存储截图区域
        self.rect = None  # 用于存储 Canvas 上的矩形
        self.start_x = None
        self.start_y = None
        self.canvas = None
        self.running = False  # 控制脚本是否在运行
        self.thread = None  # 用于保存线程
        self.init_ui()

    def init_ui(self):
        # 左侧布局：上传图片、截图、运行脚本按钮
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # 上传图片按钮
        self.upload_button = tk.Button(self.left_frame, text="上传图像", command=self.upload_image)
        self.upload_button.pack(pady=5)

        # 框选截图按钮（微信风格截图）
        self.screenshot_button = tk.Button(self.left_frame, text="框选截图", command=self.prepare_capture_screenshot)
        self.screenshot_button.pack(pady=5)

        # 删除选中图片按钮
        self.delete_button = tk.Button(self.left_frame, text="删除图片", command=self.delete_selected_image)
        self.delete_button.pack(pady=5)

        # 运行/停止脚本按钮
        self.toggle_run_button = tk.Button(self.left_frame, text="开始运行", command=self.toggle_script)
        self.toggle_run_button.pack(pady=5)

        # 右侧布局：图像列表显示
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # 使用 Treeview 来显示图片和等待时间
        self.tree = ttk.Treeview(self.right_frame, columns=("图片", "等待时间"), show='headings')
        self.tree.heading("图片", text="图片")
        self.tree.heading("等待时间", text="等待时间 (毫秒)")
        self.tree.column("图片", width=200)  # 调整图片列宽度
        self.tree.column("等待时间", width=200)  # 调整等待时间列宽度
        self.tree.pack(pady=5)
        self.tree.bind('<Double-1>', self.edit_wait_time)  # 双击编辑等待时间

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if file_path:
            self.image_list.append((file_path, self.default_wait_time))
            self.update_image_listbox()

    def prepare_capture_screenshot(self):
        # 隐藏主窗口
        self.root.withdraw()
        time.sleep(0.5)

        # 创建一个全屏幕的透明窗口，用于捕获框选区域
        self.top = tk.Toplevel(self.root)
        self.top.attributes('-fullscreen', True)
        self.top.attributes('-alpha', 0.3)  # 透明度设置

        # 在窗口上创建 Canvas
        self.canvas = tk.Canvas(self.top, cursor="cross", bg='grey')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # 记录起始点坐标
        self.start_x = event.x
        self.start_y = event.y
        # 如果有之前的矩形，删除
        if self.rect:
            self.canvas.delete(self.rect)
        # 创建新的矩形框
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red',
                                                 width=2)

    def on_mouse_drag(self, event):
        # 动态更新矩形框的大小
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        # 记录终点坐标
        end_x = event.x
        end_y = event.y

        # 获取截图区域
        bbox = (min(self.start_x, end_x), min(self.start_y, end_y), max(self.start_x, end_x), max(self.start_y, end_y))

        # 使用规则 "JT******.png" 命名截图文件
        timestamp = f"JT{random.randint(100000, 999999)}.png"
        screenshot_path = timestamp

        # 截图指定区域
        screenshot = ImageGrab.grab(bbox)
        screenshot.save(screenshot_path)

        # 更新图像列表
        self.image_list.append((screenshot_path, self.default_wait_time))
        self.update_image_listbox()

        # 关闭全屏透明窗口
        self.top.destroy()
        self.root.deiconify()

    def update_image_listbox(self):
        # 清空旧的列表项
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 插入新项，显示图片路径和等待时间
        for img_path, wait_time in self.image_list:
            self.tree.insert("", tk.END, values=(img_path, wait_time))

    def edit_wait_time(self, event):
        # 双击列表项，编辑等待时间
        selected_item = self.tree.selection()[0]
        selected_index = self.tree.index(selected_item)
        selected_image = self.image_list[selected_index]

        # 弹出对话框修改等待时间
        new_wait_time = simpledialog.askinteger("修改等待时间", "请输入新的等待时间（毫秒）：", initialvalue=selected_image[1])
        if new_wait_time is not None:
            self.image_list[selected_index] = (selected_image[0], new_wait_time)
            self.update_image_listbox()

    def delete_selected_image(self):
        # 删除选中的图片
        selected_item = self.tree.selection()
        if selected_item:
            selected_index = self.tree.index(selected_item[0])
            del self.image_list[selected_index]
            self.update_image_listbox()

    def toggle_script(self):
        if not self.running:
            self.start_script_thread()
            self.toggle_run_button.config(text="停止运行")
        else:
            self.stop_script()
            self.toggle_run_button.config(text="开始运行")

    def start_script_thread(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_script, daemon=True)
            self.thread.start()

    def run_script(self):
        # 按顺序执行所有图片的模板匹配并点击
        while self.running and self.image_list:
            for img_path, wait_time in self.image_list:
                if not self.running:
                    break
                self.match_and_click(img_path)
                time.sleep(wait_time / 1000.0)  # 将等待时间从毫秒转换为秒

    def stop_script(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()  # 等待线程结束
        print("脚本已停止")

    def match_and_click(self, template_path):
        # 截取当前屏幕
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # 读取模板图像
        template = cv2.imread(template_path, 0)
        if template is None:
            print(f"无法读取图像: {template_path}")
            return

        # 转换截图为灰度图像
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # 进行模板匹配
        result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(result >= threshold)

        # 如果找到了相似区域，模拟点击
        found = False
        for pt in zip(*loc[::-1]):
            # 计算点击点的位置
            click_x = pt[0] + template.shape[1] // 2
            click_y = pt[1] + template.shape[0] // 2
            # 模拟点击
            pyautogui.click(click_x, click_y)
            found = True
            break  # 点击一次后跳出

        if not found:
            print(f"未找到匹配区域: {template_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRecognitionApp(root)
    root.mainloop()