# utils.py
import socket
import ipaddress
import re


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_default_ip_range(local_ip):
    """根据本机IP生成默认扫描段（如 192.168.1.1-254）"""
    try:
        parts = local_ip.strip().split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.1-254"
    except:
        return "192.168.1.1-254"


def validate_ip_range(ip_range):
    """判断用户输入的IP范围是否合规"""
    pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3})\.(\d{1,3})-(\d{1,3})$"
    match = re.match(pattern, ip_range)
    if not match:
        return False
    base, start, end = match.groups()
    return 1 <= int(start) <= 254 and 1 <= int(end) <= 254 and int(start) <= int(end)


def parse_ip_range(ip_range):
    """将形如 192.168.1.10-50 的字符串解析为 IP 列表"""
    ip_list = []
    try:
        pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3})\.(\d{1,3})-(\d{1,3})$"
        match = re.match(pattern, ip_range)
        if match:
            base, start, end = match.groups()
            start = int(start)
            end = int(end)
            for i in range(start, end + 1):
                ip_list.append(f"{base}.{i}")
        else:
            ip_list.append(ip_range)
    except:
        pass
    return ip_list
