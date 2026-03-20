import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import ctypes
import random
import os
import time
import threading
import queue
import sys
import smtplib
from email.mime.text import MIMEText
from collections import deque
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# DPI 适配
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

DEFAULT_CONFIG = {
    "refresh_interval": 2,
    "opacity": 0.55,
    "au_upper_enabled": False,
    "au_upper_value": 0.0,
    "au_lower_enabled": True,
    "au_lower_value": 1130.0,
    "intl_upper_enabled": False,
    "intl_upper_value": 0.0,
    "intl_lower_enabled": False,
    "intl_lower_value": 0.0,
    "extreme_window_min": 4,
    "extreme_threshold": 5.0,
    "intl_extreme_window_min": 4,
    "intl_extreme_threshold": 30,
    "extreme_enabled": True,
    "extreme_flash_times": 6,
    "extreme_flash_interval_ms": 150,
    "extreme_cooldown_sec": 60,
    # 提醒冷却（防阈值附近反复触发），单位：秒
    "alert_cooldown_sec": 10,
    # 邮件配置
    "email_enabled": False,
    "email_sender": "",
    "email_password": "",
    "email_receiver": "",
    # 默认汇率（当 API 失败时使用）
    "default_exchange_rate": 7.28,
}


def _config_path():
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_dir, "config.json")


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("设置")
        self.geometry("380x520")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=12, pady=12, expand=True, fill="both")

        self.tab_general = ttk.Frame(self.notebook)
        self.tab_alerts  = ttk.Frame(self.notebook)
        self.tab_extreme = ttk.Frame(self.notebook)
        self.tab_email   = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_general, text="通用")
        self.notebook.add(self.tab_alerts,  text="提醒")
        self.notebook.add(self.tab_extreme, text="异动")
        self.notebook.add(self.tab_email,   text="邮件")

        self._build_general()
        self._build_alerts()
        self._build_extreme()
        self._build_email()

        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(footer, text="保存并应用", command=self._save).pack(side="right")
        ttk.Button(footer, text="取消", command=self._on_close).pack(side="right", padx=(0, 8))

        self.after(50, self.focus_force)

    def _build_general(self):
        frame = ttk.Frame(self.tab_general)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(frame, text="刷新间隔（秒）").grid(row=0, column=0, sticky="w")
        self.var_interval = tk.StringVar(value=str(self.app.interval))
        ttk.Entry(frame, textvariable=self.var_interval, width=12).grid(row=0, column=1, sticky="w", padx=(10, 0))

        ttk.Label(frame, text="透明度（0.2~1.0）").grid(row=1, column=0, sticky="w", pady=(12, 0))
        self.var_opacity = tk.DoubleVar(value=float(self.app.root.attributes("-alpha")))
        ttk.Scale(frame, variable=self.var_opacity, from_=0.2, to=1.0, orient="horizontal",
                  command=self._on_opacity_change).grid(row=1, column=1, sticky="we", padx=(10, 0), pady=(12, 0))
        self.opacity_value_label = ttk.Label(frame, text=f"{self.var_opacity.get():.2f}")
        self.opacity_value_label.grid(row=1, column=2, sticky="e", padx=(8, 0), pady=(12, 0))

        frame.columnconfigure(1, weight=1)

    def _build_alerts(self):
        frame = ttk.Frame(self.tab_alerts)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.var_au_upper_enabled   = tk.BooleanVar(value=self.app.au_upper_target is not None)
        self.var_au_upper_value     = tk.StringVar(value=str(self.app.au_upper_target or 0.0))
        self.var_au_lower_enabled   = tk.BooleanVar(value=self.app.au_lower_target is not None)
        self.var_au_lower_value     = tk.StringVar(value=str(self.app.au_lower_target or 0.0))
        self.var_intl_upper_enabled = tk.BooleanVar(value=self.app.intl_upper_target is not None)
        self.var_intl_upper_value   = tk.StringVar(value=str(self.app.intl_upper_target or 0.0))
        self.var_intl_lower_enabled = tk.BooleanVar(value=self.app.intl_lower_target is not None)
        self.var_intl_lower_value   = tk.StringVar(value=str(self.app.intl_lower_target or 0.0))

        ttk.Label(frame, text="沪金 上破提醒").grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(frame, variable=self.var_au_upper_enabled).grid(row=0, column=1, sticky="w")
        ttk.Entry(frame, textvariable=self.var_au_upper_value, width=12).grid(row=0, column=2, sticky="e")

        ttk.Label(frame, text="沪金 下破提醒").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Checkbutton(frame, variable=self.var_au_lower_enabled).grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.var_au_lower_value, width=12).grid(row=1, column=2, sticky="e", pady=(10, 0))

        ttk.Separator(frame).grid(row=2, column=0, columnspan=3, sticky="we", pady=16)

        ttk.Label(frame, text="国际 上破提醒").grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(frame, variable=self.var_intl_upper_enabled).grid(row=3, column=1, sticky="w")
        ttk.Entry(frame, textvariable=self.var_intl_upper_value, width=12).grid(row=3, column=2, sticky="e")

        ttk.Label(frame, text="国际 下破提醒").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Checkbutton(frame, variable=self.var_intl_lower_enabled).grid(row=4, column=1, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.var_intl_lower_value, width=12).grid(row=4, column=2, sticky="e", pady=(10, 0))


        frame.columnconfigure(1, weight=1)

    def _build_extreme(self):
        frame = ttk.Frame(self.tab_extreme)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.var_extreme_enabled = tk.BooleanVar(value=self.app.extreme_enabled)
        ttk.Checkbutton(frame, text="启用异动提醒", variable=self.var_extreme_enabled).grid(
            row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(frame, text="沪金 统计窗口（分钟）").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.var_window_min = tk.StringVar(value=str(int(self.app.extreme_window_sec / 60)))
        ttk.Entry(frame, textvariable=self.var_window_min, width=12).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(frame, text="沪金 异动阈值").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.var_extreme_threshold = tk.StringVar(value=str(self.app.extreme_threshold))
        ttk.Entry(frame, textvariable=self.var_extreme_threshold, width=12).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(frame, text="国际 统计窗口（分钟）").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.var_intl_window_min = tk.StringVar(value=str(int(self.app.intl_extreme_window_sec / 60)))
        ttk.Entry(frame, textvariable=self.var_intl_window_min, width=12).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(frame, text="国际 异动阈值").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.var_intl_extreme_threshold = tk.StringVar(value=str(self.app.intl_extreme_threshold))
        ttk.Entry(frame, textvariable=self.var_intl_extreme_threshold, width=12).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Separator(frame).grid(row=5, column=0, columnspan=2, sticky="we", pady=16)

        ttk.Label(frame, text="闪烁次数").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.var_flash_times = tk.StringVar(value=str(self.app.extreme_flash_times))
        ttk.Entry(frame, textvariable=self.var_flash_times, width=12).grid(row=6, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(frame, text="闪烁间隔（毫秒）").grid(row=7, column=0, sticky="w", pady=(10, 0))
        self.var_flash_interval = tk.StringVar(value=str(self.app.extreme_flash_interval_ms))
        ttk.Entry(frame, textvariable=self.var_flash_interval, width=12).grid(row=7, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(frame, text="冷却时间（秒）").grid(row=8, column=0, sticky="w", pady=(10, 0))
        self.var_cooldown = tk.StringVar(value=str(self.app.extreme_cooldown_sec))
        ttk.Entry(frame, textvariable=self.var_cooldown, width=12).grid(row=8, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

    def _build_email(self):
        frame = ttk.Frame(self.tab_email)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.var_email_enabled = tk.BooleanVar(value=self.app.email_enabled)
        ttk.Checkbutton(
            frame,
            text="启用邮件提醒",
            variable=self.var_email_enabled,
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(frame, text="发件人地址").grid(row=1, column=0, sticky="w", pady=(12, 0))
        self.var_email_sender = tk.StringVar(value=self.app.email_sender)
        ttk.Entry(frame, textvariable=self.var_email_sender, width=26).grid(
            row=1, column=1, sticky="we", padx=(10, 0), pady=(12, 0))

        ttk.Label(frame, text="授权码").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.var_email_password = tk.StringVar(value=self.app.email_password)
        ttk.Entry(frame, textvariable=self.var_email_password, width=26, show="*").grid(
            row=2, column=1, sticky="we", padx=(10, 0), pady=(10, 0))

        ttk.Label(frame, text="收件人地址").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.var_email_receiver = tk.StringVar(value=self.app.email_receiver)
        ttk.Entry(frame, textvariable=self.var_email_receiver, width=26).grid(
            row=3, column=1, sticky="we", padx=(10, 0), pady=(10, 0))

        ttk.Separator(frame).grid(row=4, column=0, columnspan=2, sticky="we", pady=14)

        ttk.Label(frame, text="SMTP 服务器").grid(row=5, column=0, sticky="w")
        ttk.Label(frame, text="smtp.163.com  端口 465  SSL", foreground="#9AA0A6").grid(
            row=5, column=1, sticky="w", padx=(10, 0))

        ttk.Button(frame, text="发送测试邮件", command=self._test_email).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(14, 0))

        frame.columnconfigure(1, weight=1)

    def _test_email(self):
        sender   = self.var_email_sender.get().strip()
        password = self.var_email_password.get().strip()
        receiver = self.var_email_receiver.get().strip()
        if not all([sender, password, receiver]):
            messagebox.showerror("错误", "请先填写发件人、授权码和收件人", parent=self)
            return
        # 独立线程发送，防止 SMTP 握手阻塞 UI
        def do_send():
            ok, err = self.app.send_email(
                sender, password, receiver,
                subject="黄金监控 — 测试邮件",
                body="邮件提醒功能配置成功，此为测试邮件。"
            )
            if ok:
                self.after(0, lambda: messagebox.showinfo("成功", "测试邮件发送成功", parent=self))
            else:
                self.after(0, lambda: messagebox.showerror("发送失败", f"错误信息：{err}", parent=self))
        threading.Thread(target=do_send, daemon=True).start()

    def _on_opacity_change(self, value):
        try:
            self.opacity_value_label.config(text=f"{float(value):.2f}")
        except Exception:
            return

    def _save(self):
        try:
            interval = float(self.var_interval.get().strip())
            if interval <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "刷新间隔必须是有效的正数", parent=self)
            return

        opacity = float(self.var_opacity.get())
        if not (0.2 <= opacity <= 1.0):
            messagebox.showerror("错误", "透明度必须在 0.2 到 1.0 之间", parent=self)
            return

        def parse_enabled_value(enabled_var, value_var):
            if not enabled_var.get():
                return None
            try:
                return float(value_var.get().strip())
            except Exception:
                return None

        au_upper   = parse_enabled_value(self.var_au_upper_enabled,   self.var_au_upper_value)
        au_lower   = parse_enabled_value(self.var_au_lower_enabled,   self.var_au_lower_value)
        intl_upper = parse_enabled_value(self.var_intl_upper_enabled, self.var_intl_upper_value)
        intl_lower = parse_enabled_value(self.var_intl_lower_enabled, self.var_intl_lower_value)

        try:
            window_min = int(float(self.var_window_min.get().strip()))
            if window_min <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "沪金统计窗口必须是有效的正整数（分钟）", parent=self)
            return

        try:
            intl_window_min = int(float(self.var_intl_window_min.get().strip()))
            if intl_window_min <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "国际金统计窗口必须是有效的正整数（分钟）", parent=self)
            return

        try:
            extreme_threshold = float(self.var_extreme_threshold.get().strip())
            if extreme_threshold <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "沪金异动阈值必须是有效的正数", parent=self)
            return

        try:
            intl_extreme_threshold = float(self.var_intl_extreme_threshold.get().strip())
            if intl_extreme_threshold <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "国际金异动阈值必须是有效的正数", parent=self)
            return

        try:
            flash_times = int(float(self.var_flash_times.get().strip()))
            if flash_times < 1:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "闪烁次数必须是正整数", parent=self)
            return

        try:
            flash_interval = int(float(self.var_flash_interval.get().strip()))
            if flash_interval < 50:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "闪烁间隔必须是不小于 50 的整数（毫秒）", parent=self)
            return

        try:
            cooldown = int(float(self.var_cooldown.get().strip()))
            if cooldown < 1:
                raise ValueError()
        except Exception:
            messagebox.showerror("错误", "冷却时间必须是有效的正整数（秒）", parent=self)
            return

        new_config = {
            "refresh_interval":    interval,
            "opacity":             opacity,
            "au_upper_enabled":    au_upper is not None,
            "au_upper_value":      float(au_upper or 0.0),
            "au_lower_enabled":    au_lower is not None,
            "au_lower_value":      float(au_lower or 0.0),
            "intl_upper_enabled":  intl_upper is not None,
            "intl_upper_value":    float(intl_upper or 0.0),
            "intl_lower_enabled":  intl_lower is not None,
            "intl_lower_value":    float(intl_lower or 0.0),
            "extreme_enabled":           self.var_extreme_enabled.get(),
            "extreme_window_min":        window_min,
            "extreme_threshold":         extreme_threshold,
            "intl_extreme_window_min":   intl_window_min,
            "intl_extreme_threshold":    intl_extreme_threshold,
            "extreme_flash_times":       flash_times,
            "extreme_flash_interval_ms": flash_interval,
            "extreme_cooldown_sec":      cooldown,
            # 邮件
            "email_enabled":  self.var_email_enabled.get(),
            "email_sender":   self.var_email_sender.get().strip(),
            "email_password": self.var_email_password.get().strip(),
            "email_receiver": self.var_email_receiver.get().strip(),
        }

        self.app.apply_config(new_config)
        self.app.save_config()
        messagebox.showinfo("成功", "设置已保存并应用", parent=self)

    def _on_close(self):
        self.app.settings_window = None
        self.destroy()


class GoldTaskbarDoubleLine:
    def __init__(self):
        self.config = self.load_config()
        self.root   = tk.Tk()

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.bg_color              = "#000000"
        self.card_color            = "#101218"
        self.card_border           = "#2A2D36"
        self.card_highlight_color  = "#1B1F2A"
        self.card_border_highlight = "#3A4150"
        self.text_color            = "#F5F5F7"
        self.muted_color           = "#9AA0A6"
        self.up_color              = "#FF3B30"
        self.down_color            = "#00C853"
        self.font_family           = "Segoe UI"
        self.text_font_size        = 10
        self.flash_text_font_size  = 12
        self.arrow_font_size       = 15
        self.card_width            = 130
        self.card_height           = 80
        self.corner_radius         = 15

        self.root.configure(bg=self.bg_color)
        self.root.attributes("-transparentcolor", self.bg_color)
        self.root.attributes("-alpha", float(self.config.get("opacity", 0.55)))

        user32  = ctypes.windll.user32
        self.sw = user32.GetSystemMetrics(0)
        self.sh = user32.GetSystemMetrics(1)

        position = self._load_position()
        if position:
            x, y = position
        else:
            x = self.sw - self.card_width  - 20
            y = self.sh - self.card_height - 80
        self.root.geometry(f"{self.card_width}x{self.card_height}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.root, width=self.card_width, height=self.card_height,
            bg=self.bg_color, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.card_fill_items   = []
        self.card_border_items = []
        self._draw_card()

        self.au_icon = self.canvas.create_text(
            18, 20, text="Ⓐ", fill=self.text_color,
            font=(self.font_family, self.text_font_size, "bold"))
        self.au_value_text = self.canvas.create_text(
            36, 20, text="--", fill=self.text_color,
            font=(self.font_family, self.text_font_size, "bold"), anchor="w")
        self.au_arrow_text = self.canvas.create_text(
            120, 20, text="•", fill=self.muted_color,
            font=(self.font_family, self.arrow_font_size, "bold"), anchor="e")

        self.intl_icon = self.canvas.create_text(
            18, 44, text="Ⓖ", fill=self.text_color,
            font=(self.font_family, self.text_font_size, "bold"))
        self.intl_value_text = self.canvas.create_text(
            36, 44, text="--", fill=self.text_color,
            font=(self.font_family, self.text_font_size, "bold"), anchor="w")
        self.intl_arrow_text = self.canvas.create_text(
            120, 44, text="•", fill=self.muted_color,
            font=(self.font_family, self.arrow_font_size, "bold"), anchor="e")
        
        # 第三行：国际金人民币价格显示（样式与第二行统一）
        self.intl_cny_label = self.canvas.create_text(
            18, 64, text="G¥", fill=self.text_color,
            font=(self.font_family, self.text_font_size, "bold"))
        self.intl_cny_value_text = self.canvas.create_text(
            36, 64, text="--", fill=self.text_color,
            font=(self.font_family, self.text_font_size, "bold"), anchor="w")
        self.intl_cny_arrow_text = self.canvas.create_text(
            120, 64, text="•", fill=self.muted_color,
            font=(self.font_family, self.arrow_font_size, "bold"), anchor="e")

        self._bind_drag()

        # ===== Session =====
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Linux; arm_64; Android 10; TECNO KD7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.7204.23 YaBrowser/25.8.9.23.00 (beta) SA/3 Mobile Safari/537.36"
            ),
            "Accept":          "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection":      "keep-alive",
        })

        # ===== 价格监控目标 =====
        self.au_upper_target   = None
        self.au_lower_target   = 1130.00
        self.intl_upper_target = None
        self.intl_lower_target = None

        # 触发锁（单次穿越只通知一次）
        self.au_upper_triggered   = False
        self.au_lower_triggered   = False
        self.intl_upper_triggered = False
        self.intl_lower_triggered = False

        # 提醒冷却时间戳（防阈值附近反复触发，10 秒内不重复）
        self.au_upper_last_ts   = 0.0
        self.au_lower_last_ts   = 0.0
        self.intl_upper_last_ts = 0.0
        self.intl_lower_last_ts = 0.0
        self.alert_cooldown_sec = 10  # 由 apply_config 从配置覆盖

        # 邮件配置（由 apply_config 填充）
        self.email_enabled  = False
        self.email_sender   = ""
        self.email_password = ""
        self.email_receiver = ""

        # ===== 线程共享价格 =====
        self.au        = None
        self.prev_au   = None
        self.intl      = None
        self.prev_intl = None
        self.intl_cny  = None  # 国际金换算后的人民币价格（元/克）

        # ===== 异动检测 =====
        self.interval                = 2
        self.extreme_window_sec      = 300
        self.intl_extreme_window_sec = 300
        self.extreme_threshold       = 5.0
        self.intl_extreme_threshold  = 5.0
        self.extreme_enabled         = True
        self.extreme_flash_times     = 6
        self.extreme_flash_interval_ms = 150
        self.extreme_cooldown_sec    = 60
        self.au_history              = deque()
        self.intl_history            = deque()
        self.extreme_last_ts         = 0.0
        self.intl_extreme_last_ts    = 0.0
        self.flash_active            = False

        # 线程同步
        self._price_lock   = threading.Lock()
        self._action_queue = queue.Queue()

        self.apply_config(self.config)
        self.settings_window = None
        self.tray   = None
        self.hidden = False
        self._setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.data_thread = threading.Thread(target=self._data_fetch_loop, daemon=True)
        self.data_thread.start()

        self._update_ui_cycle()

    # ------------------------------------------------------------------ config

    def load_config(self):
        try:
            path = _config_path()
            if not os.path.exists(path):
                return DEFAULT_CONFIG.copy()
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return {**DEFAULT_CONFIG, **saved}
        except Exception:
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(_config_path(), "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception:
            return

    def apply_config(self, cfg):
        self.config   = {**self.config, **cfg}
        self.interval = float(self.config.get("refresh_interval", self.interval))
        self.root.attributes("-alpha", float(self.config.get("opacity", self.root.attributes("-alpha"))))

        def target(enabled_key, value_key):
            if not self.config.get(enabled_key, False):
                return None
            try:
                return float(self.config.get(value_key, 0.0))
            except Exception:
                return None

        self.au_upper_target   = target("au_upper_enabled",   "au_upper_value")
        self.au_lower_target   = target("au_lower_enabled",   "au_lower_value")
        self.intl_upper_target = target("intl_upper_enabled", "intl_upper_value")
        self.intl_lower_target = target("intl_lower_enabled", "intl_lower_value")

        self.extreme_window_sec      = int(self.config.get("extreme_window_min",      int(self.extreme_window_sec / 60))) * 60
        self.extreme_threshold       = float(self.config.get("extreme_threshold",     self.extreme_threshold))
        self.intl_extreme_window_sec = int(self.config.get("intl_extreme_window_min", int(self.intl_extreme_window_sec / 60))) * 60
        self.intl_extreme_threshold  = float(self.config.get("intl_extreme_threshold",self.intl_extreme_threshold))
        self.extreme_enabled         = bool(self.config.get("extreme_enabled",        self.extreme_enabled))
        self.extreme_flash_times     = int(self.config.get("extreme_flash_times",     self.extreme_flash_times))
        self.extreme_flash_interval_ms = int(self.config.get("extreme_flash_interval_ms", self.extreme_flash_interval_ms))
        self.extreme_cooldown_sec    = int(self.config.get("extreme_cooldown_sec",    self.extreme_cooldown_sec))

        self.alert_cooldown_sec = int(self.config.get("alert_cooldown_sec", self.alert_cooldown_sec))

        self.email_enabled  = bool(self.config.get("email_enabled",  self.email_enabled))
        self.email_sender   = str(self.config.get("email_sender",    self.email_sender))
        self.email_password = str(self.config.get("email_password",  self.email_password))
        self.email_receiver = str(self.config.get("email_receiver",  self.email_receiver))

        self.au_history.clear()
        self.intl_history.clear()

    # ------------------------------------------------------------------ tray

    def _setup_tray(self):
        try:
            img = Image.new("RGB", (64, 64), color=(18, 18, 18))
            d   = ImageDraw.Draw(img)
            d.ellipse([8, 8, 56, 56], fill=(255, 215, 0))
            d.text((22, 22), "Au", fill=(0, 0, 0))
        except Exception:
            img = None
        menu = (
            item("显示/隐藏", self._tray_toggle),
            item("设置",      self._tray_settings),
            item("退出",      self._tray_quit),
        )
        self.tray = pystray.Icon("GoldMonitor", img, "Gold Monitor", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def _tray_toggle(self,   icon=None, menu_item=None): self.root.after(0, self.toggle_visible)
    def _tray_settings(self, icon=None, menu_item=None): self.root.after(0, self.open_settings)
    def _tray_quit(self,     icon=None, menu_item=None): self.root.after(0, self.quit_app)

    def toggle_visible(self):
        if self.hidden:
            self.root.deiconify(); self.hidden = False
        else:
            self.root.withdraw();  self.hidden = True

    def open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
        self.settings_window = SettingsWindow(self.root, self)

    def quit_app(self):
        try:
            if self.tray is not None:
                self.tray.stop()
        except Exception:
            pass
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

    # ------------------------------------------------------------------ card drawing

    def _draw_card(self):
        for it in self.card_fill_items:   self.canvas.delete(it)
        for it in self.card_border_items: self.canvas.delete(it)
        self.card_fill_items   = []
        self.card_border_items = []
        r, (x1, y1, x2, y2) = self.corner_radius, (0, 0, self.card_width, self.card_height)
        cc, cb = self.card_color, self.card_border
        self.card_fill_items += [
            self.canvas.create_rectangle(x1+r, y1,     x2-r, y2,     fill=cc, outline=cc),
            self.canvas.create_rectangle(x1,   y1+r,   x2,   y2-r,   fill=cc, outline=cc),
            self.canvas.create_oval(x1,     y1,     x1+2*r, y1+2*r, fill=cc, outline=cc),
            self.canvas.create_oval(x2-2*r, y1,     x2,     y1+2*r, fill=cc, outline=cc),
            self.canvas.create_oval(x1,     y2-2*r, x1+2*r, y2,     fill=cc, outline=cc),
            self.canvas.create_oval(x2-2*r, y2-2*r, x2,     y2,     fill=cc, outline=cc),
        ]
        self.card_border_items += [
            self.canvas.create_rectangle(x1+r, y1+1,  x2-r, y1+2,  fill=cb, outline=cb),
            self.canvas.create_rectangle(x1+r, y2-2,  x2-r, y2-1,  fill=cb, outline=cb),
            self.canvas.create_rectangle(x1+1, y1+r,  x1+2, y2-r,  fill=cb, outline=cb),
            self.canvas.create_rectangle(x2-2, y1+r,  x2-1, y2-r,  fill=cb, outline=cb),
        ]

    def _apply_card_style(self, fill_color, border_color):
        for it in self.card_fill_items:   self.canvas.itemconfig(it, fill=fill_color,   outline=fill_color)
        for it in self.card_border_items: self.canvas.itemconfig(it, fill=border_color, outline=border_color)

    # ------------------------------------------------------------------ drag

    def _bind_drag(self):
        for w in (self.canvas, self.root):
            w.bind("<ButtonPress-1>",  self._start_drag)
            w.bind("<B1-Motion>",      self._on_drag)
            w.bind("<ButtonRelease-1>",self._end_drag)

    def _start_drag(self, event):
        self.drag_offset_x = event.x_root - self.root.winfo_x()
        self.drag_offset_y = event.y_root - self.root.winfo_y()

    def _on_drag(self, event):
        self.root.geometry(f"{self.card_width}x{self.card_height}"
                           f"+{event.x_root - self.drag_offset_x}"
                           f"+{event.y_root - self.drag_offset_y}")

    def _end_drag(self, event):
        self._save_position()

    # ------------------------------------------------------------------ position persistence

    def _save_position(self):
        try:
            self.config["window_x"] = self.root.winfo_x()
            self.config["window_y"] = self.root.winfo_y()
            self.save_config()
        except Exception:
            pass

    def _load_position(self):
        try:
            x = self.config.get("window_x")
            y = self.config.get("window_y")
            if x is None or y is None:
                return None
            return int(x), int(y)
        except Exception:
            return None

    # ------------------------------------------------------------------ data fetching

    def _fetch_au(self):
        """沪金价格：GET pcQueryGoldProduct，取 priceValue 字段。返回：价格（元/克）"""
        url     = "https://ms.jr.jd.com/gw2/generic/CreatorSer/pc/m/pcQueryGoldProduct"
        params  = {"reqData": '{"goldType":"2"}'}
        headers = {"Origin": "https://jdjr.jd.com", "Referer": "https://jdjr.jd.com/"}
        try:
            res = self.session.get(url, params=params, headers=headers, timeout=2)
            # print(res.json())
            res.raise_for_status()
            return float(res.json()["resultData"]["data"]["priceValue"])
        except KeyboardInterrupt:
            raise
        except Exception:
            return None

    def _fetch_intl(self):
        """国际金价格：POST getQuoteExtendUseUniqueCodeWithCache，取 lastPrice 字段。返回：价格（美元/盎司）"""
        url     = "https://ms.jr.jd.com/gw2/generic/CaiFuPC/pc/m/getQuoteExtendUseUniqueCodeWithCache"
        payload = {"ticket": "jd-jr-pc", "uniqueCode": "WG-XAUUSD"}
        try:
            res = self.session.post(url, json=payload, timeout=2)
            # print(res.json())
            res.raise_for_status()
            return float(json.loads(res.json()["resultData"]["data"])["lastPrice"])
        except KeyboardInterrupt:
            raise
        except Exception:
            return None

    def _fetch_exchange_rate(self):
        """获取美元兑人民币汇率。返回：汇率值，失败返回 None"""
        # 使用多个可能的 API 源获取汇率（按优先级排序）
        apis = [
            # API 1: 公开汇率 API (exchangerate-api.com) - 稳定可靠
            {
                "url": "https://api.exchangerate-api.com/v4/latest/USD",
                "method": "GET",
                "timeout": 5,
                "parser": lambda r: float(r.json().get("rates", {}).get("CNY", 0))
            },
            # API 2: 另一个公开汇率 API (备用)
            {
                "url": "https://open.er-api.com/v6/latest/USD",
                "method": "GET",
                "timeout": 5,
                "parser": lambda r: float(r.json().get("rates", {}).get("CNY", 0))
            }
        ]
        
        for api in apis:
            try:
                timeout = api.get("timeout", 5)
                res = self.session.get(api["url"], timeout=timeout)
                res.raise_for_status()
                rate = api["parser"](res)
                if rate and 6.0 <= rate <= 8.0:  # 合理汇率范围检查
                    return rate
            except Exception as e:
                print(f"汇率 API 失败：{api['url']}, 错误：{e}")
                continue
        
        # 如果所有 API 都失败，返回默认汇率（可在配置中调整）
        print("使用默认汇率：", self.config.get("default_exchange_rate", 7.28))
        return self.config.get("default_exchange_rate", 7.28)

    # ------------------------------------------------------------------ notifications

    def _notify(self, msg):
        """系统托盘通知。线程安全。"""
        if self.tray is not None:
            self.tray.notify(msg, "波动提醒")
        else:
            print(f"通知: {msg}")

    def send_email(self, sender, password, receiver, subject, body):
        """163 SMTP SSL 发送邮件。线程安全，任意线程可调用。
        返回 (True, "") 成功；(False, err_str) 失败。
        """
        try:
            msg            = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"]    = sender
            msg["To"]      = receiver
            with smtplib.SMTP_SSL("smtp.163.com", 465, timeout=10) as smtp:
                smtp.login(sender, password)
                smtp.sendmail(sender, [receiver], msg.as_string())
            return True, ""
        except Exception as e:
            return False, str(e)

    def _send_alert_email(self, subject, body):
        """异步发送提醒邮件，不阻塞 fetch 循环。"""
        if not self.email_enabled:
            return
        if not all([self.email_sender, self.email_password, self.email_receiver]):
            return
        threading.Thread(
            target=self.send_email,
            args=(self.email_sender, self.email_password,
                  self.email_receiver, subject, body),
            daemon=True
        ).start()

    # ------------------------------------------------------------------ alert logic

    def _check_alert(self, price, symbol):
        """价格阈值穿越检测。
        双重保护：
          1. 触发锁 — 单次穿越只触发一次，价格回落后重置。
          2. 冷却时间戳 — 即使连续穿越，两次通知间隔不短于 alert_cooldown_sec（默认 10 秒）。
        """
        if price is None:
            return
        now = time.time()

        # === 沪金 ===
        if symbol == "AU":
            if self.au_upper_target is not None:
                if price >= self.au_upper_target and not self.au_upper_triggered:
                    if now - self.au_upper_last_ts >= self.alert_cooldown_sec:
                        msg = f"Au {self.au_upper_target}，当前价格：{price:.2f}"
                        self._notify(msg)
                        self._send_alert_email("沪金提醒 — 上破", msg)
                        self.au_upper_last_ts = now
                    self.au_upper_triggered = True
                if price < self.au_upper_target:
                    self.au_upper_triggered = False

            if self.au_lower_target is not None:
                if price <= self.au_lower_target and not self.au_lower_triggered:
                    if now - self.au_lower_last_ts >= self.alert_cooldown_sec:
                        msg = f"Au {self.au_lower_target}，当前价格：{price:.2f}"
                        self._notify(msg)
                        self._send_alert_email("沪金提醒 — 下破", msg)
                        self.au_lower_last_ts = now
                    self.au_lower_triggered = True
                if price > self.au_lower_target:
                    self.au_lower_triggered = False

        # === 国际金 ===
        if symbol == "INTL":
            if self.intl_upper_target is not None:
                if price >= self.intl_upper_target and not self.intl_upper_triggered:
                    if now - self.intl_upper_last_ts >= self.alert_cooldown_sec:
                        msg = f"Gold {self.intl_upper_target}，当前价格：{price:.2f}"
                        self._notify(msg)
                        self._send_alert_email("国际提醒 — 上破", msg)
                        self.intl_upper_last_ts = now
                    self.intl_upper_triggered = True
                if price < self.intl_upper_target:
                    self.intl_upper_triggered = False

            if self.intl_lower_target is not None:
                if price <= self.intl_lower_target and not self.intl_lower_triggered:
                    if now - self.intl_lower_last_ts >= self.alert_cooldown_sec:
                        msg = f"Gold {self.intl_lower_target}，当前价格：{price:.2f}"
                        self._notify(msg)
                        self._send_alert_email("国际提醒 — 下破", msg)
                        self.intl_lower_last_ts = now
                    self.intl_lower_triggered = True
                if price > self.intl_lower_target:
                    self.intl_lower_triggered = False

    # ------------------------------------------------------------------ extreme movement

    def _track_au_extreme(self, price):
        if not self.extreme_enabled:
            return
        now = time.time()
        self.au_history.append((now, price))
        cutoff = now - self.extreme_window_sec
        while self.au_history and self.au_history[0][0] < cutoff:
            self.au_history.popleft()
        if len(self.au_history) < 2:
            return
        delta = price - self.au_history[0][1]
        if abs(delta) < self.extreme_threshold:
            return
        if now - self.extreme_last_ts < self.extreme_cooldown_sec:
            return
        self.extreme_last_ts = now
        self._action_queue.put(("flash", self.up_color if delta > 0 else self.down_color, self.extreme_flash_times))

    def _track_intl_extreme(self, price):
        if not self.extreme_enabled:
            return
        now = time.time()
        self.intl_history.append((now, price))
        cutoff = now - self.intl_extreme_window_sec
        while self.intl_history and self.intl_history[0][0] < cutoff:
            self.intl_history.popleft()
        if len(self.intl_history) < 2:
            return
        delta = price - self.intl_history[0][1]
        if abs(delta) < self.intl_extreme_threshold:
            return
        if now - self.intl_extreme_last_ts < self.extreme_cooldown_sec:
            return
        self.intl_extreme_last_ts = now
        self._action_queue.put(("flash", self.up_color if delta > 0 else self.down_color, self.extreme_flash_times))

    # ------------------------------------------------------------------ flash

    def _flash_text(self, color, times):
        if times <= 0 or self.flash_active:
            return
        self.flash_active = True
        items = [self.au_icon, self.au_value_text, self.intl_icon, self.intl_value_text,
                 self.intl_cny_label, self.intl_cny_value_text]
        total = times * 2

        def toggle(remaining):
            if remaining <= 0:
                for it in items:
                    self.canvas.itemconfig(it, fill=self.text_color,
                                           font=(self.font_family, self.text_font_size, "bold"))
                self._apply_card_style(self.card_color, self.card_border)
                self.flash_active = False
                return
            use_color = remaining % 2 == 0
            fill = color if use_color else self.text_color
            size = self.flash_text_font_size if use_color else self.text_font_size
            for it in items:
                self.canvas.itemconfig(it, fill=fill, font=(self.font_family, size, "bold"))
            if use_color:
                self._apply_card_style(self.card_highlight_color, self.card_border_highlight)
            else:
                self._apply_card_style(self.card_color, self.card_border)
            self.root.after(self.extreme_flash_interval_ms, lambda: toggle(remaining - 1))

        toggle(total)

    # ------------------------------------------------------------------ UI loop

    def _update_ui_cycle(self):
        """主线程：消费 action 队列 + 刷新价格显示（每 200 ms）。"""
        try:
            while True:
                action = self._action_queue.get_nowait()
                if action[0] == "flash":
                    self._flash_text(action[1], action[2])
        except queue.Empty:
            pass

        with self._price_lock:
            au        = self.au
            prev_au   = self.prev_au
            intl      = self.intl
            prev_intl = self.prev_intl
            intl_cny  = self.intl_cny

        if au is not None:
            self.canvas.itemconfig(self.au_value_text, text=f"{au:.2f}")
            if prev_au is not None:
                arrow = "↑" if au > prev_au else ("↓" if au < prev_au else "•")
                clr   = self.up_color if au > prev_au else (self.down_color if au < prev_au else self.muted_color)
                self.canvas.itemconfig(self.au_arrow_text, text=arrow, fill=clr)

        if intl is not None:
            self.canvas.itemconfig(self.intl_value_text, text=f"{intl:.2f}")
            if prev_intl is not None:
                arrow = "↑" if intl > prev_intl else ("↓" if intl < prev_intl else "•")
                clr   = self.up_color if intl > prev_intl else (self.down_color if intl < prev_intl else self.muted_color)
                self.canvas.itemconfig(self.intl_arrow_text, text=arrow, fill=clr)
        
        # 更新国际金人民币价格
        if intl_cny is not None:
            self.canvas.itemconfig(self.intl_cny_value_text, text=f"{intl_cny:.2f}")
            # 第三行也显示涨跌箭头（与国际金同步）
            if prev_intl is not None:
                arrow = "↑" if intl > prev_intl else ("↓" if intl < prev_intl else "•")
                clr   = self.up_color if intl > prev_intl else (self.down_color if intl < prev_intl else self.muted_color)
                self.canvas.itemconfig(self.intl_cny_arrow_text, text=arrow, fill=clr)

        self.root.after(200, self._update_ui_cycle)

    # ------------------------------------------------------------------ fetch loop

    def _data_fetch_loop(self):
        """后台线程：轮询价格。禁止在此调用任何 tkinter 对象。"""
        # 汇率缓存，避免频繁请求
        exchange_rate = None
        rate_last_update = 0
        rate_cache_duration = 300  # 汇率缓存 5 分钟
        
        while True:
            try:
                new_au   = self._fetch_au()
                new_intl = self._fetch_intl()
                
                # 获取汇率（用于将国际金从美元/盎司转换为元/克）
                current_time = time.time()
                if exchange_rate is None or (current_time - rate_last_update) > rate_cache_duration:
                    fetched_rate = self._fetch_exchange_rate()
                    if fetched_rate:
                        exchange_rate = fetched_rate
                        rate_last_update = current_time
                        print(f"汇率更新：{exchange_rate:.4f}")

                if new_au is not None:
                    with self._price_lock:
                        self.prev_au = self.au
                        self.au      = new_au
                    self._check_alert(new_au, "AU")
                    self._track_au_extreme(new_au)

                if new_intl is not None:
                    # 国际金换算：美元/盎司 → 元/克
                    # 1 金衡盎司 = 31.1035 克
                    if exchange_rate:
                        intl_cny_value = new_intl * exchange_rate / 31.1035
                    else:
                        intl_cny_value = None
                    
                    with self._price_lock:
                        self.prev_intl = self.intl
                        self.intl      = new_intl
                        self.intl_cny  = intl_cny_value
                    
                    self._check_alert(new_intl, "INTL")
                    self._track_intl_extreme(new_intl)

            except Exception as e:
                print(f"Data fetch loop error: {e}")

            time.sleep(self.interval + random.uniform(0.08, 0.7))

    # ------------------------------------------------------------------ run

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            try:
                self.root.destroy()
            except Exception:
                pass


if __name__ == "__main__":
    app = GoldTaskbarDoubleLine()
    app.run()