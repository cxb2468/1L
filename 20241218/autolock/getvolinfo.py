import wmi
import sys
import ctypes
import hashlib


def get_drives():
    c = wmi.WMI()
    drives = dict()
    for drive in c.Win32_LogicalDisk(DriveType=2):  # DriveType 2 可移动驱动器 理论上移动硬盘也包含但是太大不方便
        try:
            drives[drive.DeviceID] = drive.VolumeSerialNumber
        except Exception as e:
            print(f"Error retrieving SN for '{drive.DeviceID}': {e}")
    return drives


if __name__ == "__main__":
    d = get_drives()
    s = hashlib.sha256()
    print('检测到 ' + str(len(d)) + ' 个已连接的可移动卷.')
    if '--sha256' in sys.argv[1:]:
        print('卷标及序列号 SHA 256 列表：')
        for i, o in d.items():
            s.update(str.encode(o))
            print(i, s.hexdigest())
            s = hashlib.sha256()
    else:
        print('卷标及序列号列表：')
        for i, o in d.items():
            print(i, o)
    print('按任意键或关闭窗口退出...')
    input()
