import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
from flask import Flask, Response, request
import mss
import mss.tools
import os
import sys
import time
import subprocess
from PIL import Image
import io
import queue
import json
import ctypes
import numpy as np
import cv2  # 添加OpenCV用于高效图像处理


class ScreenMirrorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("低延迟屏幕投屏工具")
        self.root.geometry("550x550")
        self.root.resizable(False, False)

        # 设置应用图标
        self.set_icon()

        # 获取本机IP地址
        self.ip_address = self.get_ip_address()

        # 创建UI
        self.create_widgets()

        # 获取显示器信息
        self.monitors = self.get_monitors()

        # 初始化投屏状态
        self.mirroring = False
        self.server_thread = None
        self.flask_app = None
        self.last_frame = None
        self.frame_queue = queue.Queue(maxsize=1)
        self.capture_thread = None
        self.stop_capture = threading.Event()

        # 自动添加防火墙规则
        self.add_firewall_rule()

        # 性能参数默认值
        self.quality = 70
        self.frame_rate = 30
        self.resolution = 0.7

        # 性能计数器
        self.frame_count = 0
        self.start_time = time.time()

        # 客户端连接状态
        self.active_clients = set()

        # 黑屏图像
        self.black_image = self.create_black_image()

        # 加载上次选择的设置
        self.load_config()

    def create_black_image(self):
        """创建黑屏图像"""
        img = Image.new('RGB', (100, 100), (0, 0, 0))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=1)
        return img_byte_arr.getvalue()

    def set_icon(self):
        """设置应用图标"""
        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                icon_path = 'icon.ico'
            self.root.iconbitmap(icon_path)
        except:
            pass

    def get_ip_address(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except:
            return "127.0.0.1"

    def get_monitors(self):
        """获取所有显示器信息"""
        with mss.mss() as sct:
            return sct.monitors

    def load_config(self):
        """加载上次的设置"""
        config_path = os.path.join(os.path.expanduser("~"), ".screen_mirror_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)

                    # 加载屏幕设置
                    last_screen = config.get("last_screen", 1)
                    if 1 <= last_screen <= len(self.monitors):
                        self.screen_var.set(last_screen)

                    # 加载性能设置
                    quality = config.get("quality", 70)
                    if 30 <= quality <= 95:
                        self.quality_var.set(quality)

                    frame_rate = config.get("frame_rate", 30)
                    if 5 <= frame_rate <= 60:
                        self.fps_var.set(frame_rate)

                    resolution = config.get("resolution", 0.7)
                    if 0.3 <= resolution <= 1.0:
                        self.res_var.set(resolution)

                    self.status_var.set("已加载上次的设置")
        except Exception as e:
            self.status_var.set(f"加载配置失败: {str(e)}")

    def save_config(self):
        """保存当前设置到配置文件"""
        config_path = os.path.join(os.path.expanduser("~"), ".screen_mirror_config.json")
        try:
            config = {
                "last_screen": self.screen_var.get(),
                "quality": self.quality_var.get(),
                "frame_rate": self.fps_var.get(),
                "resolution": self.res_var.get()
            }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w") as f:
                json.dump(config, f)
        except Exception as e:
            self.status_var.set(f"保存配置失败: {str(e)}")

    def create_widgets(self):
        """创建UI界面"""
        # 标题
        title_label = ttk.Label(self.root, text="低延迟屏幕投屏工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 屏幕选择
        screen_frame = ttk.LabelFrame(self.root, text="选择投屏屏幕")
        screen_frame.pack(pady=5, padx=20, fill="x")

        self.screen_var = tk.IntVar(value=1)
        screens = ["主屏幕", "屏幕2", "屏幕3", "屏幕4"]

        for i, screen in enumerate(screens):
            rb = ttk.Radiobutton(
                screen_frame,
                text=screen,
                variable=self.screen_var,
                value=i + 1,
                command=self.save_config
            )
            rb.grid(row=0, column=i, padx=10, pady=5)

        # 性能设置
        perf_frame = ttk.LabelFrame(self.root, text="性能设置")
        perf_frame.pack(pady=5, padx=20, fill="x")

        # 图像质量
        quality_frame = ttk.Frame(perf_frame)
        quality_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(quality_frame, text="图像质量:").pack(side="left")
        self.quality_var = tk.IntVar(value=70)
        quality_scale = ttk.Scale(
            quality_frame,
            from_=30,
            to=95,
            variable=self.quality_var,
            orient="horizontal",
            length=200,
            command=lambda _: self.save_config()
        )
        quality_scale.pack(side="left", padx=10)
        ttk.Label(quality_frame, textvariable=self.quality_var).pack(side="left")

        # 帧率
        fps_frame = ttk.Frame(perf_frame)
        fps_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(fps_frame, text="帧率:").pack(side="left")
        self.fps_var = tk.IntVar(value=30)
        fps_scale = ttk.Scale(
            fps_frame,
            from_=5,
            to=60,
            variable=self.fps_var,
            orient="horizontal",
            length=200,
            command=lambda _: self.save_config()
        )
        fps_scale.pack(side="left", padx=10)
        ttk.Label(fps_frame, textvariable=self.fps_var).pack(side="left")

        # 分辨率
        res_frame = ttk.Frame(perf_frame)
        res_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(res_frame, text="分辨率:").pack(side="left")
        self.res_var = tk.DoubleVar(value=0.7)
        res_scale = ttk.Scale(
            res_frame,
            from_=0.3,
            to=1.0,
            variable=self.res_var,
            orient="horizontal",
            length=200,
            command=lambda _: self.save_config()
        )
        res_scale.pack(side="left", padx=10)
        ttk.Label(res_frame, textvariable=self.res_var).pack(side="left")

        # 控制按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="启动投屏",
            command=self.start_mirroring,
            width=15
        )
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(
            button_frame,
            text="停止投屏",
            command=self.stop_mirroring,
            state="disabled",
            width=15
        )
        self.stop_button.grid(row=0, column=1, padx=10)

        # 链接显示
        link_frame = ttk.LabelFrame(self.root, text="投屏链接")
        link_frame.pack(pady=5, padx=20, fill="x")

        self.link_var = tk.StringVar(value="请先启动投屏")
        link_label = ttk.Label(
            link_frame,
            textvariable=self.link_var,
            font=("Arial", 10),
            anchor="center"
        )
        link_label.pack(pady=5, padx=10)

        # 复制链接按钮
        copy_button = ttk.Button(
            link_frame,
            text="复制链接",
            command=self.copy_link,
            width=10
        )
        copy_button.pack(pady=5)

        # 性能信息
        perf_info_frame = ttk.LabelFrame(self.root, text="性能信息")
        perf_info_frame.pack(pady=5, padx=20, fill="x")

        self.fps_info_var = tk.StringVar(value="FPS: --")
        self.latency_var = tk.StringVar(value="延迟: --")
        self.size_var = tk.StringVar(value="帧大小: --")

        ttk.Label(perf_info_frame, textvariable=self.fps_info_var).pack(anchor="w", padx=10, pady=2)
        ttk.Label(perf_info_frame, textvariable=self.latency_var).pack(anchor="w", padx=10, pady=2)
        ttk.Label(perf_info_frame, textvariable=self.size_var).pack(anchor="w", padx=10, pady=2)

        # 联系信息
        contact_frame = ttk.Frame(self.root)
        contact_frame.pack(pady=5, padx=20, fill="x")

        contact_label = ttk.Label(
            contact_frame,
            text="来自吾爱破解原创 52pojie.cn 如有问题请联系开发者VX: SoullesFox",
            font=("Arial", 10, "bold"),
            foreground="red",
            anchor="center"
        )
        contact_label.pack(fill="x")

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )
        status_bar.pack(side="bottom", fill="x")

    def add_firewall_rule(self):
        """添加防火墙规则允许端口5000"""
        try:
            command = f'netsh advfirewall firewall show rule name="ScreenMirrorPort5000"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)

            if "没有规则" in result.stdout:
                command = (
                    'netsh advfirewall firewall add rule name="ScreenMirrorPort5000" '
                    'dir=in action=allow protocol=TCP localport=5000'
                )
                subprocess.run(command, shell=True)
                self.status_var.set("已添加防火墙规则")
        except Exception as e:
            self.status_var.set(f"防火墙设置失败: {str(e)}")

    def copy_link(self):
        """复制链接到剪贴板"""
        if self.link_var.get() != "请先启动投屏":
            self.root.clipboard_clear()
            self.root.clipboard_append(self.link_var.get())
            self.status_var.set("链接已复制到剪贴板")

    def start_mirroring(self):
        """启动投屏服务"""
        if self.mirroring:
            return

        self.mirroring = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="enabled")
        self.status_var.set("loading...")

        # 获取当前设置
        self.quality = self.quality_var.get()
        self.frame_rate = self.fps_var.get()
        self.resolution = self.res_var.get()

        # 重置性能计数器
        self.frame_count = 0
        self.start_time = time.time()

        # 创建Flask应用
        self.flask_app = Flask(__name__)

        # 添加路由
        @self.flask_app.route('/')
        def index():
            return """
            <html>
                <head>
                    <title></title>
                    <meta charset="UTF-8">
                    <style>
                        body {
                            text-align: center;
                            background-color: #000;
                            margin: 0;
                            padding: 0;
                            overflow: hidden;
                        }
                        h1 {
                            color: #333;
                            margin-top: 10px;
                        }
                        img {
                            max-width: 100%;
                            max-height: 90vh;
                            box-shadow: 0 0 10px rgba(0,0,0,0.3);
                            cursor: pointer;
                        }
                        .status {
                            margin: 10px;
                            padding: 8px;
                            background-color: #e0e0e0;
                            border-radius: 5px;
                        }
                        .stats {
                            margin: 5px;
                            padding: 5px;
                            background-color: #d0d0d0;
                            border-radius: 5px;
                            display: inline-block;
                        }
                        .controls {
                            position: fixed;
                            top: 10px;
                            right: 10px;
                            background: rgba(255, 255, 255, 0.7);
                            padding: 5px;
                            border-radius: 5px;
                        }
                        .fullscreen-btn {
                            background: #4CAF50;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 3px;
                            cursor: pointer;
                        }
                        .fullscreen-btn:hover {
                            background: #45a049;
                        }
                    </style>
                    <script>
                        let lastFrameTime = 0;
                        let frameTimes = [];
                        let fps = 0;
                        let latency = 0;
                        let isFullscreen = false;
                        let connectionId = Date.now(); // 唯一连接ID

                        function updateImage() {
                            const img = document.getElementById('screenImg');
                            const status = document.getElementById('status');
                            const fpsDisplay = document.getElementById('fps');
                            const latencyDisplay = document.getElementById('latency');

                            // 添加时间戳防止缓存
                            const startTime = performance.now();
                            img.src = '/screen?cid=' + connectionId + '&t=' + new Date().getTime();

                            img.onload = function() {
                                const endTime = performance.now();
                                latency = endTime - startTime;

                                // 计算FPS
                                const now = performance.now();
                                if (lastFrameTime > 0) {
                                    const delta = now - lastFrameTime;
                                    frameTimes.push(delta);
                                    if (frameTimes.length > 10) frameTimes.shift();

                                    const avgDelta = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
                                    fps = Math.round(1000 / avgDelta);
                                }
                                lastFrameTime = now;

                                // 更新显示
                                status.textContent = '投屏中...';
                                fpsDisplay.textContent = `FPS: ${fps}`;
                                latencyDisplay.textContent = `延迟: ${Math.round(latency)}ms`;

                                setTimeout(updateImage, 10);
                            };

                            img.onerror = function() {
                                status.textContent = '连接失败，正在重试...';
                                setTimeout(updateImage, 1000);
                            };
                        }

                        function toggleFullscreen() {
                            const img = document.getElementById('screenImg');

                            if (!isFullscreen) {
                                if (img.requestFullscreen) {
                                    img.requestFullscreen();
                                } else if (img.mozRequestFullScreen) {
                                    img.mozRequestFullScreen();
                                } else if (img.webkitRequestFullscreen) {
                                    img.webkitRequestFullscreen();
                                } else if (img.msRequestFullscreen) {
                                    img.msRequestFullscreen();
                                }
                                isFullscreen = true;
                                document.getElementById('fullscreenBtn').textContent = '退出全屏';
                            } else {
                                if (document.exitFullscreen) {
                                    document.exitFullscreen();
                                } else if (document.mozCancelFullScreen) {
                                    document.mozCancelFullScreen();
                                } else if (document.webkitExitFullscreen) {
                                    document.webkitExitFullscreen();
                                } else if (document.msExitFullscreen) {
                                    document.msExitFullscreen();
                                }
                                isFullscreen = false;
                                document.getElementById('fullscreenBtn').textContent = '全屏显示';
                            }
                        }

                        // 监听全屏状态变化
                        document.addEventListener('fullscreenchange', handleFullscreenChange);
                        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
                        document.addEventListener('mozfullscreenchange', handleFullscreenChange);
                        document.addEventListener('MSFullscreenChange', handleFullscreenChange);

                        function handleFullscreenChange() {
                            isFullscreen = !!(document.fullscreenElement ||
                                            document.webkitFullscreenElement ||
                                            document.mozFullScreenElement ||
                                            document.msFullscreenElement);
                            document.getElementById('fullscreenBtn').textContent = isFullscreen ? '退出全屏' : '全屏显示';
                        }

                        // 双击图像切换全屏
                        function setupDoubleClick() {
                            const img = document.getElementById('screenImg');
                            img.addEventListener('dblclick', toggleFullscreen);
                        }

                        window.onload = function() {
                            updateImage();
                            setupDoubleClick();
                        };
                    </script>
                </head>
                <body>
                    <div class="controls">
                        <button id="fullscreenBtn" class="fullscreen-btn">全屏显示</button>
                    </div>
                    <div id="status" class="status">正在连接...</div>
                    <div class="stats">
                        <span id="fps">FPS: --</span> |
                        <span id="latency">延迟: --</span>
                    </div>
                    <img id="screenImg" />
                </body>
            </html>
            """

        @self.flask_app.route('/screen')
        def screen():
            # 获取客户端唯一ID
            client_id = request.args.get('cid', '')

            # 生成实时帧
            return Response(
                self.generate_frames(client_id),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

        # 启动屏幕捕获线程
        self.start_capture_thread()

        # 在后台线程中运行Flask服务器
        self.server_thread = threading.Thread(
            target=self.run_server,
            daemon=True
        )
        self.server_thread.start()

        # 更新链接显示
        port = 5000
        self.link_var.set(f"http://{self.ip_address}:{port}")
        self.status_var.set(f"投屏已启动 - 正在监听端口 {port}")

        # 启动性能监控
        self.root.after(1000, self.update_performance)

    def start_capture_thread(self):
        """启动屏幕捕获线程"""
        if self.capture_thread and self.capture_thread.is_alive():
            self.stop_capture.set()
            self.capture_thread.join(timeout=1.0)

        # 清空队列
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

        # 重置停止标志
        self.stop_capture.clear()

        # 创建新线程
        self.capture_thread = threading.Thread(
            target=self.capture_screen,
            args=(self.screen_var.get(), self.quality, self.frame_rate, self.resolution),
            daemon=True
        )
        self.capture_thread.start()

    def capture_screen(self, monitor_idx, quality, frame_rate, resolution):
        """屏幕捕获线程 - 使用OpenCV优化版本"""
        try:
            # 获取显示器信息
            monitor = self.monitors[monitor_idx]

            # 计算目标尺寸
            width = int(monitor['width'] * resolution)
            height = int(monitor['height'] * resolution)

            # 计算帧间隔
            frame_interval = 1.0 / frame_rate

            # 初始化性能计数器
            last_time = time.time()
            frame_counter = 0

            # 使用OpenCV进行高效捕获
            with mss.mss() as sct:
                while not self.stop_capture.is_set():
                    start_time = time.time()

                    try:
                        # 捕获屏幕
                        screenshot = sct.grab(monitor)

                        # 转换为numpy数组
                        img = np.array(screenshot)

                        # 调整分辨率
                        if resolution < 1.0:
                            # 使用OpenCV进行快速缩放
                            img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

                        # 转换为JPEG - 使用OpenCV高效编码
                        _, jpeg_data = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

                        # 放入队列（如果队列已满则替换）
                        try:
                            self.frame_queue.put(jpeg_data.tobytes(), block=False)
                        except queue.Full:
                            try:
                                self.frame_queue.get_nowait()
                            except queue.Empty:
                                pass
                            self.frame_queue.put(jpeg_data.tobytes(), block=False)

                        # 控制帧率 - 使用更精确的方法
                        elapsed = time.time() - start_time
                        sleep_time = max(0, frame_interval - elapsed)

                        # 如果处理时间超过帧间隔，跳过下一帧
                        if sleep_time > 0:
                            time.sleep(sleep_time)

                        # 性能计数
                        frame_counter += 1
                        current_time = time.time()
                        if current_time - last_time >= 1.0:
                            actual_fps = frame_counter / (current_time - last_time)
                            self.status_var.set(f"捕获中: {actual_fps:.1f} FPS")
                            last_time = current_time
                            frame_counter = 0

                    except Exception as e:
                        self.status_var.set(f"捕获错误: {str(e)}")
                        time.sleep(0.1)
        except Exception as e:
            self.status_var.set(f"捕获初始化错误: {str(e)}")

    def update_performance(self):
        """更新性能信息"""
        if self.mirroring:
            # 计算FPS
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            self.fps_info_var.set(f"FPS: {fps:.1f}")

            # 重置计数器
            self.frame_count = 0
            self.start_time = time.time()

            # 定期检查
            self.root.after(1000, self.update_performance)

    def stop_mirroring(self):
        """停止投屏服务"""
        if not self.mirroring:
            return

        self.mirroring = False
        self.start_button.config(state="enabled")
        self.stop_button.config(state="disabled")
        self.status_var.set("投屏已停止")

        # 停止捕获线程
        self.stop_capture.set()
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)

    def generate_frames(self, client_id):
        """生成屏幕帧（JPEG格式）"""
        while self.mirroring:
            try:
                # 从队列获取帧数据
                jpeg_data = self.frame_queue.get(timeout=0.1)  # 缩短超时时间

                # 保存最后一帧
                self.last_frame = jpeg_data

                # 更新帧计数
                self.frame_count += 1

                # 更新帧大小信息
                self.size_var.set(f"帧大小: {len(jpeg_data) / 1024:.1f} KB")

                # 生成帧
                yield (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n'
                )
            except queue.Empty:
                # 队列为空，等待下一帧
                time.sleep(0.01)
            except Exception as e:
                self.status_var.set(f"传输错误: {str(e)}")
                time.sleep(0.1)

        # 投屏停止后发送黑屏图像
        while True:
            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + self.black_image + b'\r\n'
            )
            time.sleep(0.1)

    def run_server(self):
        """运行Flask服务器"""
        try:
            self.flask_app.run(
                host='0.0.0.0',
                port=5000,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            self.status_var.set(f"服务器错误: {str(e)}")
            self.mirroring = False
            self.start_button.config(state="enabled")
            self.stop_button.config(state="disabled")


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    # 检查是否以管理员权限运行
    if os.name == 'nt' and not is_admin():
        # 重新以管理员权限运行
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

    root = tk.Tk()
    app = ScreenMirrorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_mirroring(), root.destroy()))
    root.mainloop()