import configparser
import time
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw
import threading
import ctypes
import sys


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    daily_salary = float(config['work']['daily_salary'])
    start_time = config['work']['start_time']
    end_time = config['work']['end_time']
    return daily_salary, start_time, end_time


def calculate_earnings(daily_salary, start_time, end_time):
    now = datetime.now()
    today = now.date()

    start_time = datetime.strptime(start_time, "%H:%M").time()
    end_time = datetime.strptime(end_time, "%H:%M").time()

    start_datetime = datetime.combine(today, start_time)
    end_datetime = datetime.combine(today, end_time)

    if now < start_datetime:
        earned_amount = 0.00
        time_to_end = end_datetime - start_datetime
    elif now > end_datetime:
        worked_time = end_datetime - start_datetime
        time_to_end = timedelta(0)
    else:
        worked_time = now - start_datetime
        time_to_end = end_datetime - now

    if now >= start_datetime and now <= end_datetime:
        worked_hours = worked_time.total_seconds() / 3600
        hourly_rate = daily_salary / ((end_datetime - start_datetime).total_seconds() / 3600)
        earned_amount = worked_hours * hourly_rate
    else:
        earned_amount = 0.00

    hours, remainder = divmod(time_to_end.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    return round(earned_amount, 4), int(hours), int(minutes), int(seconds)


def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image


def update_tray_icon(icon, config_file):
    daily_salary, start_time, end_time = read_config(config_file)
    while True:
        print("Updating icon..." , datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Add this line for debugging
        earnings, hours, minutes, seconds = calculate_earnings(daily_salary, start_time, end_time)
        icon.title = f"已经赚取: ¥{earnings:.2f}\n距离下班: {hours}小时{minutes}分{seconds}秒"
        time.sleep(1)


def on_quit(icon):
    icon.stop()


def about():
    ctypes.windll.user32.MessageBoxW(0, "该程序由Swback制作", "关于", 0)


def main():
    config_file = 'config.ini'
    icon_image = create_image(64, 64, 'black', 'white')
    icon = pystray.Icon("earnings", icon_image, "请确保config.ini存在")
    icon.menu = pystray.Menu(
        pystray.MenuItem("关于", about),
        pystray.MenuItem("退出", on_quit)
    )
    icon_thread = threading.Thread(target=update_tray_icon, args=(icon, config_file), daemon=True)
    icon_thread.start()

    icon.run()


if __name__ == "__main__":
    main()