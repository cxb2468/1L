import wmi
import json
import time
import ctypes
import hashlib

sha256 = hashlib.sha256()
target_psn = set()
psn_num = 0
config = {}
sleep = 1
reload_delay = 10


def r_config():
    global target_psn
    global config
    global sleep
    global reload_delay
    with open('config.json', 'r') as f:
        config = json.load(f)
        target_psn = set(config['psn256'])
        sleep = config['sleep']
        reload_delay = config['reload_delay']


# 锁定电脑
def lock_workstation():
    ctypes.windll.user32.LockWorkStation()


# 获取所有连接的移动存储卷的卷序列号
def get_drives():
    global sha256
    c = wmi.WMI()
    drives = set()
    for drive in c.Win32_LogicalDisk(DriveType=2):  # DriveType 2 可移动驱动器 理论上移动硬盘也包含但是太大不方便
        try:
            sha256.update(str.encode(drive.VolumeSerialNumber))
            drives.add(sha256.hexdigest())
            sha256 = hashlib.sha256()
        except Exception as e:
            print(f"Error retrieving SN for '{drive.DeviceID}': {e}")
    return drives


# 主监控循环
def monitor():
    global psn_num
    while True:
        drives = get_drives()
        psn_num += 1
        if psn_num == reload_delay:
            psn_num = 0
            r_config()
        target_connected = target_psn.intersection(drives)

        if target_psn:
            if not target_connected:
                if ctypes.windll.user32.GetForegroundWindow() != 0:
                    lock_workstation()
                    continue

        time.sleep(sleep)


if __name__ == "__main__":
    r_config()
    monitor()
