import pyautogui
import time
import math
import json
import os
import sys
from datetime import datetime
import threading
from threading import Event
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class MouseTrajectoryRecorder:
    def __init__(self):
        self.recording = False
        self.trajectory = deque(maxlen=500)  # 固定长度队列存储轨迹，自动管理内存
        self.mode = "办公模式"
        self.patterns = {}
        self.root = None
        self.log_text = None
        self.stop_event = Event()  # 线程退出信号
        self.last_action_time = 0  # 动作防抖计时
        self.action_cooldown = 1.0  # 动作冷却时间（秒），防止频繁触发

        # 启动前检查必要组件
        if not self.pre_check():
            sys.exit(1)

        # 加载配置模式
        self.patterns = self.load_patterns()

        # 创建图形界面
        self.create_gui()
        self.root.attributes('-topmost', True)  # 窗口置顶

        # 启动轨迹检测线程
        self.detection_thread = threading.Thread(target=self.detect_trajectories, daemon=True)
        self.detection_thread.start()

        self.log("程序已启动，点击'开始录制'开始识别鼠标轨迹")

    def pre_check(self):
        """启动前检查PyAutoGUI和Tkinter是否正常工作"""
        try:
            # 检查PyAutoGUI
            pyautogui.position()
        except Exception as e:
            print(f"PyAutoGUI初始化失败: {str(e)}")
            messagebox.showerror("初始化失败", f"鼠标控制模块无法正常工作: {str(e)}\n可能需要管理员权限或系统不支持")
            return False

        try:
            # 检查Tkinter
            test_root = tk.Tk()
            test_root.destroy()
        except Exception as e:
            print(f"Tkinter初始化失败: {str(e)}")
            messagebox.showerror("初始化失败", f"图形界面模块无法正常工作: {str(e)}")
            return False

        return True

    def load_patterns(self):
        """加载预定义轨迹模式（优先从文件加载，否则使用默认配置）"""
        default_patterns = {
            "办公模式": {
                "快速左移": {
                    "action": "page_up",
                    "min_distance": 300,
                    "max_time": 0.5,
                    "direction": "left",
                    "threshold": 0.7
                },
                "快速右移": {
                    "action": "page_down",
                    "min_distance": 300,
                    "max_time": 0.5,
                    "direction": "right",
                    "threshold": 0.7
                },
                "画圆": {
                    "action": "minimize",
                    "min_points": 30,
                    "circularity_threshold": 0.7,
                    "min_radius": 50
                },
                "画矩形": {
                    "action": "screenshot",
                    "min_points": 40,
                    "rectangularity_threshold": 0.6
                }
            },
            "游戏模式": {
                "右上斜线": {
                    "action": "up+right",
                    "min_distance": 200,
                    "max_time": 0.4,
                    "direction": "up-right",
                    "threshold": 0.6
                },
                "左下斜线": {
                    "action": "down+left",
                    "min_distance": 200,
                    "max_time": 0.4,
                    "direction": "down-left",
                    "threshold": 0.6
                },
                "快速上移": {
                    "action": "up",
                    "min_distance": 250,
                    "max_time": 0.4,
                    "direction": "up",
                    "threshold": 0.7
                },
                "快速下移": {
                    "action": "down",
                    "min_distance": 250,
                    "max_time": 0.4,
                    "direction": "down",
                    "threshold": 0.7
                }
            }
        }

        if os.path.exists("patterns.json"):
            try:
                with open("patterns.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"加载配置文件失败，使用默认配置: {str(e)}")

        return default_patterns

    def save_patterns(self):
        """保存轨迹模式配置到文件"""
        try:
            with open("patterns.json", "w", encoding="utf-8") as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.log(f"保存配置文件失败: {str(e)}")
            return False

    def calculate_distance(self, p1, p2):
        """计算两点间欧氏距离"""
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def calculate_direction(self, start, end):
        """计算上下左右方向"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

    def calculate_diagonal_direction(self, start, end):
        """计算对角线方向（如右上、左下）"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if dx > 0 and dy < 0:
            return "up-right"
        elif dx < 0 and dy < 0:
            return "up-left"
        elif dx > 0 and dy > 0:
            return "down-right"
        elif dx < 0 and dy > 0:
            return "down-left"
        return None

    def is_circular(self, points):
        """判断轨迹是否为圆形（优化版本：去除异常值影响）"""
        if len(points) < 30:
            return False

        # 计算中心点
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)

        # 计算半径并去除异常值（1.5倍四分位距法则）
        radii = [self.calculate_distance((x, y), (center_x, center_y)) for x, y, _ in points]
        radii_sorted = sorted(radii)
        q1 = radii_sorted[int(len(radii_sorted) * 0.25)]
        q3 = radii_sorted[int(len(radii_sorted) * 0.75)]
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        filtered_radii = [r for r in radii if lower_bound <= r <= upper_bound]

        if not filtered_radii:
            return False

        avg_radius = sum(filtered_radii) / len(filtered_radii)

        # 过滤过小的圆
        if avg_radius < self.patterns[self.mode]["画圆"]["min_radius"]:
            return False

        # 计算圆度（标准差/平均值越小，越接近圆）
        std_dev = math.sqrt(sum((r - avg_radius) ** 2 for r in filtered_radii) / len(filtered_radii))
        circularity = 1 - (std_dev / avg_radius)

        return circularity > self.patterns[self.mode]["画圆"]["circularity_threshold"]

    def is_rectangular(self, points):
        """判断轨迹是否为矩形"""
        if len(points) < 40:
            return False

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # 统计边缘点数量（距离边界20像素内）
        left_edge = sum(1 for x, _, _ in points if abs(x - min_x) < 20)
        right_edge = sum(1 for x, _, _ in points if abs(x - max_x) < 20)
        top_edge = sum(1 for _, y, _ in points if abs(y - min_y) < 20)
        bottom_edge = sum(1 for _, y, _ in points if abs(y - max_y) < 20)

        edge_points = left_edge + right_edge + top_edge + bottom_edge
        rectangularity = edge_points / len(points)  # 边缘点比例

        return rectangularity > self.patterns[self.mode]["画矩形"]["rectangularity_threshold"]

    def perform_action(self, action):
        """执行识别到的动作（添加防抖机制）"""
        current_time = time.time()
        # 冷却时间内忽略重复动作
        if current_time - self.last_action_time < self.action_cooldown:
            self.log(f"动作 {action} 触发过于频繁，已忽略")
            return

        self.last_action_time = current_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"识别到动作: {action}，时间: {timestamp}")

        try:
            if action == "page_up":
                pyautogui.press('pageup')
            elif action == "page_down":
                pyautogui.press('pagedown')
            elif action == "minimize":
                pyautogui.hotkey('win', 'down')  # 最小化当前窗口
            elif action == "screenshot":
                # 原子化创建截图目录（避免多线程竞争）
                os.makedirs("screenshots", exist_ok=True)
                pyautogui.screenshot(f"screenshots/screenshot_{timestamp.replace(':', '-')}.png")
            else:
                # 处理组合键（如up+right、ctrl+c等）
                keys = action.split("+")
                with pyautogui.hold(keys[:-1]):
                    pyautogui.press(keys[-1])
        except Exception as e:
            self.log(f"执行动作失败: {str(e)}")

    def detect_trajectories(self):
        """检测鼠标轨迹并识别模式（优化线程退出机制）"""
        while not self.stop_event.is_set():
            if not self.recording:
                # 非录制状态：用事件等待替代sleep，支持立即唤醒
                self.stop_event.wait(0.5)
                continue

            try:
                x, y = pyautogui.position()
                self.trajectory.append((x, y, time.time()))  # 记录坐标和时间
                self.check_patterns()  # 检查是否匹配模式
            except pyautogui.FailSafeException:
                # 处理鼠标移至角落的安全机制
                self.log("触发安全机制（鼠标移至角落），停止录制")
                self.recording = False
                self.trajectory.clear()
                # 线程安全更新按钮状态
                self.root.after(0, lambda: self.record_button.config(text="开始录制", style="TButton"))
            except Exception as e:
                self.log(f"轨迹检测出错: {str(e)}")
                time.sleep(1)  # 出错时暂停避免频繁报错

            # 录制状态短延迟，支持被事件唤醒
            if self.stop_event.wait(0.01):
                break

    def check_patterns(self):
        """检查当前轨迹是否匹配任何预设模式"""
        if len(self.trajectory) < 5:
            return

        start_point = self.trajectory[0]
        end_point = self.trajectory[-1]
        total_time = end_point[2] - start_point[2]
        total_distance = self.calculate_distance(
            (start_point[0], start_point[1]),
            (end_point[0], end_point[1])
        )

        for pattern_name, pattern in self.patterns[self.mode].items():
            try:
                # 检测方向移动模式（如快速左移、右上斜线）
                if "direction" in pattern and "min_distance" in pattern and "max_time" in pattern:
                    if (total_distance > pattern["min_distance"] and
                            total_time < pattern["max_time"]):

                        if pattern["direction"] in ["left", "right", "up", "down"]:
                            direction = self.calculate_direction(
                                (start_point[0], start_point[1]),
                                (end_point[0], end_point[1])
                            )
                        else:
                            direction = self.calculate_diagonal_direction(
                                (start_point[0], start_point[1]),
                                (end_point[0], end_point[1])
                            )

                        if direction == pattern["direction"]:
                            self.perform_action(pattern["action"])
                            self.trajectory.clear()
                            return

                # 检测圆形轨迹模式
                elif "circularity_threshold" in pattern:
                    if (len(self.trajectory) > pattern["min_points"] and
                            self.is_circular(self.trajectory)):
                        self.perform_action(pattern["action"])
                        self.trajectory.clear()
                        return

                # 检测矩形轨迹模式
                elif "rectangularity_threshold" in pattern:
                    if (len(self.trajectory) > pattern["min_points"] and
                            self.is_rectangular(self.trajectory)):
                        self.perform_action(pattern["action"])
                        self.trajectory.clear()
                        return
            except Exception as e:
                self.log(f"模式检查出错 ({pattern_name}): {str(e)}")

    def log(self, message):
        """线程安全的日志记录（确保GUI操作在主线程）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        print(f"[LOG] {full_message}")  # 同时输出到控制台

        if self.log_text is not None and self.root is not None:
            # 委托主线程更新日志界面
            def update_log():
                try:
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, full_message + "\n")
                    self.log_text.see(tk.END)  # 滚动到最新日志
                    self.log_text.config(state=tk.DISABLED)
                except Exception as e:
                    print(f"日志输出失败: {str(e)}")

            self.root.after(0, update_log)  # 0延迟确保主线程执行

    def toggle_recording(self):
        """切换录制状态（开始/停止识别轨迹）"""
        self.recording = not self.recording
        if self.recording:
            self.record_button.config(text="停止录制", style="Accent.TButton")
            self.log("开始录制鼠标轨迹...")
        else:
            self.record_button.config(text="开始录制", style="TButton")
            self.log("停止录制鼠标轨迹")
            self.trajectory.clear()  # 停止时清空轨迹

    def change_mode(self, event):
        """切换工作模式（办公/游戏）"""
        self.mode = self.mode_combobox.get()
        self.trajectory.clear()  # 切换模式时清空轨迹避免误判
        self.log(f"切换到 {self.mode}")
        self.update_pattern_list()

    def update_pattern_list(self):
        """更新模式列表（保留选中状态）"""
        # 保存当前选中项
        selected_indices = self.pattern_list.curselection()
        selected_name = None
        if selected_indices:
            selected_name = self.pattern_list.get(selected_indices[0])

        # 更新列表内容
        self.pattern_list.delete(0, tk.END)
        for i, pattern_name in enumerate(self.patterns[self.mode]):
            self.pattern_list.insert(tk.END, pattern_name)
            # 恢复选中状态
            if pattern_name == selected_name:
                self.pattern_list.selection_set(i)

    def delete_pattern(self):
        """删除选中的模式"""
        selected = self.pattern_list.curselection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个模式")
            return

        pattern_name = self.pattern_list.get(selected[0])
        if messagebox.askyesno("确认删除", f"确定要删除模式 '{pattern_name}' 吗？"):
            del self.patterns[self.mode][pattern_name]
            self.save_patterns()
            self.update_pattern_list()
            self.log(f"已删除模式: {pattern_name}")

    def configure_pattern(self):
        """配置选中的模式（带参数合法性校验）"""
        selected = self.pattern_list.curselection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个模式")
            return

        pattern_name = self.pattern_list.get(selected[0])
        pattern = self.patterns[self.mode][pattern_name]

        # 创建配置窗口
        config_window = tk.Toplevel(self.root)
        config_window.title(f"配置 {pattern_name}")
        config_window.geometry("450x350")
        config_window.transient(self.root)  # 依赖主窗口
        config_window.grab_set()  # 模态窗口

        tk.Label(config_window, text=f"当前动作: {pattern['action']}", font=("SimHei", 10)).pack(pady=5)

        tk.Label(config_window, text="绑定快捷键 (如: page_up 或 ctrl+c 或 up+right):", font=("SimHei", 10)).pack(anchor=tk.W,
                                                                                                          padx=10)
        action_var = tk.StringVar(value=pattern['action'])
        action_entry = tk.Entry(config_window, textvariable=action_var, width=40, font=("SimHei", 10))
        action_entry.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(config_window, text="示例: page_up, page_down, enter, ctrl+s, up, down, left, right",
                 fg="gray", font=("SimHei", 8)).pack(anchor=tk.W, padx=10)

        frame = ttk.Frame(config_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 存储参数与输入框的映射（确保参数对应正确）
        param_entries = {}
        row = 0

        for key, value in pattern.items():
            if key == "action":
                continue

            tk.Label(frame, text=f"{key}:", font=("SimHei", 10)).grid(row=row, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar(value=str(value))
            entry = tk.Entry(frame, textvariable=var)
            entry.grid(row=row, column=1, sticky=tk.EW, pady=2)
            param_entries[key] = entry
            frame.grid_columnconfigure(1, weight=1)  # 输入框自适应宽度
            row += 1

        def save_config():
            """保存配置并校验参数合法性"""
            pattern['action'] = action_var.get()

            # 关键参数合法性校验规则（参数名: (校验函数, 错误提示)）
            validators = {
                "min_distance": (lambda x: x > 0, "必须大于0"),
                "max_time": (lambda x: x > 0, "必须大于0"),
                "threshold": (lambda x: 0 < x < 1, "必须在0-1之间"),
                "min_points": (lambda x: x > 5, "必须大于5"),
                "circularity_threshold": (lambda x: 0 < x < 1, "必须在0-1之间"),
                "min_radius": (lambda x: x > 10, "必须大于10"),
                "rectangularity_threshold": (lambda x: 0 < x < 1, "必须在0-1之间")
            }

            for key, entry in param_entries.items():
                try:
                    value = float(entry.get())
                    if value.is_integer():
                        value = int(value)  # 整数参数转为int类型

                    # 校验参数合法性
                    if key in validators:
                        validator, msg = validators[key]
                        if not validator(value):
                            messagebox.showerror("参数错误", f"{key} {msg}")
                            return

                    pattern[key] = value
                except ValueError:
                    # 非数字参数直接保留字符串
                    pattern[key] = entry.get()

            if self.save_patterns():
                messagebox.showinfo("成功", "模式配置已更新")
                config_window.destroy()

        ttk.Button(config_window, text="保存", command=save_config).pack(pady=10)
        config_window.wait_window()  # 等待窗口关闭

    def add_new_pattern(self):
        """添加新模式"""
        pattern_name = simpledialog.askstring("新模式", "请输入新模式名称:", parent=self.root)
        if not pattern_name:
            return

        if pattern_name in self.patterns[self.mode]:
            messagebox.showwarning("警告", "该模式名称已存在")
            return

        pattern_type = simpledialog.askstring(
            "模式类型",
            "请选择模式类型:\n1. 方向移动 (如快速左移)\n2. 圆形轨迹\n3. 矩形轨迹",
            parent=self.root
        )

        if not pattern_type or pattern_type not in ["1", "2", "3"]:
            messagebox.showwarning("警告", "请选择有效的模式类型 (1, 2 或 3)")
            return

        # 根据类型初始化模式参数
        if pattern_type == "1":
            self.patterns[self.mode][pattern_name] = {
                "action": "none",
                "min_distance": 200,
                "max_time": 0.5,
                "direction": "right",
                "threshold": 0.7
            }
        elif pattern_type == "2":
            self.patterns[self.mode][pattern_name] = {
                "action": "none",
                "min_points": 30,
                "circularity_threshold": 0.7,
                "min_radius": 50
            }
        else:
            self.patterns[self.mode][pattern_name] = {
                "action": "none",
                "min_points": 40,
                "rectangularity_threshold": 0.6
            }

        if self.save_patterns():
            self.update_pattern_list()
            self.log(f"已添加新模式: {pattern_name}")
            # 自动选中新添加的模式并打开配置窗口
            self.pattern_list.selection_set(self.pattern_list.size() - 1)
            self.configure_pattern()

    def create_gui(self):
        """创建图形用户界面"""
        self.root = tk.Tk()
        self.root.title("鼠标轨迹检测软件")
        self.root.geometry("800x600")

        # 确保中文正常显示
        self.root.option_add("*Font", "SimHei 10")

        # 自定义按钮样式
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="red")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 模式选择区域
        mode_frame = ttk.LabelFrame(main_frame, text="模式选择", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mode_frame, text="当前模式:").pack(side=tk.LEFT, padx=(0, 10))
        self.mode_combobox = ttk.Combobox(mode_frame, values=["办公模式", "游戏模式"], state="readonly", width=10)
        self.mode_combobox.current(0)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.change_mode)
        self.mode_combobox.pack(side=tk.LEFT, padx=(0, 20))

        self.record_button = ttk.Button(mode_frame, text="开始录制", command=self.toggle_recording)
        self.record_button.pack(side=tk.RIGHT)

        # 模式配置区域
        config_frame = ttk.LabelFrame(main_frame, text="模式配置", padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        left_frame = ttk.Frame(config_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="可用模式:").pack(anchor=tk.W)
        self.pattern_list = tk.Listbox(left_frame, font=("SimHei", 10))
        self.pattern_list.pack(fill=tk.BOTH, expand=True, pady=5)
        self.pattern_list.bind("<Double-1>", lambda e: self.configure_pattern())  # 双击配置模式
        self.update_pattern_list()

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="配置模式", command=self.configure_pattern).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="添加模式", command=self.add_new_pattern).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除模式", command=self.delete_pattern).pack(side=tk.RIGHT, padx=5)

        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, state=tk.DISABLED, wrap=tk.WORD, font=("SimHei", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 日志滚动条
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # 底部提示信息
        ttk.Label(main_frame, text="提示: 1. 点击'开始录制'后程序开始识别鼠标轨迹 2. 鼠标移动到屏幕角落可终止程序",
                  foreground="blue").pack(anchor=tk.W, pady=5)

        # 窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """优雅关闭程序（终止线程并销毁窗口）"""
        self.stop_event.set()  # 通知检测线程退出
        self.root.destroy()


if __name__ == "__main__":
    app = MouseTrajectoryRecorder()
    app.root.mainloop()