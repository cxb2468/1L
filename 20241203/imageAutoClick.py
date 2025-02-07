import tkinter as tk
from tkinter import StringVar, ttk
import time
import asyncio
import logging
import os
import cv2
import numpy as np
from pynput.mouse import Controller, Listener, Button
from pyautogui import screenshot
import threading
import queue

# 增加了异步，防止ui卡顿
# 设置日志
logging.basicConfig(filename='PubgAuto.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')
logger = logging.getLogger(__name__)


class AutoTaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pubg: Autotask")
        self.root.geometry("400x220")
        self.root.attributes('-topmost', True)
        self.root.bind("<Unmap>", lambda event: self.toggle_topmost(False))
        self.root.bind("<Map>", lambda event: self.toggle_topmost(True))

        # 变量初始化
        self.running = False
        self.match_count = 0
        self.click_count = 0
        self.mouse = Controller()
        self.mouse_queue = queue.Queue()  # 创建队列用于传递鼠标事件

        # UI元素
        self.status_var = StringVar(value="鼠标坐标: (0, 0) | 对局次数: 0 | 鼠标点击次数: 0")
        self.runtime_var = StringVar(value="程序运行时长: 0d 0h 0m 0s")
        self.current_time_var = StringVar(value="当前系统时间: 0000-00-00 00:00")

        tk.Label(root, textvariable=self.status_var).pack()
        tk.Label(root, textvariable=self.runtime_var).pack()
        tk.Label(root, textvariable=self.current_time_var).pack()

        self.start_button = tk.Button(root, text="开始挂机", command=self.toggle_task)
        self.start_button.pack()

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=10)

        # 开始监听鼠标
        self.mouse_listener = Listener(on_move=self.on_mouse_move)
        self.mouse_listener.start()

        # 更新当前系统时间和运行时长
        self.update_current_time()
        self.update_runtime()

        # 创建一个单独的线程来运行异步事件循环
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_event_loop, args=(self.loop,))
        self.thread.start()

        # 定期检查队列中的鼠标事件
        self.root.after(100, self.check_mouse_queue)

    def run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def toggle_topmost(self, topmost):
        self.root.attributes('-topmost', topmost)

    def on_mouse_move(self, x, y):
        self.mouse_queue.put((x, y))  # 将鼠标事件放入队列

    def check_mouse_queue(self):
        while not self.mouse_queue.empty():
            x, y = self.mouse_queue.get()
            self.status_var.set(f"鼠标坐标: ({x}, {y}) | 对局次数: {self.match_count} | 鼠标点击次数: {self.click_count}")
        self.root.after(100, self.check_mouse_queue)  # 每100毫秒检查一次队列

    def update_runtime(self):
        if self.running:
            elapsed_time = int(time.time() - self.start_time)
            days, remainder = divmod(elapsed_time, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.runtime_var.set(f"程序运行时长: {days}d {hours}h {minutes}m {seconds}s")
            self.root.after(1000, self.update_runtime)

    def update_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M')
        self.current_time_var.set(f"当前系统时间: {current_time}")
        self.root.after(1000, self.update_current_time)

    def toggle_task(self):
        if self.running:
            self.stop_task()
        else:
            self.start_task()

    def start_task(self):
        self.running = True
        self.start_button.config(text="停止挂机")
        self.start_time = time.time()
        self.update_runtime()
        self.progress.start()
        asyncio.run_coroutine_threadsafe(self.run_task_async(), self.loop)

    def stop_task(self):
        self.running = False
        self.start_button.config(text="开始挂机")
        self.progress.stop()
        if hasattr(self, 'task') and not self.task.done():
            self.task.cancel()

    async def run_task_async(self):
        while self.running:
            await self.screenshot_and_match_async()
            await asyncio.sleep(5 if self.click_count % 9 != 0 else 20)

    async def screenshot_and_match_async(self):
        screenshot_path = 'screens/sc01.png'
        screenshot().save(screenshot_path)
        logger.info(f"截图保存至: {screenshot_path}")

        templates = [(cv2.imread(f'modes/{f}', 0), f) for f in os.listdir('modes') if f.endswith('.png')]
        screen = cv2.imread(screenshot_path, 0)

        for template, template_file in templates:
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):
                target = (pt[0] + template.shape[1] // 2, pt[1] + template.shape[0] // 2)
                template_name = os.path.splitext(template_file)[0]
                logger.info(f"发现目标: {template_name} 位置: {target}")
                await self.move_and_click_async(target, template_name)
                break

    async def move_and_click_async(self, target, template_name):
        start_pos = self.mouse.position
        logger.info(f"鼠标从 {start_pos} 移动到 {target}")
        self.mouse.position = target
        await asyncio.sleep(2)
        self.mouse.click(Button.left, 2)
        self.click_count += 1
        logger.info(f"双击鼠标左键于 {target} 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.click_count % 9 == 0:
            self.match_count += 1
            logger.info(f"完成一局，总对局次数: {self.match_count}")
            self.status_var.set(f"鼠标坐标: {start_pos} | 对局次数: {self.match_count} | 鼠标点击次数: {self.click_count}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoTaskApp(root)
    root.mainloop()