import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
import numpy as np
import cv2
import winsound
import time
import os
from datetime import datetime


class ScreenMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("培训中心门卫室专用监控辅助系统 v2.5")
        self.root.geometry("480x320")

        # 监控状态
        self.monitoring = False
        self.last_screen = None
        self.monitor_area = None
        self.alarm_enabled = True
        self.interval_ms = 1000  # 默认检测间隔1秒

        # 纯文本日志
        self.log_file = "screen_monitor_log.txt"
        self.init_log_file()

        # 创建UI
        self.create_ui()

    def init_log_file(self):
        """初始化纯文本日志文件"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("时间\t\t\t变化比例\t监控区域\t间隔(ms)\n")
                f.write("=" * 60 + "\n")

    def write_log_entry(self, change_ratio):
        """写入文本日志（不保存图片）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        area_info = f"{self.monitor_area[2] - self.monitor_area[0]}x{self.monitor_area[3] - self.monitor_area[1]}"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}\t{change_ratio:.2%}\t{area_info}\t{self.interval_ms}\n")

    def create_ui(self):
        """创建用户界面"""
        # 顶部控制面板（第一行）
        top_frame1 = ttk.Frame(self.root)
        top_frame1.pack(pady=(10, 0), fill=tk.X, padx=10)

        ttk.Button(top_frame1, text="&#128433;&#65039; 选择监控区域",
                   command=self.start_area_selection).pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(top_frame1, text="&#9654;&#65039; 开始监控",
                                    command=self.start_monitoring, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(top_frame1, text="&#9209;&#65039; 停止监控",
                                   command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 顶部控制面板（第二行）
        top_frame2 = ttk.Frame(self.root)
        top_frame2.pack(pady=(5, 10), fill=tk.X, padx=10)

        # 声音报警开关
        self.alarm_btn = ttk.Checkbutton(top_frame2, text="&#128266; 启用声音报警",
                                         command=self.toggle_alarm)
        self.alarm_btn.pack(side=tk.LEFT, padx=5)
        self.alarm_btn.state(['selected'])

        # 间隔时间设置
        ttk.Label(top_frame2, text="检测间隔:").pack(side=tk.LEFT, padx=(10, 0))
        self.interval_var = tk.StringVar(value="1000")
        self.interval_spin = ttk.Spinbox(top_frame2, from_=100, to=10000, increment=100,
                                         textvariable=self.interval_var, width=6)
        self.interval_spin.pack(side=tk.LEFT)
        ttk.Label(top_frame2, text="毫秒").pack(side=tk.LEFT, padx=(0, 10))

        # 日志操作按钮
        log_btn_frame = ttk.Frame(top_frame2)
        log_btn_frame.pack(side=tk.RIGHT)

        ttk.Button(log_btn_frame, text="清空日志",
                   command=self.clear_log_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_btn_frame, text="查看日志",
                   command=self.open_log_file).pack(side=tk.LEFT, padx=5)

        # 监控区域显示
        self.area_label = ttk.Label(self.root, text="监控区域: 未选择", font=('Arial', 10))
        self.area_label.pack(pady=5)

        # 高级设置面板
        settings_frame = ttk.LabelFrame(self.root, text="高灵敏:  低像素，低阈值，低降噪")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        # 像素变化阈值设置
        ttk.Label(settings_frame, text="像素阈值:").pack(side=tk.LEFT)
        self.pixel_threshold = tk.StringVar(value="25")
        self.pixel_spin = ttk.Spinbox(settings_frame, from_=1, to=50, increment=1,
                                      textvariable=self.pixel_threshold, width=4)
        self.pixel_spin.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(settings_frame, text="(1-50)").pack(side=tk.LEFT, padx=(0, 10))

        # 变化比例阈值设置
        ttk.Label(settings_frame, text="变化阈值:").pack(side=tk.LEFT, padx=(10, 0))
        self.change_threshold = tk.StringVar(value="3.0")
        self.change_spin = ttk.Spinbox(settings_frame, from_=0.1, to=10.0, increment=0.1,
                                       textvariable=self.change_threshold, width=4,
                                       format="%.1f")
        self.change_spin.pack(side=tk.LEFT)
        ttk.Label(settings_frame, text="%(0.1-10.0)").pack(side=tk.LEFT, padx=(0, 10))

        # 降噪强度设置
        ttk.Label(settings_frame, text="降噪:").pack(side=tk.LEFT, padx=(10, 0))
        self.denoise_level = ttk.Combobox(settings_frame, values=["低", "中", "高"], width=5)
        self.denoise_level.current(1)
        self.denoise_level.pack(side=tk.LEFT)

        # 状态监控面板
        self.status_frame = ttk.LabelFrame(self.root, text="监控日志")
        self.status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.status_text = tk.Text(self.status_frame, height=15, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)

    def clear_log_file(self):
        """清空日志文件"""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("时间\t\t\t变化比例\t监控区域\t间隔(ms)\n")
                f.write("=" * 60 + "\n")
            self.log("日志文件已清空")
        except Exception as e:
            self.log(f"清空日志失败: {str(e)}")

    def open_log_file(self):
        """打开文本日志文件"""
        try:
            os.startfile(self.log_file)  # Windows
        except:
            try:
                os.system(f"open {self.log_file}")  # MacOS
            except:
                os.system(f"xdg-open {self.log_file}")  # Linux

    def toggle_alarm(self):
        """切换声音报警状态"""
        self.alarm_enabled = not self.alarm_enabled
        self.log(f"声音报警已 {'启用' if self.alarm_enabled else '禁用'}")

    def play_alarm_sound(self):
        """播放单次报警声（不保存文件）"""
        if self.alarm_enabled:
            try:
                winsound.Beep(2500, 500)  # 频率2500Hz，持续500ms
            except Exception as e:
                self.log(f"播放报警音失败: {str(e)}")

    def start_area_selection(self):
        """启动全屏区域选择"""
        self.root.withdraw()  # 隐藏主窗口

        # 创建透明全屏选择窗口
        self.selection_window = tk.Toplevel()
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.attributes('-topmost', True)

        # 创建选择画布
        self.selection_canvas = tk.Canvas(self.selection_window, cursor="cross")
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定鼠标事件
        self.selection_canvas.bind("<Button-1>", self.on_selection_start)
        self.selection_canvas.bind("<B1-Motion>", self.on_selection_drag)
        self.selection_canvas.bind("<ButtonRelease-1>", self.on_selection_end)
        self.selection_canvas.bind("<Button-3>", lambda e: self.cancel_selection())

        # 显示操作提示
        screen_width = self.selection_window.winfo_screenwidth()
        screen_height = self.selection_window.winfo_screenheight()
        self.selection_canvas.create_text(
            screen_width // 2, screen_height // 2,
            text="拖动鼠标选择监控区域\n右键取消选择",
            fill="white", font=('Arial', 16), justify='center'
        )

    def on_selection_start(self, event):
        """开始选择区域"""
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.selection_canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2, dash=(5, 5))

    def on_selection_drag(self, event):
        """拖动选择区域"""
        if self.rect:
            self.selection_canvas.coords(
                self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_selection_end(self, event):
        """结束区域选择"""
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)

        min_size = 50  # 最小50x50像素
        if abs(x2 - x1) > min_size and abs(y2 - y1) > min_size:
            self.monitor_area = (x1, y1, x2, y2)
            self.area_label.config(
                text=f"监控区域: ({x1},{y1}) 到 ({x2},{y2}) | 尺寸: {x2 - x1}x{y2 - y1}")
            self.start_btn.config(state=tk.NORMAL)
            self.log(f"区域选择完成: {self.monitor_area}")
        else:
            self.log(f"选择区域过小 (需大于{min_size}x{min_size}像素)")

        self.selection_window.destroy()
        self.root.deiconify()  # 恢复主窗口

    def cancel_selection(self):
        """取消区域选择"""
        self.selection_window.destroy()
        self.root.deiconify()
        self.log("区域选择已取消")

    def start_monitoring(self):
        """开始监控"""
        if not self.monitor_area:
            messagebox.showerror("错误", "请先选择监控区域!")
            return

        try:
            self.interval_ms = int(self.interval_var.get())
            if not 100 <= self.interval_ms <= 10000:
                raise ValueError

            pixel_thresh = int(self.pixel_threshold.get())
            if not 1 <= pixel_thresh <= 50:
                raise ValueError

            change_thresh = float(self.change_threshold.get())
            if not 0.1 <= change_thresh <= 10.0:
                raise ValueError

        except:
            messagebox.showerror("错误", "参数设置无效!\n"
                                       "检测间隔: 100-10000毫秒\n"
                                       "像素阈值: 1-50\n"
                                       "变化阈值: 0.1-10.0%")
            return

        self.monitoring = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # 获取初始屏幕状态
        self.last_screen = self.capture_screen()
        self.log(f"监控已启动 (间隔: {self.interval_ms}ms, 像素阈值: {pixel_thresh}, 变化阈值: {change_thresh}%)...")
        self.write_log_entry(0.0)  # 记录启动事件

        # 开始监控循环
        self.monitor_screen()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("监控已停止")

    def capture_screen(self):
        """捕获屏幕并预处理（不保存文件）"""
        img = np.array(ImageGrab.grab(bbox=self.monitor_area))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 根据降噪级别应用高斯模糊
        denoise = self.denoise_level.get()
        ksize = 3 if denoise == "低" else 5 if denoise == "中" else 7
        return cv2.GaussianBlur(gray, (ksize, ksize), 0)

    def monitor_screen(self):
        """监控主逻辑（无截图保存功能）"""
        if not self.monitoring:
            return

        try:
            # 获取参数设置
            pixel_thresh = int(self.pixel_threshold.get())
            change_thresh = float(self.change_threshold.get()) / 100  # 转换为小数

            # 1. 获取当前屏幕
            current_screen = self.capture_screen()

            # 2. 如果是第一帧，只存储不检测
            if self.last_screen is None:
                self.last_screen = current_screen
                self.root.after(self.interval_ms, self.monitor_screen)
                return

            # 3. 计算差异
            diff = cv2.absdiff(current_screen, self.last_screen)
            _, threshold_diff = cv2.threshold(diff, pixel_thresh, 255, cv2.THRESH_BINARY)

            # 4. 降噪处理
            kernel_size = 3 if self.denoise_level.get() == "低" else 5
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            cleaned_diff = cv2.morphologyEx(threshold_diff, cv2.MORPH_OPEN, kernel)

            # 5. 计算变化比例
            changed_pixels = np.sum(cleaned_diff) / 255
            change_ratio = changed_pixels / (current_screen.size)

            # 6. 触发条件判断
            if change_ratio > change_thresh:
                self.log(f"&#128680; 检测到有效变化! 变化比例: {change_ratio:.2%} (阈值: {change_thresh:.2%})")
                self.play_alarm_sound()
                self.write_log_entry(change_ratio)

            # 7. 更新参考帧（带衰减）
            self.last_screen = cv2.addWeighted(current_screen, 0.3, self.last_screen, 0.7, 0)

            # 8. 继续监控循环
            self.root.after(self.interval_ms, self.monitor_screen)

        except Exception as e:
            self.log(f"监控错误: {str(e)}")
            self.stop_monitoring()

    def log(self, message):
        """记录状态信息"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)  # 自动滚动到底部
        self.status_text.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenMonitorApp(root)
    root.mainloop()